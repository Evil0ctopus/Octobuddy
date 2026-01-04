import yaml
from pathlib import Path

def load_config():
    # Load YAML normally
    with Path("config.yaml").open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Config loaded as-is (no XP system generation)
    return config


CONFIG = load_config()
