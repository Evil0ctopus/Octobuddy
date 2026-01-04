#!/usr/bin/env python3
"""
OctoBuddy Desktop Companion - Main Entry Point

Launch OctoBuddy as a Windows desktop companion with full evolution,
animation, memory, and ability systems.

Usage:
    python main.py              # Launch desktop companion
    python main.py --terminal   # Launch terminal UI (legacy)
    python main.py --test       # Run system tests
"""

import sys
import argparse
from pathlib import Path

# Add octo directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "octo"))


def launch_desktop():
    """Launch the desktop companion UI."""
    from octo.desktop import run_desktop_companion
    
    print("🐙 Launching OctoBuddy Desktop Companion...")
    print("📍 Right-click OctoBuddy for options")
    print("🖱️  Left-click and drag to move")
    print()
    
    run_desktop_companion()


def launch_terminal():
    """Launch the terminal UI (legacy mode)."""
    from octo.core import handle_event
    from octo.config import load_config
    from octo.storage import load_state, save_state
    
    print("🐙 OctoBuddy Terminal Mode")
    print("=" * 50)
    
    config = load_config()
    state = load_state()
    
    # Show current status
    from octo.brain import get_mood, get_stage
    mood = get_mood(state, config)
    stage = get_stage(state, config)
    
    print(f"Stage: {stage}")
    print(f"Mood: {mood}")
    print(f"Mutations: {len(state.get('mutations', []))}")
    print()
    
    # Interactive loop
    while True:
        print("\nActions:")
        print("  1. Study Python")
        print("  2. Study Security+")
        print("  3. Finish Class")
        print("  4. TryHackMe Room")
        print("  5. Pass Lab")
        print("  6. Show Status")
        print("  0. Quit")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            state = handle_event(state, "studied_python", {})
        elif choice == "2":
            state = handle_event(state, "studied_security_plus", {})
        elif choice == "3":
            state = handle_event(state, "finished_class", {})
        elif choice == "4":
            state = handle_event(state, "did_tryhackme", {})
        elif choice == "5":
            state = handle_event(state, "passed_lab", {})
        elif choice == "6":
            show_status(state, config)
        
        save_state(state)


def show_status(state, config):
    """Display detailed status."""
    from octo.brain import get_mood, get_stage
    from octo.evolution_engine import get_evolution_summary
    from octo.abilities import get_available_abilities
    
    print("\n" + "=" * 50)
    print("📊 OctoBuddy Status")
    print("=" * 50)
    
    # Basic info
    stage = get_stage(state, config)
    mood = get_mood(state, config)
    print(f"Stage: {stage}")
    print(f"Mood: {mood}")
    
    # Evolution variables
    print("\nEvolution Variables:")
    ev_vars = state.get("evolution_vars", {})
    for name, value in sorted(ev_vars.items()):
        print(f"  {name}: {value:.1f}")
    
    # Personality traits
    print("\nPersonality Traits:")
    traits = state.get("personality_traits", {})
    sorted_traits = sorted(traits.items(), key=lambda x: x[1], reverse=True)
    for name, value in sorted_traits[:5]:
        print(f"  {name}: {value:.1f}")
    
    # Evolution summary
    summary = get_evolution_summary(state)
    print(f"\nMutations: {summary['mutation_count']}")
    for mut in summary['mutations'][:3]:
        print(f"  - {mut}")
    
    print(f"\nDominant Drift: {summary['dominant_drift']}")
    print(f"Evolution Triggers: {len(summary['evolution_triggers'])}")
    
    # Abilities
    available = get_available_abilities(state)
    print(f"\nAvailable Abilities: {len(available)}")
    for ability in available[:5]:
        print(f"  - {ability}")
    
    # Activity
    print("\nActivity:")
    print(f"  Study Events: {state.get('study_events', 0)}")
    print(f"  Security+ Study: {state.get('security_plus_study', 0)}")
    print(f"  Classes Finished: {state.get('classes_finished', 0)}")
    print(f"  TryHackMe Rooms: {state.get('tryhackme_rooms', 0)}")
    print(f"  Labs Passed: {state.get('labs_passed', 0)}")
    
    print("=" * 50)


def run_tests():
    """Run system tests."""
    print("🧪 Running OctoBuddy System Tests...")
    print()
    
    # Test 1: Configuration
    print("Test 1: Configuration Loading")
    try:
        from octo.config import load_config
        config = load_config()
        assert "evolution" in config
        assert "personality" in config
        print("  ✓ Config loaded successfully")
    except Exception as e:
        print(f"  ✗ Config test failed: {e}")
        return False
    
    # Test 2: State Management
    print("\nTest 2: State Management")
    try:
        from octo.storage import load_state, save_state, DEFAULT_STATE
        state = load_state()
        assert "evolution_vars" in state
        assert "personality_traits" in state
        print("  ✓ State management working")
    except Exception as e:
        print(f"  ✗ State test failed: {e}")
        return False
    
    # Test 3: Memory System
    print("\nTest 3: Memory System")
    try:
        from octo import memory
        memory.initialize_memory()
        memory.remember_event("test_event", {"test": True}, config)
        recent = memory.get_recent_events(1)
        assert len(recent) > 0
        print("  ✓ Memory system working")
    except Exception as e:
        print(f"  ✗ Memory test failed: {e}")
        return False
    
    # Test 4: Evolution Engine
    print("\nTest 4: Evolution Engine")
    try:
        from octo.evolution_engine import process_evolution_cycle
        test_state = dict(DEFAULT_STATE)
        result = process_evolution_cycle(test_state, config)
        assert "evolution_vars" in result
        print("  ✓ Evolution engine working")
    except Exception as e:
        print(f"  ✗ Evolution test failed: {e}")
        return False
    
    # Test 5: Abilities System
    print("\nTest 5: Abilities System")
    try:
        from octo.abilities import list_abilities, get_available_abilities
        abilities = list_abilities()
        assert len(abilities) > 0
        print(f"  ✓ Abilities system working ({len(abilities)} abilities)")
    except Exception as e:
        print(f"  ✗ Abilities test failed: {e}")
        return False
    
    # Test 6: Animation System
    print("\nTest 6: Animation System")
    try:
        from octo.animation import initialize_animation_state, update_animation
        anim_state = initialize_animation_state(config)
        updated = update_animation(anim_state, state, config, 0.016)
        assert "tentacles" in updated
        print("  ✓ Animation system working")
    except Exception as e:
        print(f"  ✗ Animation test failed: {e}")
        return False
    
    # Test 7: Pixel Art Rendering
    print("\nTest 7: Pixel Art Rendering")
    try:
        from octo.pixel_art import render_pixel_art
        from octo.brain import get_mood, get_stage
        mood = get_mood(state, config)
        stage = get_stage(state, config)
        pixels = render_pixel_art(state, config, stage, mood)
        assert pixels.shape == (128, 128, 3)
        print("  ✓ Pixel art rendering working")
    except Exception as e:
        print(f"  ✗ Pixel art test failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All tests passed!")
    print("=" * 50)
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="OctoBuddy - Self-evolving AI desktop companion"
    )
    parser.add_argument(
        "--terminal",
        action="store_true",
        help="Launch terminal UI instead of desktop companion"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run system tests"
    )
    
    args = parser.parse_args()
    
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    elif args.terminal:
        launch_terminal()
    else:
        launch_desktop()


if __name__ == "__main__":
    main()
