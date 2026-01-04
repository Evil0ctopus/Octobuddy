"""
Physics engine for OctoBuddy's procedural animation system.

This module provides the core physics components for natural, spring-based motion:
- Vector2D: 2D vector operations
- TentacleSegment: Individual bone/segment with physics properties
- Spring-damper system for realistic motion
"""

import math


class Vector2D:
    """Simple 2D vector class for physics calculations."""
    
    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)
    
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar):
        return Vector2D(self.x / scalar, self.y / scalar)
    
    def length(self):
        """Calculate vector magnitude."""
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def normalize(self):
        """Return normalized vector (length = 1)."""
        length = self.length()
        if length > 0:
            return Vector2D(self.x / length, self.y / length)
        return Vector2D(0, 0)
    
    def dot(self, other):
        """Calculate dot product."""
        return self.x * other.x + self.y * other.y
    
    def distance_to(self, other):
        """Calculate distance to another vector."""
        return (self - other).length()
    
    def copy(self):
        """Create a copy of this vector."""
        return Vector2D(self.x, self.y)
    
    def __repr__(self):
        return f"Vector2D({self.x:.2f}, {self.y:.2f})"


class TentacleSegment:
    """
    A single segment (bone) of a tentacle with physics properties.
    
    Uses Verlet integration for stable physics simulation:
    - Position and previous position track movement
    - Forces are accumulated and applied each frame
    - Spring constraints connect segments together
    """
    
    def __init__(self, position, length=20.0, mass=1.0):
        """
        Initialize a tentacle segment.
        
        Args:
            position: Vector2D starting position
            length: Desired length from parent (used for constraints)
            mass: Mass for physics calculations
        """
        self.position = position.copy()
        self.prev_position = position.copy()
        self.length = length
        self.mass = mass
        self.forces = Vector2D(0, 0)
        self.pinned = False  # If True, segment doesn't move
    
    def apply_force(self, force):
        """Apply a force to this segment."""
        self.forces = self.forces + force
    
    def update(self, dt, damping=0.98):
        """
        Update segment position using Verlet integration.
        
        Args:
            dt: Time step (delta time)
            damping: Velocity damping factor (0-1), lower = more damping
        """
        if self.pinned:
            self.forces = Vector2D(0, 0)
            return
        
        # Verlet integration: x(t+dt) = x(t) + (x(t) - x(t-dt)) * damping + a * dt^2
        velocity = (self.position - self.prev_position) * damping
        acceleration = self.forces / self.mass
        
        self.prev_position = self.position.copy()
        self.position = self.position + velocity + acceleration * (dt * dt)
        
        # Reset forces for next frame
        self.forces = Vector2D(0, 0)
    
    def constrain_to_parent(self, parent_pos, stiffness=1.0):
        """
        Apply spring constraint to maintain distance from parent.
        
        Args:
            parent_pos: Vector2D position of parent segment
            stiffness: Constraint strength (0-1), higher = stiffer
        """
        if self.pinned:
            return
        
        # Calculate difference from desired length
        delta = self.position - parent_pos
        current_length = delta.length()
        
        if current_length > 0:
            # Move segment toward correct distance
            difference = (current_length - self.length) / current_length
            offset = delta * (difference * stiffness * 0.5)
            self.position = self.position - offset


def apply_spring_force(seg1, seg2, rest_length, spring_k=0.5, damping_k=0.1):
    """
    Apply spring-damper force between two segments.
    
    This creates natural, bouncy motion between connected segments.
    
    Args:
        seg1: First TentacleSegment
        seg2: Second TentacleSegment
        rest_length: Natural spring length
        spring_k: Spring stiffness constant
        damping_k: Damping constant (reduces oscillation)
    """
    # Calculate displacement
    delta = seg2.position - seg1.position
    current_length = delta.length()
    
    if current_length == 0:
        return
    
    # Spring force (Hooke's law: F = -k * x)
    extension = current_length - rest_length
    direction = delta.normalize()
    spring_force = direction * (extension * spring_k)
    
    # Velocity-based damping
    velocity1 = seg1.position - seg1.prev_position
    velocity2 = seg2.position - seg2.prev_position
    relative_velocity = velocity2 - velocity1
    damping_force = direction * (relative_velocity.dot(direction) * damping_k)
    
    # Apply equal and opposite forces
    total_force = spring_force + damping_force
    seg1.apply_force(total_force)
    seg2.apply_force(total_force * -1.0)


def apply_gravity(segment, gravity=Vector2D(0, 0.5)):
    """Apply gravity force to a segment."""
    segment.apply_force(gravity * segment.mass)


def apply_wind(segment, wind_force=Vector2D(0, 0)):
    """Apply wind/environmental force to a segment."""
    segment.apply_force(wind_force)
