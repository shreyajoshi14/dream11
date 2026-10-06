from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"
PROC_DIR = ROOT / "data" / "processed"
ART_DIR = ROOT / "model_artifacts"
CRICSHEET_URL = "https://cricsheet.org/downloads/all_json.zip"

# HARD RULE from the problem statement: nothing after this date is used for training.
TRAIN_CUTOFF = "2024-06-30"

SQUAD_WINDOW = 10      # squad proxy = players used by the team in its last N matches
TEAM_MAX_PER_ROLE = 8  # Dream11 role range 1-8

for _d in (RAW_DIR, PROC_DIR, ART_DIR):
    _d.mkdir(parents=True, exist_ok=True)
