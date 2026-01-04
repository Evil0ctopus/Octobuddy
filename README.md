# OctoBuddy (working title)

OctoBuddy is a cute, funny, slightly chaotic creature–AI hybrid that learns and grows with me as I study cybersecurity, Python, and WGU courses.

Inspired by projects like Pwnagotchi (agent loop, plugins, personality), but focused entirely on **safe, legal learning**. OctoBuddy acts as a study companion, XP tracker, and code-explaining buddy as it evolves alongside my skills.

## Features

- **Procedural Animation System**: Real-time physics-based animation with tentacles that sway, react, and express moods
- **Mood-Driven Behavior**: Energy, curiosity, happiness, and calmness variables influence all movement
- **Interactive Desktop Creature**: Track your mouse cursor with eyes and tentacles, react to clicks and events
- **Event System**: Responds to user activity, idle time, typing bursts, and learning moments
- **Extensible Architecture**: Modular design allows easy addition of new body parts, moods, and behaviors
- Track study sessions and earned XP
- Show mood, level, and evolving personality
- React to events (studied Python, finished a class, etc.)

## Run locally

### Terminal Mode

```bash
pip install -r requirements.txt
python examples/demo_run.py
```

### Desktop Mode (Procedural Animation)

```bash
pip install -r requirements.txt
python examples/demo_desktop.py
```

**Keyboard shortcuts in desktop mode:**
- `Q` - Quit
- `D` - Toggle debug display
- `L` - Trigger learning moment
- `E` - High energy mode
- `S` - Sleepy mode
- `C` - Curious mode
- `N` - Nervous mode

## Animation System

OctoBuddy uses a fully procedural animation engine instead of static sprites:

### Tentacle Physics
- Each tentacle is a chain of segments with spring-damper physics
- Natural idle swaying with sinusoidal motion
- Smooth cursor tracking based on curiosity level
- Mood-driven stiffness, damping, and responsiveness

### Mood Variables
- **Energy** (0-1): Affects motion speed, amplitude, and gravity resistance
  - High energy → fast, bouncy, perky movement
  - Low energy → slow, droopy, soft motion
- **Curiosity** (0-1): Affects cursor tracking responsiveness
  - High curiosity → tentacles follow cursor eagerly
  - Low curiosity → tentacles ignore cursor
- **Happiness** (0-1): Affects perkiness and upward tendency
  - High happiness → tentacles stay upright
  - Low happiness → tentacles droop down
- **Calmness** (0-1): Affects motion smoothness
  - High calmness → smooth, gentle motion
  - Low calmness → jittery, nervous movement

### Event Reactions
The animation system responds to:
- **User clicks**: Energy burst, increased curiosity
- **Window focus changes**: Adjusts energy and attention
- **Typing bursts**: Brief excitement reaction
- **Idle time**: Gradually becomes sleepy and calm
- **Learning moments**: High energy and curiosity spike

### Architecture

The animation system is modular and extensible:

- `octo/physics.py` - Vector math, physics simulation, Verlet integration
- `octo/tentacles.py` - Tentacle system with mood-driven parameters
- `octo/animation_engine.py` - Mood state management and transitions
- `octo/events.py` - Event tracking and dispatching
- `octo/ui_desktop.py` - PyQt5-based rendering and interaction

New body parts, moods, and behaviors can be easily added by extending these modules

