"""
OctoBuddy Desktop Application Launcher
Main entry point for the Windows desktop companion
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from octo.config import CONFIG
from octo.core_enhanced import EnhancedOctoBuddy
from octo.ui_desktop import run_desktop_ui, OctoBuddyWindow
from octo.brain import get_mood, get_stage
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer


def main():
    """Main entry point for OctoBuddy desktop application"""
    parser = argparse.ArgumentParser(description="OctoBuddy - Your AI Desktop Companion")
    parser.add_argument('--enable-observation', action='store_true',
                       help='Enable window/activity observation (requires permission)')
    parser.add_argument('--terminal', action='store_true',
                       help='Run in terminal mode instead of desktop UI')
    
    args = parser.parse_args()
    
    # Create OctoBuddy instance
    buddy = EnhancedOctoBuddy(CONFIG, enable_observation=args.enable_observation)
    
    # Get initial state
    mood = get_mood(buddy.state, CONFIG)
    stage = get_stage(buddy.state, CONFIG)
    
    if args.terminal:
        # Terminal mode
        from octo.ui_terminal import render
        
        phrase = "Hello! I'm OctoBuddy! I'm running in terminal mode."
        render({**buddy.state, "config": CONFIG}, mood, stage, phrase)
        
        print("\n" + "="*50)
        print("OctoBuddy is running in terminal mode.")
        print("Try: python octobuddy_desktop.py (without --terminal)")
        print("="*50)
        
    else:
        # Desktop UI mode
        app = QApplication(sys.argv)
        
        # Create window
        window = OctoBuddyWindow(buddy.state, CONFIG, mood, stage)
        buddy.ui = window
        
        # Set initial phrase
        initial_phrases = [
            "Hello! I'm OctoBuddy! Double-click me to chat!",
            "Hi there! I'm here to help you learn and grow!",
            "Hey! I'm your AI companion! Let's do great things together!",
        ]
        
        import random
        window.set_phrase(random.choice(initial_phrases))
        
        # Position window in bottom-right corner
        screen = app.primaryScreen().geometry()
        window.move(screen.width() - window.width() - 50,
                   screen.height() - window.height() - 100)
        
        # Show window
        window.show()
        
        # Setup idle timer to call buddy.idle_update()
        idle_timer = QTimer()
        idle_timer.timeout.connect(buddy.idle_update)
        idle_timer.start(15000)  # Every 15 seconds
        
        # Attach buddy to window for interaction
        window.buddy = buddy
        
        # Run application
        try:
            sys.exit(app.exec())
        finally:
            buddy.shutdown()


if __name__ == "__main__":
    main()
