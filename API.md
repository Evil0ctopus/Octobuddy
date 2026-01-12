# OctoBuddy API Documentation

This document describes the internal APIs for extending and integrating with OctoBuddy.

## Core API

### EnhancedOctoBuddy Class

Main controller for OctoBuddy functionality.

```python
from octo.core_enhanced import EnhancedOctoBuddy
from octo.config import CONFIG

buddy = EnhancedOctoBuddy(CONFIG, enable_observation=False)
```

#### Methods

##### `handle_event(event_type, data=None)`
Process an event (study session, achievement, etc.)

**Parameters:**
- `event_type` (str): Type of event ('studied_python', 'finished_class', etc.)
- `data` (any, optional): Additional event data

**Returns:** Dictionary with `state`, `mood`, `stage`, and `phrase`

**Example:**
```python
result = buddy.handle_event('studied_python')
print(result['phrase'])  # "PYTHON TIME LET'S GOOOOO!"
```

##### `teach(category, content)`
Teach OctoBuddy a new fact

**Parameters:**
- `category` (str): Category for the fact
- `content` (str): The fact content

**Returns:** Response message string

**Example:**
```python
buddy.teach('cybersecurity', 'A firewall filters network traffic')
```

##### `execute_skill(skill_name, context=None)`
Execute a custom skill

**Parameters:**
- `skill_name` (str): Name of the skill to execute
- `context` (dict, optional): Context dictionary passed to skill

**Returns:** Dictionary with `success` and `message`

##### `recall_knowledge(query)`
Search knowledge base for information

**Parameters:**
- `query` (str): Search query

**Returns:** Dictionary with `knowledge` and `memories` arrays

##### `get_status()`
Get comprehensive status information

**Returns:** Dictionary with current XP, level, mood, stage, personality, capabilities, and memory stats

##### `enable_observation()` / `disable_observation()`
Enable or disable activity monitoring

## Brain API

### Memory Class

Manages short-term and long-term memory.

```python
from octo.ai_brain import Memory

memory = Memory(storage_path="memory")
```

#### Methods

##### `add_short_term(memory_type, content, metadata=None)`
Add to short-term memory (current session)

##### `add_long_term(memory_type, content, importance=5)`
Add to long-term memory (persistent)

**Parameters:**
- `importance` (int): 1-10, events ≥8 are marked as important

##### `learn_fact(category, fact, source="user")`
Learn and store a new fact

##### `get_facts(category=None)`
Retrieve learned facts, optionally filtered by category

##### `learn_skill(skill_name, description)`
Register a learned skill

##### `search_knowledge(query)`
Search all knowledge for a query

### PersonalityTraits Class

Manages evolving personality traits.

```python
from octo.ai_brain import PersonalityTraits

personality = PersonalityTraits(storage_path="memory")
```

#### Traits (0-10 scale)

- `curiosity`: How curious OctoBuddy is
- `playfulness`: How playful the responses are
- `helpfulness`: How helpful OctoBuddy tries to be
- `chaos_level`: How chaotic behavior is
- `seriousness`: How serious responses are
- `humor`: Sense of humor level
- `empathy`: Emotional understanding
- `intelligence`: Knowledge level (grows with learning)
- `confidence`: Self-assurance (grows with achievements)
- `social`: Social engagement level
- `evolution_stage`: Current personality evolution stage (1-5)

#### Methods

##### `update_trait(trait_name, delta, reason="")`
Modify a personality trait

**Parameters:**
- `trait_name` (str): Name of trait to modify
- `delta` (float): Change amount (-10 to +10)
- `reason` (str): Why the change occurred

##### `get_dominant_traits(top_n=3)`
Get the strongest personality traits

**Returns:** List of tuples: `[(trait_name, value), ...]`

##### `evolve(trigger="time")`
Attempt personality evolution

**Returns:** `True` if evolved, `False` otherwise

## Observation API

### ObservationSystem Class

Safe activity monitoring and event tracking.

```python
from octo.observation import ObservationSystem

obs = ObservationSystem(brain, permissions={
    "monitor_windows": True,
    "detect_activities": True,
    "track_events": True,
    "learn_from_observation": False
})
```

#### Components

##### WindowMonitor
- `get_active_window()`: Get current window info
- `start_monitoring(interval=5)`: Start background monitoring
- `stop_monitoring()`: Stop monitoring
- `get_recent_windows(limit=10)`: Get window history

##### ActivityDetector
- `detect_activity(window_info)`: Detect activity from window
- `log_activity(activity_type, details)`: Log an activity

##### EventSystem
- `register_handler(event_type, handler)`: Register event callback
- `trigger_event(event_type, data)`: Trigger an event
- `get_recent_events(event_type, limit)`: Get event history

##### TeachingInterface
- `teach_fact(category, fact)`: Teach a fact
- `teach_skill(skill_name, description)`: Teach a skill
- `teach_behavior(trigger, response)`: Teach a behavior pattern

## Expansion API

### SkillLoader Class

Load and execute custom skills safely.

```python
from octo.expansion import SkillLoader

skills = SkillLoader(skills_dir="expansions/skills")
```

#### Skill File Format

```python
def skill_info():
    """Required: Return skill metadata"""
    return {
        "name": "skill_name",
        "description": "What it does",
        "author": "Your name",
        "version": "1.0.0"
    }

def execute(context=None):
    """Required: Execute the skill"""
    # Access context
    user_name = context.get("user_name", "friend")
    state = context.get("state", {})
    mood = context.get("mood", "neutral")
    
    # Do something
    result = f"Hello {user_name}!"
    
    # Return result
    return {
        "success": True,
        "message": result,
        "data": {"custom_key": "custom_value"}
    }
```

#### Methods

##### `load_skill(skill_name)`
Load a skill from the skills directory

##### `execute_skill(skill_name, context)`
Execute a loaded skill with context

##### `list_skills()`
List all available skills

### AnimationLoader Class

Load custom animations.

```python
from octo.expansion import AnimationLoader

anims = AnimationLoader(animations_dir="expansions/animations")
```

#### Animation File Format (JSON)

```json
{
  "name": "animation_name",
  "description": "What this animation shows",
  "frames": [
    {
      "ascii": "  ( ^‿^ )\n  __|__",
      "duration_ms": 200
    },
    {
      "ascii": "  ( ^o^ )\n  __|__",
      "duration_ms": 200
    }
  ],
  "loop": false
}
```

#### Methods

##### `load_animation(animation_name)`
Load an animation definition

##### `get_animation(animation_name)`
Get loaded animation (loads if needed)

##### `list_animations()`
List all available animations

### DialogueExpander Class

Expand OctoBuddy's dialogue.

```python
from octo.expansion import DialogueExpander

dialogue = DialogueExpander(dialogue_dir="expansions/dialogue")
```

#### Dialogue File Format (JSON)

```json
{
  "category": "greetings",
  "mood_variants": {
    "happy": [
      "Hi! Great to see you!",
      "Hello! Ready to learn?"
    ],
    "sleepy": [
      "Oh... hi there...",
      "*yawn* Hello..."
    ]
  },
  "generic": [
    "Hello!",
    "Hi there!"
  ]
}
```

#### Methods

##### `load_dialogue_set(category)`
Load a dialogue category

##### `get_dialogue(category, mood=None)`
Get random dialogue for category and mood

##### `add_dialogue(category, mood, phrase)`
Add a new dialogue phrase

## UI API

### Desktop UI

```python
from octo.ui_desktop import run_desktop_ui, OctoBuddyWindow
from PyQt6.QtWidgets import QApplication

app = QApplication(sys.argv)
window = OctoBuddyWindow(state, config, mood, stage)
window.show()
app.exec()
```

#### OctoBuddyWindow Methods

##### `set_phrase(phrase)`
Update the displayed phrase

##### `update_state(state, mood, stage)`
Update OctoBuddy's visual state

## Events Reference

### Built-in Event Types

- `studied_python`: Python study session
- `studied_security_plus`: Security+ study session
- `finished_class`: Completed a class
- `did_tryhackme`: TryHackMe room completed
- `passed_lab`: Lab/exercise passed

### Custom Events

You can create custom events:

```python
buddy.handle_event('my_custom_event', {'details': 'data'})
```

## Storage Formats

### State File (octo_state.json)

```json
{
  "xp": 150,
  "level": 3,
  "study_events": 15,
  "name": "OctoBuddy",
  "classes_finished": 2,
  "security_plus_study": 5
}
```

### Long-term Memory (memory/long_term_memory.json)

```json
{
  "memories": [
    {
      "type": "event",
      "content": "Studied Python for 2 hours",
      "timestamp": "2024-01-15T14:30:00",
      "importance": 5
    }
  ],
  "important_events": [
    {
      "type": "achievement",
      "content": "Finished first class!",
      "timestamp": "2024-01-20T16:00:00",
      "importance": 10
    }
  ]
}
```

### Knowledge Base (memory/knowledge_base.json)

```json
{
  "facts": {
    "python": [
      {
        "fact": "Python uses dynamic typing",
        "source": "user",
        "learned_at": "2024-01-15T10:00:00",
        "confidence": 1.0
      }
    ]
  },
  "learned_skills": [
    {
      "name": "greeting_skill",
      "description": "Custom greeting",
      "learned_at": "2024-01-15T12:00:00",
      "usage_count": 5
    }
  ],
  "custom_behaviors": [
    {
      "trigger": "coding",
      "response": "Great choice! Keep coding!",
      "timestamp": "2024-01-15T13:00:00"
    }
  ]
}
```

### Personality Traits (memory/personality_traits.json)

```json
{
  "curiosity": 7,
  "playfulness": 8,
  "helpfulness": 9,
  "intelligence": 6,
  "evolution_stage": 2,
  "traits_history": [
    {
      "trait": "intelligence",
      "old_value": 5,
      "new_value": 6,
      "delta": 1,
      "reason": "learned about python",
      "timestamp": "2024-01-15T14:00:00"
    }
  ]
}
```

## Error Handling

All major APIs return dictionaries with status:

```python
result = buddy.execute_skill('my_skill')
if result['success']:
    print(result['message'])
else:
    print(f"Error: {result.get('error', 'Unknown error')}")
```

## Security Considerations

### Skill Validation

Skills are validated before loading:
- No `eval`, `exec`, or `__import__` calls
- No dangerous imports (`subprocess`, `os.system`)
- AST parsing ensures safe code

### Observation Permissions

All observation features are opt-in:
```python
permissions = {
    "monitor_windows": False,      # Window monitoring
    "detect_activities": False,    # Activity detection
    "track_events": True,          # Event tracking (safe)
    "learn_from_observation": False # Learning from observation
}
```

## Examples

### Complete Integration Example

```python
from octo.core_enhanced import EnhancedOctoBuddy
from octo.config import CONFIG

# Initialize
buddy = EnhancedOctoBuddy(CONFIG)

# Handle study event
result = buddy.handle_event('studied_python')
print(f"OctoBuddy says: {result['phrase']}")

# Teach something
buddy.teach('programming', 'Variables store data')

# Get status
status = buddy.get_status()
print(f"Level: {status['level']}, XP: {status['xp']}")

# Execute custom skill
skill_result = buddy.execute_skill('example_greeting')
print(skill_result['message'])

# Recall knowledge
knowledge = buddy.recall_knowledge('programming')
print(knowledge)
```

---

For more examples, see the `/examples` directory and SETUP.md.
