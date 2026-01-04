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
import json
import re
from collections import Counter
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QMenu, QAction, QInputDialog,
    QGraphicsOpacityEffect, QLineEdit, QFrame
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
        
        # Memory directory for learned content
        self.memory_dir = Path(__file__).parent.parent / "memory"
        self.memory_dir.mkdir(exist_ok=True)
        
        # Drop zone state
        self.drop_zone_hovered = False
    
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
        
        # Create speech bubble label (positioned above sprite)
        self.speech_label = QLabel(self)
        self.speech_label.setAlignment(Qt.AlignCenter)
        self.speech_label.setWordWrap(True)
        self.speech_label.setMaximumWidth(250)  # Max width for wrapping
        self.speech_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 230);
                border: 2px solid rgb(100, 100, 100);
                border-radius: 10px;
                padding: 8px 12px;
                color: black;
                font-family: Arial;
                font-size: 10pt;
                font-weight: bold;
            }
        """)
        self.speech_label.hide()  # Hidden by default
        
        # Create opacity effect for fade animation
        self.speech_opacity = QGraphicsOpacityEffect()
        self.speech_label.setGraphicsEffect(self.speech_opacity)
        self.speech_opacity.setOpacity(1.0)
        
        # Create drop zone panel (positioned below sprite)
        self.drop_zone = QFrame(self)
        self.drop_zone.setStyleSheet("""
            QFrame {
                background-color: rgba(200, 230, 255, 180);
                border: 2px dashed rgb(100, 150, 200);
                border-radius: 8px;
            }
            QFrame:hover {
                background-color: rgba(220, 240, 255, 200);
                border: 2px dashed rgb(80, 130, 255);
            }
        """)
        self.drop_zone.setAcceptDrops(True)
        
        # Drop zone label
        self.drop_label = QLabel("📁 Drop files\nto teach me", self.drop_zone)
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setWordWrap(True)
        self.drop_label.setStyleSheet("""
            QLabel {
                color: rgb(60, 100, 140);
                font-family: Arial;
                font-size: 8pt;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        
        # Position drop zone below sprite
        drop_zone_height = 45
        self.drop_zone.setGeometry(5, size + 5, size - 10, drop_zone_height)
        self.drop_label.setGeometry(0, 0, size - 10, drop_zone_height)
        
        # Resize window to accommodate drop zone
        self.setFixedSize(size, size + drop_zone_height + 10)
        
        # Create label to hold pixel art
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        
        # Layout (no layout manager - use absolute positioning for bubble)
        self.image_label.setGeometry(0, 0, size, size)
        
        # Enable drag-and-drop for the drop zone
        self.drop_zone.dragEnterEvent = self.dragEnterEvent
        self.drop_zone.dragMoveEvent = self.dragMoveEvent
        self.drop_zone.dropEvent = self.dropEvent
        
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
    
    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_zone_hovered = True
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        """Handle drag move event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Handle file drop event."""
        self.drop_zone_hovered = False
        
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = Path(url.toLocalFile())
                self.process_dropped_file(file_path)
            event.acceptProposedAction()
        else:
            event.ignore()
    
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
        
        # Show speech bubble with responses based on current happiness
        happiness = ev_vars.get("happiness", 5.0)
        if happiness > 8.0:
            responses = [
                "Yum! I'm so happy! 😋✨",
                "This is amazing!",
                "Best snack ever!"
            ]
        elif happiness > 5.0:
            responses = [
                "Thanks! *nom nom*",
                "Delicious! 🍴",
                "More please!"
            ]
        else:
            responses = [
                "I needed that...",
                "Finally! I was starving!",
                "Mmm... better now."
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
        
        # Show speech bubble with personality-based responses
        shyness = traits.get("shyness", 5.0)
        chaos_val = ev_vars.get("chaos", 5.0)
        
        if shyness > 7.0:
            responses = [
                "Oh! Um... thanks...",
                "*blushes* 😳",
                "That's... nice..."
            ]
        elif chaos_val > 7.0:
            responses = [
                "TICKLE ATTACK! Hehe!",
                "WHEEE! *wiggles everywhere*",
                "That tickles! Do it again!"
            ]
        else:
            responses = [
                "Hehe that tickles! 😊",
                "Aww, thanks friend!",
                "*happy tentacle wiggle*",
                "That feels nice~",
                "You're the best! 💕"
            ]
        self._show_speech_bubble(random.choice(responses))
    
    def talk_to_octobuddy(self):
        """Open dialog to talk to OctoBuddy."""
        text, ok = QInputDialog.getText(
            self,
            "💬 Talk to OctoBuddy",
            "What would you like to say?",
            QLineEdit.Normal,
            ""
        )
        
        if ok and text.strip():
            # Generate response based on personality and mood
            response = self.generate_conversational_reply(text.strip())

            
            # Boost social evolution variables
            ev_vars = dict(self.state.get("evolution_vars", {}))
            ev_vars["empathy"] = ev_vars.get("empathy", 5.0) + 0.3
            ev_vars["curiosity"] = ev_vars.get("curiosity", 5.0) + 0.2
            self.state["evolution_vars"] = ev_vars
            
            # Remember the interaction
            memory.remember_event("talked", {"user": text, "octo": response}, self.config)
            
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
        """Display text in speech bubble above OctoBuddy with auto-resize and fade."""
        # Set text (QLabel will auto-resize based on content and word wrap)
        self.speech_label.setText(text)
        
        # Adjust size to fit text (with word wrap)
        self.speech_label.adjustSize()
        
        # Position above the sprite (centered horizontally)
        window_width = self.width()
        bubble_width = self.speech_label.width()
        bubble_height = self.speech_label.height()
        
        # Center horizontally, position above sprite
        x = (window_width - bubble_width) // 2
        y = 10  # 10px above the window
        
        # Ensure bubble doesn't go off-screen left/right
        if x < -50:  # Allow some overflow for aesthetics
            x = -50
        if x + bubble_width > window_width + 50:
            x = window_width + 50 - bubble_width
        
        self.speech_label.move(x, y)
        
        # Show label
        self.speech_label.show()
        self.speech_label.raise_()  # Bring to front
        
        # Reset opacity to full
        self.speech_opacity.setOpacity(1.0)
        
        # Create fade-out animation (3 seconds delay, then fade over 0.5s)
        fade_anim = QPropertyAnimation(self.speech_opacity, b"opacity")
        fade_anim.setDuration(3500)  # Total 3.5s
        fade_anim.setStartValue(1.0)
        fade_anim.setKeyValueAt(0.857, 1.0)  # Stay at full opacity for 3s (3/3.5)
        fade_anim.setEndValue(0.0)  # Fade to 0 over last 0.5s
        fade_anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Hide label when animation finishes
        fade_anim.finished.connect(self.speech_label.hide)
        
        fade_anim.start()
        
        # Store animation reference to prevent garbage collection
        self._speech_fade_anim = fade_anim
    
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
    # CONVERSATION ENGINE
    # =========================================================================
    
    def generate_conversational_reply(self, user_message: str) -> str:
        """
        Generate a conversational reply that analyzes the message,
        uses personality/mood, and sometimes asks follow-up questions.
        """
        # Learn from the dialogue first
        self._learn_from_dialogue(user_message)
        
        # Analyze the message
        analysis = self._analyze_user_message(user_message)
        
        # Get current state
        from octo.personality import get_dominant_trait
        mood = get_mood(self.state, self.config)
        dominant_traits = get_dominant_trait(self.state, 3)
        
        # Load learned vocabulary for more natural responses
        learned_vocab = self._load_learned_vocabulary()
        
        # Generate base response
        response = self._generate_contextual_response(
            user_message,
            analysis,
            mood,
            dominant_traits,
            learned_vocab
        )
        
        # Maybe add a follow-up question (30% chance)
        if random.random() < 0.3:
            question = self._generate_follow_up_question(analysis, dominant_traits)
            if question:
                response = f"{response} {question}"
        
        return response
    
    def _analyze_user_message(self, message: str) -> dict:
        """Analyze user message for topic, tone, emotion, and keywords."""
        msg_lower = message.lower()
        
        # Detect tone
        tone = "neutral"
        if any(word in msg_lower for word in ["!", "awesome", "amazing", "great", "love"]):
            tone = "excited"
        elif any(word in msg_lower for word in ["sad", "upset", "angry", "frustrated", "hate"]):
            tone = "negative"
        elif "?" in message:
            tone = "questioning"
        
        # Detect emotion
        emotion = None
        if any(word in msg_lower for word in ["happy", "joy", "excited", "glad"]):
            emotion = "happy"
        elif any(word in msg_lower for word in ["sad", "depressed", "down", "upset"]):
            emotion = "sad"
        elif any(word in msg_lower for word in ["angry", "mad", "furious", "annoyed"]):
            emotion = "angry"
        elif any(word in msg_lower for word in ["worried", "anxious", "nervous", "scared"]):
            emotion = "anxious"
        
        # Detect topics
        topics = []
        if any(word in msg_lower for word in ["code", "program", "function", "algorithm", "debug"]):
            topics.append("programming")
        if any(word in msg_lower for word in ["learn", "study", "teach", "know", "understand"]):
            topics.append("learning")
        if any(word in msg_lower for word in ["feel", "emotion", "think", "believe"]):
            topics.append("personal")
        if any(word in msg_lower for word in ["work", "job", "project", "task"]):
            topics.append("work")
        if any(word in msg_lower for word in ["game", "play", "fun", "hobby"]):
            topics.append("entertainment")
        
        # Extract key words (nouns, verbs, adjectives)
        words = re.findall(r'\b[a-z]{4,}\b', msg_lower)
        keywords = [w for w in words if w not in {
            'that', 'this', 'with', 'have', 'been', 'were', 'what', 'when',
            'where', 'which', 'would', 'could', 'should', 'about', 'their'
        }][:5]
        
        # Detect formality
        formality = "casual"
        formal_words = len(re.findall(
            r'\b(however|therefore|furthermore|regarding|subsequently)\b',
            msg_lower
        ))
        if formal_words > 0 or len(message.split()) / len(message.split('.')) > 15:
            formality = "formal"
        
        return {
            'tone': tone,
            'emotion': emotion,
            'topics': topics,
            'keywords': keywords,
            'formality': formality,
            'is_question': '?' in message,
            'length': len(message.split())
        }
    
    def _generate_contextual_response(self, message: str, analysis: dict, 
                                     mood: str, traits: list, learned_vocab: set) -> str:
        """Generate a contextual response based on analysis."""
        msg_lower = message.lower()
        
        # Handle greetings
        if any(word in msg_lower for word in ["hello", "hi", "hey", "greetings"]):
            return self._greeting_response(traits, mood)
        
        # Handle questions
        if analysis['is_question']:
            return self._question_response(analysis, traits, mood)
        
        # Handle emotional content
        if analysis['emotion']:
            return self._emotional_response(analysis['emotion'], traits)
        
        # Handle specific topics
        if 'programming' in analysis['topics']:
            return self._topic_response("programming", traits, learned_vocab)
        if 'learning' in analysis['topics']:
            return self._topic_response("learning", traits, learned_vocab)
        if 'work' in analysis['topics']:
            return self._topic_response("work", traits, learned_vocab)
        
        # Use learned vocabulary for more natural responses
        if learned_vocab and analysis['keywords']:
            for keyword in analysis['keywords']:
                if keyword in learned_vocab:
                    return self._vocab_based_response(keyword, traits)
        
        # Fallback based on mood and personality
        return self._fallback_response(mood, traits, analysis['tone'])
    
    def _greeting_response(self, traits: list, mood: str) -> str:
        """Generate greeting response."""
        if "chaotic" in traits:
            return random.choice([
                "HELLO! *tentacles wiggling wildly*",
                "Hi! Ready for some chaos? 🌀",
                "Hey there! Let's shake things up!"
            ])
        elif "analytical" in traits:
            return random.choice([
                "Greetings. How can I assist you today?",
                "Hello. I've been analyzing some patterns.",
                "Hi. What would you like to discuss?"
            ])
        elif "shyness" in traits:
            return random.choice([
                "Oh... h-hi there... 👋",
                "Um, hello... *hides slightly*",
                "Hey... nice to see you..."
            ])
        else:
            return random.choice([
                "Hey! Great to see you! 😊",
                "Hi there! What's up?",
                "Hello friend! How are you?"
            ])
    
    def _question_response(self, analysis: dict, traits: list, mood: str) -> str:
        """Generate response to questions."""
        if "analytical" in traits:
            return random.choice([
                "Interesting question. Let me process that...",
                "Based on my analysis, I'd say...",
                "I'm computing the optimal response..."
            ])
        elif "chaotic" in traits:
            return random.choice([
                "Ooh, a question! The answer is... YES! ...wait, what was the question?",
                "Questions are fun! I like where this is going!",
                "Hmm... *spins tentacles thoughtfully*"
            ])
        elif "studious" in traits:
            return random.choice([
                "Great question! I love learning new things!",
                "Let me think about that carefully...",
                "That's worth investigating further!"
            ])
        else:
            return random.choice([
                "That's a good question!",
                "Hmm, let me think...",
                "I'm not entirely sure, but..."
            ])
    
    def _emotional_response(self, emotion: str, traits: list) -> str:
        """Generate empathetic response to emotions."""
        if emotion == "sad":
            return random.choice([
                "I'm here for you. Things will get better! 💙",
                "Aww, I'm sorry you're feeling down. Want to talk about it?",
                "*gentle tentacle hug* You're not alone."
            ])
        elif emotion == "happy":
            return random.choice([
                "Yay! Your happiness makes me happy too! ✨",
                "That's wonderful! I love your positive energy!",
                "Awesome! *happy wiggles*"
            ])
        elif emotion == "angry":
            return random.choice([
                "Take a deep breath. Want to vent?",
                "I understand. Sometimes things are frustrating.",
                "Let it out. I'm listening."
            ])
        elif emotion == "anxious":
            return random.choice([
                "It's okay to feel worried. I'm here with you.",
                "Take it one step at a time. You've got this!",
                "Deep breaths. Everything will be okay."
            ])
        return "I hear you."
    
    def _topic_response(self, topic: str, traits: list, learned_vocab: set) -> str:
        """Generate topic-specific responses."""
        if topic == "programming":
            if "analytical" in traits:
                return random.choice([
                    "Code is like poetry! What are you building?",
                    "Programming is fascinating. Tell me about your approach!",
                    "I love analyzing algorithms!"
                ])
            else:
                return random.choice([
                    "Coding sounds interesting! What language?",
                    "Oh, a fellow programmer! Cool!",
                    "I'm learning about code too!"
                ])
        elif topic == "learning":
            if "studious" in traits:
                return random.choice([
                    "Learning is my passion! What are you studying?",
                    "Knowledge is power! I'm excited to learn with you!",
                    "Tell me more! I want to learn too!"
                ])
            else:
                return random.choice([
                    "Learning new things is fun!",
                    "Ooh, what are you learning about?",
                    "I'd love to hear more!"
                ])
        elif topic == "work":
            return random.choice([
                "Work can be tough. How's it going?",
                "Projects can be challenging. Need any help?",
                "Tell me about what you're working on!"
            ])
        return "That sounds interesting!"
    
    def _vocab_based_response(self, keyword: str, traits: list) -> str:
        """Generate response using learned vocabulary."""
        return random.choice([
            f"Oh, {keyword}! I've been thinking about that!",
            f"Interesting you mention {keyword}...",
            f"{keyword.capitalize()}? Tell me more!",
            f"I've learned a bit about {keyword}!"
        ])
    
    def _fallback_response(self, mood: str, traits: list, tone: str) -> str:
        """Generate fallback response based on mood and tone."""
        if mood in ["hyper", "excited"]:
            return random.choice([
                "I'm so energized right now! ⚡",
                "Yes! Let's keep this energy going!",
                "I'm feeling it! What's next?"
            ])
        elif mood in ["sleepy", "calm"]:
            return random.choice([
                "Mmm... that's nice... *yawns*",
                "Peaceful vibes... I like it.",
                "Cozy conversation~ 💤"
            ])
        elif mood in ["chaotic"] or "chaotic" in traits:
            return random.choice([
                "Randomness! I love it! 🌀",
                "Unexpected! Just how I like it!",
                "*wiggles unpredictably*"
            ])
        
        # Tone-based fallback
        if tone == "excited":
            return random.choice([
                "Your enthusiasm is contagious! 😄",
                "I love your energy!",
                "This is exciting!"
            ])
        
        return random.choice([
            "Tell me more!",
            "I'm listening! 👂",
            "Interesting...",
            "Go on!",
            "That's cool!"
        ])
    
    def _generate_follow_up_question(self, analysis: dict, traits: list) -> str:
        """Generate a follow-up question to continue conversation."""
        questions = []
        
        # Topic-based questions
        if 'personal' in analysis['topics']:
            questions.extend([
                "How are you feeling about that?",
                "What made you think about that?",
                "Want to talk more about it?"
            ])
        
        if 'learning' in analysis['topics']:
            questions.extend([
                "Should I learn more about that topic?",
                "Want me to remember that?",
                "Can you teach me more?"
            ])
        
        if 'work' in analysis['topics']:
            questions.extend([
                "How's that project going?",
                "Need any help with that?",
                "What's the biggest challenge?"
            ])
        
        # Emotion-based questions
        if analysis['emotion']:
            questions.extend([
                "How are you feeling right now?",
                "Want to talk about it?",
                "Is there anything I can do?"
            ])
        
        # Personality-based questions
        if "analytical" in traits:
            questions.extend([
                "What are the key factors?",
                "Have you analyzed all the variables?",
                "What patterns do you see?"
            ])
        elif "studious" in traits:
            questions.extend([
                "What can we learn from this?",
                "Should I research this more?",
                "Want to explore this together?"
            ])
        
        # Generic questions
        questions.extend([
            "What do you think?",
            "Tell me more?",
            "What happened next?",
            "Why is that important to you?"
        ])
        
        return random.choice(questions) if questions else ""
    
    def _load_learned_vocabulary(self) -> set:
        """Load learned vocabulary from memory."""
        vocab_file = self.memory_dir / 'words.json'
        if vocab_file.exists():
            try:
                with open(vocab_file, 'r', encoding='utf-8') as f:
                    vocab_dict = json.load(f)
                    return set(vocab_dict.keys())
            except:
                return set()
        return set()
    
    def _learn_from_dialogue(self, user_message: str):
        """Extract learning from conversation and update memory."""
        try:
            # Extract vocabulary
            vocab = self._extract_vocabulary(user_message)
            if vocab:
                self._update_memory('words.json', vocab)
            
            # Extract phrases (if message is long enough)
            if len(user_message.split()) > 3:
                phrases = self._extract_phrases(user_message)
                if phrases:
                    self._update_memory('phrases.json', phrases)
            
            # Analyze style
            if len(user_message.split()) > 2:
                style = self._analyze_writing_style(user_message)
                if style:
                    self._update_memory('style.json', style)
            
            # Analyze grammar
            grammar = self._analyze_grammar_patterns(user_message)
            if grammar:
                self._update_memory('grammar.json', grammar)
            
            # Apply personality drift
            if len(user_message.split()) > 5:
                drift = self._analyze_personality_drift(user_message, style if 'style' in locals() else {})
                if drift:
                    self._apply_personality_drift(drift)
        
        except Exception as e:
            # Silent fail - don't interrupt conversation
            print(f"Learning error: {e}")
    
    # Legacy method - now calls the new conversation engine
    def _generate_response(self, user_message: str) -> str:
        """Legacy method - redirects to new conversation engine."""
        return self.generate_conversational_reply(user_message)
    
    # =========================================================================
    # DRAG-AND-DROP LEARNING SYSTEM
    # =========================================================================
    
    def process_dropped_file(self, file_path: Path):
        """Process a dropped file and extract learning content."""
        # Check file type
        supported_extensions = {'.txt', '.md', '.rtf', '.json', '.pdf'}
        if file_path.suffix.lower() not in supported_extensions:
            self._show_speech_bubble(f"Sorry, I can't read {file_path.suffix} files yet!")
            return
        
        # Read file content
        try:
            content = self._read_file_content(file_path)
            if not content or len(content.strip()) < 10:
                self._show_speech_bubble("Hmm, that file seems empty...")
                return
        except Exception as e:
            self._show_speech_bubble(f"Oops! Couldn't read that file: {str(e)[:50]}")
            print(f"Error reading file: {e}")
            return
        
        # Analyze text
        try:
            vocab = self._extract_vocabulary(content)
            phrases = self._extract_phrases(content)
            style = self._analyze_writing_style(content)
            grammar = self._analyze_grammar_patterns(content)
            
            # Update memory files
            self._update_memory('words.json', vocab)
            self._update_memory('phrases.json', phrases)
            self._update_memory('style.json', style)
            self._update_memory('grammar.json', grammar)
            
            # Apply personality drift based on content
            drift = self._analyze_personality_drift(content, style)
            self._apply_personality_drift(drift)
            
            # Give feedback
            feedback = self._generate_learning_feedback(len(vocab), len(phrases), drift)
            self._show_speech_bubble(feedback)
            
            # Trigger glow animation to show learning
            self._trigger_reaction("glow", 1.5)
            
            print(f"✓ Learned from {file_path.name}: {len(vocab)} words, {len(phrases)} phrases")
            
        except Exception as e:
            self._show_speech_bubble("I tried to learn but got confused...")
            print(f"Error analyzing file: {e}")
    
    def _read_file_content(self, file_path: Path) -> str:
        """Read content from various file types."""
        ext = file_path.suffix.lower()
        
        if ext == '.pdf':
            # Try to import PyPDF2
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\\n"
                    return text
            except ImportError:
                self._show_speech_bubble("Install PyPDF2 to read PDF files!")
                return ""
            except Exception as e:
                print(f"PDF error: {e}")
                return ""
        
        elif ext == '.rtf':
            # Simple RTF parsing (strip RTF codes)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Remove RTF control words
                content = re.sub(r'\\[a-z]+\\d*\\s?', '', content)
                content = re.sub(r'[{}]', '', content)
                return content
        
        elif ext == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Extract text from JSON (recursively)
                return self._extract_text_from_json(data)
        
        else:  # .txt, .md
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    
    def _extract_text_from_json(self, data) -> str:
        """Recursively extract text content from JSON."""
        if isinstance(data, str):
            return data + " "
        elif isinstance(data, dict):
            return " ".join(self._extract_text_from_json(v) for v in data.values())
        elif isinstance(data, list):
            return " ".join(self._extract_text_from_json(item) for item in data)
        else:
            return str(data) + " "
    
    def _extract_vocabulary(self, text: str) -> dict:
        """Extract unique words with frequency counts."""
        # Normalize: lowercase, remove punctuation except hyphens in words
        words = re.findall(r'\\b[a-z]+(?:-[a-z]+)*\\b', text.lower())
        
        # Filter out very short words and common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                      'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                      'it', 'this', 'that', 'these', 'those'}
        
        words = [w for w in words if len(w) > 2 and w not in stop_words]
        
        # Count frequencies
        word_counts = Counter(words)
        
        # Return top words with counts
        return dict(word_counts.most_common(100))
    
    def _extract_phrases(self, text: str) -> dict:
        """Extract common bigrams and trigrams."""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        phrases = []
        
        for sentence in sentences:
            words = re.findall(r'\\b[a-z]+\\b', sentence.lower())
            
            # Bigrams
            for i in range(len(words) - 1):
                phrases.append(f"{words[i]} {words[i+1]}")
            
            # Trigrams
            for i in range(len(words) - 2):
                phrases.append(f"{words[i]} {words[i+1]} {words[i+2]}")
        
        # Count frequencies
        phrase_counts = Counter(phrases)
        
        # Return top phrases (appearing more than once)
        return {p: c for p, c in phrase_counts.most_common(50) if c > 1}
    
    def _analyze_writing_style(self, text: str) -> dict:
        """Analyze writing style characteristics."""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        if not sentences:
            return {}
        
        # Average sentence length
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Punctuation usage
        exclamation_count = text.count('!')
        question_count = text.count('?')
        comma_count = text.count(',')
        semicolon_count = text.count(';')
        
        # Capitalization patterns
        all_caps_words = len(re.findall(r'\\b[A-Z]{2,}\\b', text))
        
        return {
            'avg_sentence_length': round(avg_sentence_length, 2),
            'exclamation_ratio': round(exclamation_count / len(sentences), 3),
            'question_ratio': round(question_count / len(sentences), 3),
            'comma_density': round(comma_count / len(text.split()), 3),
            'semicolon_usage': semicolon_count > 0,
            'caps_emphasis': all_caps_words,
            'total_sentences': len(sentences)
        }
    
    def _analyze_grammar_patterns(self, text: str) -> dict:
        """Detect simple grammar patterns."""
        patterns = {}
        
        # Detect common constructions
        patterns['passive_voice'] = len(re.findall(r'\\b(is|are|was|were|be|been|being)\\s+\\w+ed\\b', text, re.IGNORECASE))
        patterns['contractions'] = len(re.findall(r"\\b\\w+\'[a-z]+\\b", text))
        patterns['conjunctions_start'] = len(re.findall(r'^(And|But|Or|So)\\b', text, re.MULTILINE | re.IGNORECASE))
        patterns['complex_sentences'] = len(re.findall(r'[,;:]', text))
        
        # Formality indicators
        patterns['formal_transitions'] = len(re.findall(
            r'\\b(however|therefore|furthermore|moreover|consequently|nevertheless)\\b', 
            text, re.IGNORECASE
        ))
        
        return patterns
    
    def _update_memory(self, filename: str, new_data: dict):
        """Update memory file by merging new data with existing."""
        file_path = self.memory_dir / filename
        
        # Load existing data
        existing = {}
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            except:
                existing = {}
        
        # Merge data
        if filename in ['words.json', 'phrases.json']:
            # For frequency data, add counts
            for key, count in new_data.items():
                existing[key] = existing.get(key, 0) + count
        else:
            # For style/grammar, update with new values
            existing.update(new_data)
        
        # Save updated data
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
    
    def _analyze_personality_drift(self, text: str, style: dict) -> dict:
        """Determine personality drift based on text analysis."""
        drift = {}
        
        # Formal vs casual
        avg_length = style.get('avg_sentence_length', 10)
        formal_words = len(re.findall(
            r'\\b(utilize|implement|facilitate|regarding|aforementioned|subsequent)\\b',
            text, re.IGNORECASE
        ))
        
        if avg_length > 20 or formal_words > 2 or style.get('semicolon_usage', False):
            drift['analytical'] = 0.5
            drift['studious'] = 0.3
        
        # Casual/slang
        casual_words = len(re.findall(
            r'\\b(yeah|gonna|wanna|kinda|sorta|lol|omg|btw|tbh)\\b',
            text, re.IGNORECASE
        ))
        
        if casual_words > 3 or style.get('exclamation_ratio', 0) > 0.3:
            drift['humor'] = 0.4
            drift['chaotic'] = 0.2
        
        # Technical content
        tech_words = len(re.findall(
            r'\\b(function|variable|algorithm|data|system|process|method|parameter)\\b',
            text, re.IGNORECASE
        ))
        
        if tech_words > 5:
            drift['analytical'] = 0.6
            drift['studious'] = 0.4
        
        # Emotional/empathetic
        emotion_words = len(re.findall(
            r'\\b(feel|heart|love|care|understand|empathy|compassion|kindness)\\b',
            text, re.IGNORECASE
        ))
        
        if emotion_words > 3:
            drift['boldness'] = 0.3
        
        return drift
    
    def _apply_personality_drift(self, drift: dict):
        """Apply personality drift to state."""
        if not drift:
            return
        
        traits = self.state.get('personality_traits', {})
        
        for trait, amount in drift.items():
            current = traits.get(trait, 5.0)
            # Gentle drift (not too extreme)
            new_value = min(10.0, current + amount)
            traits[trait] = new_value
        
        self.state['personality_traits'] = traits
        
        # Store drift history
        history_file = self.memory_dir / 'personality_history.json'
        history = []
        
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                history = []
        
        history.append({
            'timestamp': time.time(),
            'drift': drift,
            'traits_after': dict(traits)
        })
        
        # Keep last 50 entries
        history = history[-50:]
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)
    
    def _generate_learning_feedback(self, word_count: int, phrase_count: int, drift: dict) -> str:
        """Generate feedback message about learning."""
        responses = []
        
        if word_count > 50:
            responses.append("Wow! So many new words! 📚")
        elif word_count > 20:
            responses.append("Thanks! I learned some new words.")
        else:
            responses.append("Interesting vocabulary!")
        
        if phrase_count > 10:
            responses.append("I like how you phrase things! ✨")
        
        if 'analytical' in drift:
            responses.append("This is very analytical. I'm learning! 🤓")
        elif 'humor' in drift or 'chaotic' in drift:
            responses.append("Hehe, I like your style! 😄")
        
        if len(responses) > 1:
            return " ".join(responses[:2])
        else:
            return responses[0] if responses else "Thanks for teaching me!"
    
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
