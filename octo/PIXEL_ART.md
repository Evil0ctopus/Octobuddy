# Pixel Art Renderer Documentation

## Overview

The pixel art renderer generates procedural 128x128 pixel images of OctoBuddy that evolve based on state. It follows OctoBuddy's architectural principles:

- **Pure rendering functions** - Same state always produces same output (deterministic)
- **Logic/presentation separation** - State determines appearance, rendering is just visualization
- **Evolution integration** - Mutations, drift, stage, and mood all affect visuals

## Architecture

### Core Principle: Rendering is Presentation Only

The renderer **never modifies state**. It reads state and produces pixels:

```python
state (read-only) → render_pixel_art() → pixel grid
```

All evolution logic lives in `evolution_engine.py`. The renderer just visualizes it.

### Pure Function Design

```python
def render_pixel_art(state: Dict[str, Any], config: Optional[Dict[str, Any]]) -> PixelGrid:
    """Pure function: state in, pixels out. No side effects."""
```

- Same state = same pixels (deterministic)
- No randomness except seeded by state values (e.g., `random.seed(xp)`)
- No file I/O except optional save functions
- Fully testable

## Visual Evolution System

### 1. Stage-Based Colors

Each evolution stage has distinct base colors:

| Stage | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| Baby | Light blue | Pink | Pale yellow |
| Learner | Medium blue | Green | Orange |
| Chaotic Gremlin | Magenta | Bright orange | Cyan |
| Analyst | Deep blue | Purple | Light purple |
| Fully Evolved Hybrid | Purple | Teal | Gold |

**Implementation:**
```python
base_palette = STAGE_COLORS.get(stage, STAGE_COLORS["Baby"])
```

### 2. Mood-Based Tints

Moods apply multiplicative color tints:

- **Sleepy**: Dimmed, blue tint (0.7, 0.7, 0.9)
- **Hyper**: Brighter, warm (1.2, 1.1, 0.9)
- **Chaotic**: Intense magenta (1.3, 0.8, 1.2)
- **Excited**: Very bright (1.2, 1.2, 1.1)

Mouth shape also changes with mood (smile, neutral, crooked grin).

### 3. Personality Drift Color Shifts

Dominant drift adds color bias:

- **Analytical**: +30 blue
- **Chaotic**: +40 red, -20 green, +40 blue (magenta shift)
- **Studious**: +30 green
- **Ambitious**: +30 red, +20 green (gold/orange shift)

**Calculation:**
```python
dominant_drift = get_dominant_drift(state)
if dominant_drift:
    shift = DRIFT_COLOR_SHIFTS[dominant_drift]
    palette_color = clamp_color(palette_color + shift)
```

### 4. Mutation Visual Effects

Each mutation adds unique visual elements:

| Mutation | Visual Effect |
|----------|--------------|
| Speed Learner | Sparkles around body |
| Night Owl | Glowing aura |
| Chaos Incarnate | Spiky protrusions + color shift |
| Analytical Mind | Geometric patterns + 2 extra eyes |
| Unstoppable | Energy aura rings |
| Personality Fracture | 4 extra eyes + strong color shift |
| Transcendent | Glow + aura + sparkles (combined) |

**Effect Stacking:**
Multiple mutations stack effects. Example:
- Transcendent + Analytical Mind = glow + aura + sparkles + geometric patterns + 2 extra eyes

## Rendering Pipeline

### Order of Operations

1. **Create blank canvas** (128x128, dark background)
2. **Calculate evolution palette** (stage → mood tint → drift shift)
3. **Get mutation effects** (scan mutations, build effect flags)
4. **Draw base layers** (tentacles, body, eyes, mouth)
5. **Apply mutation effects** (aura, glow, spikes, patterns, sparkles)

Layering matters! Effects are drawn on top of base octopus.

### Drawing Functions

**Primitives:**
- `draw_circle(grid, cx, cy, radius, color, filled)` - Circles
- `draw_ellipse(grid, cx, cy, rx, ry, color)` - Ellipses for body
- `draw_tentacle(grid, x, y, angle, length, color, thickness)` - Curved tentacles

**Components:**
- `draw_octopus_body()` - Main head/mantle
- `draw_eyes()` - Eyes (with mutation-based extras)
- `draw_tentacles()` - 8 tentacles radiating from body
- `draw_mouth()` - Mood-dependent mouth shape

**Effects:**
- `draw_glow_effect()` - Concentric glow rings
- `draw_sparkles()` - Small plus-shaped sparkles
- `draw_spikes()` - Radiating chaotic spikes
- `draw_aura()` - Energy wave pattern
- `draw_geometric_patterns()` - Grid and diagonal overlays

## Output Formats

### 1. Pixel Grid (Native)

```python
grid = render_pixel_art(state, config)
# Returns: List[List[Tuple[int, int, int]]]
# 128x128 RGB tuples
```

### 2. PPM Image File

```python
save_pixel_art_ppm(grid, "octobuddy.ppm")
# Simple image format, no dependencies
# Open with GIMP, IrfanView, ImageMagick, or online converters
```

### 3. ASCII Art

```python
ascii_art = pixel_art_to_ascii(grid, width=60)
print(ascii_art)
# Terminal-friendly ASCII representation
# Uses grayscale mapping: " .:-=+*#%@"
```

## Integration with OctoBuddy

### Option 1: Standalone Rendering

```python
from pixel_art import render_pixel_art
from storage import load_state
from config import CONFIG

state = load_state()
state["config"] = CONFIG
grid = render_pixel_art(state, CONFIG)

# Display grid in your UI...
```

### Option 2: Live Updates in UI

```python
# In a GUI/web UI:
class PixelArtWidget:
    def update(self, state, config):
        self.grid = render_pixel_art(state, config)
        self.repaint()  # Trigger redraw
```

### Option 3: Export on Events

```python
# In core.py after handle_event():
if some_milestone:
    grid = render_pixel_art(self.state, self.config)
    save_pixel_art_ppm(grid, f"evolution_{self.state['level']}.ppm")
```

## Testing

Run the comprehensive test suite:

```bash
cd octo
python test_pixel_art.py
```

Tests cover:
1. Basic render (default state)
2. Evolved render (level 50 + mutations)
3. Transcendent form (max level + legendary)
4. Mood variations
5. Personality drift color shifts
6. PPM export

## Performance

**Complexity:** O(width × height) = O(128 × 128) = ~16k pixels

**Timing:** ~10-50ms per render (pure Python, no optimization)

**Optimization opportunities:**
- Use NumPy arrays instead of nested lists
- Compile hot paths with Numba
- Pre-calculate palettes
- Parallelize effect rendering

For real-time UI updates (60 FPS), consider caching renders and only regenerating when state changes.

## Extension Examples

### Add New Mutation Effect

```python
# 1. Add to get_mutation_visual_effects()
if mutation == "my_new_mutation":
    effects["custom_flag"] = True

# 2. Create draw function
def draw_custom_effect(grid, palette):
    # Your rendering logic...
    pass

# 3. Call in render_pixel_art()
if effects["custom_flag"]:
    draw_custom_effect(grid, palette)
```

### Add New Body Part

```python
def draw_hat(grid, state, palette):
    """Draw a fancy hat on top of octopus."""
    cx, cy = 64, 25  # Above head
    draw_circle(grid, cx, cy, 10, palette["accent"])

# Add to render_pixel_art() after body:
draw_hat(grid, state, palette)
```

### Animate Over Time

```python
# Use XP or timestamp as animation frame
def render_animated_frame(state, config, frame_number):
    # Inject frame into state for seeded randomness
    state_copy = {**state, "animation_frame": frame_number}
    return render_pixel_art(state_copy, config)

# Generate animation frames:
frames = [render_animated_frame(state, config, i) for i in range(60)]
# Save as GIF/video...
```

## Design Rationale

**Why 128x128?**
- Large enough for detail
- Small enough to render quickly
- Power of 2 (GPU-friendly if porting to shaders)

**Why procedural?**
- No asset files to manage
- Infinite variations from state
- Deterministic (reproducible from state)
- Easy to extend with code

**Why pure functions?**
- Testable in isolation
- No hidden state/side effects
- Can be memoized/cached
- Parallel-safe

**Why separate from evolution logic?**
- Follows OctoBuddy architecture (logic/presentation split)
- Can swap renderers (pixel art, 3D, SVG, etc.) without changing evolution
- Renderer can be in different process/thread/language

## Future UI Ideas

1. **Live Desktop Widget** - SDL/Pygame window showing pixel art
2. **Web Dashboard** - Canvas API or Three.js for WebGL rendering
3. **Terminal UI Enhancement** - Replace ASCII with Kitty/iTerm2 inline images
4. **Screensaver Mode** - Full-screen pixel art with idle animations
5. **Export to NFT** - Generate unique pixel art from evolution state
6. **Tilemap Integration** - Export as sprite sheet for game engine
