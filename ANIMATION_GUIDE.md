# OctoBuddy Animation System Guide

This guide explains how to use and extend OctoBuddy's procedural animation system.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Using the Animation System](#using-the-animation-system)
4. [Extending the System](#extending-the-system)
5. [Performance Tips](#performance-tips)

## Quick Start

### Running the Desktop Demo

```bash
# Install dependencies
pip install -r requirements.txt

# Run the desktop animation demo
python examples/demo_desktop.py
```

### Keyboard Shortcuts

- `Q` - Quit the application
- `D` - Toggle debug display (shows FPS and mood values)
- `L` - Trigger learning moment (high energy + curiosity spike)
- `E` - High energy mode
- `S` - Sleepy mode
- `C` - Curious mode
- `N` - Nervous mode

### Interacting with OctoBuddy

- **Click and drag** to move OctoBuddy around the screen
- **Move your cursor** near OctoBuddy to make the tentacles track it
- **Click** on OctoBuddy for an energy burst reaction
- Leave it **idle** and watch it gradually become sleepy

## Architecture Overview

### Core Modules

1. **`octo/physics.py`** - Physics engine
   - `Vector2D`: 2D vector math
   - `TentacleSegment`: Physics-enabled segment with Verlet integration
   - Spring-damper forces for realistic motion

2. **`octo/tentacles.py`** - Tentacle system
   - `Tentacle`: Chain of segments with idle swaying and cursor tracking
   - `TentacleSystem`: Manager for multiple tentacles

3. **`octo/animation_engine.py`** - Animation state
   - `AnimationState`: Manages mood variables and transitions
   - Mood mapping from traditional OctoBuddy moods

4. **`octo/events.py`** - Event system
   - `EventSystem`: Unified event management
   - Tracks clicks, typing, focus, idle time

5. **`octo/ui_desktop.py`** - PyQt5 UI
   - `OctoBuddyWidget`: Transparent desktop creature window
   - Real-time rendering at 60 FPS
   - Eye tracking and head tilt

## Using the Animation System

### Creating a Basic Animation

```python
from octo.physics import Vector2D
from octo.tentacles import TentacleSystem
from octo.animation_engine import AnimationState

# Create tentacle system at position (200, 200) with 6 tentacles
center = Vector2D(200, 200)
tentacle_system = TentacleSystem(center, num_tentacles=6)

# Create animation state
animation_state = AnimationState()

# Set mood
animation_state.set_mood_targets(
    energy=0.8,      # High energy
    curiosity=0.7,   # Very curious
    happiness=0.9,   # Very happy
    calmness=0.4     # Somewhat nervous
)

# Animation loop
while running:
    # Update animation state (smooth transitions)
    animation_state.update(dt=1.0)
    
    # Apply mood to tentacles
    tentacle_system.update_mood(
        energy=animation_state.energy,
        curiosity=animation_state.curiosity,
        happiness=animation_state.happiness,
        calmness=animation_state.calmness
    )
    
    # Update tentacles with cursor tracking
    cursor_pos = Vector2D(mouse_x, mouse_y)
    cursor_attraction = animation_state.curiosity * 0.8
    tentacle_system.update(
        dt=1.0,
        cursor_pos=cursor_pos,
        cursor_attraction=cursor_attraction
    )
    
    # Render (your rendering code here)
    render_tentacles(tentacle_system)
```

### Event-Driven Mood Changes

```python
from octo.events import EventSystem, EventType

# Create event system
event_system = EventSystem()

# Connect events to animation state
event_system.add_listener(
    EventType.CLICK,
    lambda e: animation_state.on_click()
)

event_system.add_listener(
    EventType.LEARNING_MOMENT,
    lambda e: animation_state.on_learning_moment(10.0)
)

# In your main loop
event_system.update()  # Updates idle tracking

# When user clicks
event_system.on_click()

# When user types
event_system.on_keystroke()

# When focus changes
event_system.on_focus_change(has_focus=True)

# Trigger special events
event_system.trigger_learning_moment(duration=10.0)
```

### Mood Variables Explained

Each mood variable ranges from 0.0 to 1.0:

- **Energy** (0-1)
  - Affects motion speed, amplitude, gravity resistance
  - High (0.8-1.0): Fast, bouncy, perky movement
  - Medium (0.4-0.7): Normal, balanced motion
  - Low (0.0-0.3): Slow, droopy, soft motion

- **Curiosity** (0-1)
  - Affects cursor tracking responsiveness
  - High (0.8-1.0): Tentacles eagerly follow cursor
  - Medium (0.4-0.7): Gentle cursor tracking
  - Low (0.0-0.3): Mostly ignores cursor

- **Happiness** (0-1)
  - Affects perkiness and upward tendency
  - High (0.8-1.0): Tentacles stay upright
  - Medium (0.4-0.7): Balanced posture
  - Low (0.0-0.3): Tentacles droop down

- **Calmness** (0-1)
  - Affects motion smoothness
  - High (0.8-1.0): Smooth, gentle motion
  - Medium (0.4-0.7): Normal motion
  - Low (0.0-0.3): Jittery, nervous movement

## Extending the System

### Adding New Body Parts

```python
# Create a new body part class in octo/body_parts.py
from octo.physics import Vector2D, TentacleSegment

class Antenna:
    def __init__(self, base_position, length=30.0):
        self.base = base_position
        self.tip = TentacleSegment(
            Vector2D(base_position.x, base_position.y - length),
            length=length
        )
        self.tip.pinned = False
    
    def update(self, dt, mood_energy):
        # Apply forces based on mood
        self.tip.apply_force(Vector2D(0, -mood_energy * 2))
        self.tip.update(dt)
        
        # Constrain to base
        self.tip.constrain_to_parent(self.base, stiffness=0.8)
    
    def get_position(self):
        return self.tip.position

# Use in ui_desktop.py
from octo.body_parts import Antenna

class OctoBuddyWidget(QWidget):
    def __init__(self, width=400, height=400):
        # ... existing code ...
        
        # Add antennae
        self.antenna_left = Antenna(
            Vector2D(center_x - 15, center_y - 40)
        )
        self.antenna_right = Antenna(
            Vector2D(center_x + 15, center_y - 40)
        )
    
    def _update_animation(self):
        # ... existing code ...
        
        # Update antennae
        self.antenna_left.update(1.0, self.animation_state.energy)
        self.antenna_right.update(1.0, self.animation_state.energy)
```

### Adding New Moods

```python
# In octo/animation_engine.py, add to get_mood_string():

def get_mood_string(self):
    # ... existing code ...
    
    # Add new mood
    if self.energy > 0.9 and self.happiness > 0.9:
        return "ecstatic"
    
    # ... rest of code ...

# Update mood mapping
def map_octobuddy_mood_to_animation(octobuddy_mood):
    mood_mappings = {
        # ... existing moods ...
        "ecstatic": (1.0, 0.9, 1.0, 0.2),  # max energy, happiness
    }
    return mood_mappings.get(octobuddy_mood, (0.5, 0.5, 0.5, 0.5))
```

### Adding New Events

```python
# In octo/events.py, add new event type:

class EventType:
    # ... existing types ...
    CODE_COMPILED = "code_compiled"
    TEST_PASSED = "test_passed"

# In your application:
event_system.add_listener(
    EventType.CODE_COMPILED,
    lambda e: animation_state.set_mood_targets(
        energy=0.7, 
        happiness=0.8
    )
)

# Trigger the event
event_system.event_handler.emit(
    EventType.CODE_COMPILED,
    {"success": True, "time": 2.5}
)
```

### Creating Custom Behaviors

```python
# Create a new behavior class
class BounceBehavior:
    def __init__(self, tentacle_system):
        self.tentacles = tentacle_system
        self.bounce_phase = 0
    
    def update(self, dt, active=False):
        if not active:
            return
        
        self.bounce_phase += 0.2
        bounce_force = math.sin(self.bounce_phase) * 5.0
        
        for tentacle in self.tentacles.tentacles:
            for segment in tentacle.segments:
                segment.apply_force(Vector2D(0, bounce_force))

# Use in your animation loop:
bounce_behavior = BounceBehavior(tentacle_system)

while running:
    # Activate bounce when happy
    is_bouncing = animation_state.happiness > 0.8
    bounce_behavior.update(1.0, active=is_bouncing)
    
    # ... rest of loop ...
```

## Performance Tips

### Optimizing Physics

```python
# Reduce segment count for better performance
tentacle = Tentacle(
    base_position,
    num_segments=5,  # Instead of 8
    segment_length=20.0
)

# Reduce constraint iterations
for _ in range(2):  # Instead of 3
    for i in range(1, len(self.segments)):
        self.segments[i].constrain_to_parent(...)
```

### Optimizing Rendering

```python
# Lower FPS for better performance
self.fps = 30  # Instead of 60
self.timer.start(1000 // self.fps)

# Use fewer tentacles
tentacle_system = TentacleSystem(center, num_tentacles=4)

# Disable cursor tracking when not needed
self.cursor_tracking_enabled = False
```

### CPU-Friendly Settings

```python
# For low-end systems, use these settings:
animation_state.transition_speed = 0.1  # Faster transitions
tentacle_system.update_mood(
    energy=0.5,
    curiosity=0.3,  # Less cursor tracking
    happiness=0.5,
    calmness=0.7    # Smoother, less computation
)
```

## Testing Your Changes

```bash
# Run the test suite
python test_animation.py

# Run headless simulation
python examples/demo_headless.py

# Run desktop demo
python examples/demo_desktop.py
```

## Platform Notes

### Windows 10/11
- PyQt5 works out of the box
- Transparent windows supported
- Always-on-top works correctly

### Linux
- May need additional Qt dependencies
- Window transparency requires compositor

### macOS
- PyQt5 supported
- May need permissions for window overlay

## Troubleshooting

### Window doesn't appear
- Check if PyQt5 is installed correctly
- Try disabling transparency temporarily

### Performance issues
- Reduce segment count
- Lower FPS
- Disable debug display
- Reduce number of tentacles

### Tentacles not moving
- Verify update loop is running
- Check that dt is being passed correctly
- Ensure mood values are set

### Events not triggering
- Verify event listeners are connected
- Check EventType constants match
- Ensure event_system.update() is called

## Further Reading

- See `test_animation.py` for usage examples
- See `examples/demo_headless.py` for simulation example
- See `examples/demo_desktop.py` for full desktop implementation
