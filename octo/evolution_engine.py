"""
Evolution Engine: Mutation, Personality Drift, and Evolution Systems

This module implements advanced evolution mechanics following the project's
architectural patterns:
- Pure functions accepting (state, config)
- Logic/presentation separation
- Explicit state transformations

Systems:
1. Mutations - Random trait acquisition based on activity and evolution vars
2. Personality Drift - Gradual personality shifts based on activity patterns
3. Evolution Triggers - Special evolution events from unique conditions
4. Evolution Variables - Open-ended variables (curiosity, creativity, etc.)

No XP or levels - evolution is continuous and unbounded.
"""

import random
from typing import Dict, Any, List, Tuple, Optional

# Import mutation rules (all mutation logic is in mutation_rules.py)
from .mutation_rules import (
    calculate_mutation_chance,
    select_mutation,
    get_mutation_modifiers,
    get_mutation_display_name,
)


# =============================================================================
# MUTATION SYSTEM (using mutation_rules)
# =============================================================================

def apply_mutation(state: Dict[str, Any], config: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Attempt to apply a mutation to the state.
    
    Uses mutation_rules for all logic - this is just orchestration.
    
    Returns (updated_state, mutation_name) where mutation_name is None if no mutation occurred.
    """
    state = dict(state)  # Immutable pattern
    
    chance = calculate_mutation_chance(state, config)
    
    if random.random() < chance:
        mutation_key = select_mutation(state, config)
        
        if mutation_key:
            mutations = state.get("mutations", [])
            mutations.append(mutation_key)
            state["mutations"] = mutations
            
            # Track mutation history (activity-based)
            history = state.get("evolution_history", [])
            total_activity = (
                state.get("study_events", 0) +
                state.get("security_plus_study", 0) +
                state.get("classes_finished", 0) +
                state.get("tryhackme_rooms", 0) +
                state.get("labs_passed", 0)
            )
            history.append({
                "type": "mutation",
                "mutation": mutation_key,
                "total_activity": total_activity,
            })
            state["evolution_history"] = history
            
            return state, get_mutation_display_name(mutation_key)
    
    return state, None


# =============================================================================
# EVOLUTION VARIABLES SYSTEM
# =============================================================================

def apply_evolution_var_drift(
    state: Dict[str, Any],
    event_type: str,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Apply drift to evolution variables based on events.
    
    Evolution variables (curiosity, creativity, confidence, etc.) drift
    continuously based on activities and interactions.
    """
    state = dict(state)
    ev_vars = dict(state.get("evolution_vars", {}))
    
    # Get drift rates from config
    drift_config = config.get("evolution", {}).get("drift_rates", {})
    learning_rate = drift_config.get("learning_event", 0.1)
    interaction_rate = drift_config.get("interaction_event", 0.05)
    milestone_rate = drift_config.get("milestone_event", 0.5)
    
    # Apply event-specific drifts
    if event_type == "studied_python":
        ev_vars["curiosity"] = ev_vars.get("curiosity", 5.0) + learning_rate
        ev_vars["focus"] = ev_vars.get("focus", 5.0) + learning_rate * 0.8
        ev_vars["chaos"] = ev_vars.get("chaos", 5.0) - learning_rate * 0.3
    
    elif event_type == "studied_security_plus":
        ev_vars["focus"] = ev_vars.get("focus", 5.0) + learning_rate * 1.2
        ev_vars["curiosity"] = ev_vars.get("curiosity", 5.0) + learning_rate * 0.6
        ev_vars["calmness"] = ev_vars.get("calmness", 5.0) + learning_rate * 0.4
    
    elif event_type == "finished_class":
        ev_vars["confidence"] = ev_vars.get("confidence", 5.0) + milestone_rate
        ev_vars["creativity"] = ev_vars.get("creativity", 5.0) + milestone_rate * 0.6
        ev_vars["empathy"] = ev_vars.get("empathy", 5.0) + milestone_rate * 0.3
    
    elif event_type == "did_tryhackme":
        ev_vars["chaos"] = ev_vars.get("chaos", 5.0) + learning_rate
        ev_vars["creativity"] = ev_vars.get("creativity", 5.0) + learning_rate * 0.7
        ev_vars["calmness"] = ev_vars.get("calmness", 5.0) - learning_rate * 0.5
    
    elif event_type == "passed_lab":
        ev_vars["confidence"] = ev_vars.get("confidence", 5.0) + milestone_rate * 0.7
        ev_vars["focus"] = ev_vars.get("focus", 5.0) + milestone_rate * 0.5
    
    elif event_type in ["fed", "petted"]:
        ev_vars["empathy"] = ev_vars.get("empathy", 5.0) + interaction_rate
        ev_vars["calmness"] = ev_vars.get("calmness", 5.0) + interaction_rate
    
    # Apply variable interactions from config
    interactions = config.get("evolution", {}).get("interactions", {})
    
    chaos_val = ev_vars.get("chaos", 5.0)
    focus_val = ev_vars.get("focus", 5.0)
    curiosity_val = ev_vars.get("curiosity", 5.0)
    
    # Chaos reduces calmness
    if "chaos_reduces_calmness" in interactions:
        rate = interactions["chaos_reduces_calmness"]
        ev_vars["calmness"] = ev_vars.get("calmness", 5.0) - (chaos_val - 5.0) * rate
    
    # Focus reduces chaos
    if "focus_reduces_chaos" in interactions:
        rate = interactions["focus_reduces_chaos"]
        ev_vars["chaos"] = ev_vars.get("chaos", 5.0) - (focus_val - 5.0) * rate
    
    # Curiosity boosts creativity
    if "curiosity_boosts_creativity" in interactions:
        rate = interactions["curiosity_boosts_creativity"]
        ev_vars["creativity"] = ev_vars.get("creativity", 5.0) + (curiosity_val - 5.0) * rate
    
    state["evolution_vars"] = ev_vars
    return state


# =============================================================================
# PERSONALITY DRIFT SYSTEM (Legacy - kept for compatibility)
# =============================================================================

def calculate_personality_drift(state: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate personality drift based on recent activity patterns.
    
    Personality drift tracks tendencies:
    - analytical: security/lab focus
    - chaotic: tryhackme rooms
    - studious: python study events
    - ambitious: class completions
    
    Returns updated state with drift scores.
    """
    state = dict(state)
    
    # Initialize drift if not present
    drift = state.get("personality_drift", {
        "analytical": 0.0,
        "chaotic": 0.0,
        "studious": 0.0,
        "ambitious": 0.0,
    })
    
    # Activity counters
    security_study = state.get("security_plus_study", 0)
    labs_passed = state.get("labs_passed", 0)
    tryhackme_rooms = state.get("tryhackme_rooms", 0)
    study_events = state.get("study_events", 0)
    classes_finished = state.get("classes_finished", 0)
    
    # Calculate drift (normalized 0.0 to 1.0)
    total_activity = security_study + labs_passed + tryhackme_rooms + study_events + classes_finished
    
    if total_activity > 0:
        drift["analytical"] = (security_study + labs_passed) / total_activity
        drift["chaotic"] = tryhackme_rooms / total_activity
        drift["studious"] = study_events / total_activity
        drift["ambitious"] = classes_finished / total_activity
    
    # Apply decay to prevent old patterns from dominating (80% retention)
    for key in drift:
        drift[key] *= 0.98
    
    state["personality_drift"] = drift
    
    return state


def get_dominant_drift(state: Dict[str, Any]) -> Optional[str]:
    """
    Get the dominant personality drift tendency.
    
    Returns drift type string or None if no clear dominance.
    """
    drift = state.get("personality_drift", {})
    
    if not drift:
        return None
    
    max_drift = max(drift.values())
    
    # Require at least 30% tendency to be dominant
    if max_drift < 0.30:
        return None
    
    for drift_type, value in drift.items():
        if value == max_drift:
            return drift_type
    
    return None


# =============================================================================
# EVOLUTION TRIGGER SYSTEM
# =============================================================================

def check_evolution_triggers(state: Dict[str, Any], config: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Check for special evolution triggers based on unique conditions.
    
    Triggers:
    - "ascension": 500+ total activity with 3+ mutations
    - "chaos_master": 50+ tryhackme rooms with chaos mutation
    - "scholar": 10+ classes finished with analytical drift
    - "hybrid_form": Balanced drift across all personality types
    
    Returns (updated_state, trigger_name) where trigger_name is None if no trigger.
    """
    state = dict(state)
    total_activity = (
        state.get("study_events", 0) +
        state.get("security_plus_study", 0) +
        state.get("classes_finished", 0) * 5 +
        state.get("tryhackme_rooms", 0) +
        state.get("labs_passed", 0)
    )
    mutations = state.get("mutations", [])
    drift = state.get("personality_drift", {})
    triggered_evolutions = set(state.get("evolution_triggers", []))
    
    trigger_name = None
    
    # Ascension trigger
    if (total_activity >= 500 and len(mutations) >= 3 and 
        "ascension" not in triggered_evolutions):
        trigger_name = "ascension"
    
    # Chaos Master trigger
    elif (state.get("tryhackme_rooms", 0) >= 50 and
          "chaos_incarnate" in mutations and
          "chaos_master" not in triggered_evolutions):
        trigger_name = "chaos_master"
    
    # Scholar trigger
    elif (state.get("classes_finished", 0) >= 10 and
          drift.get("analytical", 0) > 0.5 and
          "scholar" not in triggered_evolutions):
        trigger_name = "scholar"
    
    # Hybrid Form trigger (balanced personality)
    elif (all(v > 0.2 for v in drift.values()) and
          "hybrid_form" not in triggered_evolutions):
        trigger_name = "hybrid_form"
    
    if trigger_name:
        triggers = list(triggered_evolutions)
        triggers.append(trigger_name)
        state["evolution_triggers"] = triggers
        
        # Add to history (activity-based)
        history = state.get("evolution_history", [])
        history.append({
            "type": "evolution_trigger",
            "trigger": trigger_name,
            "total_activity": total_activity,
        })
        state["evolution_history"] = history
    
    return state, trigger_name


# =============================================================================
# MAIN EVOLUTION ENGINE ORCHESTRATION
# =============================================================================

def process_evolution_cycle(
    state: Dict[str, Any],
    config: Dict[str, Any],
    event_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run a complete evolution cycle: variables, mutations, drift, and triggers.
    
    This is called after each event to update evolution systems.
    
    Args:
        state: Current state
        config: Configuration
        event_type: Optional event that triggered this cycle
    
    Returns updated state with evolution changes and any special events.
    """
    state = dict(state)
    
    # Track what happened this cycle
    evolution_events = []
    
    # 0. Apply evolution variable drift (if event provided)
    if event_type:
        state = apply_evolution_var_drift(state, event_type, config)
        
        # Also apply personality trait drift
        from .personality import apply_trait_drift
        state = apply_trait_drift(state, event_type, config)
    
    # 1. Check for mutations
    state, mutation_name = apply_mutation(state, config)
    if mutation_name:
        evolution_events.append(("mutation", mutation_name))
    
    # 2. Update personality drift (legacy system)
    state = calculate_personality_drift(state, config)
    
    # 3. Check evolution triggers
    state, trigger_name = check_evolution_triggers(state, config)
    if trigger_name:
        evolution_events.append(("evolution_trigger", trigger_name))
    
    # Store events for UI to potentially display
    if evolution_events:
        state["last_evolution_events"] = evolution_events
    
    return state


def get_evolution_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a summary of current evolution state for display/debugging.
    
    Returns dict with mutations, drift, triggers, and modifiers.
    """
    return {
        "mutations": state.get("mutations", []),
        "mutation_count": len(state.get("mutations", [])),
        "personality_drift": state.get("personality_drift", {}),
        "dominant_drift": get_dominant_drift(state),
        "evolution_triggers": state.get("evolution_triggers", []),
        "modifiers": get_mutation_modifiers(state),
        "evolution_history": state.get("evolution_history", []),
    }
