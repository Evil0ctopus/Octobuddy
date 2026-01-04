"""
ASCII visualization of OctoBuddy's procedural animation.

This creates a simple text-based visualization showing how the tentacles
move and respond to simulated cursor positions.
"""

import time
import math
from octo.physics import Vector2D
from octo.tentacles import TentacleSystem
from octo.animation_engine import AnimationState


def clear_screen():
    """Clear the terminal screen."""
    print("\033[2J\033[H", end="")


def draw_ascii_frame(tentacle_system, animation_state, cursor_pos, frame_num):
    """Draw an ASCII art frame of OctoBuddy."""
    width = 60
    height = 30
    
    # Create canvas
    canvas = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Draw tentacles
    for tentacle in tentacle_system.tentacles:
        positions = tentacle.get_segment_positions()
        for pos in positions:
            x = int(pos.x / 10)
            y = int(pos.y / 10)
            if 0 <= x < width and 0 <= y < height:
                canvas[y][x] = '~'
    
    # Draw body (center)
    center_x = int(tentacle_system.center.x / 10)
    center_y = int(tentacle_system.center.y / 10)
    for dy in range(-2, 3):
        for dx in range(-3, 4):
            x = center_x + dx
            y = center_y + dy
            if 0 <= x < width and 0 <= y < height:
                if dx * dx + dy * dy <= 6:
                    canvas[y][x] = '#'
    
    # Draw eyes
    if center_y - 1 >= 0:
        if center_x - 1 >= 0 and center_x - 1 < width:
            canvas[center_y - 1][center_x - 1] = 'o'
        if center_x + 1 >= 0 and center_x + 1 < width:
            canvas[center_y - 1][center_x + 1] = 'o'
    
    # Draw cursor position
    cursor_x = int(cursor_pos.x / 10)
    cursor_y = int(cursor_pos.y / 10)
    if 0 <= cursor_x < width and 0 <= cursor_y < height:
        canvas[cursor_y][cursor_x] = 'X'
    
    # Print frame
    clear_screen()
    print("=" * 70)
    print("  OctoBuddy ASCII Animation Demo - Frame", frame_num)
    print("=" * 70)
    print()
    
    # Print canvas
    for row in canvas:
        print('  ' + ''.join(row))
    
    print()
    print("=" * 70)
    print(f"  Mood: {animation_state.get_mood_string():<12} | ", end="")
    print(f"Energy: {animation_state.energy:.2f} | ", end="")
    print(f"Curiosity: {animation_state.curiosity:.2f}")
    print(f"  Happiness: {animation_state.happiness:.2f} | ", end="")
    print(f"Calmness: {animation_state.calmness:.2f}")
    print("=" * 70)
    print("  Cursor: X   |   Tentacles: ~   |   Body: #   |   Eyes: o")
    print("=" * 70)


def run_ascii_demo():
    """Run ASCII animation demo."""
    print("\nStarting OctoBuddy ASCII Animation Demo...")
    print("This simulates the desktop creature in text mode.\n")
    time.sleep(2)
    
    # Create animation components
    center = Vector2D(300, 150)
    tentacle_system = TentacleSystem(center, num_tentacles=6)
    animation_state = AnimationState()
    
    # Start with curious mood
    animation_state.set_mood_targets(energy=0.7, curiosity=0.8, happiness=0.7)
    
    # Simulate cursor movement in a circle
    cursor_angle = 0
    cursor_radius = 100
    
    # Run animation
    for frame in range(150):
        # Update cursor position (circular motion)
        cursor_angle += 0.05
        cursor_x = center.x + math.cos(cursor_angle) * cursor_radius
        cursor_y = center.y + math.sin(cursor_angle) * cursor_radius
        cursor_pos = Vector2D(cursor_x, cursor_y)
        
        # Trigger events at specific frames
        if frame == 40:
            print("\n>>> EVENT: Click detected! <<<\n")
            animation_state.on_click()
            time.sleep(1)
        elif frame == 80:
            print("\n>>> EVENT: Learning moment! <<<\n")
            animation_state.on_learning_moment(10.0)
            time.sleep(1)
        elif frame == 120:
            print("\n>>> EVENT: Getting sleepy... <<<\n")
            animation_state.set_mood_targets(energy=0.2, calmness=0.9)
            time.sleep(1)
        
        # Update animation
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
        
        # Draw frame
        draw_ascii_frame(tentacle_system, animation_state, cursor_pos, frame)
        
        # Frame delay
        time.sleep(0.1)
    
    print("\nDemo complete! The full desktop version has:")
    print("  - Smooth graphics with PyQt5")
    print("  - Real mouse cursor tracking")
    print("  - Click and drag to move")
    print("  - Keyboard shortcuts for mood control")
    print("\nRun: python examples/demo_desktop.py")


if __name__ == "__main__":
    try:
        run_ascii_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye!")
