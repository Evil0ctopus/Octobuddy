import json
from pathlib import Path

STATE_FILE = Path("octo_state.json")

DEFAULT_STATE = {
    "xp": 0,
    "level": 1,
    "study_events": 0,
    "name": "OctoBuddy",
}

def load_state():
    if STATE_FILE.exists():
        try:
            with STATE_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # If state is corrupted, start fresh
            return DEFAULT_STATE.copy()
    return DEFAULT_STATE.copy()

def save_state(state):
    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
