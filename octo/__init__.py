"""
OctoBuddy - Your AI Desktop Companion

A living, learning AI desktop companion for Windows that evolves with you.
"""

__version__ = "1.0.0"
__author__ = "Evil0ctopus"

# Core imports
from .core import OctoBuddy
from .core_enhanced import EnhancedOctoBuddy
from .config import CONFIG

# AI Brain
from .ai_brain import EnhancedBrain, Memory, PersonalityTraits

# Observation & Interaction
from .observation import ObservationSystem, WindowMonitor, ActivityDetector, TeachingInterface

# Expansion System
from .expansion import ExpansionSystem, SkillLoader, AnimationLoader, DialogueExpander

# UI
from .ui_terminal import render
# Desktop UI imported separately to avoid PyQt6 requirement if not needed

__all__ = [
    # Core
    'OctoBuddy',
    'EnhancedOctoBuddy',
    'CONFIG',
    
    # AI Brain
    'EnhancedBrain',
    'Memory',
    'PersonalityTraits',
    
    # Observation
    'ObservationSystem',
    'WindowMonitor',
    'ActivityDetector',
    'TeachingInterface',
    
    # Expansion
    'ExpansionSystem',
    'SkillLoader',
    'AnimationLoader',
    'DialogueExpander',
    
    # UI
    'render',
]

