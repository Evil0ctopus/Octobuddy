"""
Mutation Rules: Data-driven mutation system for OctoBuddy

This module contains all mutation definitions and logic as pure, data-driven rules.
Following OctoBuddy's architecture:
- Pure functions accepting (state, config)
- Data-driven configuration (mutations defined as data, not code)
- Explicit modifier application

All mutation logic lives here. Other modules import rules but don't define them.
"""

from typing import Dict, Any, List, Optional
import random


# =============================================================================
# MUTATION DEFINITIONS (Data-driven configuration)
# =============================================================================

MUTATION_POOL: Dict[str, Dict[str, Any]] = {
    "speed_learner": {
        "name": "Speed Learner",
        "description": "Gains XP 10% faster",
        "rarity": "common",
        "modifiers": {
            "xp_modifier": 1.10,
        },
    },
    "night_owl": {
        "name": "Night Owl",
        "description": "Extra energetic at night",
        "rarity": "common",
        "modifiers": {
            "mood_influence": {"hyper": 0.15},
        },
    },
    "chaos_incarnate": {
        "name": "Chaos Incarnate",
        "description": "Unpredictable mood swings intensify",
        "rarity": "uncommon",
        "modifiers": {
            "chaos_factor": 2.0,
        },
    },
    "analytical_mind": {
        "name": "Analytical Mind",
        "description": "Better at understanding complex topics",
        "rarity": "uncommon",
        "modifiers": {
            "xp_modifier_security": 1.25,
        },
    },
    "unstoppable": {
        "name": "Unstoppable",
        "description": "Massive XP boost on milestones",
        "rarity": "rare",
        "modifiers": {
            "xp_modifier_milestone": 1.50,
        },
    },
    "personality_fracture": {
        "name": "Personality Fracture",
        "description": "Multiple personalities emerge",
        "rarity": "rare",
        "modifiers": {
            "special_flags": ["multi_personality"],
        },
    },
    "transcendent": {
        "name": "Transcendent",
        "description": "Has achieved enlightenment",
        "rarity": "legendary",
        "modifiers": {
            "xp_modifier": 1.25,
            "special_flags": ["wisdom_bonus"],
        },
    },
}


# Rarity weights for mutation selection
RARITY_WEIGHTS: Dict[str, int] = {
    "common": 50,
    "uncommon": 25,
    "rare": 10,
    "legendary": 2,
}


# Mutation chance configuration (activity-based)
MUTATION_CHANCE_CONFIG = {
    "base_chance": 0.005,              # 0.5% base chance
    "max_chance": 0.05,                # 5% max chance
    "activity_scaling": 0.00009,       # Increase per activity point
    "diminishing_penalty": 0.1,        # Penalty per existing mutation
    "minimum_chance": 0.3,             # Minimum chance multiplier
}


# =============================================================================
# MUTATION CHANCE CALCULATION
# =============================================================================

def calculate_mutation_chance(state: Dict[str, Any], config: Dict[str, Any]) -> float:
    """
    Calculate chance of mutation occurring based on total activity and existing mutations.
    
    Pure function using data-driven configuration.
    
    Args:
        state: Current state with activity counters and mutations
        config: OctoBuddy config (currently unused, for future extensibility)
    
    Returns:
        Probability between 0.0 and 1.0
    """
    # Calculate total activity
    total_activity = (
        state.get("study_events", 0) +
        state.get("security_plus_study", 0) +
        state.get("classes_finished", 0) * 5 +  # Classes worth more
        state.get("tryhackme_rooms", 0) +
        state.get("labs_passed", 0)
    )
    existing_mutations = len(state.get("mutations", []))
    
    # Base chance increases with activity
    base_chance = min(
        MUTATION_CHANCE_CONFIG["max_chance"],
        MUTATION_CHANCE_CONFIG["base_chance"] + 
        (total_activity * MUTATION_CHANCE_CONFIG["activity_scaling"])
    )
    
    # Reduce chance if already have many mutations (diminishing returns)
    mutation_penalty = max(
        MUTATION_CHANCE_CONFIG["minimum_chance"],
        1.0 - (existing_mutations * MUTATION_CHANCE_CONFIG["diminishing_penalty"])
    )
    
    return base_chance * mutation_penalty


# =============================================================================
# MUTATION SELECTION
# =============================================================================

def get_available_mutations(state: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Get mutations that haven't been acquired yet.
    
    Args:
        state: Current state with list of acquired mutations
    
    Returns:
        Dict of available mutation definitions
    """
    existing_mutations = set(state.get("mutations", []))
    
    return {
        key: mutation 
        for key, mutation in MUTATION_POOL.items()
        if key not in existing_mutations
    }


def select_mutation(state: Dict[str, Any], config: Dict[str, Any]) -> Optional[str]:
    """
    Select a random mutation based on rarity weights.
    
    Pure function - uses weighted random selection based on rarity.
    
    Args:
        state: Current state (to filter out acquired mutations)
        config: OctoBuddy config (currently unused)
    
    Returns:
        Mutation key or None if no mutations available
    """
    available_mutations = get_available_mutations(state)
    
    if not available_mutations:
        return None
    
    # Build weighted pool based on rarity
    weighted_pool = []
    for key, mutation in available_mutations.items():
        rarity = mutation.get("rarity", "common")
        weight = RARITY_WEIGHTS.get(rarity, 10)
        weighted_pool.extend([key] * weight)
    
    return random.choice(weighted_pool) if weighted_pool else None


# =============================================================================
# MODIFIER APPLICATION
# =============================================================================

def get_mutation_modifiers(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate all active mutation modifiers for XP, mood, etc.
    
    Pure function - scans acquired mutations and aggregates their modifiers.
    
    Args:
        state: Current state with list of acquired mutations
    
    Returns:
        Dict of modifier types and their cumulative effects
    """
    mutations = state.get("mutations", [])
    
    # Initialize with neutral modifiers
    modifiers = {
        "xp_modifier": 1.0,
        "xp_modifier_security": 1.0,
        "xp_modifier_milestone": 1.0,
        "chaos_factor": 1.0,
        "mood_influence": {},
        "special_flags": [],
    }
    
    # Aggregate modifiers from all acquired mutations
    for mutation_key in mutations:
        mutation = MUTATION_POOL.get(mutation_key)
        if not mutation:
            continue
        
        mutation_modifiers = mutation.get("modifiers", {})
        
        # Stack multiplicative modifiers
        for modifier_key in ["xp_modifier", "xp_modifier_security", 
                             "xp_modifier_milestone", "chaos_factor"]:
            if modifier_key in mutation_modifiers:
                modifiers[modifier_key] *= mutation_modifiers[modifier_key]
        
        # Accumulate mood influences
        if "mood_influence" in mutation_modifiers:
            for mood, influence in mutation_modifiers["mood_influence"].items():
                modifiers["mood_influence"][mood] = (
                    modifiers["mood_influence"].get(mood, 0) + influence
                )
        
        # Collect special flags
        if "special_flags" in mutation_modifiers:
            modifiers["special_flags"].extend(mutation_modifiers["special_flags"])
    
    return modifiers


# =============================================================================
# MUTATION METADATA QUERIES
# =============================================================================

def get_mutation_info(mutation_key: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a specific mutation.
    
    Args:
        mutation_key: Mutation identifier
    
    Returns:
        Mutation definition dict or None if not found
    """
    return MUTATION_POOL.get(mutation_key)


def get_mutation_display_name(mutation_key: str) -> str:
    """
    Get human-readable name for a mutation.
    
    Args:
        mutation_key: Mutation identifier
    
    Returns:
        Display name or mutation_key if not found
    """
    mutation = MUTATION_POOL.get(mutation_key)
    return mutation["name"] if mutation else mutation_key


def list_all_mutations() -> List[str]:
    """
    Get list of all possible mutation keys.
    
    Returns:
        List of mutation identifiers
    """
    return list(MUTATION_POOL.keys())


def get_mutations_by_rarity(rarity: str) -> List[str]:
    """
    Get all mutations of a specific rarity.
    
    Args:
        rarity: Rarity tier (common, uncommon, rare, legendary)
    
    Returns:
        List of mutation keys matching rarity
    """
    return [
        key for key, mutation in MUTATION_POOL.items()
        if mutation.get("rarity") == rarity
    ]


# =============================================================================
# VALIDATION
# =============================================================================

def validate_mutation_pool() -> List[str]:
    """
    Validate mutation pool for consistency.
    
    Returns:
        List of validation errors (empty if all valid)
    """
    errors = []
    
    for key, mutation in MUTATION_POOL.items():
        # Check required fields
        if "name" not in mutation:
            errors.append(f"{key}: missing 'name' field")
        if "description" not in mutation:
            errors.append(f"{key}: missing 'description' field")
        if "rarity" not in mutation:
            errors.append(f"{key}: missing 'rarity' field")
        
        # Check rarity is valid
        rarity = mutation.get("rarity")
        if rarity and rarity not in RARITY_WEIGHTS:
            errors.append(f"{key}: invalid rarity '{rarity}'")
        
        # Check modifiers structure
        modifiers = mutation.get("modifiers", {})
        if not isinstance(modifiers, dict):
            errors.append(f"{key}: 'modifiers' must be a dict")
    
    return errors


# Run validation on import (development safety check)
_validation_errors = validate_mutation_pool()
if _validation_errors:
    import warnings
    warnings.warn(f"Mutation pool validation errors: {_validation_errors}")
