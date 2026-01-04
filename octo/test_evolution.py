"""
Test script for the evolution engine system.

This demonstrates:
1. Mutation acquisition
2. Personality drift tracking
3. Evolution triggers
4. XP modifier effects
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG
from core import OctoBuddy
from evolution_engine import get_evolution_summary

def main():
    print("=" * 60)
    print("OCTOBUDDY EVOLUTION ENGINE TEST")
    print("=" * 60)
    print()
    
    # Initialize OctoBuddy
    buddy = OctoBuddy(CONFIG)
    
    print("Initial state:")
    print(f"  XP: {buddy.state.get('xp', 0)}")
    print(f"  Level: {buddy.state.get('level', 1)}")
    print(f"  Mutations: {buddy.state.get('mutations', [])}")
    print()
    
    # Simulate learning events
    print("Simulating learning journey...")
    print("-" * 60)
    
    events = [
        ("studied_python", "Python study session"),
        ("studied_python", "Python study session"),
        ("studied_security_plus", "Security+ study"),
        ("did_tryhackme", "TryHackMe room"),
        ("did_tryhackme", "TryHackMe room"),
        ("studied_python", "Python study session"),
        ("passed_lab", "Lab completion"),
        ("studied_security_plus", "Security+ study"),
        ("studied_python", "Python study session"),
        ("finished_class", "WGU class finished!"),
    ]
    
    for event_type, description in events:
        print(f"\nEvent: {description}")
        buddy.handle_event(event_type)
        
        # Check for mutations or triggers
        if buddy.state.get("last_evolution_events"):
            for evo_type, evo_data in buddy.state.get("last_evolution_events", []):
                print(f"  🌟 {evo_type.upper()}: {evo_data}")
    
    print("\n" + "=" * 60)
    print("FINAL EVOLUTION SUMMARY")
    print("=" * 60)
    
    summary = get_evolution_summary(buddy.state)
    
    print(f"\nXP: {buddy.state.get('xp', 0)}")
    print(f"Level: {buddy.state.get('level', 1)}")
    print(f"\nMutations ({summary['mutation_count']}):")
    for mutation in summary['mutations']:
        print(f"  - {mutation}")
    
    print(f"\nPersonality Drift:")
    for drift_type, value in summary['personality_drift'].items():
        bar = "█" * int(value * 20)
        print(f"  {drift_type:12s}: {bar} {value:.2%}")
    
    if summary['dominant_drift']:
        print(f"\nDominant Tendency: {summary['dominant_drift'].upper()}")
    
    print(f"\nEvolution Triggers:")
    for trigger in summary['evolution_triggers']:
        print(f"  - {trigger}")
    
    print(f"\nActive Modifiers:")
    mods = summary['modifiers']
    print(f"  XP Multiplier: {mods['xp_modifier']:.2f}x")
    print(f"  Security XP: {mods['xp_modifier_security']:.2f}x")
    print(f"  Milestone XP: {mods['xp_modifier_milestone']:.2f}x")
    print(f"  Chaos Factor: {mods['chaos_factor']:.2f}x")
    
    if mods['special_flags']:
        print(f"\nSpecial Flags: {', '.join(mods['special_flags'])}")
    
    print("\n" + "=" * 60)
    print("Note: Run this multiple times to see different mutations!")
    print("=" * 60)

if __name__ == "__main__":
    main()
