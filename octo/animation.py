"""
Procedural Animation Engine for OctoBuddy

Implements physics-based animation for tentacles and body movement:
- Spring-like tentacle physics (position, velocity, damping)
- Mood-based motion (amplitude, frequency controlled by evolution vars)
- Idle fidgeting and cursor tracking
- Event-driven reactions

Architecture:
- Separates animation state from rendering
- Pure functions for physics updates
- State holds current animation frame data
- Rendering consumes animation data without modifying it
"""

import math
import random
from typing import Dict, Any, List, Tuple, Optional


# =============================================================================
# ANIMATION STATE
# =============================================================================

def initialize_animation_state(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create initial animation state for OctoBuddy.
    
    Returns dict with:
    - tentacles: List of tentacle states (position, velocity, target)
    - body: Body position and rotation
    - eyes: Eye positions and blink state
    - cursor_pos: Last known cursor position
    """
    return {
        "tentacles": [
            {
                "id": i,
                "position": {"x": 0.0, "y": 0.0},
                "velocity": {"x": 0.0, "y": 0.0},
                "target": {"x": 0.0, "y": 0.0},
                "angle": (i / 8) * 360,  # Evenly distributed
            }
            for i in range(8)  # 8 tentacles
        ],
        "body": {
            "position": {"x": 64.0, "y": 64.0},  # Center of 128x128
            "rotation": 0.0,
            "bob_phase": 0.0,  # For bobbing animation
        },
        "eyes": {
            "left": {"x": 50.0, "y": 50.0, "pupil_offset_x": 0.0, "pupil_offset_y": 0.0},
            "right": {"x": 78.0, "y": 50.0, "pupil_offset_x": 0.0, "pupil_offset_y": 0.0},
            "blink": 0.0,  # 0.0 = open, 1.0 = closed
            "blink_timer": 0.0,
        },
        "cursor_pos": None,
        "time": 0.0,
    }


# =============================================================================
# TENTACLE PHYSICS
# =============================================================================

def update_tentacle_physics(
    tentacle: Dict[str, Any],
    dt: float,
    spring_k: float,
    damping: float,
    mass: float,
) -> Dict[str, Any]:
    """
    Update a single tentacle using spring physics.
    
    F = -k * displacement - damping * velocity
    a = F / mass
    v = v + a * dt
    p = p + v * dt
    """
    tentacle = dict(tentacle)  # Immutable
    
    # Spring force toward target
    dx = tentacle["target"]["x"] - tentacle["position"]["x"]
    dy = tentacle["target"]["y"] - tentacle["position"]["y"]
    
    # F = -k * displacement
    force_x = spring_k * dx
    force_y = spring_k * dy
    
    # Apply damping: F_damping = -damping * velocity
    force_x -= damping * tentacle["velocity"]["x"]
    force_y -= damping * tentacle["velocity"]["y"]
    
    # Acceleration = F / m
    accel_x = force_x / mass
    accel_y = force_y / mass
    
    # Update velocity
    tentacle["velocity"]["x"] += accel_x * dt
    tentacle["velocity"]["y"] += accel_y * dt
    
    # Update position
    tentacle["position"]["x"] += tentacle["velocity"]["x"] * dt
    tentacle["position"]["y"] += tentacle["velocity"]["y"] * dt
    
    return tentacle


# =============================================================================
# IDLE FIDGETING
# =============================================================================

def apply_idle_fidget(
    anim_state: Dict[str, Any],
    state: Dict[str, Any],
    config: Dict[str, Any],
    dt: float,
) -> Dict[str, Any]:
    """
    Apply idle fidgeting motion to tentacles.
    
    Each tentacle wiggles based on:
    - Frequency (from config and chaos variable)
    - Amplitude (from config and calmness variable)
    - Phase offset (unique per tentacle)
    """
    anim_state = dict(anim_state)
    
    # Get motion parameters from config
    anim_config = config.get("animation", {}).get("idle_fidget", {})
    base_freq = anim_config.get("frequency", 2.0)
    base_amp = anim_config.get("amplitude", 5.0)
    
    # Modulate with evolution variables
    ev_vars = state.get("evolution_vars", {})
    chaos = ev_vars.get("chaos", 5.0)
    calmness = ev_vars.get("calmness", 5.0)
    
    # More chaos = faster, more erratic
    freq = base_freq * (1.0 + chaos / 10.0)
    
    # Less calmness = bigger movements
    amp = base_amp * (1.0 + (10.0 - calmness) / 5.0)
    
    # Update time
    anim_state["time"] += dt
    time = anim_state["time"]
    
    # Update each tentacle target
    new_tentacles = []
    for tentacle in anim_state["tentacles"]:
        tentacle = dict(tentacle)
        
        # Circular motion with phase offset
        phase = tentacle["angle"] * (math.pi / 180.0) + time * freq
        
        tentacle["target"]["x"] = math.cos(phase) * amp
        tentacle["target"]["y"] = math.sin(phase) * amp
        
        new_tentacles.append(tentacle)
    
    anim_state["tentacles"] = new_tentacles
    
    return anim_state


# =============================================================================
# CURSOR TRACKING
# =============================================================================

def apply_cursor_tracking(
    anim_state: Dict[str, Any],
    cursor_pos: Tuple[int, int],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Make tentacles and eyes track cursor position.
    
    Only applies if cursor is within max_distance of body.
    """
    anim_state = dict(anim_state)
    
    tracking_config = config.get("animation", {}).get("cursor_tracking", {})
    
    if not tracking_config.get("enabled", True):
        return anim_state
    
    max_dist = tracking_config.get("max_distance", 200)
    attraction = tracking_config.get("attraction_strength", 0.1)
    
    # Calculate distance from body to cursor
    body_x = anim_state["body"]["position"]["x"]
    body_y = anim_state["body"]["position"]["y"]
    
    cursor_x, cursor_y = cursor_pos
    
    dx = cursor_x - body_x
    dy = cursor_y - body_y
    distance = math.sqrt(dx * dx + dy * dy)
    
    if distance > max_dist:
        return anim_state  # Too far, ignore
    
    # Store cursor position
    anim_state["cursor_pos"] = {"x": cursor_x, "y": cursor_y}
    
    # Make tentacles lean toward cursor
    new_tentacles = []
    for tentacle in anim_state["tentacles"]:
        tentacle = dict(tentacle)
        
        # Add attraction to target
        tentacle["target"]["x"] += dx * attraction
        tentacle["target"]["y"] += dy * attraction
        
        new_tentacles.append(tentacle)
    
    anim_state["tentacles"] = new_tentacles
    
    # Update eye pupils to look at cursor
    eyes = dict(anim_state["eyes"])
    
    # Left eye
    left_eye = dict(eyes["left"])
    left_dx = cursor_x - left_eye["x"]
    left_dy = cursor_y - left_eye["y"]
    left_dist = math.sqrt(left_dx * left_dx + left_dy * left_dy)
    
    if left_dist > 0:
        left_eye["pupil_offset_x"] = (left_dx / left_dist) * 3.0  # 3 pixel max offset
        left_eye["pupil_offset_y"] = (left_dy / left_dist) * 3.0
    
    # Right eye
    right_eye = dict(eyes["right"])
    right_dx = cursor_x - right_eye["x"]
    right_dy = cursor_y - right_eye["y"]
    right_dist = math.sqrt(right_dx * right_dx + right_dy * right_dy)
    
    if right_dist > 0:
        right_eye["pupil_offset_x"] = (right_dx / right_dist) * 3.0
        right_eye["pupil_offset_y"] = (right_dy / right_dist) * 3.0
    
    eyes["left"] = left_eye
    eyes["right"] = right_eye
    anim_state["eyes"] = eyes
    
    return anim_state


# =============================================================================
# BODY BOBBING
# =============================================================================

def apply_body_bobbing(
    anim_state: Dict[str, Any],
    state: Dict[str, Any],
    dt: float,
) -> Dict[str, Any]:
    """
    Apply gentle bobbing motion to body (breathing effect).
    """
    anim_state = dict(anim_state)
    body = dict(anim_state["body"])
    
    # Get calmness (calmer = slower bob)
    ev_vars = state.get("evolution_vars", {})
    calmness = ev_vars.get("calmness", 5.0)
    
    bob_speed = 1.0 + (10.0 - calmness) / 10.0
    
    body["bob_phase"] += dt * bob_speed
    
    # Vertical bobbing (sine wave)
    bob_amount = math.sin(body["bob_phase"]) * 2.0
    body["position"]["y"] = 64.0 + bob_amount
    
    anim_state["body"] = body
    
    return anim_state


# =============================================================================
# BLINKING
# =============================================================================

def apply_blinking(
    anim_state: Dict[str, Any],
    dt: float,
) -> Dict[str, Any]:
    """
    Apply random blinking animation.
    """
    anim_state = dict(anim_state)
    eyes = dict(anim_state["eyes"])
    
    eyes["blink_timer"] -= dt
    
    if eyes["blink_timer"] <= 0:
        # Start new blink
        eyes["blink"] = 1.0
        eyes["blink_timer"] = random.uniform(2.0, 5.0)  # Next blink in 2-5 seconds
    else:
        # Decay blink
        eyes["blink"] = max(0.0, eyes["blink"] - dt * 10.0)  # Blink lasts ~0.1s
    
    anim_state["eyes"] = eyes
    
    return anim_state


# =============================================================================
# EVENT REACTIONS
# =============================================================================

def apply_event_reaction(
    anim_state: Dict[str, Any],
    event_type: str,
    state: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Apply animation reaction to an event (jump, wiggle, etc.).
    
    Event types:
    - "studied_python": Gentle wiggle
    - "finished_class": Big celebration
    - "mutation": Dramatic shake
    - "evolution_trigger": Radial expansion
    """
    anim_state = dict(anim_state)
    
    if event_type in ["studied_python", "studied_security_plus"]:
        # Gentle wiggle
        for i, tentacle in enumerate(anim_state["tentacles"]):
            tentacle = dict(tentacle)
            tentacle["velocity"]["x"] += random.uniform(-10, 10)
            tentacle["velocity"]["y"] += random.uniform(-10, 10)
            anim_state["tentacles"][i] = tentacle
    
    elif event_type == "finished_class":
        # Big celebration - all tentacles up
        for i, tentacle in enumerate(anim_state["tentacles"]):
            tentacle = dict(tentacle)
            tentacle["target"]["y"] -= 30
            tentacle["velocity"]["y"] -= 50
            anim_state["tentacles"][i] = tentacle
    
    elif event_type == "mutation":
        # Dramatic shake
        body = dict(anim_state["body"])
        body["rotation"] += random.uniform(-15, 15)
        anim_state["body"] = body
        
        for i, tentacle in enumerate(anim_state["tentacles"]):
            tentacle = dict(tentacle)
            tentacle["velocity"]["x"] += random.uniform(-30, 30)
            tentacle["velocity"]["y"] += random.uniform(-30, 30)
            anim_state["tentacles"][i] = tentacle
    
    elif event_type == "evolution_trigger":
        # Radial expansion
        for i, tentacle in enumerate(anim_state["tentacles"]):
            tentacle = dict(tentacle)
            angle = tentacle["angle"] * (math.pi / 180.0)
            tentacle["velocity"]["x"] += math.cos(angle) * 50
            tentacle["velocity"]["y"] += math.sin(angle) * 50
            anim_state["tentacles"][i] = tentacle
    
    return anim_state


# =============================================================================
# MAIN UPDATE FUNCTION
# =============================================================================

def update_animation(
    anim_state: Dict[str, Any],
    state: Dict[str, Any],
    config: Dict[str, Any],
    dt: float,
    cursor_pos: Optional[Tuple[int, int]] = None,
    event: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Main animation update function - call every frame.
    
    Args:
        anim_state: Current animation state
        state: Current OctoBuddy state (for evolution vars, traits)
        config: Configuration
        dt: Delta time since last frame (seconds)
        cursor_pos: Optional (x, y) cursor position
        event: Optional event that just occurred
    
    Returns:
        Updated animation state
    """
    # Apply event reactions first
    if event:
        anim_state = apply_event_reaction(anim_state, event, state)
    
    # Apply idle fidgeting (sets tentacle targets)
    anim_state = apply_idle_fidget(anim_state, state, config, dt)
    
    # Apply cursor tracking (modifies tentacle targets and eyes)
    if cursor_pos:
        anim_state = apply_cursor_tracking(anim_state, cursor_pos, config)
    
    # Update tentacle physics (moves toward targets)
    physics_config = config.get("animation", {}).get("tentacle_physics", {})
    spring_k = physics_config.get("spring_constant", 0.5)
    damping = physics_config.get("damping", 0.8)
    mass = physics_config.get("mass", 1.0)
    
    new_tentacles = []
    for tentacle in anim_state["tentacles"]:
        updated = update_tentacle_physics(tentacle, dt, spring_k, damping, mass)
        new_tentacles.append(updated)
    
    anim_state = dict(anim_state)
    anim_state["tentacles"] = new_tentacles
    
    # Apply body bobbing
    anim_state = apply_body_bobbing(anim_state, state, dt)
    
    # Apply blinking
    anim_state = apply_blinking(anim_state, dt)
    
    return anim_state


# =============================================================================
# HELPERS FOR RENDERING
# =============================================================================

def get_tentacle_tip_position(tentacle: Dict[str, Any], body_pos: Dict[str, float]) -> Tuple[float, float]:
    """
    Calculate absolute tip position of a tentacle.
    
    Returns (x, y) in pixel coordinates.
    """
    x = body_pos["x"] + tentacle["position"]["x"]
    y = body_pos["y"] + tentacle["position"]["y"]
    return (x, y)


def get_eye_state(anim_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get current eye rendering state.
    
    Returns dict with left/right eye positions and blink amount.
    """
    return anim_state["eyes"]


def get_body_transform(anim_state: Dict[str, Any]) -> Dict[str, float]:
    """
    Get body transformation for rendering.
    
    Returns dict with position and rotation.
    """
    return anim_state["body"]
