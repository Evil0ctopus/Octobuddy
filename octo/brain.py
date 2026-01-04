import random

def update_state_from_event(state, event_type, data, config):
    """Update state based on event - track activity counts only."""
    state = dict(state)  # shallow copy

    # -----------------------------
    # Track activity events (no XP)
    # -----------------------------
    if event_type == "studied_python":
        state["study_events"] = state.get("study_events", 0) + 1

    if event_type == "studied_security_plus":
        state["security_plus_study"] = state.get("security_plus_study", 0) + 1

    if event_type == "finished_class":
        state["classes_finished"] = state.get("classes_finished", 0) + 1

    if event_type == "did_tryhackme":
        state["tryhackme_rooms"] = state.get("tryhackme_rooms", 0) + 1

    if event_type == "passed_lab":
        state["labs_passed"] = state.get("labs_passed", 0) + 1

    return state


def get_mood(state, config):
    """Calculate mood based on total activity and mutations."""
    from .evolution_engine import get_mutation_modifiers
    
    # Calculate total activity as proxy for progression
    total_activity = (
        state.get("study_events", 0) +
        state.get("security_plus_study", 0) +
        state.get("classes_finished", 0) * 5 +  # Classes worth more
        state.get("tryhackme_rooms", 0) +
        state.get("labs_passed", 0)
    )
    
    # Map activity to mood index
    moods = config.get("moods", [])
    if not moods:
        return "curious"
    
    # Simple progression: one mood per 20 activities
    mood_index = min(total_activity // 20, len(moods) - 1)
    selected_mood = moods[mood_index]["name"]
    
    # Get mutation modifiers
    modifiers = get_mutation_modifiers(state)
    chaos_factor = modifiers["chaos_factor"]
    
    # Random mood swing (base 5% chance, increased by chaos_factor)
    swing_chance = 0.05 * chaos_factor
    if random.random() < swing_chance:
        return random.choice([m["name"] for m in moods])
    
    return selected_mood


def get_stage(state, config):
    """Calculate evolution stage based on total activity and triggers."""
    # Check for special evolution triggers first
    triggers = set(state.get("evolution_triggers", []))
    
    if "ascension" in triggers or "hybrid_form" in triggers:
        return "Fully Evolved Hybrid"
    
    # Calculate total activity
    total_activity = (
        state.get("study_events", 0) +
        state.get("security_plus_study", 0) +
        state.get("classes_finished", 0) * 5 +
        state.get("tryhackme_rooms", 0) +
        state.get("labs_passed", 0)
    )
    
    # Stage progression based on activity thresholds
    if total_activity < 10:
        return "Baby"
    elif total_activity < 50:
        return "Learner"
    elif total_activity < 150:
        # Check personality drift for specialization
        from .evolution_engine import get_dominant_drift
        dominant = get_dominant_drift(state)
        if dominant == "chaotic" and state.get("personality_drift", {}).get("chaotic", 0) > 0.5:
            return "Chaotic Gremlin"
        elif dominant == "analytical" and state.get("personality_drift", {}).get("analytical", 0) > 0.5:
            return "Analyst"
        else:
            return "Learner"  # Still learning
    elif total_activity < 300:
        # Advanced stages
        dominant = get_dominant_drift(state)
        if dominant == "chaotic":
            return "Chaotic Gremlin"
        elif dominant == "analytical":
            return "Analyst"
        else:
            return "Analyst"  # Default advanced stage
    else:
        return "Fully Evolved Hybrid"
