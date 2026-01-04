"""
Pixel Art Renderer: Procedural 128x128 pixel octopus generation

This module implements procedural pixel art generation following OctoBuddy's
architecture patterns:
- Pure rendering functions accepting (state, config)
- Logic/presentation separation (state determines appearance, not vice versa)
- Evolution-aware (mutations, drift, stage, mood affect visuals)

Output: 128x128 RGB pixel arrays that can be displayed in any UI
"""

import math
import random
from typing import Dict, Any, List, Tuple, Optional

# Type alias for clarity
RGB = Tuple[int, int, int]
PixelGrid = List[List[RGB]]


# =============================================================================
# COLOR PALETTES
# =============================================================================

# Base colors for different stages
STAGE_COLORS = {
    "Baby": {
        "primary": (180, 220, 255),    # Light blue
        "secondary": (255, 200, 220),   # Pink
        "accent": (255, 255, 150),      # Pale yellow
    },
    "Learner": {
        "primary": (120, 180, 255),     # Medium blue
        "secondary": (150, 200, 150),   # Green
        "accent": (255, 200, 100),      # Orange
    },
    "Chaotic Gremlin": {
        "primary": (200, 50, 200),      # Magenta
        "secondary": (255, 100, 0),     # Bright orange
        "accent": (0, 255, 255),        # Cyan
    },
    "Analyst": {
        "primary": (100, 100, 200),     # Deep blue
        "secondary": (150, 150, 200),   # Purple
        "accent": (200, 200, 255),      # Light purple
    },
    "Fully Evolved Hybrid": {
        "primary": (150, 100, 255),     # Purple
        "secondary": (100, 255, 200),   # Teal
        "accent": (255, 255, 100),      # Gold
    },
}

# Mood-based color modifiers (applied as multipliers)
MOOD_TINTS = {
    "sleepy": (0.7, 0.7, 0.9),          # Dimmed, blue tint
    "curious": (0.9, 1.0, 0.9),         # Slight green
    "hyper": (1.2, 1.1, 0.9),           # Brighter, warm
    "goofy": (1.1, 0.9, 1.1),           # Purple-ish
    "chaotic": (1.3, 0.8, 1.2),         # Intense magenta
    "proud": (1.1, 1.1, 1.0),           # Bright
    "confused": (0.9, 0.9, 1.0),        # Cool tint
    "excited": (1.2, 1.2, 1.1),         # Very bright
}

# Personality drift color influences
DRIFT_COLOR_SHIFTS = {
    "analytical": (0, 0, 30),           # More blue
    "chaotic": (40, -20, 40),           # More magenta
    "studious": (0, 30, 0),             # More green
    "ambitious": (30, 20, 0),           # More gold/orange
}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_blank_canvas(width: int = 128, height: int = 128, bg_color: RGB = (20, 20, 30)) -> PixelGrid:
    """Create a blank pixel grid filled with background color."""
    return [[bg_color for _ in range(width)] for _ in range(height)]


def clamp_color(color: RGB) -> RGB:
    """Clamp RGB values to valid 0-255 range."""
    return tuple(max(0, min(255, int(c))) for c in color)


def apply_tint(base_color: RGB, tint: Tuple[float, float, float]) -> RGB:
    """Apply multiplicative tint to a color."""
    return clamp_color(tuple(base_color[i] * tint[i] for i in range(3)))


def blend_colors(color1: RGB, color2: RGB, ratio: float) -> RGB:
    """Blend two colors with given ratio (0.0 = color1, 1.0 = color2)."""
    ratio = max(0.0, min(1.0, ratio))
    return clamp_color(tuple(
        int(color1[i] * (1 - ratio) + color2[i] * ratio)
        for i in range(3)
    ))


def distance(x1: int, y1: int, x2: int, y2: int) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def set_pixel(grid: PixelGrid, x: int, y: int, color: RGB) -> None:
    """Set a pixel in the grid (with bounds checking)."""
    if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
        grid[y][x] = color


def draw_circle(grid: PixelGrid, cx: int, cy: int, radius: int, color: RGB, filled: bool = True) -> None:
    """Draw a circle on the pixel grid."""
    for y in range(max(0, cy - radius), min(len(grid), cy + radius + 1)):
        for x in range(max(0, cx - radius), min(len(grid[0]), cx + radius + 1)):
            dist = distance(x, y, cx, cy)
            if filled and dist <= radius:
                set_pixel(grid, x, y, color)
            elif not filled and abs(dist - radius) < 1:
                set_pixel(grid, x, y, color)


def draw_ellipse(grid: PixelGrid, cx: int, cy: int, rx: int, ry: int, color: RGB) -> None:
    """Draw a filled ellipse on the pixel grid."""
    for y in range(max(0, cy - ry), min(len(grid), cy + ry + 1)):
        for x in range(max(0, cx - rx), min(len(grid[0]), cx + rx + 1)):
            # Ellipse equation: (x-cx)^2/rx^2 + (y-cy)^2/ry^2 <= 1
            if rx > 0 and ry > 0:
                norm_dist = ((x - cx) ** 2) / (rx ** 2) + ((y - cy) ** 2) / (ry ** 2)
                if norm_dist <= 1:
                    set_pixel(grid, x, y, color)


def draw_tentacle(grid: PixelGrid, start_x: int, start_y: int, angle: float, 
                  length: int, color: RGB, thickness: int = 3) -> None:
    """Draw a curved tentacle using multiple segments."""
    segments = 12
    curve_amount = 0.3  # How much the tentacle curves
    
    for i in range(segments):
        t = i / segments
        # Bezier-like curve
        current_angle = angle + math.sin(t * math.pi) * curve_amount
        
        x = int(start_x + math.cos(current_angle) * length * t)
        y = int(start_y + math.sin(current_angle) * length * t)
        
        # Draw thick line segment
        draw_circle(grid, x, y, thickness, color)


# =============================================================================
# EVOLUTION-AWARE COLOR SYSTEM
# =============================================================================

def get_evolution_palette(state: Dict[str, Any]) -> Dict[str, RGB]:
    """
    Calculate color palette based on stage, mood, and personality drift.
    
    Returns dict with 'primary', 'secondary', 'accent' colors.
    """
    from .brain import get_stage, get_mood
    from .evolution_engine import get_dominant_drift
    
    # Get base colors from stage
    stage = get_stage(state, state.get("config", {}))
    mood = get_mood(state, state.get("config", {}))
    
    base_palette = STAGE_COLORS.get(stage, STAGE_COLORS["Baby"]).copy()
    
    # Apply mood tint
    mood_tint = MOOD_TINTS.get(mood, (1.0, 1.0, 1.0))
    for key in base_palette:
        base_palette[key] = apply_tint(base_palette[key], mood_tint)
    
    # Apply personality drift shifts
    dominant_drift = get_dominant_drift(state)
    if dominant_drift:
        shift = DRIFT_COLOR_SHIFTS.get(dominant_drift, (0, 0, 0))
        for key in base_palette:
            shifted = tuple(base_palette[key][i] + shift[i] for i in range(3))
            base_palette[key] = clamp_color(shifted)
    
    return base_palette


def get_mutation_visual_effects(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get visual effect flags based on active mutations.
    
    Returns dict with effect flags and parameters.
    """
    mutations = state.get("mutations", [])
    
    effects = {
        "glow": False,
        "sparkles": False,
        "spikes": False,
        "extra_eyes": 0,
        "aura": False,
        "geometric_patterns": False,
        "color_shift": 0,
    }
    
    for mutation in mutations:
        if mutation == "speed_learner":
            effects["sparkles"] = True
        elif mutation == "night_owl":
            effects["glow"] = True
        elif mutation == "chaos_incarnate":
            effects["spikes"] = True
            effects["color_shift"] = 20
        elif mutation == "analytical_mind":
            effects["geometric_patterns"] = True
            effects["extra_eyes"] = 2
        elif mutation == "unstoppable":
            effects["aura"] = True
        elif mutation == "personality_fracture":
            effects["extra_eyes"] = 4
            effects["color_shift"] = 40
        elif mutation == "transcendent":
            effects["glow"] = True
            effects["aura"] = True
            effects["sparkles"] = True
    
    return effects


# =============================================================================
# PROCEDURAL BODY GENERATION
# =============================================================================

def draw_octopus_body(grid: PixelGrid, state: Dict[str, Any], palette: Dict[str, RGB]) -> None:
    """Draw the main octopus body (head/mantle)."""
    cx, cy = 64, 50  # Center of head
    
    # Main head (ellipse)
    head_width = 35
    head_height = 30
    
    draw_ellipse(grid, cx, cy, head_width, head_height, palette["primary"])
    
    # Shading/highlight
    highlight = blend_colors(palette["primary"], (255, 255, 255), 0.3)
    draw_ellipse(grid, cx - 8, cy - 8, 15, 12, highlight)


def draw_eyes(grid: PixelGrid, state: Dict[str, Any], palette: Dict[str, RGB], 
              effects: Dict[str, Any]) -> None:
    """Draw eyes (with mutation-based extra eyes)."""
    # Base eyes
    eye_positions = [
        (50, 45),  # Left eye
        (78, 45),  # Right eye
    ]
    
    # Add extra eyes from mutations
    if effects["extra_eyes"] >= 2:
        eye_positions.extend([
            (40, 50),
            (88, 50),
        ])
    if effects["extra_eyes"] >= 4:
        eye_positions.extend([
            (55, 38),
            (73, 38),
        ])
    
    for ex, ey in eye_positions:
        # Eye white
        draw_circle(grid, ex, ey, 6, (240, 240, 250))
        # Pupil
        draw_circle(grid, ex, ey, 3, (30, 30, 50))
        # Highlight
        draw_circle(grid, ex - 1, ey - 1, 1, (255, 255, 255))


def draw_tentacles(grid: PixelGrid, state: Dict[str, Any], palette: Dict[str, RGB]) -> None:
    """Draw 8 octopus tentacles."""
    cx, cy = 64, 70  # Tentacle origin point
    num_tentacles = 8
    tentacle_length = 45
    
    for i in range(num_tentacles):
        angle = (i / num_tentacles) * 2 * math.pi - math.pi / 2
        # Offset angle slightly for natural look
        angle += (i % 2) * 0.2
        
        draw_tentacle(grid, cx, cy, angle, tentacle_length, palette["secondary"], thickness=4)


def draw_mouth(grid: PixelGrid, state: Dict[str, Any], palette: Dict[str, RGB]) -> None:
    """Draw mouth (varies by mood)."""
    from .brain import get_mood
    
    mood = get_mood(state, state.get("config", {}))
    mx, my = 64, 58  # Mouth position
    
    mouth_color = blend_colors(palette["primary"], (0, 0, 0), 0.5)
    
    # Different mouth shapes based on mood
    if mood in ["hyper", "excited"]:
        # Big smile
        for x in range(mx - 10, mx + 11):
            y = my + int(math.sin((x - mx) / 10 * math.pi) * 3)
            draw_circle(grid, x, y, 1, mouth_color)
    elif mood in ["sleepy", "confused"]:
        # Small neutral mouth
        for x in range(mx - 5, mx + 6):
            set_pixel(grid, x, my, mouth_color)
    elif mood in ["chaotic", "goofy"]:
        # Crooked grin
        for x in range(mx - 8, mx + 9):
            y = my + int((x - mx) / 4)
            draw_circle(grid, x, y, 1, mouth_color)
    else:
        # Normal smile
        for x in range(mx - 8, mx + 9):
            y = my + int(math.sin((x - mx) / 8 * math.pi) * 2)
            draw_circle(grid, x, y, 1, mouth_color)


# =============================================================================
# MUTATION VISUAL EFFECTS
# =============================================================================

def draw_glow_effect(grid: PixelGrid, palette: Dict[str, RGB]) -> None:
    """Add glowing aura around the octopus (night_owl, transcendent)."""
    cx, cy = 64, 50
    glow_color = blend_colors(palette["accent"], (255, 255, 255), 0.5)
    
    # Multiple glow rings with decreasing opacity
    for radius in range(50, 65, 3):
        for y in range(max(0, cy - radius), min(128, cy + radius + 1)):
            for x in range(max(0, cx - radius), min(128, cx + radius + 1)):
                dist = distance(x, y, cx, cy)
                if abs(dist - radius) < 2:
                    # Blend with existing pixel
                    existing = grid[y][x]
                    blended = blend_colors(existing, glow_color, 0.3)
                    set_pixel(grid, x, y, blended)


def draw_sparkles(grid: PixelGrid, state: Dict[str, Any]) -> None:
    """Add sparkle effects (speed_learner, transcendent)."""
    # Use XP as seed for consistent sparkle positions
    xp = state.get("xp", 0)
    random.seed(xp % 1000)
    
    sparkle_color = (255, 255, 200)
    num_sparkles = 15
    
    for _ in range(num_sparkles):
        x = random.randint(10, 118)
        y = random.randint(10, 118)
        
        # Draw small plus-shaped sparkle
        set_pixel(grid, x, y, sparkle_color)
        set_pixel(grid, x - 1, y, sparkle_color)
        set_pixel(grid, x + 1, y, sparkle_color)
        set_pixel(grid, x, y - 1, sparkle_color)
        set_pixel(grid, x, y + 1, sparkle_color)
    
    random.seed()  # Reset seed


def draw_spikes(grid: PixelGrid, palette: Dict[str, RGB]) -> None:
    """Add chaotic spikes around body (chaos_incarnate)."""
    cx, cy = 64, 50
    num_spikes = 12
    spike_color = blend_colors(palette["accent"], (255, 0, 0), 0.5)
    
    for i in range(num_spikes):
        angle = (i / num_spikes) * 2 * math.pi
        
        # Spike starts at body edge
        start_x = int(cx + math.cos(angle) * 35)
        start_y = int(cy + math.sin(angle) * 30)
        
        # Spike extends outward
        end_x = int(cx + math.cos(angle) * 50)
        end_y = int(cy + math.sin(angle) * 45)
        
        # Draw line for spike
        steps = 10
        for step in range(steps):
            t = step / steps
            sx = int(start_x + (end_x - start_x) * t)
            sy = int(start_y + (end_y - start_y) * t)
            thickness = int(3 * (1 - t))  # Taper
            draw_circle(grid, sx, sy, thickness, spike_color)


def draw_aura(grid: PixelGrid, palette: Dict[str, RGB]) -> None:
    """Add energy aura (unstoppable, transcendent)."""
    cx, cy = 64, 50
    aura_color = palette["accent"]
    
    # Radiating wave pattern
    for wave in range(3):
        radius = 55 + wave * 8
        for angle_deg in range(0, 360, 10):
            angle = math.radians(angle_deg)
            x = int(cx + math.cos(angle) * radius)
            y = int(cy + math.sin(angle) * radius * 0.8)
            
            draw_circle(grid, x, y, 2, blend_colors(aura_color, (255, 255, 255), 0.4))


def draw_geometric_patterns(grid: PixelGrid, palette: Dict[str, RGB]) -> None:
    """Add analytical geometric overlays (analytical_mind)."""
    pattern_color = blend_colors(palette["accent"], (255, 255, 255), 0.6)
    
    # Grid pattern
    for x in range(20, 108, 10):
        for y in range(20, 108):
            if y % 10 < 2:
                set_pixel(grid, x, y, blend_colors(grid[y][x], pattern_color, 0.2))
    
    # Diagonal lines
    for i in range(-128, 128, 20):
        for offset in range(128):
            x = offset
            y = offset + i
            if 0 <= y < 128:
                set_pixel(grid, x, y, blend_colors(grid[y][x], pattern_color, 0.1))


# =============================================================================
# MAIN RENDER FUNCTION
# =============================================================================

def render_pixel_art(
    state: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
    stage: Optional[str] = None,
    mood: Optional[str] = None
) -> PixelGrid:
    """
    Main rendering function: Generate 128x128 pixel art from state.

    This version is backward-compatible with both:
    - render_pixel_art(state)
    - render_pixel_art(state, config)
    - render_pixel_art(state, config, stage, mood)

    The extra stage/mood arguments are accepted for compatibility with
    the desktop companion, but the renderer still derives stage/mood
    from state unless explicitly provided.
    """

    # Ensure config is available
    if config is None:
        config = state.get("config", {})
    if "config" not in state:
        state = {**state, "config": config}

    # Override stage/mood only if explicitly passed
    # (Desktop companion passes them, terminal version does not)
    if stage is not None:
        state["forced_stage"] = stage
    if mood is not None:
        state["forced_mood"] = mood

    # Create canvas
    grid = create_blank_canvas()

    # Get evolution-aware palette
    palette = get_evolution_palette(state)

    # Get mutation effects
    effects = get_mutation_visual_effects(state)

    # Draw base octopus (order matters for layering)
    draw_tentacles(grid, state, palette)
    draw_octopus_body(grid, state, palette)
    draw_eyes(grid, state, palette, effects)
    draw_mouth(grid, state, palette)

    # Apply mutation effects
    if effects["aura"]:
        draw_aura(grid, palette)
    if effects["glow"]:
        draw_glow_effect(grid, palette)
    if effects["spikes"]:
        draw_spikes(grid, palette)
    if effects["geometric_patterns"]:
        draw_geometric_patterns(grid, palette)
    if effects["sparkles"]:
        draw_sparkles(grid, state)

    # Convert to NumPy array so the desktop companion can read .shape
    import numpy as np
    return np.array(grid, dtype=np.uint8)


    return grid


def save_pixel_art_ppm(grid: PixelGrid, filename: str) -> None:
    """
    Save pixel grid as PPM image file (simple format, no dependencies).
    
    Args:
        grid: Pixel grid to save
        filename: Output filename (should end in .ppm)
    """
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0
    
    with open(filename, 'w') as f:
        # PPM header
        f.write(f"P3\n")
        f.write(f"{width} {height}\n")
        f.write(f"255\n")
        
        # Pixel data
        for row in grid:
            for pixel in row:
                f.write(f"{pixel[0]} {pixel[1]} {pixel[2]} ")
            f.write("\n")


def pixel_art_to_ascii(grid: PixelGrid, width: int = 64) -> str:
    """
    Convert pixel art to ASCII representation for terminal display.
    
    Args:
        grid: Pixel grid to convert
        width: Target ASCII width (height scaled proportionally)
    
    Returns:
        Multi-line string with ASCII art
    """
    height = len(grid)
    original_width = len(grid[0]) if height > 0 else 0
    
    # Calculate sampling rate
    x_step = original_width / width
    y_step = height / (width // 2)  # Account for character aspect ratio
    
    # ASCII gradient (dark to light)
    chars = " .:-=+*#%@"
    
    lines = []
    for y in range(int(height / y_step)):
        line = ""
        for x in range(width):
            # Sample pixel
            px = int(x * x_step)
            py = int(y * y_step)
            
            if py < height and px < original_width:
                pixel = grid[py][px]
                # Convert to grayscale
                gray = (pixel[0] + pixel[1] + pixel[2]) / 3
                # Map to ASCII char
                char_idx = int(gray / 255 * (len(chars) - 1))
                line += chars[char_idx]
            else:
                line += " "
        lines.append(line)
    
    return "\n".join(lines)
