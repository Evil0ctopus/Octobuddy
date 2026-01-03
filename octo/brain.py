import random

def calculate_xp_gain(level, base=5, step=10):
    """
    Dynamic XP gain:
    - Starts at +5 XP
    - Increases by +1 every 10 levels
    """
    return base + (level // step)


def update_state_from_event(state, event_type, data, config):
    state = dict(state)  # shallow copy
    level = state.get("level", 1)

    # Calculate dynamic XP gain for this level
    dynamic_xp = calculate_xp_gain(level)

    # -----------------------------
    # Base Python study event
    # -----------------------------
    if event_type == "studied_python":
        state["xp"] += dynamic_xp
        state["study_events"] = state.get("study_events", 0) + 1

    # -----------------------------
    # Cybersecurity + WGU events
    # (scaled versions of your old values)
    # -----------------------------
    if event_type == "studied_security_plus":
        state["xp"] += dynamic_xp * 2
        state["security_plus_study"] = state.get("security_plus_study", 0) + 1

    if event_type == "finished_class":
        state["xp"] += dynamic_xp * 10
        state["classes_finished"] = state.get("classes_finished", 0) + 1

    if event_type == "did_tryhackme":
        state["xp"] += dynamic_xp * 3
        state["tryhackme_rooms"] = state.get("tryhackme_rooms", 0) + 1

    if event_type == "passed_lab":
        state["xp"] += dynamic_xp * 5
        state["labs_passed"] = state.get("labs_passed", 0) + 1

    # -----------------------------
    # New cybersecurity events
    # -----------------------------
    if event_type == "bug_bounty":
        state["xp"] += dynamic_xp * 8
        state["bug_bounties"] = state.get("bug_bounties", 0) + 1

    if event_type == "ctf_challenge":
        state["xp"] += dynamic_xp * 6
        state["ctf_challenges"] = state.get("ctf_challenges", 0) + 1

    if event_type == "code_review":
        state["xp"] += dynamic_xp * 4
        state["code_reviews"] = state.get("code_reviews", 0) + 1

    if event_type == "read_documentation":
        state["xp"] += dynamic_xp * 2
        state["docs_read"] = state.get("docs_read", 0) + 1

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
