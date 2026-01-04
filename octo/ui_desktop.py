"""
PyQt5-based desktop UI for OctoBuddy.

Creates a transparent, frameless window that displays OctoBuddy as a
desktop creature with real-time procedural animation.
"""

import sys
import math
import time
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTimer, Qt, QPoint, QRect
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QCursor

from .physics import Vector2D
from .tentacles import TentacleSystem
from .animation_engine import AnimationState
from .events import EventSystem, EventType


class OctoBuddyWidget(QWidget):
    """
    Main OctoBuddy desktop widget.
    
    Features:
    - Transparent, frameless window
    - Real-time procedural animation
    - Cursor tracking
    - Event-driven mood changes
    """
    
    def __init__(self, width=400, height=400):
        """
        Initialize OctoBuddy widget.
        
        Args:
            width: Window width
            height: Window height
        """
        super().__init__()
        
        # Window setup
        self.setWindowTitle("OctoBuddy")
        self.resize(width, height)
        
        # Make window frameless and transparent
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Make window draggable
        self._dragging = False
        self._drag_position = QPoint()
        
        # Animation components
        center_x = width // 2
        center_y = height // 2
        self.center_position = Vector2D(center_x, center_y)
        
        self.tentacle_system = TentacleSystem(self.center_position, num_tentacles=6)
        self.animation_state = AnimationState()
        self.event_system = EventSystem()
        
        # Eye parameters
        self.eye_offset_left = Vector2D(-25, -20)
        self.eye_offset_right = Vector2D(25, -20)
        self.eye_size = 15
        self.pupil_size = 8
        self.eye_look_target = Vector2D(0, 0)  # Where eyes are looking
        self.eye_smoothing = 0.1
        
        # Head tilt
        self.head_tilt = 0.0
        self.target_head_tilt = 0.0
        
        # Connect events to animation state
        self._setup_event_listeners()
        
        # Animation loop timer (60 FPS target)
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_animation)
        self.fps = 60
        self.timer.start(1000 // self.fps)
        
        # Performance tracking
        self.last_frame_time = time.time()
        self.frame_count = 0
        self.fps_display = 60.0
        
        # Cursor tracking
        self.cursor_tracking_enabled = True
        self.cursor_position = Vector2D(0, 0)
    
    def _setup_event_listeners(self):
        """Setup event system listeners."""
        # Connect events to animation state methods
        self.event_system.add_listener(
            EventType.CLICK,
            lambda e: self.animation_state.on_click()
        )
        self.event_system.add_listener(
            EventType.FOCUS_GAINED,
            lambda e: self.animation_state.on_focus_gained()
        )
        self.event_system.add_listener(
            EventType.FOCUS_LOST,
            lambda e: self.animation_state.on_focus_lost()
        )
        self.event_system.add_listener(
            EventType.TYPING_BURST,
            lambda e: self.animation_state.on_typing_burst()
        )
        self.event_system.add_listener(
            EventType.IDLE_TIMEOUT,
            lambda e: self.animation_state.on_idle_timeout(e.data.get("duration", 0))
        )
        self.event_system.add_listener(
            EventType.LEARNING_MOMENT,
            lambda e: self.animation_state.on_learning_moment(e.data.get("duration", 10))
        )
    
    def _update_animation(self):
        """Main animation update loop (called every frame)."""
        # Calculate delta time
        current_time = time.time()
        dt = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Update FPS counter
        self.frame_count += 1
        if self.frame_count % 60 == 0:
            self.fps_display = 1.0 / dt if dt > 0 else 60.0
        
        # Update event system
        self.event_system.update()
        
        # Update animation state
        self.animation_state.update(dt)
        
        # Apply occasional random mood shifts for organic feel
        if self.frame_count % 300 == 0:  # Every ~5 seconds at 60fps
            self.animation_state.apply_random_mood_shift(0.05)
        
        # Update tentacle system with current mood
        self.tentacle_system.update_mood(
            energy=self.animation_state.energy,
            curiosity=self.animation_state.curiosity,
            happiness=self.animation_state.happiness,
            calmness=self.animation_state.calmness
        )
        
        # Get cursor position for tracking
        if self.cursor_tracking_enabled:
            global_cursor = QCursor.pos()
            widget_cursor = self.mapFromGlobal(global_cursor)
            self.cursor_position = Vector2D(widget_cursor.x(), widget_cursor.y())
            
            # Smooth eye tracking
            target = self.cursor_position - self.center_position
            self.eye_look_target = Vector2D(
                self.eye_look_target.x + (target.x - self.eye_look_target.x) * self.eye_smoothing,
                self.eye_look_target.y + (target.y - self.eye_look_target.y) * self.eye_smoothing
            )
            
            # Calculate head tilt based on cursor position
            dx = target.x
            max_tilt = 0.2  # radians (~11 degrees)
            self.target_head_tilt = max(-max_tilt, min(max_tilt, dx / 200.0))
            self.head_tilt += (self.target_head_tilt - self.head_tilt) * 0.1
            
            # Update tentacles with cursor attraction
            cursor_attraction = self.animation_state.curiosity * 0.8
            self.tentacle_system.update(
                dt=1.0,
                cursor_pos=self.cursor_position,
                cursor_attraction=cursor_attraction
            )
        else:
            self.tentacle_system.update(dt=1.0)
        
        # Trigger repaint
        self.update()
    
    def paintEvent(self, event):
        """Paint OctoBuddy on the widget."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw tentacles
        self._draw_tentacles(painter)
        
        # Draw body (circle)
        self._draw_body(painter)
        
        # Draw eyes
        self._draw_eyes(painter)
        
        # Draw mood indicator (optional debug)
        if hasattr(self, '_show_debug') and self._show_debug:
            self._draw_debug_info(painter)
    
    def _draw_tentacles(self, painter):
        """Draw all tentacles."""
        # Tentacle color based on mood
        energy = self.animation_state.energy
        happiness = self.animation_state.happiness
        
        # Color transitions: low energy = blue, high energy = orange/yellow
        r = int(100 + happiness * 155)
        g = int(150 + energy * 105)
        b = int(200 - energy * 100)
        
        pen = QPen(QColor(r, g, b), 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        
        for tentacle in self.tentacle_system.tentacles:
            positions = tentacle.get_segment_positions()
            
            # Draw tentacle as smooth curve
            path = QPainterPath()
            if positions:
                path.moveTo(positions[0].x, positions[0].y)
                for pos in positions[1:]:
                    path.lineTo(pos.x, pos.y)
                painter.drawPath(path)
    
    def _draw_body(self, painter):
        """Draw OctoBuddy's main body."""
        # Body color based on mood
        happiness = self.animation_state.happiness
        energy = self.animation_state.energy
        
        r = int(150 + happiness * 105)
        g = int(120 + energy * 135)
        b = int(180 + (1.0 - energy) * 75)
        
        brush = QBrush(QColor(r, g, b))
        painter.setBrush(brush)
        painter.setPen(QPen(QColor(80, 80, 80), 2))
        
        # Body with slight tilt based on head_tilt
        body_radius = 40
        center_x = self.center_position.x + math.sin(self.head_tilt) * 5
        center_y = self.center_position.y
        
        painter.drawEllipse(
            int(center_x - body_radius),
            int(center_y - body_radius),
            body_radius * 2,
            body_radius * 2
        )
    
    def _draw_eyes(self, painter):
        """Draw eyes with cursor tracking."""
        # Eye white
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(QPen(QColor(80, 80, 80), 2))
        
        # Calculate eye positions with head tilt
        tilt_offset_x = math.sin(self.head_tilt) * 5
        tilt_offset_y = -abs(math.sin(self.head_tilt) * 3)
        
        left_eye = Vector2D(
            self.center_position.x + self.eye_offset_left.x + tilt_offset_x,
            self.center_position.y + self.eye_offset_left.y + tilt_offset_y
        )
        right_eye = Vector2D(
            self.center_position.x + self.eye_offset_right.x + tilt_offset_x,
            self.center_position.y + self.eye_offset_right.y + tilt_offset_y
        )
        
        # Draw eye whites
        painter.drawEllipse(
            int(left_eye.x - self.eye_size),
            int(left_eye.y - self.eye_size),
            self.eye_size * 2,
            self.eye_size * 2
        )
        painter.drawEllipse(
            int(right_eye.x - self.eye_size),
            int(right_eye.y - self.eye_size),
            self.eye_size * 2,
            self.eye_size * 2
        )
        
        # Draw pupils (track cursor)
        painter.setBrush(QBrush(QColor(20, 20, 20)))
        painter.setPen(Qt.NoPen)
        
        # Calculate pupil offset based on look target
        max_offset = self.eye_size - self.pupil_size
        look_distance = self.eye_look_target.length()
        if look_distance > 0:
            look_dir = self.eye_look_target.normalize()
            pupil_offset = look_dir * min(max_offset, look_distance * 0.05)
        else:
            pupil_offset = Vector2D(0, 0)
        
        # Draw pupils
        painter.drawEllipse(
            int(left_eye.x + pupil_offset.x - self.pupil_size),
            int(left_eye.y + pupil_offset.y - self.pupil_size),
            self.pupil_size * 2,
            self.pupil_size * 2
        )
        painter.drawEllipse(
            int(right_eye.x + pupil_offset.x - self.pupil_size),
            int(right_eye.y + pupil_offset.y - self.pupil_size),
            self.pupil_size * 2,
            self.pupil_size * 2
        )
    
    def _draw_debug_info(self, painter):
        """Draw debug information."""
        painter.setPen(QColor(255, 255, 255))
        
        debug_text = [
            f"FPS: {self.fps_display:.1f}",
            f"Energy: {self.animation_state.energy:.2f}",
            f"Curiosity: {self.animation_state.curiosity:.2f}",
            f"Happiness: {self.animation_state.happiness:.2f}",
            f"Calmness: {self.animation_state.calmness:.2f}",
            f"Mood: {self.animation_state.get_mood_string()}",
        ]
        
        y = 20
        for line in debug_text:
            painter.drawText(10, y, line)
            y += 20
    
    # Event handlers
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging and clicking."""
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            
            # Emit click event
            self.event_system.on_click()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if self._dragging:
            self.move(event.globalPos() - self._drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.LeftButton:
            self._dragging = False
    
    def focusInEvent(self, event):
        """Handle focus gained."""
        self.event_system.on_focus_change(True)
        super().focusInEvent(event)
    
    def focusOutEvent(self, event):
        """Handle focus lost."""
        self.event_system.on_focus_change(False)
        super().focusOutEvent(event)
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        # Track typing
        self.event_system.on_keystroke()
        
        # Keyboard shortcuts for testing
        if event.key() == Qt.Key_Q:
            self.close()
        elif event.key() == Qt.Key_D:
            # Toggle debug display
            self._show_debug = not getattr(self, '_show_debug', False)
        elif event.key() == Qt.Key_L:
            # Trigger learning moment
            self.event_system.trigger_learning_moment(10.0)
        elif event.key() == Qt.Key_E:
            # High energy
            self.animation_state.set_mood_targets(energy=1.0, happiness=0.8)
        elif event.key() == Qt.Key_S:
            # Sleepy
            self.animation_state.set_mood_targets(energy=0.1, calmness=0.9)
        elif event.key() == Qt.Key_C:
            # Curious
            self.animation_state.set_mood_targets(curiosity=1.0, energy=0.7)
        elif event.key() == Qt.Key_N:
            # Nervous
            self.animation_state.set_mood_targets(calmness=0.1, energy=0.8)
        
        super().keyPressEvent(event)


def run_desktop_ui():
    """Launch the desktop UI."""
    app = QApplication(sys.argv)
    widget = OctoBuddyWidget()
    widget.show()
    sys.exit(app.exec_())
