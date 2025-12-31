import random

def update_state_from_event(state, event_type, data, config):
    state = dict(state)  # shallow copy

    # -----------------------------
    # Base Python study event
    # -----------------------------
    if event_type == "studied_python":
        state["xp"] += config["xp_per_study_event"]
        state["study_events"] = state.get("study_events", 0) + 1

    # -----------------------------
    # New cybersecurity + WGU events
    # -----------------------------
    if event_type == "studied_security_plus":
        state["xp"] += 20
        state["security_plus_study"] = state.get("security_plus_study", 0) + 1

    if event_type == "finished_class":
        state["xp"] += 100
        state["classes_finished"] = state.get("classes_finished", 0) + 1

    if event_type == "did_tryhackme":
        state["xp"] += 30
        state["tryhackme_rooms"] = state.get("tryhackme_rooms", 0) + 1

    if event_type == "passed_lab":
        state["xp"] += 50
        state["labs_passed"] = state.get("labs_passed", 0) + 1

    # -----------------------------
    # Level calculation
    # -----------------------------
    current_level = state.get("level", 1)
    for lv in sorted(config["xp_levels"], key=lambda x: x["threshold"]):
        if state["xp"] >= lv["threshold"]:
            current_level = lv["level"]
    state["level"] = current_level

    return state


def get_mood(state, config):
    xp = state.get("xp", 0)

    # Normal mood selection
    selected_mood = "hyper"
    for mood in config["moods"]:
        if mood["min_xp"] <= xp < mood["max_xp"]:
            selected_mood = mood["name"]
            break

    # Random mood swing (5% chance)
    if random.random() < 0.05:
        return random.choice([m["name"] for m in config["moods"]])

    return selected_mood


def get_stage(state, config):
    xp = state.get("xp", 0)
    for stage in config.get("stages", []):
        if stage["min_xp"] <= xp < stage["max_xp"]:
            return stage["name"]

    return "Unknown"
