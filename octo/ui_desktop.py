"""
Desktop UI for OctoBuddy - Always-on-top transparent window with animations
Supports sprite rendering, dragging, and interactive features for Windows
"""

import sys
import random
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QWidget, 
                              QVBoxLayout, QTextEdit, QLineEdit, QPushButton)
from PyQt6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QRect
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen


class OctoBuddyWindow(QMainWindow):
    """Main desktop window for OctoBuddy - draggable, always-on-top, transparent"""
    
    def __init__(self, state, config, mood, stage):
        super().__init__()
        
        self.state = state
        self.config = config
        self.mood = mood
        self.stage = stage
        self.current_phrase = "Hello! I'm OctoBuddy!"
        
        # Animation state
        self.animation_frame = 0
        self.animation_frames = self._load_animation_frames()
        
        # For dragging
        self.drag_position = None
        
        self._init_ui()
        self._setup_animations()
        
    def _init_ui(self):
        """Initialize the UI window"""
        # Window properties
        self.setWindowTitle("OctoBuddy")
        self.setFixedSize(300, 400)
        
        # Always on top, frameless, transparent background
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Main widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        self.central_widget.setLayout(layout)
        
        # Character display area
        self.character_label = QLabel()
        self.character_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.character_label.setStyleSheet("""
            QLabel {
                background-color: rgba(30, 30, 30, 220);
                border-radius: 15px;
                padding: 20px;
                color: #00ffff;
                font-family: 'Courier New', monospace;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.character_label)
        
        # Info display
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("""
            QLabel {
                background-color: rgba(20, 20, 20, 200);
                border-radius: 10px;
                padding: 10px;
                color: #ffff00;
                font-family: Arial;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.info_label)
        
        # Phrase display
        self.phrase_label = QLabel()
        self.phrase_label.setWordWrap(True)
        self.phrase_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.phrase_label.setStyleSheet("""
            QLabel {
                background-color: rgba(40, 40, 40, 200);
                border-radius: 10px;
                padding: 15px;
                color: #ffffff;
                font-family: Arial;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.phrase_label)
        
        # Update display
        self.update_display()
        
    def _load_animation_frames(self):
        """Load animation frames based on mood"""
        # ASCII art frames for different moods
        frames = {
            "sleepy": [
                "    ( -.- ) zZ\n   __|__",
                "    ( -.- ) ..\n   __|__"
            ],
            "curious": [
                "    ( o.O )\n   __|__",
                "    ( O.o )\n   __|__"
            ],
            "hyper": [
                "    ( ^o^ )/\n   __|__",
                "   \\( ^o^ )\n   __|__"
            ],
            "goofy": [
                "    ( @v@ )\n   __|__",
                "    ( @.@ )\n   __|__"
            ],
            "chaotic": [
                "    ( >:D )\n   __|__",
                "    ( >XD )\n   __|__"
            ],
            "proud": [
                "    ( ^‿^ )\n   __|__",
                "    ( ^▿^ )\n   __|__"
            ],
            "confused": [
                "    ( ?_? )\n   __|__",
                "    ( ?.? )\n   __|__"
            ],
            "excited": [
                "    ( ^O^ )!!\n   __|__",
                "    ( ^0^ )!!\n   __|__"
            ]
        }
        
        return frames.get(self.mood, frames["hyper"])
        
    def _setup_animations(self):
        """Setup animation timer"""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate)
        self.animation_timer.start(500)  # Update every 500ms
        
        # Idle behavior timer (random thoughts/movements)
        self.idle_timer = QTimer()
        self.idle_timer.timeout.connect(self._idle_behavior)
        self.idle_timer.start(10000)  # Check every 10 seconds
        
    def _animate(self):
        """Animate the character"""
        self.animation_frame = (self.animation_frame + 1) % len(self.animation_frames)
        self.update_display()
        
    def _idle_behavior(self):
        """Random idle behaviors"""
        if random.random() < 0.3:  # 30% chance
            idle_phrases = [
                "I wonder what you're working on...",
                "Hmm... interesting patterns in your workflow!",
                "*wiggles tentacles*",
                "I'm learning so much just by watching!",
                "Do you need help with anything?",
                "I could go for a digital snack right about now...",
            ]
            self.set_phrase(random.choice(idle_phrases))
            
            # Occasionally bounce or move slightly
            if random.random() < 0.2:
                self._bounce_animation()
                
    def _bounce_animation(self):
        """Create a small bounce animation"""
        original_pos = self.pos()
        
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(300)
        anim.setStartValue(QRect(original_pos.x(), original_pos.y(), 
                                 self.width(), self.height()))
        anim.setEndValue(QRect(original_pos.x(), original_pos.y() - 20, 
                               self.width(), self.height()))
        anim.start()
        
        # Return to original position
        QTimer.singleShot(300, lambda: self.move(original_pos))
        
    def update_display(self):
        """Update all display elements"""
        # Character animation
        frame = self.animation_frames[self.animation_frame]
        self.character_label.setText(frame)
        
        # Info display
        xp = self.state.get("xp", 0)
        level = self.state.get("level", 1)
        info_text = f"Stage: {self.stage}\nMood: {self.mood}\nLevel: {level}\nXP: {xp}"
        self.info_label.setText(info_text)
        
        # Phrase display
        self.phrase_label.setText(self.current_phrase)
        
    def set_phrase(self, phrase):
        """Set the phrase OctoBuddy says"""
        self.current_phrase = phrase
        self.update_display()
        
    def update_state(self, state, mood, stage):
        """Update OctoBuddy's state"""
        self.state = state
        self.mood = mood
        self.stage = stage
        self.animation_frames = self._load_animation_frames()
        self.update_display()
        
    # Mouse event handling for dragging
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Get global position (compatible with PyQt6)
            try:
                global_pos = event.globalPosition().toPoint()
            except AttributeError:
                # Fallback for older PyQt6 versions
                global_pos = event.globalPos()
            self.drag_position = global_pos - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            try:
                global_pos = event.globalPosition().toPoint()
            except AttributeError:
                global_pos = event.globalPos()
            self.move(global_pos - self.drag_position)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self.drag_position = None
        
    def mouseDoubleClickEvent(self, event):
        """Handle double-click to show interaction window"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.show_interaction_window()
            
    def show_interaction_window(self):
        """Show the interaction/teaching window"""
        self.interaction_window = InteractionWindow(self)
        self.interaction_window.show()


class InteractionWindow(QWidget):
    """Window for interacting with and teaching OctoBuddy"""
    
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.buddy = getattr(parent_window, 'buddy', None)
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the interaction UI"""
        self.setWindowTitle("Chat with OctoBuddy")
        self.setFixedSize(400, 500)
        
        # Keep on top
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Chat history
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Courier New';
                font-size: 12px;
                border: 2px solid #00ffff;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.chat_display)
        
        # Input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a command or message...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #2e2e2e;
                color: #ffffff;
                font-family: Arial;
                font-size: 12px;
                border: 2px solid #00ff00;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        self.input_field.returnPressed.connect(self._send_message)
        layout.addWidget(self.input_field)
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #00ff00;
                color: #000000;
                font-weight: bold;
                font-size: 12px;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #00cc00;
            }
        """)
        self.send_button.clicked.connect(self._send_message)
        layout.addWidget(self.send_button)
        
        # Add welcome message
        self._add_message("OctoBuddy", "Hi! You can chat with me, teach me new things, or give me commands!")
        self._add_message("OctoBuddy", "Try: 'studied_python', 'teach me about...', 'what do you know?'")
        
    def _add_message(self, sender, message):
        """Add a message to the chat display"""
        self.chat_display.append(f"<b>{sender}:</b> {message}")
        
    def _send_message(self):
        """Handle sending a message"""
        message = self.input_field.text().strip()
        if not message:
            return
            
        self._add_message("You", message)
        self.input_field.clear()
        
        # Process the message
        response = self._process_input(message)
        self._add_message("OctoBuddy", response)
        
    def _process_input(self, message):
        """Process user input and generate response"""
        message_lower = message.lower()
        
        # If we have the enhanced buddy, use it
        if self.buddy:
            # Check for commands
            if message_lower.startswith("teach "):
                # Extract what to teach
                parts = message[6:].split(":", 1)
                if len(parts) == 2:
                    category = parts[0].strip()
                    content = parts[1].strip()
                    self.buddy.teach(category, content)
                    return f"Got it! I learned about {category}!"
                else:
                    return "To teach me, use: teach <category>: <fact>"
                    
            elif message_lower.startswith("recall "):
                # Recall knowledge
                query = message[7:].strip()
                results = self.buddy.recall_knowledge(query)
                
                if results["knowledge"] or results["memories"]:
                    response = f"Here's what I know about '{query}':\n"
                    for item in results["knowledge"][:3]:
                        if item["type"] == "fact":
                            response += f"- {item['content']['fact']}\n"
                    return response if len(response) > 50 else "I don't have much information about that yet."
                else:
                    return "I don't know much about that yet. Teach me!"
                    
            elif message_lower == "status":
                status = self.buddy.get_status()
                return f"Level {status['level']}, {status['xp']} XP\n" \
                       f"Mood: {status['mood']}, Stage: {status['stage']}\n" \
                       f"Evolution: Stage {status['personality']['evolution_stage']}"
                       
            elif message_lower == "enable observation":
                self.buddy.enable_observation()
                return "Observation enabled! I'll pay attention to what you're doing to help better."
                
            elif message_lower == "disable observation":
                self.buddy.disable_observation()
                return "Observation disabled!"
                
            elif message_lower in ["studied_python", "python", "study python"]:
                result = self.buddy.handle_event("studied_python")
                return result["phrase"]
                
            elif "security" in message_lower:
                result = self.buddy.handle_event("studied_security_plus")
                return result["phrase"]
                
            elif message_lower == "finished_class":
                result = self.buddy.handle_event("finished_class")
                return result["phrase"]
                
            elif message_lower.startswith("skill "):
                # Execute a skill
                skill_name = message[6:].strip()
                result = self.buddy.execute_skill(skill_name)
                return result.get("message", "Skill executed!")
                
            elif "help" in message_lower:
                return """Commands I understand:
- teach <category>: <fact> - Teach me something
- recall <query> - Ask what I know
- status - See my current status
- studied_python - Log a Python study session
- finished_class - Log finishing a class
- enable/disable observation - Control monitoring
- skill <name> - Execute a custom skill"""
        
        # Fallback responses
        if message_lower in ["studied_python", "python", "study python"]:
            return "Awesome! Python is so cool! I'm learning too! 🐙"
        elif "security" in message_lower:
            return "Security+ vibes! Let's become cyber-experts together!"
        elif message_lower == "finished_class":
            return "YESSS! Another class conquered! We're unstoppable!"
        elif "teach" in message_lower:
            return "I'm listening! Tell me what you want me to learn!"
        elif "what do you know" in message_lower or "knowledge" in message_lower:
            return "I know about Python, cybersecurity, and how awesome you are! I'm always learning more!"
        elif "help" in message_lower:
            return "You can chat with me, tell me about your studies, or teach me new facts!"
        else:
            responses = [
                "Interesting! Tell me more!",
                "I'm taking notes on that! 📝",
                "Fascinating! My circuits are tingling!",
                "I'll remember that!",
                "Thanks for sharing! I'm learning so much from you!",
            ]
            return random.choice(responses)


def run_desktop_ui(state, config, mood, stage, phrase="Hello! I'm OctoBuddy!"):
    """Run the desktop UI application"""
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = OctoBuddyWindow(state, config, mood, stage)
    window.set_phrase(phrase)
    window.show()
    
    # Position in bottom-right corner by default
    screen = app.primaryScreen().geometry()
    window.move(screen.width() - window.width() - 50, 
                screen.height() - window.height() - 100)
    
    return app.exec()
