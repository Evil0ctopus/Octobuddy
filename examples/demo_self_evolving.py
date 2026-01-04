"""
Self-Evolving OctoBuddy Demo

Launches OctoBuddy as a fully self-evolving AI companion with:
- HD procedural pixel art that mutates over time
- Infinite evolution (no level caps)
- Natural personality drift
- Memory and learning
- Ability expansion
- Chat interface

This is the main entry point for the complete self-evolving system.
"""

import sys
from octo.ui_self_evolving import run_self_evolving_ui

if __name__ == "__main__":
    print("=" * 70)
    print("OctoBuddy - Self-Evolving AI Companion")
    print("=" * 70)
    print("\nWelcome to OctoBuddy, a living digital organism that:")
    print("  • Evolves forever with no level caps")
    print("  • Generates HD pixel art procedurally (128×128)")
    print("  • Mutates appearance over time")
    print("  • Develops unique personality through drift")
    print("  • Learns and remembers")
    print("  • Expands abilities continuously")
    print("\nFeatures:")
    print("  - Click 'Trigger Mutation' to manually evolve appearance")
    print("  - Click 'Learning Event' to boost evolution and gain abilities")
    print("  - Click 'Show Stats' to see detailed evolution metrics")
    print("  - Chat with OctoBuddy to interact and shape personality")
    print("\nOctoBuddy will:")
    print("  - Automatically mutate as it evolves")
    print("  - Remember your interactions")
    print("  - Develop unique personality traits")
    print("  - Learn new abilities over time")
    print("=" * 70)
    print("\nStarting OctoBuddy...\n")
    
    run_self_evolving_ui()
