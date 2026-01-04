# OctoBuddy package init

# Core modules
from .core import OctoBuddy
from .brain import update_state_from_event, get_mood, get_stage
from .personality import get_phrase_for_event
from .storage import load_state, save_state
from .config import CONFIG

# Animation system
from .physics import Vector2D, TentacleSegment
from .tentacles import Tentacle, TentacleSystem
from .animation_engine import AnimationState, map_octobuddy_mood_to_animation
from .events import EventSystem, EventType

__all__ = [
    # Core
    'OctoBuddy',
    'update_state_from_event',
    'get_mood',
    'get_stage',
    'get_phrase_for_event',
    'load_state',
    'save_state',
    'CONFIG',
    # Animation
    'Vector2D',
    'TentacleSegment',
    'Tentacle',
    'TentacleSystem',
    'AnimationState',
    'map_octobuddy_mood_to_animation',
    'EventSystem',
    'EventType',
]

