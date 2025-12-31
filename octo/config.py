import yaml
from pathlib import Path

def load_config():
    # Load YAML normally
    with Path("config.yaml").open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # --- Dynamic XP System -----------------------------------------
    xp_system = config.get("xp_system", {})

    max_level = xp_system.get("max_level", 100)
    base_xp = xp_system.get("base_xp", 50)          # XP needed for level 2
    multiplier = xp_system.get("multiplier", 2)     # XP doubles every level

    xp_levels = []

    for level in range(1, max_level + 1):
        if level == 1:
            threshold = 0
        else:
            # Level 2 = base_xp
            # Level 3 = base_xp * 2
            # Level 4 = base_xp * 4
            # ...
            threshold = base_xp * (multiplier ** (level - 2))

        xp_levels.append({
            "level": level,
            "threshold": threshold
        })

    # Inject generated XP table into config
    config["xp_levels"] = xp_levels

    return config


CONFIG = load_config()
