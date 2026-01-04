"""
Test suite for OctoBuddy's procedural animation system.

This file tests the physics engine, tentacle system, animation state,
and event system to ensure everything works correctly.
"""

import sys
import time
from octo.physics import Vector2D, TentacleSegment, apply_spring_force, apply_gravity
from octo.tentacles import Tentacle, TentacleSystem
from octo.animation_engine import AnimationState, map_octobuddy_mood_to_animation
from octo.events import EventSystem, EventType


def test_vector2d():
    """Test Vector2D class."""
    print("Testing Vector2D...")
    
    # Basic operations
    v1 = Vector2D(3, 4)
    v2 = Vector2D(1, 2)
    
    assert v1.length() == 5.0, "Vector length calculation failed"
    
    v3 = v1 + v2
    assert v3.x == 4 and v3.y == 6, "Vector addition failed"
    
    v4 = v1 - v2
    assert v4.x == 2 and v4.y == 2, "Vector subtraction failed"
    
    v5 = v1 * 2
    assert v5.x == 6 and v5.y == 8, "Vector multiplication failed"
    
    v6 = v1.normalize()
    assert abs(v6.length() - 1.0) < 0.001, "Vector normalization failed"
    
    distance = v1.distance_to(v2)
    assert abs(distance - 2.828) < 0.01, "Vector distance calculation failed"
    
    print("  ✓ Vector2D tests passed")


def test_tentacle_segment():
    """Test TentacleSegment physics."""
    print("Testing TentacleSegment...")
    
    # Create segment
    seg = TentacleSegment(Vector2D(0, 0), length=10.0, mass=1.0)
    
    # Apply force and update
    seg.apply_force(Vector2D(10, 0))
    initial_pos = seg.position.copy()
    seg.update(1.0, damping=0.98)
    
    # Segment should have moved
    assert seg.position.x > initial_pos.x, "Segment didn't move after force"
    
    # Test pinned segment
    seg.pinned = True
    seg.apply_force(Vector2D(10, 0))
    pos_before = seg.position.copy()
    seg.update(1.0)
    assert seg.position.x == pos_before.x, "Pinned segment moved"
    
    print("  ✓ TentacleSegment tests passed")


def test_tentacle():
    """Test Tentacle class."""
    print("Testing Tentacle...")
    
    # Create tentacle
    tentacle = Tentacle(Vector2D(100, 100), num_segments=8, segment_length=15.0)
    
    assert len(tentacle.segments) == 8, "Wrong number of segments"
    assert tentacle.segments[0].pinned, "Base segment should be pinned"
    
    # Test mood update
    tentacle.update_mood(energy=1.0, curiosity=0.8, happiness=0.9, calmness=0.3)
    assert tentacle.energy == 1.0, "Energy not set correctly"
    assert tentacle.responsiveness == 0.8, "Responsiveness not set correctly"
    
    # Test update without cursor
    initial_tip = tentacle.get_tip_position()
    for _ in range(10):
        tentacle.update(1.0)
    
    # Tip should have moved due to physics
    final_tip = tentacle.get_tip_position()
    distance_moved = initial_tip.distance_to(final_tip)
    assert distance_moved > 0, "Tentacle didn't animate"
    
    # Test cursor tracking
    cursor_pos = Vector2D(200, 200)
    for _ in range(20):
        tentacle.update(1.0, cursor_pos=cursor_pos, cursor_attraction=1.0)
    
    print("  ✓ Tentacle tests passed")


def test_tentacle_system():
    """Test TentacleSystem."""
    print("Testing TentacleSystem...")
    
    system = TentacleSystem(Vector2D(200, 200), num_tentacles=6)
    
    assert len(system.tentacles) == 6, "Wrong number of tentacles"
    
    # Test mood propagation
    system.update_mood(energy=0.7, curiosity=0.6, happiness=0.8, calmness=0.5)
    
    for tentacle in system.tentacles:
        assert tentacle.energy == 0.7, "Mood not propagated to tentacle"
    
    # Test update
    for _ in range(10):
        system.update(1.0)
    
    # Test center repositioning
    new_center = Vector2D(300, 300)
    system.set_center(new_center)
    assert system.center.x == 300 and system.center.y == 300, "Center not moved"
    
    print("  ✓ TentacleSystem tests passed")


def test_animation_state():
    """Test AnimationState."""
    print("Testing AnimationState...")
    
    state = AnimationState()
    
    # Test initial values
    assert 0 <= state.energy <= 1, "Invalid initial energy"
    assert 0 <= state.curiosity <= 1, "Invalid initial curiosity"
    
    # Test mood targets
    state.set_mood_targets(energy=0.9, curiosity=0.8, happiness=0.7, calmness=0.3)
    
    # Update several times to allow transition
    for _ in range(20):
        state.update(1.0)
    
    # Should be close to target
    assert state.energy > 0.7, "Energy didn't transition toward target"
    assert state.curiosity > 0.6, "Curiosity didn't transition toward target"
    
    # Test immediate mood change
    state.set_mood_immediate(energy=0.2, curiosity=0.1)
    assert abs(state.energy - 0.2) < 0.01, "Immediate mood change failed"
    
    # Test mood string
    state.set_mood_immediate(energy=0.1, calmness=0.9)
    mood = state.get_mood_string()
    assert mood == "sleepy", f"Expected 'sleepy', got '{mood}'"
    
    print("  ✓ AnimationState tests passed")


def test_event_system():
    """Test EventSystem."""
    print("Testing EventSystem...")
    
    event_system = EventSystem()
    
    # Test event listener
    event_count = [0]  # Use list to modify in closure
    
    def on_click_handler(event):
        event_count[0] += 1
    
    event_system.add_listener(EventType.CLICK, on_click_handler)
    
    # Trigger click
    event_system.on_click()
    assert event_count[0] == 1, "Event listener not called"
    
    # Test idle tracking
    initial_idle = event_system.idle_tracker.get_idle_duration()
    time.sleep(0.1)
    new_idle = event_system.idle_tracker.get_idle_duration()
    assert new_idle > initial_idle, "Idle time not tracking"
    
    # Activity should reset idle
    event_system.on_click()
    reset_idle = event_system.idle_tracker.get_idle_duration()
    assert reset_idle < 0.01, "Idle time not reset after activity"
    
    # Test typing detector
    typing_count = [0]
    
    def on_typing_handler(event):
        typing_count[0] += 1
    
    event_system.add_listener(EventType.TYPING_BURST, on_typing_handler)
    
    # Simulate typing burst
    for _ in range(6):
        event_system.on_keystroke()
    
    # Should have triggered typing burst event
    assert typing_count[0] >= 1, "Typing burst not detected"
    
    print("  ✓ EventSystem tests passed")


def test_mood_mapping():
    """Test mood mapping from old system to animation system."""
    print("Testing mood mapping...")
    
    # Test various moods
    moods = ["sleepy", "curious", "hyper", "goofy", "chaotic", "proud", "confused", "excited"]
    
    for mood in moods:
        energy, curiosity, happiness, calmness = map_octobuddy_mood_to_animation(mood)
        
        # All values should be in valid range
        assert 0 <= energy <= 1, f"Invalid energy for {mood}"
        assert 0 <= curiosity <= 1, f"Invalid curiosity for {mood}"
        assert 0 <= happiness <= 1, f"Invalid happiness for {mood}"
        assert 0 <= calmness <= 1, f"Invalid calmness for {mood}"
    
    # Test specific mappings
    energy, _, _, calmness = map_octobuddy_mood_to_animation("sleepy")
    assert energy < 0.5, "Sleepy should have low energy"
    assert calmness > 0.5, "Sleepy should have high calmness"
    
    energy, _, _, _ = map_octobuddy_mood_to_animation("hyper")
    assert energy > 0.8, "Hyper should have high energy"
    
    print("  ✓ Mood mapping tests passed")


def test_integration():
    """Test full integration of animation system."""
    print("Testing integration...")
    
    # Create full system
    center = Vector2D(200, 200)
    tentacle_system = TentacleSystem(center, num_tentacles=6)
    animation_state = AnimationState()
    event_system = EventSystem()
    
    # Connect event to animation state
    def on_click(event):
        animation_state.on_click()
    
    event_system.add_listener(EventType.CLICK, on_click)
    
    # Simulate user interaction
    event_system.on_click()
    
    # Update animation loop
    for i in range(60):
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
        
        # Update tentacles
        tentacle_system.update(1.0)
    
    # Animation state should have high energy after click
    assert animation_state.energy > 0.5, "Energy didn't increase after click"
    
    print("  ✓ Integration tests passed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("OctoBuddy Animation System Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        test_vector2d,
        test_tentacle_segment,
        test_tentacle,
        test_tentacle_system,
        test_animation_state,
        test_event_system,
        test_mood_mapping,
        test_integration,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
