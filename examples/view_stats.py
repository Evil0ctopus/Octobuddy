#!/usr/bin/env python3
"""
View OctoBuddy's current stats and progress
"""
import json
from pathlib import Path
from octo.config import CONFIG

def view_stats():
    """Display OctoBuddy's current stats"""
    
    state_file = Path("octo_state.json")
    
    if not state_file.exists():
        print("No state file found. OctoBuddy hasn't been run yet!")
        print("Run: python examples/demo_run.py studied_python")
        return
    
    with state_file.open("r") as f:
        state = json.load(f)
    
    # Calculate current mood and stage
    from octo.brain import get_mood, get_stage
    
    mood = get_mood(state, CONFIG)
    stage = get_stage(state, CONFIG)
    
    print("\n" + "="*50)
    print("         OctoBuddy Stats")
    print("="*50)
    print(f"\nName:   {state.get('name', 'OctoBuddy')}")
    print(f"Level:  {state.get('level', 1)}")
    print(f"XP:     {state.get('xp', 0)}")
    print(f"Mood:   {mood}")
    print(f"Stage:  {stage}")
    
    print("\n" + "-"*50)
    print("Activity Summary")
    print("-"*50)
    
    activities = {
        "Python study sessions": state.get("study_events", 0),
        "Security+ study sessions": state.get("security_plus_study", 0),
        "WGU classes finished": state.get("classes_finished", 0),
        "TryHackMe rooms": state.get("tryhackme_rooms", 0),
        "Labs passed": state.get("labs_passed", 0),
        "Bug bounties": state.get("bug_bounties", 0),
        "CTF challenges": state.get("ctf_challenges", 0),
        "Code reviews": state.get("code_reviews", 0),
        "Docs read": state.get("docs_read", 0),
    }
    
    for activity, count in activities.items():
        if count > 0:
            print(f"  {activity}: {count}")
    
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    view_stats()
