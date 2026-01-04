"""
Enhanced Desktop UI for Self-Evolving OctoBuddy.

Integrates all systems:
- HD procedural pixel art rendering
- Evolution tracking and display
- Mutation visualization
- Memory system
- Personality-driven interactions
- Ability system
- Chat interface

This is the main window that users interact with.
"""

import sys
import time
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout,
                            QHBoxLayout, QTextEdit, QLineEdit, QPushButton)
from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtGui import QPainter, QPixmap, QImage, QColor

from .physics import Vector2D
from .tentacles import TentacleSystem
from .animation_engine import AnimationState
from .events import EventSystem, EventType
from .art_engine import ArtEngine, ColorPalette
from .evolution import EvolutionEngine, EvolutionState
from .mutations import MutationEngine, MutationType
from .memory import MemorySystem
from .personality_drift import PersonalityDrift
from .abilities import AbilitySystem


class SelfEvolvingOctoBuddyWidget(QWidget):
    """
    Main desktop widget for self-evolving OctoBuddy.
    
    Features:
    - HD procedural sprite rendering (128x128)
    - Real-time evolution and mutation
    - Memory and learning
    - Personality drift
    - Ability expansion
    - Chat interface
    """
    
    def __init__(self, width=600, height=700):
        """
        Initialize OctoBuddy widget.
        
        Args:
            width: Window width
            height: Window height
        """
        super().__init__()
        
        # Window setup
        self.setWindowTitle("OctoBuddy - Self-Evolving AI Companion")
        self.resize(width, height)
        
        # Keep window on top but not frameless (need controls)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        # Core systems
        self.art_engine = ArtEngine()
        self.evolution_engine = EvolutionEngine()
        self.mutation_engine = MutationEngine()
        self.memory_system = MemorySystem()
        self.personality = PersonalityDrift()
        self.ability_system = AbilitySystem()
        
        # Animation systems (existing)
        center_x = 300
        center_y = 200
        self.center_position = Vector2D(center_x, center_y)
        self.tentacle_system = TentacleSystem(self.center_position, num_tentacles=6)
        self.animation_state = AnimationState()
        self.event_system = EventSystem()
        
        # Setup event listeners
        self._setup_event_listeners()
        
        # UI elements
        self._setup_ui()
        
        # Animation loop timer (30 FPS for better performance with rendering)
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_animation)
        self.fps = 30
        self.timer.start(1000 // self.fps)
        
        # Performance tracking
        self.last_frame_time = time.time()
        self.frame_count = 0
        
        # HD sprite cache
        self.sprite_pixmap = None
        self.sprite_update_counter = 0
        self._regenerate_sprite()
    
    def _setup_ui(self):
        """Setup UI layout."""
        layout = QVBoxLayout()
        
        # Sprite display area
        self.sprite_label = QLabel()
        self.sprite_label.setAlignment(Qt.AlignCenter)
        self.sprite_label.setMinimumSize(128, 128)
        layout.addWidget(self.sprite_label)
        
        # Info display
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        # Chat area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMaximumHeight(200)
        layout.addWidget(self.chat_display)
        
        # Input area
        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Chat with OctoBuddy...")
        self.chat_input.returnPressed.connect(self._handle_chat_input)
        input_layout.addWidget(self.chat_input)
        
        send_button = QPushButton("Send")
        send_button.clicked.connect(self._handle_chat_input)
        input_layout.addWidget(send_button)
        
        layout.addLayout(input_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        mutate_button = QPushButton("Trigger Mutation")
        mutate_button.clicked.connect(self._trigger_manual_mutation)
        button_layout.addWidget(mutate_button)
        
        learn_button = QPushButton("Learning Event")
        learn_button.clicked.connect(self._trigger_learning)
        button_layout.addWidget(learn_button)
        
        stats_button = QPushButton("Show Stats")
        stats_button.clicked.connect(self._show_stats)
        button_layout.addWidget(stats_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Initial greeting
        greeting = self.personality.generate_greeting()
        self._add_chat_message("OctoBuddy", greeting)
    
    def _setup_event_listeners(self):
        """Setup event system listeners."""
        # Connect events to evolution
        self.event_system.add_listener(
            EventType.CLICK,
            lambda e: self._on_user_interaction("click")
        )
        self.event_system.add_listener(
            EventType.TYPING_BURST,
            lambda e: self._on_user_interaction("typing")
        )
        self.event_system.add_listener(
            EventType.LEARNING_MOMENT,
            lambda e: self._on_learning_event("exploration")
        )
        
        # Connect to animation state
        self.event_system.add_listener(
            EventType.CLICK,
            lambda e: self.animation_state.on_click()
        )
    
    def _update_animation(self):
        """Main animation update loop."""
        # Calculate delta time
        current_time = time.time()
        dt = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Update systems
        self.frame_count += 1
        
        # Update event system
        self.event_system.update()
        
        # Update animation state
        self.animation_state.update(dt)
        
        # Update evolution (natural drift)
        if self.frame_count % (30 * 60) == 0:  # Every minute at 30fps
            self.evolution_engine.apply_natural_drift(60)  # 60 seconds passed
            self.personality.apply_natural_drift(60)
            
            # Check for mutation
            if self.evolution_engine.trigger_mutation_check():
                self._trigger_auto_mutation()
        
        # Apply evolution influence on personality
        if self.frame_count % (30 * 30) == 0:  # Every 30 seconds
            evolution_dict = self.evolution_engine.state.to_dict()
            self.personality.apply_evolution_influence(evolution_dict)
        
        # Map evolution to animation state
        appearance_mods = self.evolution_engine.get_appearance_modifiers()
        self.animation_state.energy = appearance_mods.get('movement_speed', 0.5)
        self.animation_state.curiosity = appearance_mods.get('glow_intensity', 0.5)
        
        # Update tentacles
        self.tentacle_system.update_mood(
            energy=self.animation_state.energy,
            curiosity=self.animation_state.curiosity,
            happiness=self.animation_state.happiness,
            calmness=self.animation_state.calmness
        )
        
        self.tentacle_system.update(dt=1.0)
        
        # Regenerate sprite periodically or after mutations
        if self.sprite_update_counter > 0:
            self.sprite_update_counter -= 1
            if self.sprite_update_counter == 0:
                self._regenerate_sprite()
        
        # Update info display
        self._update_info_display()
        
        # Trigger repaint
        self.update()
    
    def _regenerate_sprite(self):
        """Regenerate the HD pixel art sprite."""
        # Generate new sprite image
        sprite_img = self.art_engine.generate_sprite(size=128)
        
        # Convert PIL Image to QPixmap
        sprite_img = sprite_img.convert("RGBA")
        data = sprite_img.tobytes("raw", "RGBA")
        qimage = QImage(data, 128, 128, QImage.Format_RGBA8888)
        self.sprite_pixmap = QPixmap.fromImage(qimage)
        
        # Scale up for better visibility
        self.sprite_pixmap = self.sprite_pixmap.scaled(
            256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        
        # Update label
        self.sprite_label.setPixmap(self.sprite_pixmap)
    
    def _update_info_display(self):
        """Update info label with current stats."""
        stage = self.evolution_engine.state.get_evolution_stage()
        archetype = self.personality.traits.get_personality_archetype()
        
        info = f"""
<b>Evolution Stage:</b> {stage}<br>
<b>Personality:</b> {archetype}<br>
<b>Age:</b> {self.evolution_engine.state.age_in_hours():.1f} hours<br>
<b>Mutations:</b> {self.evolution_engine.state.total_mutations}<br>
<b>Abilities:</b> {len(self.ability_system.get_available_abilities())}<br>
<b>Memories:</b> {len(self.memory_system.long_term.memories)}
"""
        self.info_label.setText(info)
    
    def _on_user_interaction(self, interaction_type: str):
        """Handle user interaction."""
        # Record in memory
        self.memory_system.remember(
            "interaction",
            f"User {interaction_type}",
            importance=0.5
        )
        
        # Update evolution
        self.evolution_engine.on_interaction(interaction_type)
        
        # Update personality
        if interaction_type == "click":
            self.personality.on_positive_interaction()
    
    def _on_learning_event(self, learning_type: str):
        """Handle learning event."""
        # Record in memory
        self.memory_system.remember(
            "learning",
            f"Learning: {learning_type}",
            importance=0.7
        )
        
        # Update evolution
        self.evolution_engine.on_learning_event(learning_type)
        
        # Update personality
        self.personality.on_learning_event()
    
    def _trigger_auto_mutation(self):
        """Trigger automatic mutation based on evolution."""
        evolution_dict = self.evolution_engine.state.to_dict()
        
        # Try visual mutation
        mutation = self.mutation_engine.trigger_mutation(
            MutationType.VISUAL,
            evolution_dict,
            forced=False
        )
        
        if mutation:
            # Apply to art engine
            self.mutation_engine.apply_mutation_to_art_engine(mutation, self.art_engine)
            
            # Schedule sprite regeneration
            self.sprite_update_counter = 30  # Regenerate in 1 second
            
            # Remember mutation
            self.memory_system.remember(
                "mutation",
                f"Mutated: {mutation.description}",
                importance=0.8
            )
            
            # Notify user
            self._add_chat_message(
                "OctoBuddy",
                f"I just evolved! {mutation.description}"
            )
    
    def _trigger_manual_mutation(self):
        """Trigger mutation manually (button press)."""
        evolution_dict = self.evolution_engine.state.to_dict()
        
        mutation = self.mutation_engine.trigger_mutation(
            MutationType.VISUAL,
            evolution_dict,
            forced=True
        )
        
        if mutation:
            self.mutation_engine.apply_mutation_to_art_engine(mutation, self.art_engine)
            self.sprite_update_counter = 5
            
            self._add_chat_message(
                "OctoBuddy",
                f"Mutation triggered! {mutation.description}"
            )
    
    def _trigger_learning(self):
        """Trigger learning event (button press)."""
        self._on_learning_event("study")
        self.evolution_engine.on_learning_event("study")
        
        # Maybe learn a new ability
        suggestion = self.ability_system.suggest_new_ability(
            self.evolution_engine.state.to_dict()
        )
        
        if suggestion:
            self.ability_system.learn_ability(
                name=suggestion['name'],
                category=suggestion['category'],
                description=suggestion['description'],
                proficiency=suggestion['proficiency']
            )
            
            self._add_chat_message(
                "OctoBuddy",
                f"I learned a new ability: {suggestion['name']}!"
            )
        else:
            self._add_chat_message(
                "OctoBuddy",
                "I'm learning and growing!"
            )
    
    def _show_stats(self):
        """Show detailed stats."""
        stats = f"""
=== Evolution ===
{self.evolution_engine.get_summary()}

=== Personality ===
{self.personality.get_summary()}

=== Abilities ===
{self.ability_system.get_summary()}

=== Memory ===
{self.memory_system.get_summary()}
"""
        self._add_chat_message("System", stats)
    
    def _handle_chat_input(self):
        """Handle chat input from user."""
        text = self.chat_input.text().strip()
        if not text:
            return
        
        self._add_chat_message("You", text)
        self.chat_input.clear()
        
        # Record interaction
        self._on_user_interaction("chat")
        
        # Remember the conversation
        self.memory_system.remember(
            "interaction",
            f"User said: {text}",
            importance=0.6
        )
        
        # Generate response based on personality
        response = self.personality.generate_reaction("chat")
        self._add_chat_message("OctoBuddy", response)
    
    def _add_chat_message(self, sender: str, message: str):
        """Add message to chat display."""
        self.chat_display.append(f"<b>{sender}:</b> {message}")
    
    def closeEvent(self, event):
        """Handle window close."""
        # Save all systems
        self.evolution_engine.save()
        self.mutation_engine.save()
        self.memory_system.end_session()
        self.personality.save()
        self.ability_system.save()
        
        event.accept()


def run_self_evolving_ui():
    """Launch the self-evolving desktop UI."""
    app = QApplication(sys.argv)
    widget = SelfEvolvingOctoBuddyWidget()
    widget.show()
    sys.exit(app.exec_())
