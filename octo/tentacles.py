"""
Tentacle system for OctoBuddy's procedural animation.

Each tentacle is a chain of physics-enabled segments that can:
- Sway idly with natural motion
- React to external stimuli (cursor, mood changes)
- Express different moods through motion parameters
"""

import math
import random
from .physics import Vector2D, TentacleSegment, apply_spring_force, apply_gravity


class Tentacle:
    """
    A procedural tentacle made of physics-based segments.
    
    Tentacles respond to:
    - Mood parameters (stiffness, energy, responsiveness)
    - Cursor position (attraction/tracking)
    - Idle motion (natural swaying)
    """
    
    def __init__(self, base_position, num_segments=8, segment_length=15.0, angle=0.0):
        """
        Initialize a tentacle chain.
        
        Args:
            base_position: Vector2D anchor point (doesn't move)
            num_segments: Number of segments in the chain
            segment_length: Length of each segment
            angle: Initial angle in radians
        """
        self.base_position = base_position.copy()
        self.segments = []
        self.num_segments = num_segments
        self.segment_length = segment_length
        
        # Create segment chain
        current_pos = base_position.copy()
        for i in range(num_segments):
            # Initial position follows the angle
            offset_x = math.cos(angle) * segment_length * i
            offset_y = math.sin(angle) * segment_length * i
            pos = Vector2D(
                base_position.x + offset_x,
                base_position.y + offset_y
            )
            
            segment = TentacleSegment(pos, segment_length, mass=1.0 - i * 0.05)
            
            # First segment is pinned to base
            if i == 0:
                segment.pinned = True
            
            self.segments.append(segment)
        
        # Idle motion parameters
        self.idle_phase = random.uniform(0, math.pi * 2)
        self.idle_speed = 0.05
        self.idle_amplitude = 1.0
        
        # Mood-driven parameters (set by update_mood)
        self.stiffness = 0.5
        self.energy = 1.0
        self.responsiveness = 0.5
        self.gravity_strength = 0.3
    
    def update_mood(self, energy=1.0, curiosity=0.5, happiness=0.5, calmness=0.5):
        """
        Update tentacle behavior based on mood variables.
        
        Args:
            energy: 0-1, affects motion speed and gravity resistance
            curiosity: 0-1, affects responsiveness to cursor
            happiness: 0-1, affects perkiness (upward tendency)
            calmness: 0-1, affects motion smoothness and damping
        """
        self.energy = energy
        self.responsiveness = curiosity
        
        # High energy = stiffer, faster movement
        self.stiffness = 0.3 + energy * 0.5
        self.idle_speed = 0.03 + energy * 0.07
        self.idle_amplitude = 0.5 + energy * 2.0
        
        # High happiness = less gravity droop
        self.gravity_strength = 0.5 - happiness * 0.4
        
        # Low calmness = more jittery (higher amplitude)
        if calmness < 0.3:
            self.idle_amplitude *= 1.5
    
    def update(self, dt=1.0, cursor_pos=None, cursor_attraction=0.0):
        """
        Update tentacle physics simulation.
        
        Args:
            dt: Delta time (frame time step)
            cursor_pos: Vector2D cursor position (or None)
            cursor_attraction: 0-1, how much to track cursor
        """
        # Update idle motion phase
        self.idle_phase += self.idle_speed * self.energy
        
        # Apply forces to segments
        for i, segment in enumerate(self.segments):
            if segment.pinned:
                continue
            
            # Gravity (with mood-based strength)
            gravity = Vector2D(0, self.gravity_strength * segment.mass)
            segment.apply_force(gravity)
            
            # Idle swaying (sinusoidal wave motion)
            # Each segment has a phase offset for wave-like motion
            phase_offset = i * 0.3
            sway_x = math.sin(self.idle_phase + phase_offset) * self.idle_amplitude
            sway_force = Vector2D(sway_x * 0.1, 0)
            segment.apply_force(sway_force)
            
            # Cursor attraction (if enabled)
            if cursor_pos and cursor_attraction > 0:
                to_cursor = cursor_pos - segment.position
                distance = to_cursor.length()
                
                if distance > 0:
                    # Stronger attraction for tip segments
                    segment_factor = (i + 1) / self.num_segments
                    attraction_strength = cursor_attraction * self.responsiveness * segment_factor * 0.5
                    attraction_force = to_cursor.normalize() * attraction_strength
                    segment.apply_force(attraction_force)
        
        # Update segment positions (Verlet integration)
        damping = 0.95 + self.stiffness * 0.03  # Mood affects damping
        for segment in self.segments:
            segment.update(dt, damping=damping)
        
        # Apply constraints to keep segments connected
        # Multiple passes for stability
        for _ in range(3):
            # First segment stays at base
            self.segments[0].position = self.base_position.copy()
            
            # Constrain each segment to its parent
            for i in range(1, len(self.segments)):
                parent = self.segments[i - 1]
                self.segments[i].constrain_to_parent(
                    parent.position,
                    stiffness=self.stiffness
                )
    
    def get_tip_position(self):
        """Get the position of the tentacle tip."""
        return self.segments[-1].position if self.segments else self.base_position
    
    def get_segment_positions(self):
        """Get list of all segment positions for rendering."""
        return [seg.position for seg in self.segments]


class TentacleSystem:
    """
    Manager for multiple tentacles.
    
    Creates and updates all of OctoBuddy's tentacles,
    applying consistent mood parameters to all of them.
    """
    
    def __init__(self, center_position, num_tentacles=6):
        """
        Initialize tentacle system.
        
        Args:
            center_position: Vector2D center point for tentacle base
            num_tentacles: Number of tentacles to create
        """
        self.center = center_position
        self.tentacles = []
        
        # Create tentacles in a circle around the center
        for i in range(num_tentacles):
            angle = (i / num_tentacles) * math.pi * 2
            # Offset base positions slightly
            base_x = center_position.x + math.cos(angle) * 20
            base_y = center_position.y + math.sin(angle) * 20
            base_pos = Vector2D(base_x, base_y)
            
            # Initial angle points outward
            initial_angle = angle + math.pi / 2
            
            tentacle = Tentacle(
                base_pos,
                num_segments=8,
                segment_length=12.0,
                angle=initial_angle
            )
            self.tentacles.append(tentacle)
    
    def update_mood(self, energy=1.0, curiosity=0.5, happiness=0.5, calmness=0.5):
        """Update mood parameters for all tentacles."""
        for tentacle in self.tentacles:
            tentacle.update_mood(energy, curiosity, happiness, calmness)
    
    def update(self, dt=1.0, cursor_pos=None, cursor_attraction=0.0):
        """Update all tentacles."""
        for tentacle in self.tentacles:
            tentacle.update(dt, cursor_pos, cursor_attraction)
    
    def set_center(self, position):
        """Move the entire tentacle system to a new center position."""
        offset = position - self.center
        self.center = position.copy()
        
        for i, tentacle in enumerate(self.tentacles):
            angle = (i / len(self.tentacles)) * math.pi * 2
            base_x = position.x + math.cos(angle) * 20
            base_y = position.y + math.sin(angle) * 20
            tentacle.base_position = Vector2D(base_x, base_y)
            tentacle.segments[0].position = tentacle.base_position.copy()
