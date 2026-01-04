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
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QMenu, QAction
)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPixmap, QImage, QPainter, QCursor

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
        
        # Convert to QPixmap and display
        pixmap = QPixmap.fromImage(q_image)
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
        
        menu.addSeparator()
        
        quit_action = QAction("🚪 Quit", self)
        quit_action.triggered.connect(self.close)
        menu.addAction(quit_action)
        
        menu.exec_(event.globalPos())
    
    def feed_octobuddy(self):
        """Feed OctoBuddy (increase happiness, trigger evolution)."""
        self.state["happiness"] = self.state.get("happiness", 5) + 1
        
        # Trigger evolution cycle
        self.state = process_evolution_cycle(self.state, self.config)
        
        # Remember event
        memory.remember_event("fed", {}, self.config)
        
        # Animation reaction
        from octo.animation import apply_event_reaction
        self.anim_state = apply_event_reaction(self.anim_state, "fed", self.state)
    
    def pet_octobuddy(self):
        """Pet OctoBuddy (social interaction)."""
        # Boost empathy and happiness
        ev_vars = dict(self.state.get("evolution_vars", {}))
        ev_vars["empathy"] = ev_vars.get("empathy", 5.0) + 0.5
        self.state["evolution_vars"] = ev_vars
        
        # Remember event
        memory.remember_event("petted", {}, self.config)
        
        # Animation reaction
        from octo.animation import apply_event_reaction
        self.anim_state = apply_event_reaction(self.anim_state, "petted", self.state)
    
    def use_ability(self, ability_name: str):
        """Execute an ability."""
        from octo.abilities import execute_ability
        
        new_state, result = execute_ability(ability_name, self.state, self.config)
        
        if result["success"]:
            self.state = new_state
            print(f"✓ {result['message']}")
        else:
            print(f"✗ {result['message']}")
    
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
