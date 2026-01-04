"""
Ability System for OctoBuddy

Plugin-like ability expansion system that allows OctoBuddy to learn
and execute new abilities over time.

Architecture:
- Registry-based: abilities register themselves
- Metadata-driven: abilities define prerequisites, costs, effects
- Safe execution: sandboxed contexts with state/config access
- Extensible: new abilities can be added as Python modules

Ability lifecycle:
1. Define ability (metadata + implementation)
2. Register ability in registry
3. Check if ability is available (prerequisites met)
4. Execute ability (modify state, trigger effects)
5. Track usage in memory system
"""

from typing import Dict, Any, List, Callable, Optional
import importlib
import inspect
from pathlib import Path


# =============================================================================
# ABILITY REGISTRY
# =============================================================================

_ABILITY_REGISTRY: Dict[str, Dict[str, Any]] = {}


def register_ability(
    name: str,
    description: str,
    prerequisites: Optional[Dict[str, Any]] = None,
    cost: Optional[Dict[str, float]] = None,
    implementation: Optional[Callable] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Register a new ability in the global registry.
    
    Args:
        name: Unique ability identifier
        description: Human-readable description
        prerequisites: Requirements to unlock (e.g., {"mutations": ["analytical_mind"]})
        cost: Costs to execute (e.g., {"curiosity": 1.0, "focus": 0.5})
        implementation: Callable that executes the ability
        metadata: Additional ability-specific data
    """
    ability = {
        "name": name,
        "description": description,
        "prerequisites": prerequisites or {},
        "cost": cost or {},
        "implementation": implementation,
        "metadata": metadata or {},
    }
    
    _ABILITY_REGISTRY[name] = ability


def unregister_ability(name: str) -> None:
    """Remove an ability from the registry."""
    if name in _ABILITY_REGISTRY:
        del _ABILITY_REGISTRY[name]


def list_abilities(include_locked: bool = False) -> List[str]:
    """
    List all registered ability names.
    
    Args:
        include_locked: If False, only list available abilities
    """
    return list(_ABILITY_REGISTRY.keys())


def get_ability_info(name: str) -> Optional[Dict[str, Any]]:
    """Get metadata for a specific ability."""
    return _ABILITY_REGISTRY.get(name)


# =============================================================================
# ABILITY AVAILABILITY
# =============================================================================

def is_ability_available(name: str, state: Dict[str, Any]) -> bool:
    """
    Check if an ability's prerequisites are met.
    
    Prerequisites can include:
    - mutations: List of required mutations
    - traits: Dict of minimum trait values
    - evolution_vars: Dict of minimum evolution variable values
    - triggers: List of required evolution triggers
    """
    ability = _ABILITY_REGISTRY.get(name)
    if not ability:
        return False
    
    prereqs = ability["prerequisites"]
    
    # Check mutation requirements
    if "mutations" in prereqs:
        required_mutations = set(prereqs["mutations"])
        current_mutations = set(state.get("mutations", []))
        if not required_mutations.issubset(current_mutations):
            return False
    
    # Check trait requirements
    if "traits" in prereqs:
        traits = state.get("personality_traits", {})
        for trait_name, min_value in prereqs["traits"].items():
            if traits.get(trait_name, 0.0) < min_value:
                return False
    
    # Check evolution variable requirements
    if "evolution_vars" in prereqs:
        ev_vars = state.get("evolution_vars", {})
        for var_name, min_value in prereqs["evolution_vars"].items():
            if ev_vars.get(var_name, 0.0) < min_value:
                return False
    
    # Check trigger requirements
    if "triggers" in prereqs:
        required_triggers = set(prereqs["triggers"])
        current_triggers = set(state.get("evolution_triggers", []))
        if not required_triggers.issubset(current_triggers):
            return False
    
    return True


def get_available_abilities(state: Dict[str, Any]) -> List[str]:
    """Get all abilities that are currently available (prerequisites met)."""
    return [
        name for name in _ABILITY_REGISTRY.keys()
        if is_ability_available(name, state)
    ]


# =============================================================================
# ABILITY EXECUTION
# =============================================================================

def execute_ability(
    name: str,
    state: Dict[str, Any],
    config: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Execute an ability and return updated state and results.
    
    Args:
        name: Ability name
        state: Current state
        config: Current config
        context: Optional execution context (user input, event data, etc.)
    
    Returns:
        (updated_state, result_dict)
        result_dict contains: {"success": bool, "message": str, "data": Any}
    """
    ability = _ABILITY_REGISTRY.get(name)
    if not ability:
        return state, {
            "success": False,
            "message": f"Unknown ability: {name}",
            "data": None,
        }
    
    if not is_ability_available(name, state):
        return state, {
            "success": False,
            "message": f"Prerequisites not met for {name}",
            "data": None,
        }
    
    # Check if we can afford the cost
    cost = ability["cost"]
    ev_vars = state.get("evolution_vars", {})
    
    for var_name, cost_amount in cost.items():
        if ev_vars.get(var_name, 0.0) < cost_amount:
            return state, {
                "success": False,
                "message": f"Not enough {var_name} to use {name}",
                "data": None,
            }
    
    # Create execution context
    exec_context = {
        "state": dict(state),  # Immutable copy
        "config": config,
        "context": context or {},
    }
    
    # Execute ability
    implementation = ability["implementation"]
    if not implementation:
        return state, {
            "success": False,
            "message": f"No implementation for {name}",
            "data": None,
        }
    
    try:
        # Call implementation
        result = implementation(exec_context)
        
        # Apply costs to state
        new_state = dict(state)
        new_ev_vars = dict(new_state.get("evolution_vars", {}))
        
        for var_name, cost_amount in cost.items():
            new_ev_vars[var_name] = new_ev_vars.get(var_name, 0.0) - cost_amount
        
        new_state["evolution_vars"] = new_ev_vars
        
        # Merge any state changes from ability
        if isinstance(result, dict) and "state_changes" in result:
            for key, value in result["state_changes"].items():
                new_state[key] = value
        
        # Record ability usage in memory
        from octo.memory import register_ability_usage
        register_ability_usage(name, True, context or {})
        
        return new_state, {
            "success": True,
            "message": result.get("message", f"Successfully used {name}"),
            "data": result.get("data"),
        }
    
    except Exception as e:
        # Record failure
        from octo.memory import register_ability_usage
        register_ability_usage(name, False, context or {})
        
        return state, {
            "success": False,
            "message": f"Error executing {name}: {str(e)}",
            "data": None,
        }


# =============================================================================
# ABILITY LOADER (for dynamic loading from files)
# =============================================================================

def load_abilities_from_directory(directory: Path) -> int:
    """
    Load all ability modules from a directory.
    
    Each module should define abilities using register_ability().
    
    Returns:
        Number of abilities loaded
    """
    count = 0
    
    if not directory.exists():
        return 0
    
    for module_file in directory.glob("*.py"):
        if module_file.name.startswith("_"):
            continue
        
        try:
            # Import module dynamically
            module_name = module_file.stem
            spec = importlib.util.spec_from_file_location(module_name, module_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Count registered functions
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) and hasattr(obj, "_is_ability"):
                    count += 1
        
        except Exception as e:
            print(f"Failed to load ability module {module_file}: {e}")
    
    return count


# =============================================================================
# DECORATOR FOR DEFINING ABILITIES
# =============================================================================

def ability(
    name: str,
    description: str,
    prerequisites: Optional[Dict[str, Any]] = None,
    cost: Optional[Dict[str, float]] = None,
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Decorator to define an ability.
    
    Usage:
        @ability(
            name="deep_focus",
            description="Enter a state of deep concentration",
            cost={"chaos": 2.0},
            prerequisites={"traits": {"focus": 7.0}}
        )
        def deep_focus_impl(context):
            # Implementation
            return {"message": "Entered deep focus!", "data": {...}}
    """
    def decorator(func: Callable) -> Callable:
        # Register the ability
        register_ability(
            name=name,
            description=description,
            prerequisites=prerequisites,
            cost=cost,
            implementation=func,
            metadata=metadata,
        )
        
        # Mark function as ability
        func._is_ability = True
        func._ability_name = name
        
        return func
    
    return decorator


# =============================================================================
# BUILT-IN ABILITIES
# =============================================================================

@ability(
    name="analyze_pattern",
    description="Deeply analyze recent learning patterns",
    cost={"focus": 1.0, "curiosity": 0.5},
    prerequisites={"traits": {"analytical": 6.0}},
)
def analyze_pattern_impl(context):
    """Analyze recent events to find patterns."""
    from octo.memory import query_memory
    
    recent = query_memory("recent_events", count=20)
    
    # Count event types
    event_types = {}
    for event in recent:
        event_type = event.get("type", "unknown")
        event_types[event_type] = event_types.get(event_type, 0) + 1
    
    # Find dominant pattern
    if event_types:
        dominant = max(event_types.items(), key=lambda x: x[1])
        message = f"Analysis complete! Most common activity: {dominant[0]} ({dominant[1]} times)"
    else:
        message = "No patterns found in recent memory."
    
    return {
        "message": message,
        "data": {"patterns": event_types},
        "state_changes": {
            # Boost analytical trait slightly
            "personality_traits": {
                **context["state"].get("personality_traits", {}),
                "analytical": context["state"].get("personality_traits", {}).get("analytical", 0) + 0.5,
            }
        }
    }


@ability(
    name="creative_burst",
    description="Generate novel ideas and solutions",
    cost={"calmness": 1.0},
    prerequisites={"evolution_vars": {"creativity": 7.0}},
)
def creative_burst_impl(context):
    """Boost creativity temporarily."""
    import random
    
    ideas = [
        "What if we approached this from the opposite direction?",
        "Perhaps combining two unrelated concepts could help!",
        "There's a pattern here I haven't noticed before...",
        "Let's try something completely unconventional!",
        "Innovation comes from unexpected connections!",
    ]
    
    return {
        "message": random.choice(ideas),
        "data": {"creativity_boost": 2.0},
        "state_changes": {
            "evolution_vars": {
                **context["state"].get("evolution_vars", {}),
                "creativity": context["state"].get("evolution_vars", {}).get("creativity", 0) + 2.0,
            }
        }
    }


@ability(
    name="chaos_mode",
    description="Embrace unpredictability",
    cost={"calmness": 3.0},
    prerequisites={"mutations": ["chaos_incarnate"]},
)
def chaos_mode_impl(context):
    """Temporarily massively increase chaos."""
    return {
        "message": "🌀 CHAOS MODE ACTIVATED! 🌀",
        "data": {"chaos_multiplier": 5.0},
        "state_changes": {
            "evolution_vars": {
                **context["state"].get("evolution_vars", {}),
                "chaos": context["state"].get("evolution_vars", {}).get("chaos", 0) + 10.0,
            }
        }
    }
