import yaml
from pathlib import Path
from octo.core import OctoBuddy

def load_config():
    with Path("config.yaml").open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    config = load_config()
    buddy = OctoBuddy(config)

    # For now, just simulate a "studied_python" event
    buddy.handle_event("studied_python")
