import os
from pathlib import Path


CONFIG_DIR = Path(__file__).resolve().parent
LOCAL_EXEC_DIR = CONFIG_DIR.parent
PROJECT_DIR = LOCAL_EXEC_DIR.parent
WORKSPACE_DIR = PROJECT_DIR.parent

VIDEO_SRC = str(LOCAL_EXEC_DIR / "input_video" / "Sample_Video.mp4")
OUT_VIDEO = str(LOCAL_EXEC_DIR / "output_video" / "sample_result.avi")
OUTPUT_FOLDER = str(WORKSPACE_DIR / "output")
OUT_PITCH_MAP = os.path.join(OUTPUT_FOLDER, "pitch_map.png")
OUT_PITCH_VIDEO = os.path.join(OUTPUT_FOLDER, "pitch_map.avi")
OUT_STATS = os.path.join(OUTPUT_FOLDER, "stats.txt")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ROBOFLOW_API_KEY = os.environ.get("ROBOFLOW_API_KEY", "5lupAJ0ZuQ3Z3DH8ic8g")
ROBOFLOW_API_URL = os.environ.get("ROBOFLOW_API_URL", "https://serverless.roboflow.com")
PLAYER_DETECTION_MODEL_ID = "football-players-detection-3zvbc/11"
FIELD_DETECTION_MODEL_ID = "football-field-detection-f07vi/14"
DETECTION_BACKEND = os.environ.get("FOOTBALL_DETECTION_BACKEND", "auto").lower()
PLAYER_DETECTION_CONFIDENCE = float(os.environ.get("PLAYER_DETECTION_CONFIDENCE", "0.3"))
FIELD_DETECTION_CONFIDENCE = float(os.environ.get("FIELD_DETECTION_CONFIDENCE", "0.3"))
FIELD_KEYPOINT_CONFIDENCE = float(os.environ.get("FIELD_KEYPOINT_CONFIDENCE", "0.5"))
FIELD_REFRESH_FRAMES = max(1, int(os.environ.get("FIELD_REFRESH_FRAMES", "5")))
ROBOFLOW_HTTP_TIMEOUT = float(os.environ.get("ROBOFLOW_HTTP_TIMEOUT", "45"))
ROBOFLOW_JPEG_QUALITY = int(os.environ.get("ROBOFLOW_JPEG_QUALITY", "85"))
BALL_POSSESSION_CARRY_FRAMES = int(os.environ.get("BALL_POSSESSION_CARRY_FRAMES", "15"))
BALL_ASSIGNMENT_MAX_DISTANCE = float(os.environ.get("BALL_ASSIGNMENT_MAX_DISTANCE", "95"))

PITCH_PANEL_HEIGHT = 800
PITCH_PADDING = 50
PITCH_SCALE = 0.1
MODEL_CLASSES = {
     "ball":0,
     "goalkepper":1,
     "player":2,
     "referee":3,
     "team1":4,
     "team2":5,
     "active_player":6
}
