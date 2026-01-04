"""
Animation engine for OctoBuddy.

Manages:
- Mood variables (energy, curiosity, happiness, calmness)
- Animation parameters derived from moods
- Event-driven mood changes
- Smooth mood transitions
"""

import time
import random


class AnimationState:
    """
    Central animation state manager.
    
    Tracks mood variables and translates them into animation parameters
    for tentacles, eyes, and other body parts.
    """
    
    def __init__(self):
        """Initialize with neutral mood."""
        # Core mood variables (0.0 to 1.0)
        self.energy = 0.5       # High = fast, bouncy; Low = slow, droopy
        self.curiosity = 0.5    # High = responsive to cursor; Low = ignores it
        self.happiness = 0.5    # High = perky, upward; Low = droopy
        self.calmness = 0.5     # High = smooth; Low = jittery, nervous
        
        # Target values for smooth transitions
        self._target_energy = 0.5
        self._target_curiosity = 0.5
        self._target_happiness = 0.5
        self._target_calmness = 0.5
        
        # Transition speed
        self.transition_speed = 0.05
        
        # Event tracking
        self.last_click_time = 0
        self.last_idle_time = time.time()
        self.typing_burst_count = 0
        self.last_typing_time = 0
        
        # Learning moments (special events)
        self.learning_mode = False
        self.learning_end_time = 0
    
    def update(self, dt=1.0):
        """
        Update mood variables with smooth transitions.
        
        Args:
            dt: Delta time (time step)
        """
        # Smooth transition toward target moods
        self.energy = self._lerp(self.energy, self._target_energy, self.transition_speed)
        self.curiosity = self._lerp(self.curiosity, self._target_curiosity, self.transition_speed)
        self.happiness = self._lerp(self.happiness, self._target_happiness, self.transition_speed)
        self.calmness = self._lerp(self.calmness, self._target_calmness, self.transition_speed)
        
        # Handle learning mode timeout
        if self.learning_mode and time.time() > self.learning_end_time:
            self.learning_mode = False
            self.set_mood_targets(energy=0.5, curiosity=0.7, happiness=0.6)
        
        # Idle behavior: gradually reduce energy and increase calmness
        idle_time = time.time() - self.last_idle_time
        if idle_time > 30:  # After 30 seconds of no interaction
            self._target_energy = max(0.2, self._target_energy - 0.01)
            self._target_calmness = min(0.9, self._target_calmness + 0.01)
    
    def _lerp(self, current, target, speed):
        """Linear interpolation helper."""
        return current + (target - current) * speed
    
    def set_mood_targets(self, energy=None, curiosity=None, happiness=None, calmness=None):
        """
        Set target mood values for smooth transitions.
        
        Args:
            energy: Target energy level (0-1) or None to keep current
            curiosity: Target curiosity level (0-1) or None to keep current
            happiness: Target happiness level (0-1) or None to keep current
            calmness: Target calmness level (0-1) or None to keep current
        """
        if energy is not None:
            self._target_energy = max(0.0, min(1.0, energy))
        if curiosity is not None:
            self._target_curiosity = max(0.0, min(1.0, curiosity))
        if happiness is not None:
            self._target_happiness = max(0.0, min(1.0, happiness))
        if calmness is not None:
            self._target_calmness = max(0.0, min(1.0, calmness))
    
    def set_mood_immediate(self, energy=None, curiosity=None, happiness=None, calmness=None):
        """
        Set mood values immediately without transition.
        
        Useful for sudden reactions to events.
        """
        if energy is not None:
            self.energy = self._target_energy = max(0.0, min(1.0, energy))
        if curiosity is not None:
            self.curiosity = self._target_curiosity = max(0.0, min(1.0, curiosity))
        if happiness is not None:
            self.happiness = self._target_happiness = max(0.0, min(1.0, happiness))
        if calmness is not None:
            self.calmness = self._target_calmness = max(0.0, min(1.0, calmness))
    
    # Event handlers
    
    def on_click(self):
        """Handle user click event."""
        self.last_click_time = time.time()
        self.last_idle_time = time.time()
        
        # Quick energy burst
        self.set_mood_targets(energy=0.9, curiosity=0.8, happiness=0.8, calmness=0.5)
    
    def on_focus_gained(self):
        """Handle window focus gained."""
        self.last_idle_time = time.time()
        self.set_mood_targets(energy=0.7, curiosity=0.7, happiness=0.7)
    
    def on_focus_lost(self):
        """Handle window focus lost."""
        self.set_mood_targets(energy=0.3, curiosity=0.2, calmness=0.8)
    
    def on_typing_burst(self):
        """Handle typing activity burst."""
        self.last_typing_time = time.time()
        self.last_idle_time = time.time()
        self.typing_burst_count += 1
        
        # Brief excited reaction
        current_energy = min(1.0, self.energy + 0.2)
        self.set_mood_targets(energy=current_energy, curiosity=0.6, calmness=0.4)
    
    def on_idle_timeout(self, duration):
        """
        Handle idle timeout.
        
        Args:
            duration: How long the user has been idle (seconds)
        """
        if duration > 60:
            # Very idle - sleepy
            self.set_mood_targets(energy=0.1, curiosity=0.1, calmness=0.95)
        elif duration > 30:
            # Moderately idle - calm
            self.set_mood_targets(energy=0.3, curiosity=0.3, calmness=0.8)
    
    def on_learning_moment(self, duration=10.0):
        """
        Handle special learning event.
        
        Args:
            duration: How long the learning mode should last (seconds)
        """
        self.learning_mode = True
        self.learning_end_time = time.time() + duration
        self.last_idle_time = time.time()
        
        # Excited and curious during learning
        self.set_mood_targets(energy=0.9, curiosity=1.0, happiness=0.8, calmness=0.3)
    
    def get_mood_string(self):
        """
        Get a text description of current mood.
        
        Returns a string like "curious" or "sleepy" based on mood variables.
        """
        # Determine dominant mood characteristic
        if self.energy < 0.3 and self.calmness > 0.7:
            return "sleepy"
        elif self.curiosity > 0.7:
            return "curious"
        elif self.energy > 0.8:
            return "hyper"
        elif self.happiness > 0.7:
            return "happy"
        elif self.calmness < 0.3:
            return "nervous"
        elif self.happiness < 0.3:
            return "sad"
        else:
            return "neutral"
    
    def apply_random_mood_shift(self, intensity=0.1):
        """
        Apply small random mood variations for organic feel.
        
        Args:
            intensity: How much to shift (0-1)
        """
        self._target_energy += random.uniform(-intensity, intensity)
        self._target_curiosity += random.uniform(-intensity, intensity)
        self._target_happiness += random.uniform(-intensity, intensity)
        self._target_calmness += random.uniform(-intensity, intensity)
        
        # Clamp values
        self._target_energy = max(0.0, min(1.0, self._target_energy))
        self._target_curiosity = max(0.0, min(1.0, self._target_curiosity))
        self._target_happiness = max(0.0, min(1.0, self._target_happiness))
        self._target_calmness = max(0.0, min(1.0, self._target_calmness))


def map_octobuddy_mood_to_animation(octobuddy_mood):
    """
    Convert OctoBuddy's traditional mood system to animation state.
    
    This provides backward compatibility with the existing mood system.
    
    Args:
        octobuddy_mood: String mood from the existing system
    
    Returns:
        Tuple of (energy, curiosity, happiness, calmness)
    """
    mood_mappings = {
        "sleepy": (0.2, 0.2, 0.4, 0.9),
        "curious": (0.6, 0.9, 0.6, 0.6),
        "hyper": (1.0, 0.7, 0.8, 0.2),
        "goofy": (0.7, 0.5, 0.9, 0.4),
        "chaotic": (0.9, 0.8, 0.6, 0.1),
        "proud": (0.6, 0.5, 0.9, 0.7),
        "confused": (0.5, 0.7, 0.4, 0.4),
        "excited": (0.95, 0.8, 0.95, 0.3),
    }
    
    return mood_mappings.get(octobuddy_mood, (0.5, 0.5, 0.5, 0.5))
