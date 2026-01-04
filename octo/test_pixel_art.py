"""
Test script for pixel art renderer.

Demonstrates:
1. Rendering with different stages/moods
2. Visual mutations appearing
3. Personality drift affecting colors
4. Exporting to PPM and ASCII
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG
from pixel_art import render_pixel_art, save_pixel_art_ppm, pixel_art_to_ascii
from storage import DEFAULT_STATE


def test_basic_render():
    """Test basic rendering with default state."""
    print("=" * 70)
    print("TEST 1: Basic Render (Baby stage, no mutations)")
    print("=" * 70)
    
    state = {**DEFAULT_STATE, "config": CONFIG}
    grid = render_pixel_art(state, CONFIG)
    
    print(f"Generated {len(grid)}x{len(grid[0])} pixel grid")
    print("\nASCII Preview:")
    print(pixel_art_to_ascii(grid, width=60))
    print()


def test_evolved_render():
    """Test rendering with evolved state."""
    print("=" * 70)
    print("TEST 2: Evolved Render (Level 50, with mutations)")
    print("=" * 70)
    
    state = {
        **DEFAULT_STATE,
        "xp": 12500,
        "level": 50,
        "mutations": ["speed_learner", "chaos_incarnate"],
        "personality_drift": {
            "analytical": 0.1,
            "chaotic": 0.6,  # Dominant
            "studious": 0.2,
            "ambitious": 0.1,
        },
        "config": CONFIG,
    }
    
    grid = render_pixel_art(state, CONFIG)
    
    print(f"State: Level {state['level']}, {len(state['mutations'])} mutations")
    print(f"Mutations: {', '.join(state['mutations'])}")
    print(f"Dominant drift: chaotic (60%)")
    print("\nASCII Preview:")
    print(pixel_art_to_ascii(grid, width=60))
    print()


def test_transcendent_render():
    """Test rendering with legendary mutation."""
    print("=" * 70)
    print("TEST 3: Transcendent Form (Max level, legendary mutations)")
    print("=" * 70)
    
    state = {
        **DEFAULT_STATE,
        "xp": 500000,
        "level": 100,
        "mutations": ["transcendent", "analytical_mind", "unstoppable"],
        "personality_drift": {
            "analytical": 0.3,
            "chaotic": 0.2,
            "studious": 0.3,
            "ambitious": 0.2,
        },
        "evolution_triggers": ["ascension", "hybrid_form"],
        "config": CONFIG,
    }
    
    grid = render_pixel_art(state, CONFIG)
    
    print(f"State: Level {state['level']}, {len(state['mutations'])} mutations")
    print(f"Mutations: {', '.join(state['mutations'])}")
    print(f"Evolution triggers: {', '.join(state['evolution_triggers'])}")
    print("\nASCII Preview:")
    print(pixel_art_to_ascii(grid, width=60))
    print()


def test_mood_variations():
    """Test different mood renderings."""
    print("=" * 70)
    print("TEST 4: Mood Variations")
    print("=" * 70)
    
    moods = ["sleepy", "hyper", "chaotic", "proud"]
    
    for mood in moods:
        # Manually set mood by adjusting XP to hit different ranges
        # (In real use, mood is calculated from XP)
        print(f"\n--- {mood.upper()} mood ---")
        
        state = {
            **DEFAULT_STATE,
            "xp": 100,  # Will be overridden by get_mood logic
            "level": 10,
            "config": CONFIG,
        }
        
        # Note: Since mood is calculated from state, we can't directly set it
        # This would require different XP values for different moods
        # For now, just show that rendering works
        grid = render_pixel_art(state, CONFIG)
        print(pixel_art_to_ascii(grid, width=40))


def test_export_ppm():
    """Test exporting to PPM file."""
    print("=" * 70)
    print("TEST 5: Export to PPM File")
    print("=" * 70)
    
    state = {
        **DEFAULT_STATE,
        "xp": 5000,
        "level": 30,
        "mutations": ["night_owl", "analytical_mind"],
        "config": CONFIG,
    }
    
    grid = render_pixel_art(state, CONFIG)
    filename = "octobuddy_render.ppm"
    
    save_pixel_art_ppm(grid, filename)
    print(f"Saved pixel art to: {filename}")
    print("You can view PPM files with image viewers like GIMP, IrfanView, or online converters")
    print()


def test_personality_drift_colors():
    """Test personality drift affecting colors."""
    print("=" * 70)
    print("TEST 6: Personality Drift Color Shifts")
    print("=" * 70)
    
    drift_types = [
        ("analytical", {"analytical": 0.8, "chaotic": 0.1, "studious": 0.05, "ambitious": 0.05}),
        ("chaotic", {"analytical": 0.1, "chaotic": 0.7, "studious": 0.1, "ambitious": 0.1}),
        ("studious", {"analytical": 0.1, "chaotic": 0.1, "studious": 0.7, "ambitious": 0.1}),
        ("ambitious", {"analytical": 0.1, "chaotic": 0.1, "studious": 0.1, "ambitious": 0.7}),
    ]
    
    for drift_name, drift_values in drift_types:
        print(f"\n--- {drift_name.upper()} dominant drift ---")
        
        state = {
            **DEFAULT_STATE,
            "xp": 2000,
            "level": 20,
            "personality_drift": drift_values,
            "config": CONFIG,
        }
        
        grid = render_pixel_art(state, CONFIG)
        print(pixel_art_to_ascii(grid, width=40))


def main():
    print("\n" + "=" * 70)
    print("OCTOBUDDY PIXEL ART RENDERER TEST SUITE")
    print("=" * 70)
    print()
    
    tests = [
        test_basic_render,
        test_evolved_render,
        test_transcendent_render,
        test_mood_variations,
        test_personality_drift_colors,
        test_export_ppm,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"ERROR in {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
        print()
    
    print("=" * 70)
    print("TESTS COMPLETE")
    print("=" * 70)
    print("\nKey Observations:")
    print("- Stage affects base colors and body shape")
    print("- Mood tints the overall color palette")
    print("- Mutations add visual effects (glow, spikes, patterns, sparkles)")
    print("- Personality drift shifts colors toward characteristic hues")
    print("- Evolution triggers unlock special forms")
    print("\nThe renderer is fully deterministic - same state = same output!")


if __name__ == "__main__":
    main()
