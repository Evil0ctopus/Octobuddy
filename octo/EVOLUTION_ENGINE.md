# Evolution Engine Documentation

## Overview

The evolution engine adds depth to OctoBuddy through three interconnected systems:

1. **Mutations** - Random trait acquisition that modifies behavior
2. **Personality Drift** - Activity-based personality tendencies
3. **Evolution Triggers** - Special achievements unlocked by unique conditions

## Architecture

Following OctoBuddy's core patterns:
- **Pure functions** accepting `(state, config)` parameters
- **Immutable state transformations** (shallow copy before mutations)
- **Logic/presentation separation** (engine returns data, UI displays it)

## Systems

### 1. Mutation System

**How it works:**
- Each event has a chance to trigger mutation (base 0.5% at level 1, up to 5% at level 100)
- Mutations have rarity tiers: common (50 weight), uncommon (25), rare (10), legendary (2)
- Once acquired, mutations are permanent and stack effects

**Available Mutations:**

| Mutation | Rarity | Effect |
|----------|--------|--------|
| Speed Learner | Common | +10% XP gain |
| Night Owl | Common | Mood influence toward 'hyper' |
| Chaos Incarnate | Uncommon | 2x chaos factor (more mood swings) |
| Analytical Mind | Uncommon | +25% security/lab XP |
| Unstoppable | Rare | +50% milestone XP |
| Personality Fracture | Rare | Multi-personality flag |
| Transcendent | Legendary | +25% all XP + wisdom bonus |

**XP Modifier Stacking:**
```python
# Example: Speed Learner + Transcendent
base_xp = 5
total_modifier = 1.10 * 1.25  # = 1.375
final_xp = 5 * 1.375 = 6.875 → 6 XP
```

**Functions:**
- `calculate_mutation_chance(state, config)` → float probability
- `select_mutation(state, config)` → mutation_key or None
- `apply_mutation(state, config)` → (updated_state, mutation_name)
- `get_mutation_modifiers(state)` → dict of active modifiers

### 2. Personality Drift System

**How it works:**
- Tracks activity patterns across four dimensions
- Normalized 0.0-1.0 based on relative activity distribution
- Applies 2% decay per event to prevent old patterns dominating

**Drift Types:**

| Drift | Activities | Effect |
|-------|-----------|--------|
| Analytical | Security+ study, labs | Methodical, pattern-focused phrases |
| Chaotic | TryHackMe rooms | Unpredictable, chaos-loving phrases |
| Studious | Python study | Knowledge-focused, scholarly phrases |
| Ambitious | Class completions | Goal-oriented, milestone phrases |

**Dominance Threshold:**
- Requires ≥30% in one drift to be considered dominant
- Only one drift can be dominant at a time
- Used for phrase selection (10% chance to use drift phrase)

**Functions:**
- `calculate_personality_drift(state, config)` → updated state
- `get_dominant_drift(state)` → drift_type or None

### 3. Evolution Trigger System

**How it works:**
- Checks unique combinations of conditions after each event
- Triggers are one-time achievements (tracked in `evolution_triggers`)
- Added to evolution history for narrative tracking

**Available Triggers:**

| Trigger | Condition | Meaning |
|---------|-----------|---------|
| Ascension | Level 100 + 3+ mutations | Ultimate power achieved |
| Chaos Master | 50+ TryHackMe + chaos mutation | Master of unpredictability |
| Scholar | 10+ classes + analytical drift >50% | Academic excellence |
| Hybrid Form | All drifts >20% | Perfect balance |

**Functions:**
- `check_evolution_triggers(state, config)` → (updated_state, trigger_name)

### 4. Main Orchestration

**`process_evolution_cycle(state, config)`**

Called after every event in `core.py` to run the complete evolution pipeline:

1. Check for mutations → apply if triggered
2. Recalculate personality drift based on new counters
3. Check evolution triggers → fire if conditions met
4. Store events in `last_evolution_events` for UI display

Returns updated state with all evolution changes applied.

## Integration Points

### core.py
```python
# After state update, before mood/stage calculation
self.state = process_evolution_cycle(self.state, self.config)

# Display evolution events
evolution_events = self.state.get("last_evolution_events", [])
for event_type, event_data in evolution_events:
    # Render special announcement
```

### brain.py
```python
# Get mutation modifiers
modifiers = get_mutation_modifiers(state)

# Apply to XP calculations
state["xp"] += int(dynamic_xp * modifiers["xp_modifier"])

# Apply to mood swings
swing_chance = 0.05 * modifiers["chaos_factor"]
```

### personality.py
```python
# Check for mutation-influenced phrases (5% per mutation)
mutations = state.get("mutations", [])
if mutations and random.random() < 0.05 * len(mutations):
    # Select phrase from MUTATION_PHRASES

# Check for drift-influenced phrases (10% if dominant)
dominant_drift = get_dominant_drift(state)
if dominant_drift and random.random() < 0.10:
    # Select phrase from DRIFT_PHRASES
```

### storage.py
```python
DEFAULT_STATE = {
    # ... existing fields
    "mutations": [],
    "personality_drift": {...},
    "evolution_triggers": [],
    "evolution_history": [],
}
```

## State Schema

**New state fields:**

```python
{
    "mutations": ["speed_learner", "chaos_incarnate"],  # List of mutation keys
    
    "personality_drift": {
        "analytical": 0.35,
        "chaotic": 0.25,
        "studious": 0.30,
        "ambitious": 0.10,
    },
    
    "evolution_triggers": ["scholar", "hybrid_form"],  # One-time achievements
    
    "evolution_history": [
        {
            "type": "mutation",
            "mutation": "speed_learner",
            "level": 15,
            "xp": 2450,
        },
        {
            "type": "evolution_trigger",
            "trigger": "scholar",
            "level": 42,
            "xp": 15000,
        },
    ],
    
    "last_evolution_events": [  # Cleared after display
        ("mutation", "Speed Learner"),
        ("evolution_trigger", "scholar"),
    ],
}
```

## Testing

Run `test_evolution.py` to simulate a learning journey:

```bash
python test_evolution.py
```

Output includes:
- Event-by-event evolution announcements
- Final mutation list
- Personality drift visualization
- Active modifiers summary
- Evolution history

Run multiple times to see different mutation combinations due to RNG.

## Design Rationale

**Why pure functions?**
- Testable in isolation
- Predictable state transformations
- Easy to reason about side effects

**Why separate drift from mood?**
- Drift = long-term personality tendency
- Mood = immediate XP-based emotional state
- Drift influences phrase selection, not visual representation

**Why mutation modifiers stack multiplicatively?**
- Prevents linear scaling becoming overpowered
- Compound growth feels more rewarding
- Matches RPG conventions for buff stacking

**Why one-time triggers?**
- Creates memorable milestones
- Prevents spam of special events
- Encourages diverse play patterns (hybrid form requires balance)

## Extension Examples

**Add new mutation:**

1. Add to `MUTATION_POOL` in `evolution_engine.py`
2. Add phrases to `MUTATION_PHRASES` in `personality.py`
3. If special effect needed, add modifier logic in `get_mutation_modifiers()`

**Add new drift type:**

1. Add to drift calculation in `calculate_personality_drift()`
2. Add phrases to `DRIFT_PHRASES` in `personality.py`
3. Update activity tracking logic as needed

**Add new evolution trigger:**

1. Add condition check in `check_evolution_triggers()`
2. Add trigger name to list tracking
3. Consider adding special UI treatment in `core.py`
