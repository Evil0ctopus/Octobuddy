"""
Memory and Learning System for OctoBuddy

Implements persistent memory across multiple domains:
- Short-term memory: Recent events and interactions
- Long-term memory: User preferences, recurring patterns
- Personality memory: How traits have evolved
- Appearance memory: Visual evolution history
- Ability memory: Known abilities and usage patterns

Architecture:
- Pure functions for queries and transformations
- JSON-based persistence
- Separate memory domains for clarity
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


# Memory file paths
MEMORY_DIR = Path("memory")
SHORT_TERM_FILE = MEMORY_DIR / "short_term.json"
LONG_TERM_FILE = MEMORY_DIR / "long_term.json"
PERSONALITY_FILE = MEMORY_DIR / "personality_history.json"
APPEARANCE_FILE = MEMORY_DIR / "appearance_history.json"
ABILITY_FILE = MEMORY_DIR / "ability_memory.json"


# =============================================================================
# INITIALIZATION
# =============================================================================

def initialize_memory():
    """Create memory directory and files if they don't exist."""
    MEMORY_DIR.mkdir(exist_ok=True)
    
    for file_path in [SHORT_TERM_FILE, LONG_TERM_FILE, PERSONALITY_FILE, 
                      APPEARANCE_FILE, ABILITY_FILE]:
        if not file_path.exists():
            file_path.write_text("[]", encoding="utf-8")


# =============================================================================
# SHORT-TERM MEMORY
# =============================================================================

def remember_event(event_type: str, data: Dict[str, Any], config: Dict[str, Any]) -> None:
    """
    Add an event to short-term memory.
    
    Short-term memory is a rolling window of recent events with timestamps.
    """
    initialize_memory()
    
    # Load existing short-term memory
    short_term = json.loads(SHORT_TERM_FILE.read_text(encoding="utf-8"))
    
    # Add new event with timestamp
    event = {
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        "data": data,
    }
    short_term.append(event)
    
    # Keep only recent events (capacity from config)
    capacity = config.get("memory", {}).get("short_term_capacity", 50)
    if len(short_term) > capacity:
        short_term = short_term[-capacity:]
    
    # Save
    SHORT_TERM_FILE.write_text(json.dumps(short_term, indent=2), encoding="utf-8")
    
    # Check if event should be promoted to long-term
    _check_long_term_promotion(event_type, config)


def get_recent_events(count: int = 10) -> List[Dict[str, Any]]:
    """Get the N most recent events from short-term memory."""
    initialize_memory()
    short_term = json.loads(SHORT_TERM_FILE.read_text(encoding="utf-8"))
    return short_term[-count:]


def get_events_since(hours: int = 24) -> List[Dict[str, Any]]:
    """Get all events within the last N hours."""
    initialize_memory()
    short_term = json.loads(SHORT_TERM_FILE.read_text(encoding="utf-8"))
    
    cutoff = datetime.now() - timedelta(hours=hours)
    recent = []
    
    for event in short_term:
        event_time = datetime.fromisoformat(event["timestamp"])
        if event_time >= cutoff:
            recent.append(event)
    
    return recent


# =============================================================================
# LONG-TERM MEMORY
# =============================================================================

def _check_long_term_promotion(event_type: str, config: Dict[str, Any]) -> None:
    """
    Check if an event pattern should be promoted to long-term memory.
    
    Promotion happens when an event type occurs frequently enough.
    """
    initialize_memory()
    
    # Count recent occurrences
    short_term = json.loads(SHORT_TERM_FILE.read_text(encoding="utf-8"))
    count = sum(1 for e in short_term if e["type"] == event_type)
    
    threshold = config.get("memory", {}).get("long_term_threshold", 5)
    
    if count >= threshold:
        # Promote to long-term
        long_term = json.loads(LONG_TERM_FILE.read_text(encoding="utf-8"))
        
        # Check if already exists
        existing = next((p for p in long_term if p["pattern"] == event_type), None)
        
        if existing:
            existing["frequency"] += 1
            existing["last_seen"] = datetime.now().isoformat()
        else:
            long_term.append({
                "pattern": event_type,
                "frequency": 1,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
            })
        
        LONG_TERM_FILE.write_text(json.dumps(long_term, indent=2), encoding="utf-8")


def get_patterns() -> List[Dict[str, Any]]:
    """Get all learned long-term patterns."""
    initialize_memory()
    return json.loads(LONG_TERM_FILE.read_text(encoding="utf-8"))


def get_pattern_frequency(pattern: str) -> int:
    """Get how many times a pattern has been observed."""
    patterns = get_patterns()
    match = next((p for p in patterns if p["pattern"] == pattern), None)
    return match["frequency"] if match else 0


# =============================================================================
# PERSONALITY MEMORY
# =============================================================================

def record_personality_snapshot(state: Dict[str, Any]) -> None:
    """Record current personality traits for historical tracking."""
    initialize_memory()
    
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "traits": state.get("personality_traits", {}),
        "evolution_vars": state.get("evolution_vars", {}),
        "mutations": state.get("mutations", []),
    }
    
    history = json.loads(PERSONALITY_FILE.read_text(encoding="utf-8"))
    history.append(snapshot)
    
    # Keep last 100 snapshots
    if len(history) > 100:
        history = history[-100:]
    
    PERSONALITY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")


def get_personality_history(days: int = 7) -> List[Dict[str, Any]]:
    """Get personality evolution over the last N days."""
    initialize_memory()
    history = json.loads(PERSONALITY_FILE.read_text(encoding="utf-8"))
    
    cutoff = datetime.now() - timedelta(days=days)
    recent = []
    
    for snapshot in history:
        snapshot_time = datetime.fromisoformat(snapshot["timestamp"])
        if snapshot_time >= cutoff:
            recent.append(snapshot)
    
    return recent


def get_trait_delta(trait_name: str, days: int = 7) -> float:
    """Calculate how much a trait has changed over time."""
    history = get_personality_history(days)
    
    if len(history) < 2:
        return 0.0
    
    first = history[0]["traits"].get(trait_name, 0.0)
    last = history[-1]["traits"].get(trait_name, 0.0)
    
    return last - first


# =============================================================================
# APPEARANCE MEMORY
# =============================================================================

def record_appearance_milestone(state: Dict[str, Any], reason: str) -> None:
    """Record a significant appearance change (mutation, evolution trigger, etc.)."""
    initialize_memory()
    
    milestone = {
        "timestamp": datetime.now().isoformat(),
        "reason": reason,
        "mutations": state.get("mutations", []),
        "evolution_triggers": state.get("evolution_triggers", []),
        "dominant_traits": _get_dominant_traits(state, count=3),
    }
    
    history = json.loads(APPEARANCE_FILE.read_text(encoding="utf-8"))
    history.append(milestone)
    
    APPEARANCE_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")


def get_appearance_history() -> List[Dict[str, Any]]:
    """Get full appearance evolution history."""
    initialize_memory()
    return json.loads(APPEARANCE_FILE.read_text(encoding="utf-8"))


# =============================================================================
# ABILITY MEMORY
# =============================================================================

def register_ability_usage(ability_name: str, success: bool, context: Dict[str, Any]) -> None:
    """Record that an ability was used."""
    initialize_memory()
    
    memory = json.loads(ABILITY_FILE.read_text(encoding="utf-8"))
    
    # Find or create ability entry
    ability = next((a for a in memory if a["name"] == ability_name), None)
    
    if not ability:
        ability = {
            "name": ability_name,
            "uses": 0,
            "successes": 0,
            "failures": 0,
            "first_used": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat(),
        }
        memory.append(ability)
    
    # Update stats
    ability["uses"] += 1
    ability["last_used"] = datetime.now().isoformat()
    
    if success:
        ability["successes"] += 1
    else:
        ability["failures"] += 1
    
    ABILITY_FILE.write_text(json.dumps(memory, indent=2), encoding="utf-8")


def get_ability_stats(ability_name: str) -> Optional[Dict[str, Any]]:
    """Get usage statistics for a specific ability."""
    initialize_memory()
    memory = json.loads(ABILITY_FILE.read_text(encoding="utf-8"))
    return next((a for a in memory if a["name"] == ability_name), None)


def get_all_ability_stats() -> List[Dict[str, Any]]:
    """Get usage statistics for all known abilities."""
    initialize_memory()
    return json.loads(ABILITY_FILE.read_text(encoding="utf-8"))


# =============================================================================
# QUERY API
# =============================================================================

def query_memory(query_type: str, **kwargs) -> Any:
    """
    Unified query API for memory system.
    
    Examples:
        query_memory("recent_events", count=5)
        query_memory("pattern_frequency", pattern="studied_python")
        query_memory("trait_change", trait="curiosity", days=7)
    """
    if query_type == "recent_events":
        return get_recent_events(kwargs.get("count", 10))
    
    elif query_type == "events_since":
        return get_events_since(kwargs.get("hours", 24))
    
    elif query_type == "patterns":
        return get_patterns()
    
    elif query_type == "pattern_frequency":
        return get_pattern_frequency(kwargs["pattern"])
    
    elif query_type == "personality_history":
        return get_personality_history(kwargs.get("days", 7))
    
    elif query_type == "trait_change":
        return get_trait_delta(kwargs["trait"], kwargs.get("days", 7))
    
    elif query_type == "appearance_history":
        return get_appearance_history()
    
    elif query_type == "ability_stats":
        return get_ability_stats(kwargs["ability"])
    
    elif query_type == "all_abilities":
        return get_all_ability_stats()
    
    else:
        raise ValueError(f"Unknown query type: {query_type}")


# =============================================================================
# HELPERS
# =============================================================================

def _get_dominant_traits(state: Dict[str, Any], count: int = 3) -> List[str]:
    """Get the top N personality traits by value."""
    traits = state.get("personality_traits", {})
    sorted_traits = sorted(traits.items(), key=lambda x: x[1], reverse=True)
    return [name for name, _ in sorted_traits[:count]]


def load_memory() -> Dict[str, Any]:
    """Load all memory into a single dict (for inspection/debugging)."""
    initialize_memory()
    return {
        "short_term": json.loads(SHORT_TERM_FILE.read_text(encoding="utf-8")),
        "long_term": json.loads(LONG_TERM_FILE.read_text(encoding="utf-8")),
        "personality": json.loads(PERSONALITY_FILE.read_text(encoding="utf-8")),
        "appearance": json.loads(APPEARANCE_FILE.read_text(encoding="utf-8")),
        "abilities": json.loads(ABILITY_FILE.read_text(encoding="utf-8")),
    }


def save_memory(memory: Dict[str, Any]) -> None:
    """Save all memory from a single dict (for backup/restore)."""
    initialize_memory()
    
    SHORT_TERM_FILE.write_text(
        json.dumps(memory.get("short_term", []), indent=2), encoding="utf-8"
    )
    LONG_TERM_FILE.write_text(
        json.dumps(memory.get("long_term", []), indent=2), encoding="utf-8"
    )
    PERSONALITY_FILE.write_text(
        json.dumps(memory.get("personality", []), indent=2), encoding="utf-8"
    )
    APPEARANCE_FILE.write_text(
        json.dumps(memory.get("appearance", []), indent=2), encoding="utf-8"
    )
    ABILITY_FILE.write_text(
        json.dumps(memory.get("abilities", []), indent=2), encoding="utf-8"
    )
