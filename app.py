from __future__ import annotations

import csv
import importlib
import importlib.util
import json
import shutil
import subprocess
import sys
import threading
import time
import unicodedata
import uuid
from datetime import datetime
from pathlib import Path
from textwrap import wrap
from typing import Any

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"
OUTPUT_DIR = STATIC_DIR / "outputs"

TRANSFER_PACKAGE_NAME = "transfer_fee_prediction_src"
FOOTBALL_JOBS: dict[str, dict[str, Any]] = {}
FOOTBALL_JOBS_LOCK = threading.Lock()

ALLOWED_VIDEO_EXTENSIONS = {"mp4", "mov", "avi", "mkv", "webm"}
MAX_UPLOAD_MB = 800


app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-for-production"
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024


for folder in (UPLOAD_DIR, OUTPUT_DIR):
    folder.mkdir(parents=True, exist_ok=True)


def find_transfer_dir() -> Path:
    """Find the transfer project by its Python package files, not folder name."""
    for predictor_file in BASE_DIR.rglob("src/predictor.py"):
        src_dir = predictor_file.parent
        project_dir = src_dir.parent
        if (src_dir / "__init__.py").exists() and (src_dir / "constants.py").exists():
            return project_dir
    raise FileNotFoundError("Could not find transfer project: expected src/predictor.py")


def find_football_dir() -> Path:
    """Find the football CV project by its local_exec entry point."""
    for main_file in BASE_DIR.rglob("main_test.py"):
        local_exec_dir = main_file.parent
        if (
            (local_exec_dir / "config" / "config.py").exists()
            and (local_exec_dir / "utils").exists()
            and (local_exec_dir / "team_assigner").exists()
        ):
            return local_exec_dir
    raise FileNotFoundError("Could not find football project: expected local_exec/main_test.py")


TRANSFER_DIR = find_transfer_dir()
FOOTBALL_DIR = find_football_dir()


def _add_import_path(path: Path) -> None:
    resolved = str(path.resolve())
    if resolved not in sys.path:
        sys.path.insert(0, resolved)


def load_transfer_predictor():
    """Load the transfer package from its project folder without relying on `src`."""
    transfer_src = TRANSFER_DIR / "src"
    init_file = transfer_src / "__init__.py"

    if not init_file.exists():
        raise FileNotFoundError(f"Transfer package not found: {transfer_src}")

    if TRANSFER_PACKAGE_NAME not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            TRANSFER_PACKAGE_NAME,
            init_file,
            submodule_search_locations=[str(transfer_src)],
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load transfer package from {transfer_src}")

        package = importlib.util.module_from_spec(spec)
        sys.modules[TRANSFER_PACKAGE_NAME] = package
        spec.loader.exec_module(package)

    predictor = importlib.import_module(f"{TRANSFER_PACKAGE_NAME}.predictor")
    return predictor.predict_transfer_fee


def load_transfer_module(module_name: str):
    load_transfer_predictor()
    return importlib.import_module(f"{TRANSFER_PACKAGE_NAME}.{module_name}")


def allowed_video(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS


def result_basename(prefix: str) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{stamp}_{uuid.uuid4().hex[:8]}"


def public_static_path(path: Path) -> str:
    return path.relative_to(STATIC_DIR).as_posix()


def format_duration(seconds: float | int | None) -> str:
    try:
        total = max(0, int(seconds or 0))
    except (TypeError, ValueError):
        total = 0
    minutes, secs = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def update_football_job(job_id: str, **updates: Any) -> None:
    with FOOTBALL_JOBS_LOCK:
        job = FOOTBALL_JOBS.setdefault(job_id, {})
        job.update(updates)
        total = int(job.get("total_frames") or 0)
        processed = int(job.get("processed_frames") or 0)
        started_at = float(job.get("started_at") or time.time())
        elapsed = max(0.0, time.time() - started_at)
        percent = 0.0
        if total > 0:
            percent = min(100.0, (processed / total) * 100)
        elif job.get("status") == "completed":
            percent = 100.0
        job["percent"] = round(percent, 1)
        job["elapsed"] = format_duration(elapsed)
        job["remaining_frames"] = max(0, total - processed) if total else None


def football_job_snapshot(job_id: str) -> dict[str, Any] | None:
    with FOOTBALL_JOBS_LOCK:
        job = FOOTBALL_JOBS.get(job_id)
        if job is None:
            return None
        snapshot = dict(job)
    return snapshot


class FootballProgress:
    def __init__(self, job_id: str, iterable: Any, *args: Any, total: int | None = None, **_kwargs: Any):
        self.job_id = job_id
        self.iterable = iterable
        self.total = total
        if total:
            update_football_job(job_id, total_frames=int(total))

    def __iter__(self):
        processed = int(football_job_snapshot(self.job_id).get("processed_frames") or 0)
        for item in self.iterable:
            yield item
            processed += 1
            update_football_job(
                self.job_id,
                status="processing",
                message="Processing video frames...",
                processed_frames=processed,
            )

    def close(self) -> None:
        return None


def parse_football_stats(stats_path: Path) -> dict[str, Any]:
    stats: dict[str, Any] = {}
    raw_lines: list[str] = []

    if not stats_path.exists():
        return {"raw": [], "message": "No stats file was generated."}

    for line in stats_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        clean = line.strip()
        if not clean or set(clean) == {"="}:
            continue
        raw_lines.append(clean)
        if ":" not in clean:
            continue
        key, value = clean.split(":", 1)
        stats[key.strip()] = value.strip()

    return {"raw": raw_lines, "items": stats}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def write_stats_csv(path: Path, stats: dict[str, Any]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        for key, value in stats.get("items", {}).items():
            writer.writerow([key, value])


def pdf_safe_text(value: Any) -> str:
    text = str(value)
    text = text.replace("\u20ac", "EUR ").replace("\u2192", "->").replace("\u00a0", " ")
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def pdf_escape(value: Any) -> str:
    text = pdf_safe_text(value)
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def write_simple_pdf(path: Path, title: str, sections: list[tuple[str, list[tuple[str, Any]]]]) -> None:
    """Write a compact one-page PDF report without external dependencies."""
    commands: list[str] = []

    def text_line(x: int, y: int, text: Any, font: str = "F1", size: int = 10) -> None:
        commands.append(f"BT /{font} {size} Tf {x} {y} Td ({pdf_escape(text)}) Tj ET")

    y = 742
    text_line(72, y, title, font="F2", size=20)
    y -= 26
    text_line(72, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", size=9)
    y -= 34

    for section_title, rows in sections:
        if y < 96:
            break
        text_line(72, y, section_title, font="F2", size=13)
        y -= 18
        for key, value in rows:
            line = f"{pdf_safe_text(key)}: {pdf_safe_text(value)}"
            for part in wrap(line, width=86) or [""]:
                if y < 72:
                    break
                text_line(86, y, part, size=10)
                y -= 14
            if y < 72:
                break
        y -= 12

    stream = "\n".join(commands).encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    content = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(content))
        content.extend(f"{index} 0 obj\n".encode("ascii"))
        content.extend(obj)
        content.extend(b"\nendobj\n")

    xref_offset = len(content)
    content.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    content.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        content.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    content.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )

    path.write_bytes(content)


def write_transfer_pdf(path: Path, result: dict[str, Any]) -> None:
    rows = list(result.get("summary", {}).items())
    if "predicted_fee_display" in result:
        rows.extend([
            ("Player", result.get("player", "N/A")),
            ("From Club", result.get("from_club") or "N/A"),
            ("Buying Club", result.get("to_club", "N/A")),
            ("Predicted Fee", result.get("predicted_fee_display", "N/A")),
        ])

    sections = [
        (
            "Prediction Summary",
            rows or [("Result", result.get("title", "Transfer report"))],
        ),
        ("Player Context", list(result.get("insights", {}).items())),
        ("Explanation / Feature Importance", list(result.get("breakdown", {}).items())),
    ]
    if result.get("rows"):
        sections.append(("Rows", [(row.get("name", row.get("season", "Item")), row) for row in result["rows"][:12]]))
    write_simple_pdf(path, result.get("title", "Transfer Fee Prediction Report"), sections)


def format_eur_m(value: float | int | None) -> str:
    try:
        amount = float(value or 0)
    except (TypeError, ValueError):
        amount = 0.0
    return f"\u20ac{amount / 1_000_000:.1f}M"


def fix_euro_text(value: Any) -> Any:
    if isinstance(value, str):
        return value.replace("\u00e2\u201a\u00ac", "\u20ac")
    if isinstance(value, dict):
        return {key: fix_euro_text(item) for key, item in value.items()}
    if isinstance(value, list):
        return [fix_euro_text(item) for item in value]
    return value


def clean_value(value: Any) -> Any:
    if value is None:
        return "N/A"
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass
    if isinstance(value, float):
        return round(value, 2)
    return fix_euro_text(value)


def player_summary(player: dict[str, Any]) -> dict[str, Any]:
    return {
        "Name": player.get("name", "N/A"),
        "Age": player.get("age", "N/A"),
        "Position": player.get("sub_position") or player.get("position_category") or "N/A",
        "Club": player.get("current_club", "N/A"),
        "League": player.get("current_league", "N/A"),
        "Nationality": player.get("nationality", "N/A"),
        "Goals": player.get("goals_total", "N/A"),
        "Assists": player.get("assists_total", "N/A"),
        "Goals / 90": player.get("goals_per_90", "N/A"),
        "Assists / 90": player.get("assists_per_90", "N/A"),
        "Games Played": player.get("games_played", "N/A"),
        "Current Value": format_eur_m(player.get("current_value_eur", 0)),
        "Peak Value": format_eur_m(player.get("peak_value_eur", 0)),
    }


def dataframe_rows(df: Any, limit: int = 20) -> list[dict[str, Any]]:
    columns = [
        "name", "age", "current_club", "sub_position", "position_category",
        "goals_total", "assists_total", "current_value_eur", "score",
    ]
    rows = []
    for row in df.head(limit).to_dict("records"):
        item = {key: clean_value(row.get(key)) for key in columns if key in row}
        if "current_value_eur" in item:
            item["current_value_eur"] = format_eur_m(row.get("current_value_eur", 0))
        rows.append(item)
    return rows


def ffmpeg_executable() -> str | None:
    """Return a system or bundled FFmpeg executable if one is available."""
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg

    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def convert_video_for_browser(source: Path, target: Path) -> Path:
    """Create a browser-friendly H.264 MP4 copy when possible."""
    if not source.exists():
        raise FileNotFoundError(f"Processed video was not created: {source}")

    ffmpeg = ffmpeg_executable()
    if ffmpeg:
        command = [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-an",
            "-vf",
            "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(target),
        ]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            if target.exists() and target.stat().st_size > 0:
                return target
        except subprocess.CalledProcessError as exc:
            error = (exc.stderr or exc.stdout or str(exc)).strip()
            raise RuntimeError(f"FFmpeg could not create a browser-playable MP4: {error}") from exc

    try:
        import cv2

        capture = cv2.VideoCapture(str(source))
        if capture.isOpened():
            fps = capture.get(cv2.CAP_PROP_FPS) or 25
            width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            writer = cv2.VideoWriter(
                str(target),
                cv2.VideoWriter_fourcc(*"mp4v"),
                fps,
                (width, height),
            )
            while True:
                ok, frame = capture.read()
                if not ok:
                    break
                writer.write(frame)
            capture.release()
            writer.release()
            if target.exists() and target.stat().st_size > 0:
                return target
    except Exception:
        pass

    # If ffmpeg is unavailable, keep the original output as the downloadable source.
    fallback = target.with_suffix(source.suffix)
    shutil.copy2(source, fallback)
    return fallback


def run_football_analysis(uploaded_video: Path, job_id: str | None = None) -> dict[str, Any]:
    _add_import_path(FOOTBALL_DIR)
    football_main = importlib.import_module("main_test")

    run_id = result_basename("football")
    original_output_video = OUTPUT_DIR / f"{run_id}_processed.avi"
    original_pitch_video = OUTPUT_DIR / f"{run_id}_pitch.avi"
    pitch_map = OUTPUT_DIR / f"{run_id}_pitch_map.png"
    stats_txt = OUTPUT_DIR / f"{run_id}_stats.txt"

    # The CV module is CLI-style and reads module globals. Set only the IO globals
    # around its existing main() entry point so the core logic remains untouched.
    football_main.VIDEO_SRC = str(uploaded_video)
    football_main.OUT_VIDEO = str(original_output_video)
    football_main.OUT_PITCH_VIDEO = str(original_pitch_video)
    football_main.OUT_PITCH_MAP = str(pitch_map)
    football_main.OUT_STATS = str(stats_txt)
    football_main.OUTPUT_FOLDER = str(OUTPUT_DIR)

    original_tqdm = getattr(football_main, "tqdm", None)
    if job_id:
        total_frames, fps = football_main.get_number_of_frames(str(uploaded_video))
        update_football_job(
            job_id,
            status="processing",
            message="Preparing video analysis...",
            total_frames=int(total_frames or 0),
            processed_frames=0,
            fps=int(fps or 0),
        )

        def progress_tqdm(iterable: Any, *args: Any, **kwargs: Any) -> FootballProgress:
            return FootballProgress(job_id, iterable, *args, **kwargs)

        football_main.tqdm = progress_tqdm

    try:
        football_main.main()
    finally:
        if job_id and original_tqdm is not None:
            football_main.tqdm = original_tqdm

    if job_id:
        update_football_job(job_id, status="finalizing", message="Preparing web outputs...")
    display_video = convert_video_for_browser(original_output_video, OUTPUT_DIR / f"{run_id}_processed.mp4")
    display_pitch_video = None
    if original_pitch_video.exists():
        display_pitch_video = convert_video_for_browser(original_pitch_video, OUTPUT_DIR / f"{run_id}_pitch.mp4")

    stats = parse_football_stats(stats_txt)
    stats_json = OUTPUT_DIR / f"{run_id}_stats.json"
    stats_csv = OUTPUT_DIR / f"{run_id}_stats.csv"
    write_json(stats_json, stats)
    write_stats_csv(stats_csv, stats)

    return {
        "input_video": uploaded_video.name,
        "input_video_path": public_static_path(uploaded_video),
        "video": display_video.name,
        "video_path": public_static_path(display_video),
        "stats": stats,
        "stats_txt": stats_txt.name if stats_txt.exists() else None,
        "stats_json": stats_json.name,
        "stats_csv": stats_csv.name,
        "pitch_map": pitch_map.name if pitch_map.exists() else None,
        "pitch_map_path": public_static_path(pitch_map) if pitch_map.exists() else None,
        "pitch_video": display_pitch_video.name if display_pitch_video else None,
        "pitch_video_path": public_static_path(display_pitch_video) if display_pitch_video else None,
        "original_pitch_video": original_pitch_video.name if original_pitch_video.exists() else None,
        "original_video": original_output_video.name if original_output_video.exists() else None,
    }


def predict_transfer(payload: dict[str, str]) -> dict[str, Any]:
    predict_transfer_fee = load_transfer_predictor()

    result = predict_transfer_fee(
        player_name=payload["player_name"],
        from_club=payload.get("from_club", ""),
        to_club=payload["to_club"],
        model=payload.get("model", "xgboost"),
    )

    player_row = result.get("player_row", {})
    insights = {
        "Age": player_row.get("age", payload.get("age") or "N/A"),
        "Position": player_row.get("sub_position") or player_row.get("position") or payload.get("position") or "N/A",
        "Goals": player_row.get("goals_total", payload.get("goals") or "N/A"),
        "Assists": player_row.get("assists_total", payload.get("assists") or "N/A"),
        "Current Value": format_eur_m(player_row.get("current_value_eur", 0)),
        "Peak Value": format_eur_m(player_row.get("peak_value_eur", 0)),
        "Games Played": player_row.get("games_played", "N/A"),
    }

    return {
        "kind": "prediction",
        "title": "Transfer Fee Prediction Report",
        "player": result.get("player"),
        "from_club": result.get("from_club"),
        "to_club": result.get("to_club"),
        "predicted_fee": result.get("predicted_fee", 0),
        "predicted_fee_display": format_eur_m(result.get("predicted_fee", 0)),
        "breakdown": fix_euro_text(result.get("breakdown", {})),
        "insights": insights,
    }


def run_transfer_action(action: str, payload: dict[str, str]) -> dict[str, Any]:
    if action == "search":
        module = load_transfer_module("player_search")
        player = fix_euro_text(module.search_player(payload["player_name"]))
        return {
            "kind": "profile",
            "title": "Player Search Result",
            "summary": player_summary(player),
        }

    if action == "predict":
        return predict_transfer(payload)

    if action == "future":
        module = load_transfer_module("performance_predictor")
        rows, insights = module.predict_future_performance(
            payload["player_name"],
            int(payload.get("seasons") or 6),
        )
        clean_rows = []
        for row in rows:
            clean_rows.append({
                "season": row.get("season"),
                "age": row.get("age"),
                "goals": row.get("goals"),
                "assists": row.get("assists"),
                "value": format_eur_m(row.get("value", 0)),
                "is_peak": "Yes" if row.get("is_peak") else "No",
            })
        return {
            "kind": "table",
            "title": "Future Performance Prediction",
            "summary": fix_euro_text(insights),
            "rows": clean_rows,
        }

    if action == "filter":
        module = load_transfer_module("player_search")
        result_df = module.advanced_filter(
            budget_m=float(payload["budget_m"]) if payload.get("budget_m") else None,
            max_age=int(payload["max_age"]) if payload.get("max_age") else None,
            position=payload.get("position") or "Any",
            min_goals=int(payload.get("min_goals") or 0),
            min_assists=int(payload.get("min_assists") or 0),
            league=payload.get("league") or "Any",
            nationality=payload.get("nationality") or None,
            foot=payload.get("foot") or "Any",
            sort_by=payload.get("sort_by") or "score",
        )
        return {
            "kind": "table",
            "title": f"Advanced Filter Results ({len(result_df)} players)",
            "summary": {"Returned Players": len(result_df), "Showing": min(20, len(result_df))},
            "rows": dataframe_rows(result_df, 20),
        }

    if action == "compare":
        compare_module = load_transfer_module("player_compare")
        predictor_module = load_transfer_module("predictor")
        data_module = load_transfer_module("data_loader")
        verdict = fix_euro_text(compare_module.compare_players(payload["player_one"], payload["player_two"]))
        df = data_module.load_data()
        p1 = predictor_module.find_player(payload["player_one"], df).to_dict()
        p2 = predictor_module.find_player(payload["player_two"], df).to_dict()
        return {
            "kind": "comparison",
            "title": "Player Comparison",
            "summary": verdict,
            "players": [player_summary(p1), player_summary(p2)],
        }

    if action == "market":
        module = load_transfer_module("market_insights")
        data = module.generate_market_insights()
        return {
            "kind": "market",
            "title": "Market Insights & Reports",
            "summary": {
                "Average Position Groups": len(data["avg_by_position"]),
                "Top Players": len(data["top_players"]),
                "Undervalued Players": len(data["undervalued"]),
            },
            "market": {
                "Average Value by Position": {str(k): format_eur_m(v) for k, v in data["avg_by_position"].items()},
                "Value vs Age Curve": {str(k): format_eur_m(v) for k, v in data["age_curve"].items()},
                "Top Spending Clubs": {str(k): format_eur_m(v) for k, v in data["spenders"].items()},
                "Most Transferred": {str(k): clean_value(v) for k, v in data["most_transferred"].items()},
            },
            "rows": dataframe_rows(data["top_players"], 10),
        }

    if action == "simulate":
        module = load_transfer_module("transfer_simulator")
        result = fix_euro_text(module.simulate_transfer(
            payload["player_name"],
            payload.get("from_club", ""),
            payload["to_club"],
            float(payload["budget_m"]) if payload.get("budget_m") else None,
        ))
        return {
            "kind": "simulation",
            "title": "Transfer Simulation",
            "summary": {
                "Player": result.get("player"),
                "From Club": result.get("from_club"),
                "To Club": result.get("to_club"),
                "Transfer Fee": format_eur_m(result.get("fee", 0)),
                "Weekly Wages": format_eur_m(result.get("weekly_wages", 0)),
                "Contract Years": result.get("contract_years"),
                "From Strength": result.get("from_strength"),
                "To Strength": result.get("to_strength"),
            },
        }

    raise ValueError("Choose a valid transfer module action.")


def start_football_worker(job_id: str, upload_path: Path) -> None:
    def worker() -> None:
        try:
            update_football_job(
                job_id,
                status="processing",
                message="Starting video analysis...",
                started_at=time.time(),
                processed_frames=0,
            )
            result = run_football_analysis(upload_path, job_id=job_id)
            total = int(football_job_snapshot(job_id).get("total_frames") or 0)
            update_football_job(
                job_id,
                status="completed",
                message="Analysis complete.",
                processed_frames=total,
                result=result,
                percent=100,
            )
        except Exception as exc:
            update_football_job(
                job_id,
                status="failed",
                message=f"Football analysis failed: {exc}",
                error=str(exc),
            )

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()


@app.route("/")
def index():
    return render_template("index.html", active_page="home")


@app.route("/football", methods=["GET", "POST"])
def football():
    result = None
    if request.method == "POST":
        file = request.files.get("video")
        if not file or not file.filename:
            flash("Please choose a video file before starting analysis.", "error")
            return redirect(url_for("football"))
        if not allowed_video(file.filename):
            flash("Unsupported video format. Use MP4, MOV, AVI, MKV, or WEBM.", "error")
            return redirect(url_for("football"))

        filename = f"{result_basename('upload')}_{secure_filename(file.filename)}"
        upload_path = UPLOAD_DIR / filename
        file.save(upload_path)

        try:
            result = run_football_analysis(upload_path)
            flash("Football analysis completed successfully.", "success")
        except Exception as exc:
            flash(f"Football analysis failed: {exc}", "error")

    return render_template("football.html", active_page="football", result=result)


@app.route("/football/start", methods=["POST"])
def football_start():
    file = request.files.get("video")
    if not file or not file.filename:
        return jsonify({"ok": False, "error": "Please choose a video file before starting analysis."}), 400
    if not allowed_video(file.filename):
        return jsonify({"ok": False, "error": "Unsupported video format. Use MP4, MOV, AVI, MKV, or WEBM."}), 400

    filename = f"{result_basename('upload')}_{secure_filename(file.filename)}"
    upload_path = UPLOAD_DIR / filename
    file.save(upload_path)

    job_id = uuid.uuid4().hex
    update_football_job(
        job_id,
        status="queued",
        message="Video uploaded. Waiting to start...",
        input_video=filename,
        started_at=time.time(),
        processed_frames=0,
        total_frames=0,
    )
    start_football_worker(job_id, upload_path)
    return jsonify({"ok": True, "job_id": job_id, "status_url": url_for("football_status", job_id=job_id)})


@app.route("/football/status/<job_id>")
def football_status(job_id: str):
    job = football_job_snapshot(job_id)
    if job is None:
        return jsonify({"ok": False, "error": "Job not found."}), 404
    payload = {
        "ok": True,
        "job_id": job_id,
        "status": job.get("status", "queued"),
        "message": job.get("message", ""),
        "processed_frames": job.get("processed_frames", 0),
        "total_frames": job.get("total_frames", 0),
        "remaining_frames": job.get("remaining_frames"),
        "percent": job.get("percent", 0),
        "elapsed": job.get("elapsed", "0s"),
        "result_url": url_for("football_result", job_id=job_id) if job.get("status") == "completed" else None,
        "error": job.get("error"),
    }
    return jsonify(payload)


@app.route("/football/result/<job_id>")
def football_result(job_id: str):
    job = football_job_snapshot(job_id)
    if job is None:
        flash("Football analysis job was not found.", "error")
        return redirect(url_for("football"))
    if job.get("status") == "failed":
        flash(job.get("message", "Football analysis failed."), "error")
        return redirect(url_for("football"))
    if job.get("status") != "completed":
        return render_template("football.html", active_page="football", result=None, job=job)
    flash("Football analysis completed successfully.", "success")
    return render_template("football.html", active_page="football", result=job.get("result"))


@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    result = None
    active_action = request.form.get("action", "predict") if request.method == "POST" else "predict"
    form_data = request.form.to_dict() if request.method == "POST" else {}

    if request.method == "POST":
        action = form_data.get("action", "predict")
        required_by_action = {
            "search": ["player_name"],
            "predict": ["player_name", "to_club"],
            "future": ["player_name"],
            "filter": [],
            "compare": ["player_one", "player_two"],
            "market": [],
            "simulate": ["player_name", "to_club"],
        }
        required = required_by_action.get(action, [])
        missing = [field for field in required if not form_data.get(field)]
        if missing:
            flash("Please fill the required fields for this action.", "error")
            return render_template(
                "transfer.html",
                active_page="transfer",
                result=None,
                form_data=form_data,
                active_action=active_action,
            )

        try:
            result = run_transfer_action(action, form_data)
            output_name = f"{result_basename('transfer')}.pdf"
            write_transfer_pdf(OUTPUT_DIR / output_name, result)
            result["download_file"] = output_name
            flash("Transfer module action completed.", "success")
        except Exception as exc:
            flash(f"Transfer action failed: {exc}", "error")

    return render_template(
        "transfer.html",
        active_page="transfer",
        result=result,
        form_data=form_data,
        active_action=active_action,
    )


@app.route("/download/<path:filename>")
def download(filename: str):
    safe_name = secure_filename(Path(filename).name)
    return send_from_directory(OUTPUT_DIR, safe_name, as_attachment=True)


@app.errorhandler(413)
def file_too_large(_error):
    flash(f"File is too large. Maximum upload size is {MAX_UPLOAD_MB} MB.", "error")
    return redirect(request.referrer or url_for("football"))


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
