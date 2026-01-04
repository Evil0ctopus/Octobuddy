"""
Procedural HD Pixel Art Engine for OctoBuddy.

Generates 128x128 HD pixel art sprites procedurally, allowing OctoBuddy
to evolve its appearance over time through mutations.

Components:
- Palette generation with color harmony
- Body shape generation using Perlin noise
- Tentacle rendering with Bézier curves
- Eye generation with neon glow
- Shading systems (flat, soft, dithered, specular)
- Pattern/marking generation (stripes, spots, runes, veins)
- Aura/glow effects (mood-based)
"""

import math
import random
from dataclasses import dataclass
from typing import List, Tuple
from PIL import Image, ImageDraw


@dataclass
class ColorPalette:
    """Color palette for OctoBuddy's appearance."""
    primary: Tuple[int, int, int]      # Main body color
    secondary: Tuple[int, int, int]    # Accent color
    highlight: Tuple[int, int, int]    # Highlights/glow
    shadow: Tuple[int, int, int]       # Shadow color
    eye: Tuple[int, int, int]          # Eye color
    glow: Tuple[int, int, int]         # Aura/glow color
    
    @classmethod
    def generate_harmonious(cls, hue_base=None, saturation=0.7, brightness=0.8):
        """Generate a harmonious color palette."""
        if hue_base is None:
            hue_base = random.random()
        
        def hsv_to_rgb(h, s, v):
            """Convert HSV to RGB."""
            c = v * s
            x = c * (1 - abs((h * 6) % 2 - 1))
            m = v - c
            
            if h < 1/6:
                r, g, b = c, x, 0
            elif h < 2/6:
                r, g, b = x, c, 0
            elif h < 3/6:
                r, g, b = 0, c, x
            elif h < 4/6:
                r, g, b = 0, x, c
            elif h < 5/6:
                r, g, b = x, 0, c
            else:
                r, g, b = c, 0, x
            
            return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))
        
        # Generate harmonious colors using color theory
        primary = hsv_to_rgb(hue_base, saturation, brightness)
        secondary = hsv_to_rgb((hue_base + 0.33) % 1.0, saturation * 0.8, brightness * 0.9)
        highlight = hsv_to_rgb(hue_base, saturation * 0.5, min(1.0, brightness * 1.2))
        shadow = hsv_to_rgb(hue_base, saturation * 1.1, brightness * 0.5)
        eye = hsv_to_rgb((hue_base + 0.5) % 1.0, saturation * 1.2, brightness * 1.1)
        glow = hsv_to_rgb(hue_base, saturation * 0.9, min(1.0, brightness * 1.3))
        
        return cls(primary, secondary, highlight, shadow, eye, glow)
    
    def mutate(self, mutation_strength=0.1):
        """Mutate the palette slightly."""
        def mutate_color(color):
            r, g, b = color
            r = max(0, min(255, int(r + random.gauss(0, 20 * mutation_strength))))
            g = max(0, min(255, int(g + random.gauss(0, 20 * mutation_strength))))
            b = max(0, min(255, int(b + random.gauss(0, 20 * mutation_strength))))
            return (r, g, b)
        
        return ColorPalette(
            mutate_color(self.primary),
            mutate_color(self.secondary),
            mutate_color(self.highlight),
            mutate_color(self.shadow),
            mutate_color(self.eye),
            mutate_color(self.glow)
        )


class PerlinNoise:
    """Simple Perlin noise generator for organic shapes."""
    
    def __init__(self, seed=None):
        """Initialize with optional seed."""
        if seed is not None:
            random.seed(seed)
        
        # Create permutation table
        self.perm = list(range(256))
        random.shuffle(self.perm)
        self.perm *= 2
    
    def _fade(self, t):
        """Fade function for smooth interpolation."""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def _lerp(self, t, a, b):
        """Linear interpolation."""
        return a + t * (b - a)
    
    def _grad(self, hash_val, x, y):
        """Calculate gradient."""
        h = hash_val & 3
        u = x if h < 2 else y
        v = y if h < 2 else x
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)
    
    def noise(self, x, y):
        """Generate Perlin noise value at (x, y)."""
        # Find unit grid cell
        xi = int(x) & 255
        yi = int(y) & 255
        
        # Find relative x, y in cell
        xf = x - int(x)
        yf = y - int(y)
        
        # Compute fade curves
        u = self._fade(xf)
        v = self._fade(yf)
        
        # Hash coordinates of 4 corners
        aa = self.perm[self.perm[xi] + yi]
        ab = self.perm[self.perm[xi] + yi + 1]
        ba = self.perm[self.perm[xi + 1] + yi]
        bb = self.perm[self.perm[xi + 1] + yi + 1]
        
        # Blend results from 4 corners
        x1 = self._lerp(u, self._grad(aa, xf, yf), self._grad(ba, xf - 1, yf))
        x2 = self._lerp(u, self._grad(ab, xf, yf - 1), self._grad(bb, xf - 1, yf - 1))
        
        return self._lerp(v, x1, x2)


class ArtEngine:
    """
    Main procedural art engine for generating OctoBuddy's appearance.
    
    Generates 128x128 HD pixel art with full customization and mutation support.
    """
    
    def __init__(self, seed=None, palette=None):
        """
        Initialize art engine.
        
        Args:
            seed: Random seed for reproducible generation
            palette: ColorPalette instance (generates new if None)
        """
        self.seed = seed if seed is not None else random.randint(0, 999999)
        random.seed(self.seed)
        
        self.palette = palette if palette else ColorPalette.generate_harmonious()
        self.noise = PerlinNoise(self.seed)
        
        # Appearance parameters (can mutate)
        self.body_size = 40  # Radius in pixels
        self.body_roundness = 0.9  # 0-1, how round vs. squashed
        self.tentacle_count = 6
        self.tentacle_length = 35
        self.tentacle_thickness = 6
        self.tentacle_curvature = 0.5  # How much tentacles curve
        self.eye_size = 12
        self.pupil_size = 6
        self.glow_intensity = 0.5
        self.marking_style = "none"  # none, stripes, spots, runes, veins
        self.shading_style = "soft"  # flat, soft, dithered, specular
    
    def generate_sprite(self, size=128):
        """
        Generate complete OctoBuddy sprite.
        
        Args:
            size: Image size (square)
        
        Returns:
            PIL Image object
        """
        # Create transparent image
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x, center_y = size // 2, size // 2
        
        # Draw glow/aura (behind everything)
        if self.glow_intensity > 0:
            self._draw_glow(img, center_x, center_y)
        
        # Draw tentacles (behind body)
        self._draw_tentacles(draw, center_x, center_y, size)
        
        # Draw body
        self._draw_body(img, center_x, center_y)
        
        # Draw markings/patterns on body
        if self.marking_style != "none":
            self._draw_markings(img, center_x, center_y)
        
        # Draw eyes
        self._draw_eyes(draw, center_x, center_y)
        
        return img
    
    def _draw_glow(self, img, cx, cy):
        """Draw glow/aura effect around OctoBuddy."""
        glow_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(glow_layer)
        
        # Multiple layers of glow with decreasing intensity
        glow_radius = self.body_size * 1.5
        layers = 5
        
        for i in range(layers):
            alpha = int(30 * self.glow_intensity * (1 - i / layers))
            radius = glow_radius * (1 + i * 0.3)
            color = (*self.palette.glow, alpha)
            
            bbox = [
                cx - radius, cy - radius,
                cx + radius, cy + radius
            ]
            draw.ellipse(bbox, fill=color)
        
        # Composite glow onto image
        img.alpha_composite(glow_layer)
    
    def _draw_tentacles(self, draw, cx, cy, size):
        """Draw tentacles using Bézier-like curves."""
        for i in range(self.tentacle_count):
            angle = (i / self.tentacle_count) * math.pi * 2
            
            # Start point (at body edge)
            start_x = cx + math.cos(angle) * self.body_size * 0.8
            start_y = cy + math.sin(angle) * self.body_size * 0.8
            
            # End point
            end_x = cx + math.cos(angle) * (self.body_size + self.tentacle_length)
            end_y = cy + math.sin(angle) * (self.body_size + self.tentacle_length)
            
            # Control point for curve
            curve_offset = self.tentacle_curvature * 20
            ctrl_x = (start_x + end_x) / 2 + math.cos(angle + math.pi/2) * curve_offset
            ctrl_y = (start_y + end_y) / 2 + math.sin(angle + math.pi/2) * curve_offset
            
            # Draw quadratic Bézier curve as series of line segments
            segments = 10
            prev_x, prev_y = start_x, start_y
            
            for j in range(1, segments + 1):
                t = j / segments
                
                # Quadratic Bézier formula
                x = (1-t)**2 * start_x + 2*(1-t)*t * ctrl_x + t**2 * end_x
                y = (1-t)**2 * start_y + 2*(1-t)*t * ctrl_y + t**2 * end_y
                
                # Taper thickness toward tip
                thickness = self.tentacle_thickness * (1 - t * 0.5)
                
                # Draw segment
                draw.line([(prev_x, prev_y), (x, y)], 
                         fill=self.palette.primary, width=int(thickness))
                
                prev_x, prev_y = x, y
    
    def _draw_body(self, img, cx, cy):
        """Draw main body with shading."""
        # Create body layer
        body_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(body_layer)
        
        # Draw base body shape
        bbox = [
            cx - self.body_size,
            cy - self.body_size * self.body_roundness,
            cx + self.body_size,
            cy + self.body_size * self.body_roundness
        ]
        draw.ellipse(bbox, fill=self.palette.primary)
        
        # Apply shading
        if self.shading_style == "soft":
            self._apply_soft_shading(body_layer, cx, cy)
        elif self.shading_style == "dithered":
            self._apply_dithered_shading(body_layer, cx, cy)
        elif self.shading_style == "specular":
            self._apply_specular_shading(body_layer, cx, cy)
        
        img.alpha_composite(body_layer)
    
    def _apply_soft_shading(self, layer, cx, cy):
        """Apply soft gradient shading."""
        draw = ImageDraw.Draw(layer, 'RGBA')
        
        # Add highlight (top-left)
        highlight_offset = self.body_size * 0.3
        highlight_size = self.body_size * 0.6
        
        for i in range(3):
            alpha = int(50 * (1 - i / 3))
            radius = highlight_size * (1 + i * 0.2)
            color = (*self.palette.highlight, alpha)
            
            bbox = [
                cx - highlight_offset - radius,
                cy - highlight_offset - radius,
                cx - highlight_offset + radius,
                cy - highlight_offset + radius
            ]
            draw.ellipse(bbox, fill=color)
        
        # Add shadow (bottom-right)
        shadow_offset = self.body_size * 0.4
        shadow_size = self.body_size * 0.8
        
        for i in range(3):
            alpha = int(40 * (1 - i / 3))
            radius = shadow_size * (1 + i * 0.2)
            color = (*self.palette.shadow, alpha)
            
            bbox = [
                cx + shadow_offset - radius,
                cy + shadow_offset - radius,
                cx + shadow_offset + radius,
                cy + shadow_offset + radius
            ]
            draw.ellipse(bbox, fill=color)
    
    def _apply_dithered_shading(self, layer, cx, cy):
        """Apply dithered shading pattern."""
        pixels = layer.load()
        
        for y in range(layer.size[1]):
            for x in range(layer.size[0]):
                dx = x - cx
                dy = y - cy
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < self.body_size:
                    # Dither pattern based on distance
                    dither = ((x + y) % 2 == 0)
                    if dither and dist > self.body_size * 0.7:
                        # Darken with dither
                        if pixels[x, y][3] > 0:
                            r, g, b, a = pixels[x, y]
                            pixels[x, y] = (
                                max(0, r - 30),
                                max(0, g - 30),
                                max(0, b - 30),
                                a
                            )
    
    def _apply_specular_shading(self, layer, cx, cy):
        """Apply specular highlight."""
        draw = ImageDraw.Draw(layer, 'RGBA')
        
        # Bright specular highlight
        spec_x = cx - self.body_size * 0.25
        spec_y = cy - self.body_size * 0.25
        spec_size = self.body_size * 0.3
        
        draw.ellipse([
            spec_x - spec_size, spec_y - spec_size,
            spec_x + spec_size, spec_y + spec_size
        ], fill=(*self.palette.highlight, 180))
    
    def _draw_markings(self, img, cx, cy):
        """Draw patterns/markings on body."""
        marking_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(marking_layer)
        
        if self.marking_style == "stripes":
            # Horizontal stripes
            for i in range(3):
                y = cy + (i - 1) * self.body_size * 0.5
                draw.line([
                    (cx - self.body_size * 0.8, y),
                    (cx + self.body_size * 0.8, y)
                ], fill=(*self.palette.secondary, 100), width=3)
        
        elif self.marking_style == "spots":
            # Random spots
            for _ in range(5):
                x = cx + random.uniform(-self.body_size * 0.6, self.body_size * 0.6)
                y = cy + random.uniform(-self.body_size * 0.6, self.body_size * 0.6)
                size = random.uniform(3, 8)
                draw.ellipse([x-size, y-size, x+size, y+size],
                           fill=(*self.palette.secondary, 120))
        
        elif self.marking_style == "runes":
            # Simple rune-like marks
            for i in range(3):
                angle = i * math.pi * 2 / 3
                x = cx + math.cos(angle) * self.body_size * 0.6
                y = cy + math.sin(angle) * self.body_size * 0.6
                draw.line([
                    (x, y - 5), (x, y + 5)
                ], fill=(*self.palette.secondary, 150), width=2)
        
        img.alpha_composite(marking_layer)
    
    def _draw_eyes(self, draw, cx, cy):
        """Draw expressive neon eyes."""
        eye_y = cy - self.body_size * 0.3
        eye_spacing = self.body_size * 0.4
        
        # Left eye
        self._draw_single_eye(draw, cx - eye_spacing, eye_y)
        
        # Right eye
        self._draw_single_eye(draw, cx + eye_spacing, eye_y)
    
    def _draw_single_eye(self, draw, x, y):
        """Draw a single neon eye."""
        # Eye white/base
        draw.ellipse([
            x - self.eye_size, y - self.eye_size,
            x + self.eye_size, y + self.eye_size
        ], fill=(255, 255, 255, 200))
        
        # Iris (colored)
        iris_size = self.eye_size * 0.8
        draw.ellipse([
            x - iris_size, y - iris_size,
            x + iris_size, y + iris_size
        ], fill=self.palette.eye)
        
        # Pupil
        draw.ellipse([
            x - self.pupil_size, y - self.pupil_size,
            x + self.pupil_size, y + self.pupil_size
        ], fill=(20, 20, 20, 255))
        
        # Neon glow on pupil
        glow_size = self.pupil_size * 1.5
        draw.ellipse([
            x - glow_size, y - glow_size,
            x + glow_size, y + glow_size
        ], fill=(*self.palette.eye, 80))
        
        # Highlight
        highlight_x = x - self.pupil_size * 0.3
        highlight_y = y - self.pupil_size * 0.3
        highlight_size = self.pupil_size * 0.4
        draw.ellipse([
            highlight_x - highlight_size, highlight_y - highlight_size,
            highlight_x + highlight_size, highlight_y + highlight_size
        ], fill=(255, 255, 255, 200))
    
    def mutate(self, mutation_strength=0.1):
        """
        Mutate OctoBuddy's appearance.
        
        Args:
            mutation_strength: How much to mutate (0-1)
        """
        # Mutate palette
        if random.random() < 0.7:
            self.palette = self.palette.mutate(mutation_strength)
        
        # Mutate body parameters
        if random.random() < 0.3:
            self.body_size += random.gauss(0, 3 * mutation_strength)
            self.body_size = max(30, min(50, self.body_size))
        
        if random.random() < 0.3:
            self.body_roundness += random.gauss(0, 0.1 * mutation_strength)
            self.body_roundness = max(0.7, min(1.0, self.body_roundness))
        
        # Mutate tentacles
        if random.random() < 0.2:
            self.tentacle_length += random.gauss(0, 5 * mutation_strength)
            self.tentacle_length = max(25, min(45, self.tentacle_length))
        
        if random.random() < 0.2:
            self.tentacle_thickness += random.gauss(0, 1 * mutation_strength)
            self.tentacle_thickness = max(4, min(10, self.tentacle_thickness))
        
        if random.random() < 0.2:
            self.tentacle_curvature += random.gauss(0, 0.2 * mutation_strength)
            self.tentacle_curvature = max(0, min(1, self.tentacle_curvature))
        
        # Mutate eyes
        if random.random() < 0.3:
            self.eye_size += random.gauss(0, 2 * mutation_strength)
            self.eye_size = max(8, min(16, self.eye_size))
        
        # Mutate effects
        if random.random() < 0.3:
            self.glow_intensity += random.gauss(0, 0.2 * mutation_strength)
            self.glow_intensity = max(0, min(1, self.glow_intensity))
        
        # Occasionally change marking style
        if random.random() < 0.05:
            marking_options = ["none", "stripes", "spots", "runes"]
            self.marking_style = random.choice(marking_options)
        
        # Occasionally change shading style
        if random.random() < 0.05:
            shading_options = ["flat", "soft", "dithered", "specular"]
            self.shading_style = random.choice(shading_options)
