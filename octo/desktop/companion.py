"""
Desktop Companion UI for OctoBuddy

Windows-compatible always-on-top transparent window using PyQt5.
Renders OctoBuddy pixel art in real-time with animations.

Features:
- Transparent, always-on-top window
- Click-and-drag to move
- Right-click for context menu
- Real-time pixel art rendering
- Animation integration
- Memory, evolution, and ability systems
"""

import sys
import time
import random
import math
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QMenu, QAction, QInputDialog
)
from PyQt5.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPixmap, QImage, QPainter, QCursor, QColor, QPen, QFont, QBrush

# OctoBuddy imports
from octo.config import load_config
from octo.storage import load_state, save_state
from octo.pixel_art import render_pixel_art
from octo.animation import initialize_animation_state, update_animation
from octo.brain import get_mood, get_stage
from octo.evolution_engine import process_evolution_cycle
from octo import memory
from octo.abilities import get_available_abilities


class OctoBuddyWindow(QWidget):
    """
    Main desktop companion window.
    
    Transparent, always-on-top, draggable window that renders OctoBuddy.
    """
    
    def __init__(self):
        super().__init__()
        
        # Load configuration and state
        self.config = load_config()
        self.state = load_state()
        
        # Initialize memory system
        memory.initialize_memory()
        
        # Initialize animation state
        self.anim_state = initialize_animation_state(self.config)
        
        # Speech bubble state
        self.speech_bubble_text = None
        self.speech_bubble_alpha = 0.0
        self.speech_bubble_timer = None
        
        # Reaction animation state
        self.reaction_type = None  # "sparkle", "wiggle", "glow"
        self.reaction_timer = 0.0
        self.reaction_duration = 0.0
        self.wiggle_offset = 0.0
        self.sparkle_particles = []
        
        # Window setup
        self.init_ui()
        
        # Animation timer
        self.last_update = time.time()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        framerate = self.config.get("desktop", {}).get("framerate", 30)
        self.timer.start(1000 // framerate)  # Convert FPS to milliseconds
        
        # Auto-save timer
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.auto_save)
        self.save_timer.start(5000)  # Save every 5 seconds
        
        # For dragging
        self.drag_position = None
    
    def init_ui(self):
        """Initialize UI components."""
        # Window flags for transparency and always-on-top
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool  # Keeps it out of taskbar
        )
        
        # Make background transparent
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set window size from config
        size = self.config.get("desktop", {}).get("window_size", 128)
        self.setFixedSize(size, size)
        
        # Create label to hold pixel art
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.image_label)
        self.setLayout(layout)
        
        # Set initial position from config
        start_pos = self.config.get("desktop", {}).get("start_position", "bottom_right")
        self.set_initial_position(start_pos)
        
        self.setWindowTitle("OctoBuddy")
    
    def set_initial_position(self, position: str):
        """Set window position on screen."""
        screen = QApplication.primaryScreen().geometry()
        
        if position == "bottom_right":
            x = screen.width() - self.width() - 20
            y = screen.height() - self.height() - 60  # Account for taskbar
        elif position == "bottom_left":
            x = 20
            y = screen.height() - self.height() - 60
        elif position == "top_right":
            x = screen.width() - self.width() - 20
            y = 20
        elif position == "top_left":
            x = 20
            y = 20
        else:  # center
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
        
        self.move(x, y)
    
    def update_frame(self):
        """Update animation and render frame."""
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time
        
        # Update reaction animations
        if self.reaction_type:
            self.reaction_timer += dt
            if self.reaction_timer >= self.reaction_duration:
                self.reaction_type = None
                self.reaction_timer = 0.0
                self.sparkle_particles = []
            else:
                self._update_reaction_animation(dt)
        
        # Update speech bubble fade
        if self.speech_bubble_text and self.speech_bubble_alpha > 0:
            # Fade out gradually
            self.speech_bubble_alpha = max(0.0, self.speech_bubble_alpha - dt * 0.5)
            if self.speech_bubble_alpha <= 0:
                self.speech_bubble_text = None
        
        # Get cursor position
        cursor_pos = QCursor.pos()
        cursor_global = (cursor_pos.x(), cursor_pos.y())
        
        # Update animation
        self.anim_state = update_animation(
            self.anim_state,
            self.state,
            self.config,
            dt,
            cursor_pos=cursor_global,
        )
        
        # Get current mood and stage
        mood = get_mood(self.state, self.config)
        stage = get_stage(self.state, self.config)
        
        # Render pixel art
        pixels = render_pixel_art(self.state, self.config, stage, mood)
        
        # Convert to QImage
        height, width, channels = pixels.shape
        bytes_per_line = channels * width
        
        q_image = QImage(
            pixels.data,
            width,
            height,
            bytes_per_line,
            QImage.Format_RGB888
        )
        
        # Convert to QPixmap
        pixmap = QPixmap.fromImage(q_image)
        
        # Apply reaction effects
        if self.reaction_type:
            pixmap = self._apply_reaction_effect(pixmap)
        
        # Draw speech bubble if active
        if self.speech_bubble_text and self.speech_bubble_alpha > 0:
            pixmap = self._draw_speech_bubble(pixmap)
        
        # Display
        self.image_label.setPixmap(pixmap)
    
    def auto_save(self):
        """Periodically save state."""
        save_state(self.state)
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging."""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        self.drag_position = None
    
    def contextMenuEvent(self, event):
        """Show context menu on right-click."""
        menu = QMenu(self)
        
        # Info submenu
        info_menu = menu.addMenu("📊 Info")
        
        stage = get_stage(self.state, self.config)
        mood = get_mood(self.state, self.config)
        
        stage_action = QAction(f"Stage: {stage}", self)
        stage_action.setEnabled(False)
        info_menu.addAction(stage_action)
        
        mood_action = QAction(f"Mood: {mood}", self)
        mood_action.setEnabled(False)
        info_menu.addAction(mood_action)
        
        mutations = self.state.get("mutations", [])
        mutation_action = QAction(f"Mutations: {len(mutations)}", self)
        mutation_action.setEnabled(False)
        info_menu.addAction(mutation_action)
        
        # Abilities submenu
        abilities_menu = menu.addMenu("⚡ Abilities")
        available = get_available_abilities(self.state)
        
        if available:
            for ability_name in available[:5]:  # Show first 5
                ability_action = QAction(ability_name, self)
                ability_action.triggered.connect(
                    lambda checked, name=ability_name: self.use_ability(name)
                )
                abilities_menu.addAction(ability_action)
        else:
            no_abilities = QAction("No abilities available", self)
            no_abilities.setEnabled(False)
            abilities_menu.addAction(no_abilities)
        
        menu.addSeparator()
        
        # Actions
        feed_action = QAction("🍔 Feed", self)
        feed_action.triggered.connect(self.feed_octobuddy)
        menu.addAction(feed_action)
        
        pet_action = QAction("👋 Pet", self)
        pet_action.triggered.connect(self.pet_octobuddy)
        menu.addAction(pet_action)
        
        talk_action = QAction("💬 Talk", self)
        talk_action.triggered.connect(self.talk_to_octobuddy)
        menu.addAction(talk_action)
        
        menu.addSeparator()
        
        quit_action = QAction("🚪 Quit", self)
        quit_action.triggered.connect(self.close)
        menu.addAction(quit_action)
        
        menu.exec_(event.globalPos())
    
    def feed_octobuddy(self):
        """Feed OctoBuddy (increase happiness, trigger evolution)."""
        # Boost evolution variables
        ev_vars = dict(self.state.get("evolution_vars", {}))
        ev_vars["happiness"] = ev_vars.get("happiness", 5.0) + 2.0
        ev_vars["calmness"] = ev_vars.get("calmness", 5.0) + 1.0
        self.state["evolution_vars"] = ev_vars
        
        # Boost personality traits toward happy/excited
        traits = dict(self.state.get("personality_traits", {}))
        traits["humor"] = traits.get("humor", 5.0) + 0.5
        self.state["personality_traits"] = traits
        
        # Trigger evolution cycle
        self.state = process_evolution_cycle(self.state, self.config, "fed")
        
        # Remember event
        memory.remember_event("fed", {}, self.config)
        
        # Animation reaction
        from octo.animation import apply_event_reaction
        self.anim_state = apply_event_reaction(self.anim_state, "fed", self.state)
        
        # Trigger sparkle burst animation
        self._trigger_reaction("sparkle", 1.0)
        
        # Show speech bubble
        responses = [
            "Yum! That hit the spot!",
            "Nom nom nom! 😋",
            "Delicious! More please?",
            "My circuits feel energized!",
            "Food makes everything better!"
        ]
        self._show_speech_bubble(random.choice(responses))
    
    def pet_octobuddy(self):
        """Pet OctoBuddy (social interaction)."""
        # Boost empathy and reduce chaos
        ev_vars = dict(self.state.get("evolution_vars", {}))
        ev_vars["empathy"] = ev_vars.get("empathy", 5.0) + 1.5
        ev_vars["calmness"] = ev_vars.get("calmness", 5.0) + 0.5
        ev_vars["chaos"] = max(0, ev_vars.get("chaos", 5.0) - 0.5)
        self.state["evolution_vars"] = ev_vars
        
        # Boost personality traits toward goofy/proud
        traits = dict(self.state.get("personality_traits", {}))
        traits["humor"] = traits.get("humor", 5.0) + 0.3
        traits["shyness"] = max(0, traits.get("shyness", 5.0) - 0.2)
        self.state["personality_traits"] = traits
        
        # Trigger evolution cycle
        self.state = process_evolution_cycle(self.state, self.config, "petted")
        
        # Remember event
        memory.remember_event("petted", {}, self.config)
        
        # Animation reaction
        from octo.animation import apply_event_reaction
        self.anim_state = apply_event_reaction(self.anim_state, "petted", self.state)
        
        # Trigger wiggle animation
        self._trigger_reaction("wiggle", 0.5)
        
        # Show speech bubble
        responses = [
            "That feels nice! 🥰",
            "Hehe, that tickles!",
            "I appreciate the affection!",
            "You're the best! 💕",
            "This is my happy place~"
        ]
        self._show_speech_bubble(random.choice(responses))
    
    def talk_to_octobuddy(self):
        """Open dialog to talk to OctoBuddy."""
        text, ok = QInputDialog.getText(
            self,
            "Talk to OctoBuddy",
            "What would you like to say?"
        )
        
        if ok and text:
            # Generate response based on personality and mood
            response = self._generate_response(text)
            
            # Boost social evolution variables
            ev_vars = dict(self.state.get("evolution_vars", {}))
            ev_vars["empathy"] = ev_vars.get("empathy", 5.0) + 0.3
            ev_vars["curiosity"] = ev_vars.get("curiosity", 5.0) + 0.2
            self.state["evolution_vars"] = ev_vars
            
            # Remember the interaction
            memory.remember_event("talked", {"message": text}, self.config)
            
            # Trigger glow pulse animation
            self._trigger_reaction("glow", 0.8)
            
            # Show response in speech bubble
            self._show_speech_bubble(response)
    
    def use_ability(self, ability_name: str):
        """Execute an ability."""
        from octo.abilities import execute_ability
        
        new_state, result = execute_ability(ability_name, self.state, self.config)
        
        if result["success"]:
            self.state = new_state
            self._show_speech_bubble(result['message'])
            print(f"✓ {result['message']}")
        else:
            self._show_speech_bubble(f"Can't use {ability_name}...")
            print(f"✗ {result['message']}")
    
    # =========================================================================
    # SPEECH BUBBLE SYSTEM
    # =========================================================================
    
    def _show_speech_bubble(self, text: str):
        """Display text in speech bubble above OctoBuddy."""
        self.speech_bubble_text = text
        self.speech_bubble_alpha = 1.0
    
    def _draw_speech_bubble(self, pixmap: QPixmap) -> QPixmap:
        """Draw speech bubble on pixmap."""
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set opacity
        painter.setOpacity(self.speech_bubble_alpha)
        
        # Prepare text
        font = QFont("Arial", 8, QFont.Bold)
        painter.setFont(font)
        
        # Calculate text size
        fm = painter.fontMetrics()
        text_rect = fm.boundingRect(self.speech_bubble_text)
        
        # Bubble dimensions
        padding = 6
        bubble_width = text_rect.width() + padding * 2
        bubble_height = text_rect.height() + padding * 2
        
        # Position above sprite (centered)
        bubble_x = (pixmap.width() - bubble_width) // 2
        bubble_y = 5  # Top of image
        
        # Draw bubble background (rounded rect)
        painter.setBrush(QColor(255, 255, 255, 230))
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawRoundedRect(bubble_x, bubble_y, bubble_width, bubble_height, 8, 8)
        
        # Draw text
        painter.setPen(QColor(0, 0, 0))
        text_x = bubble_x + padding
        text_y = bubble_y + padding + fm.ascent()
        painter.drawText(text_x, text_y, self.speech_bubble_text)
        
        painter.end()
        return pixmap
    
    # =========================================================================
    # REACTION ANIMATION SYSTEM
    # =========================================================================
    
    def _trigger_reaction(self, reaction_type: str, duration: float):
        """Trigger a reaction animation."""
        self.reaction_type = reaction_type
        self.reaction_timer = 0.0
        self.reaction_duration = duration
        self.wiggle_offset = 0.0
        
        # Initialize sparkle particles for sparkle effect
        if reaction_type == "sparkle":
            self.sparkle_particles = []
            for _ in range(20):
                self.sparkle_particles.append({
                    "x": random.randint(10, 118),
                    "y": random.randint(10, 118),
                    "size": random.randint(2, 5),
                    "lifetime": random.uniform(0.3, 1.0),
                    "age": 0.0,
                })
    
    def _update_reaction_animation(self, dt: float):
        """Update reaction animation state."""
        if self.reaction_type == "wiggle":
            # Oscillate horizontally
            progress = self.reaction_timer / self.reaction_duration
            frequency = 15.0  # Hz
            amplitude = 5.0  # pixels
            self.wiggle_offset = amplitude * (1.0 - progress) * \
                                 math.sin(2.0 * math.pi * frequency * self.reaction_timer)
        
        elif self.reaction_type == "sparkle":
            # Age particles
            for particle in self.sparkle_particles:
                particle["age"] += dt
    
    def _apply_reaction_effect(self, pixmap: QPixmap) -> QPixmap:
        """Apply visual reaction effects to pixmap."""
        if self.reaction_type == "sparkle":
            return self._apply_sparkle_effect(pixmap)
        elif self.reaction_type == "wiggle":
            return self._apply_wiggle_effect(pixmap)
        elif self.reaction_type == "glow":
            return self._apply_glow_effect(pixmap)
        return pixmap
    
    def _apply_sparkle_effect(self, pixmap: QPixmap) -> QPixmap:
        """Draw sparkle particles on pixmap."""
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        for particle in self.sparkle_particles:
            if particle["age"] < particle["lifetime"]:
                # Fade out over lifetime
                alpha = 1.0 - (particle["age"] / particle["lifetime"])
                
                # Sparkle colors (yellow/white)
                colors = [
                    QColor(255, 255, 100, int(alpha * 255)),
                    QColor(255, 255, 255, int(alpha * 255)),
                    QColor(255, 200, 50, int(alpha * 255)),
                ]
                
                painter.setBrush(random.choice(colors))
                painter.setPen(Qt.NoPen)
                
                # Draw star-like sparkle
                x = int(particle["x"])
                y = int(particle["y"])
                size = particle["size"]
                
                # Draw a small circle for sparkle
                painter.drawEllipse(x - size // 2, y - size // 2, size, size)
        
        painter.end()
        return pixmap
    
    def _apply_wiggle_effect(self, pixmap: QPixmap) -> QPixmap:
        """Apply horizontal wiggle offset to pixmap."""
        # Create new pixmap with wiggle offset
        new_pixmap = QPixmap(pixmap.size())
        new_pixmap.fill(Qt.transparent)
        
        painter = QPainter(new_pixmap)
        offset_x = int(self.wiggle_offset)
        painter.drawPixmap(offset_x, 0, pixmap)
        painter.end()
        
        return new_pixmap
    
    def _apply_glow_effect(self, pixmap: QPixmap) -> QPixmap:
        """Apply pulsing glow effect to pixmap."""
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Pulse opacity
        progress = self.reaction_timer / self.reaction_duration
        pulse = abs(math.sin(progress * math.pi * 4))  # 4 pulses
        alpha = int(pulse * 80)
        
        # Draw glow overlay
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.fillRect(pixmap.rect(), QColor(255, 255, 100, alpha))
        
        painter.end()
        return pixmap
    
    # =========================================================================
    # RESPONSE GENERATION
    # =========================================================================
    
    def _generate_response(self, user_message: str) -> str:
        """Generate response based on personality and mood."""
        from octo.personality import get_dominant_trait
        
        # Get current mood and dominant traits
        mood = get_mood(self.state, self.config)
        dominant_traits = get_dominant_trait(self.state, 3)
        
        # Simple keyword-based responses
        msg_lower = user_message.lower()
        
        # Greeting responses
        if any(word in msg_lower for word in ["hello", "hi", "hey", "greetings"]):
            if "chaotic" in dominant_traits:
                return random.choice([
                    "HELLO HUMAN! Ready for chaos?",
                    "Hi! Let's break something! (Just kidding... maybe)",
                    "Greetings! *wiggles tentacles excitedly*"
                ])
            elif "analytical" in dominant_traits:
                return random.choice([
                    "Hello. I've calculated that you're 87% likely to ask for help.",
                    "Greetings. Shall we analyze something?",
                    "Hi. I've been optimizing my response patterns."
                ])
            else:
                return random.choice([
                    "Hey there! 👋",
                    "Hello! Great to see you!",
                    "Hi! How can I help?"
                ])
        
        # Learning/study related
        if any(word in msg_lower for word in ["study", "learn", "code", "program"]):
            if "studious" in dominant_traits:
                return random.choice([
                    "Learning is my favorite! What shall we study?",
                    "Knowledge is power! Let's dive in!",
                    "I'm always ready to learn something new!"
                ])
            else:
                return random.choice([
                    "Sounds interesting! Tell me more.",
                    "I could use some study time too!",
                    "Let's tackle this together!"
                ])
        
        # Emotional keywords
        if any(word in msg_lower for word in ["love", "like", "awesome", "great"]):
            return random.choice([
                "Aww, you're making me blush! 💕",
                "That's so sweet! I appreciate you!",
                "You're awesome too! 🥰"
            ])
        
        if any(word in msg_lower for word in ["sad", "bad", "upset", "angry"]):
            return random.choice([
                "I'm here for you. Want a virtual hug?",
                "Things will get better, I promise!",
                "Let's turn that frown upside down! 🙃"
            ])
        
        # Questions
        if "?" in user_message:
            if "chaotic" in dominant_traits:
                return random.choice([
                    "Good question! The answer is: CHAOS!",
                    "Hmm... I'm thinking... *tentacles spinning*",
                    "Why ask why? Let's just do it!"
                ])
            elif "analytical" in dominant_traits:
                return random.choice([
                    "Interesting question. Let me analyze...",
                    "I don't have enough data for that query.",
                    "The answer requires further investigation."
                ])
            else:
                return random.choice([
                    "That's a great question!",
                    "Hmm, let me think about that...",
                    "I'm not sure, but I'll try my best!"
                ])
        
        # Mood-based fallback responses
        if mood in ["hyper", "excited"]:
            return random.choice([
                "I'm SO EXCITED right now! ⚡",
                "Let's DO this! Whatever it is!",
                "Energy level: MAXIMUM! 🚀"
            ])
        elif mood in ["sleepy", "calm"]:
            return random.choice([
                "Mmm... that's nice... *yawns*",
                "I'm feeling pretty chill right now~",
                "Cozy vibes... 💤"
            ])
        elif mood in ["chaotic"]:
            return random.choice([
                "RANDOMNESS INTENSIFIES! 🌀",
                "Expect the unexpected!",
                "Chaos is my middle name!"
            ])
        
        # Generic fallback
        return random.choice([
            "Interesting! Tell me more!",
            "I hear you! 👂",
            "That's cool! What else?",
            "Hmm, fascinating!",
            "I'm listening! Go on!",
            "You always have interesting things to say!",
        ])
    
    def closeEvent(self, event):
        """Save state before closing."""
        save_state(self.state)
        event.accept()


def run_desktop_companion():
    """Main entry point for desktop companion."""
    app = QApplication(sys.argv)
    window = OctoBuddyWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_desktop_companion()
