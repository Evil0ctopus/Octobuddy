import json
from pathlib import Path

STATE_FILE = Path("octo_state.json")

DEFAULT_STATE = {
    # Activity tracking
    "study_events": 0,
    "security_plus_study": 0,
    "classes_finished": 0,
    "tryhackme_rooms": 0,
    "labs_passed": 0,
    "name": "OctoBuddy",
    
    # Evolution variables (open-ended, no caps)
    "evolution_vars": {
        "curiosity": 5.0,      # Interest in learning, exploring
        "creativity": 5.0,     # Novel solutions, playfulness
        "confidence": 5.0,     # Assertiveness, self-assurance
        "calmness": 5.0,       # Composure, patience
        "chaos": 5.0,          # Unpredictability, spontaneity
        "empathy": 5.0,        # Understanding, caring
        "focus": 5.0,          # Attention, concentration
    },
    
    # Mutation system
    "mutations": [],
    
    # Personality traits (continuous, unbounded)
    "personality_traits": {
        "humor": 5.0,          # Playfulness, wit
        "boldness": 5.0,       # Risk-taking, courage
        "shyness": 5.0,        # Reserved, cautious
        "analytical": 5.0,     # Logical thinking
        "chaotic": 5.0,        # Disorder preference
        "studious": 5.0,       # Love of learning
        "ambitious": 5.0,      # Drive, goals
    },
    
    # Legacy personality drift (kept for compatibility)
    "personality_drift": {
        "analytical": 0.0,
        "chaotic": 0.0,
        "studious": 0.0,
        "ambitious": 0.0,
    },
    
    # Evolution tracking
    "evolution_triggers": [],
    "evolution_history": [],
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
