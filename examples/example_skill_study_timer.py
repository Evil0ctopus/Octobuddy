"""
Example Custom Skill: Study Timer
Demonstrates how to create a custom skill for OctoBuddy
"""

import time
from datetime import datetime


def skill_info():
    """Return skill metadata"""
    return {
        "name": "study_timer",
        "description": "A simple study session timer",
        "author": "OctoBuddy Community",
        "version": "1.0.0",
        "category": "productivity"
    }


def execute(context=None):
    """
    Execute the skill
    
    Args:
        context: Dictionary with current state, user input, etc.
            Available keys:
            - state: Current OctoBuddy state
            - mood: Current mood
            - stage: Current evolution stage
            - user_name: User's name
            - custom parameters from user input
            
    Returns:
        Dictionary with results:
            - success: Boolean indicating if skill executed successfully
            - message: Message to display to user
            - data: Optional data dictionary
    """
    
    # Get context information
    user_name = context.get("user_name", "friend") if context else "friend"
    duration = context.get("duration", 25) if context else 25  # Default 25 minutes
    
    # Calculate end time
    start_time = datetime.now()
    
    # Create motivational message
    message = f"Good luck with your {duration}-minute study session, {user_name}! "
    message += "I'll be here cheering you on! 🐙"
    
    # Return result
    return {
        "success": True,
        "message": message,
        "data": {
            "start_time": start_time.isoformat(),
            "duration_minutes": duration,
            "activity": "studying"
        }
    }
