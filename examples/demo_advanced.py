#!/usr/bin/env python3
"""
Advanced demo showing all OctoBuddy features and new event types
"""
import sys
import time
from octo.core import OctoBuddy
from octo.config import CONFIG

def demo_all_events():
    """Demonstrate all supported event types"""
    
    events = [
        ("studied_python", "Basic Python study session"),
        ("studied_security_plus", "Security+ certification study"),
        ("did_tryhackme", "TryHackMe room completed"),
        ("passed_lab", "Lab exercise passed"),
        ("ctf_challenge", "CTF challenge solved"),
        ("code_review", "Code review completed"),
        ("read_documentation", "Documentation read"),
        ("bug_bounty", "Bug bounty submitted"),
        ("finished_class", "WGU class completed"),
    ]
    
    buddy = OctoBuddy(CONFIG)
    
    print("\n=== OctoBuddy Feature Demo ===\n")
    print("This demo will show OctoBuddy reacting to different events.")
    print("Watch as OctoBuddy gains XP and evolves!\n")
    
    for event_type, description in events:
        print(f"\n[EVENT] {description} ({event_type})")
        input("Press Enter to continue...")
        buddy.handle_event(event_type)
        time.sleep(2)  # Give user time to see the result
    
    print("\n=== Demo Complete! ===")
    print("Check octo_state.json to see OctoBuddy's progress.")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--demo-all":
        demo_all_events()
    else:
        # Single event demo (original behavior)
        event = sys.argv[1] if len(sys.argv) > 1 else "studied_python"
        buddy = OctoBuddy(CONFIG)
        buddy.handle_event(event)

if __name__ == "__main__":
    main()
