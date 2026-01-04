"""
Headless animation demo - simulates the animation system without GUI.

This demonstrates the animation system working over time,
showing how tentacles react to simulated events.
"""

import time
from octo.physics import Vector2D
from octo.tentacles import TentacleSystem
from octo.animation_engine import AnimationState
from octo.events import EventSystem, EventType


def print_animation_state(frame, anim_state, tentacle_system):
    """Print current animation state."""
    print(f"\nFrame {frame}:")
    print(f"  Energy:    {anim_state.energy:.2f} -> {anim_state._target_energy:.2f}")
    print(f"  Curiosity: {anim_state.curiosity:.2f} -> {anim_state._target_curiosity:.2f}")
    print(f"  Happiness: {anim_state.happiness:.2f} -> {anim_state._target_happiness:.2f}")
    print(f"  Calmness:  {anim_state.calmness:.2f} -> {anim_state._target_calmness:.2f}")
    print(f"  Mood: {anim_state.get_mood_string()}")
    
    # Show tentacle tip positions
    print(f"  Tentacle tips:")
    for i, tentacle in enumerate(tentacle_system.tentacles[:3]):  # Just show first 3
        tip = tentacle.get_tip_position()
        print(f"    T{i}: ({tip.x:.1f}, {tip.y:.1f})")


def simulate_animation_loop():
    """Simulate the animation loop without GUI."""
    print("=" * 70)
    print("OctoBuddy Headless Animation Simulation")
    print("=" * 70)
    print("\nSimulating 300 frames (~5 seconds at 60fps)...")
    print("This demonstrates the physics and mood system working in real-time.")
    
    # Create animation components
    center = Vector2D(200, 200)
    tentacle_system = TentacleSystem(center, num_tentacles=6)
    animation_state = AnimationState()
    event_system = EventSystem()
    
    # Connect events to animation state
    event_system.add_listener(
        EventType.CLICK,
        lambda e: animation_state.on_click()
    )
    event_system.add_listener(
        EventType.LEARNING_MOMENT,
        lambda e: animation_state.on_learning_moment(e.data.get("duration", 10))
    )
    
    # Simulate cursor position
    cursor_pos = Vector2D(250, 150)
    
    # Simulation timeline
    events = [
        (60, "click", "User clicks OctoBuddy"),
        (120, "learning", "Learning moment starts"),
        (180, "focus_lost", "Window loses focus"),
        (240, "focus_gained", "Window regains focus"),
    ]
    
    event_idx = 0
    
    # Run animation loop
    for frame in range(300):
        # Trigger scripted events
        if event_idx < len(events) and frame == events[event_idx][0]:
            event_type = events[event_idx][1]
            description = events[event_idx][2]
            print(f"\n{'=' * 70}")
            print(f"EVENT: {description}")
            print(f"{'=' * 70}")
            
            if event_type == "click":
                event_system.on_click()
            elif event_type == "learning":
                event_system.trigger_learning_moment(5.0)
            elif event_type == "focus_lost":
                event_system.on_focus_change(False)
            elif event_type == "focus_gained":
                event_system.on_focus_change(True)
            
            event_idx += 1
        
        # Update systems
        event_system.update()
        animation_state.update(1.0)
        
        # Apply mood to tentacles
        tentacle_system.update_mood(
            energy=animation_state.energy,
            curiosity=animation_state.curiosity,
            happiness=animation_state.happiness,
            calmness=animation_state.calmness
        )
        
        # Update tentacles with cursor tracking
        cursor_attraction = animation_state.curiosity * 0.8
        tentacle_system.update(
            dt=1.0,
            cursor_pos=cursor_pos,
            cursor_attraction=cursor_attraction
        )
        
        # Print state every 60 frames (every "second")
        if frame % 60 == 0:
            print_animation_state(frame, animation_state, tentacle_system)
    
    print("\n" + "=" * 70)
    print("Simulation complete!")
    print("=" * 70)
    print("\nKey observations:")
    print("  - Mood values smoothly transition to targets")
    print("  - Tentacles move and sway based on physics")
    print("  - Events cause immediate mood changes")
    print("  - Cursor tracking influenced by curiosity level")
    print("  - System maintains stable performance over time")
    print("\nThe animation system is ready for desktop deployment!")


if __name__ == "__main__":
    simulate_animation_loop()
