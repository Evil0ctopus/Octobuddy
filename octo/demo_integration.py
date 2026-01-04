"""
Integration example: Combining pixel art with OctoBuddy's evolution system.

This shows how to:
1. Run evolution events
2. Render pixel art after each major change
3. Export snapshots of evolution journey
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG
from core import OctoBuddy
from pixel_art import render_pixel_art, save_pixel_art_ppm, pixel_art_to_ascii
from evolution_engine import get_evolution_summary


def main():
    print("=" * 70)
    print("OCTOBUDDY EVOLUTION + PIXEL ART INTEGRATION DEMO")
    print("=" * 70)
    print()
    
    buddy = OctoBuddy(CONFIG)
    
    print("Starting evolution journey...")
    print(f"Initial: Level {buddy.state['level']}, XP {buddy.state['xp']}")
    print()
    
    # Define milestones to capture snapshots
    milestones = [
        (10, "studied_python", 5, "Early learning"),
        (20, "studied_security_plus", 3, "Security focus"),
        (30, "did_tryhackme", 5, "Hacking practice"),
        (50, "finished_class", 2, "First milestones"),
    ]
    
    snapshot_count = 0
    
    for target_level, event_type, repetitions, description in milestones:
        print(f"\n--- {description} (targeting level ~{target_level}) ---")
        
        # Run events until we reach target level
        while buddy.state.get("level", 1) < target_level:
            buddy.handle_event(event_type)
        
        # Show current state
        summary = get_evolution_summary(buddy.state)
        print(f"\nCurrent State:")
        print(f"  Level: {buddy.state['level']}")
        print(f"  XP: {buddy.state['xp']}")
        print(f"  Mutations: {len(summary['mutations'])}")
        if summary['mutations']:
            for mut in summary['mutations']:
                print(f"    - {mut}")
        
        if summary['dominant_drift']:
            print(f"  Dominant Drift: {summary['dominant_drift']}")
        
        # Render pixel art
        grid = render_pixel_art(buddy.state, CONFIG)
        
        # Show ASCII preview
        print("\nPixel Art (ASCII preview):")
        print(pixel_art_to_ascii(grid, width=50))
        
        # Save snapshot
        snapshot_count += 1
        filename = f"evolution_snapshot_{snapshot_count}_lvl{buddy.state['level']}.ppm"
        save_pixel_art_ppm(grid, filename)
        print(f"\nSaved: {filename}")
    
    print("\n" + "=" * 70)
    print("EVOLUTION JOURNEY COMPLETE")
    print("=" * 70)
    print(f"\nFinal State:")
    print(f"  Level: {buddy.state['level']}")
    print(f"  XP: {buddy.state['xp']}")
    
    summary = get_evolution_summary(buddy.state)
    print(f"  Mutations: {len(summary['mutations'])}")
    for mut in summary['mutations']:
        print(f"    - {mut}")
    
    print(f"\nEvolution Triggers: {len(summary['evolution_triggers'])}")
    for trigger in summary['evolution_triggers']:
        print(f"    - {trigger}")
    
    print(f"\nTotal snapshots saved: {snapshot_count}")
    print("\nView the .ppm files to see how OctoBuddy's appearance evolved!")
    print("Tip: Convert PPM to PNG with ImageMagick: convert file.ppm file.png")


if __name__ == "__main__":
    main()
