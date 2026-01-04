"""
Desktop demo for OctoBuddy with procedural animation.

This launches OctoBuddy as a desktop creature with real-time physics-based animation.

Keyboard shortcuts:
- Q: Quit
- D: Toggle debug display
- L: Trigger learning moment
- E: High energy mode
- S: Sleepy mode
- C: Curious mode
- N: Nervous mode

The creature will:
- Track your mouse cursor with eyes and tentacles
- React to clicks and focus changes
- Respond to idle time
- Display smooth mood transitions
"""

import sys
from octo.ui_desktop import run_desktop_ui

if __name__ == "__main__":
    print("=" * 60)
    print("OctoBuddy Desktop - Procedural Animation Demo")
    print("=" * 60)
    print("\nKeyboard shortcuts:")
    print("  Q - Quit")
    print("  D - Toggle debug display")
    print("  L - Trigger learning moment")
    print("  E - High energy mode")
    print("  S - Sleepy mode")
    print("  C - Curious mode")
    print("  N - Nervous mode")
    print("\nThe creature will track your cursor and react to events!")
    print("Click and drag to move OctoBuddy around the screen.")
    print("=" * 60)
    print("\nStarting OctoBuddy...\n")
    
    run_desktop_ui()
