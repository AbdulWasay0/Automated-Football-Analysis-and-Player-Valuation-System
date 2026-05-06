"""One-click setup script for the Football Player Intelligence System."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run(command: list[str]) -> None:
    subprocess.check_call(command, cwd=ROOT)


def main() -> None:
    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10 or newer is required.")
    if sys.version_info >= (3, 12):
        print("Warning: Python 3.10 or 3.11 is recommended for this XGBoost stack.")

    for path in ["data/raw", "data/processed", "models", "src"]:
        (ROOT / path).mkdir(parents=True, exist_ok=True)

    print("Installing requirements...")
    run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    from src.data_loader import build_enriched_data, find_data_dir
    from src.model_trainer import train_all

    data_dir = find_data_dir()
    print(f"Using CSV directory: {data_dir}")
    print("Building processed datasets...")
    build_enriched_data(force=True)
    print("Training models...")
    train_all(force=True)
    print("Setup complete. Run: python main.py")


if __name__ == "__main__":
    main()

