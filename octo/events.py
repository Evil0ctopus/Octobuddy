"""
Event system for OctoBuddy.

Tracks various user and system events that affect mood and behavior:
- User clicks
- Window focus changes
- Typing activity
- Idle time
- Learning moments
"""

import time
from typing import Callable, List, Dict


class EventType:
    """Event type constants."""
    CLICK = "click"
    FOCUS_GAINED = "focus_gained"
    FOCUS_LOST = "focus_lost"
    TYPING_BURST = "typing_burst"
    IDLE_TIMEOUT = "idle_timeout"
    LEARNING_MOMENT = "learning_moment"
    CUSTOM = "custom"


class Event:
    """Represents a single event."""
    
    def __init__(self, event_type, data=None):
        """
        Create an event.
        
        Args:
            event_type: Type of event (from EventType)
            data: Optional event data (dict)
        """
        self.event_type = event_type
        self.data = data or {}
        self.timestamp = time.time()


class EventHandler:
    """
    Manages event listeners and dispatching.
    
    Allows different parts of the system to react to events.
    """
    
    def __init__(self):
        """Initialize event handler."""
        self._listeners: Dict[str, List[Callable]] = {}
    
    def add_listener(self, event_type, callback):
        """
        Add an event listener.
        
        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs (receives Event object)
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
    
    def remove_listener(self, event_type, callback):
        """
        Remove an event listener.
        
        Args:
            event_type: Type of event
            callback: Callback function to remove
        """
        if event_type in self._listeners:
            self._listeners[event_type] = [
                cb for cb in self._listeners[event_type] if cb != callback
            ]
    
    def dispatch(self, event):
        """
        Dispatch an event to all listeners.
        
        Args:
            event: Event object to dispatch
        """
        if event.event_type in self._listeners:
            for callback in self._listeners[event.event_type]:
                callback(event)
    
    def emit(self, event_type, data=None):
        """
        Create and dispatch an event.
        
        Args:
            event_type: Type of event
            data: Optional event data
        """
        event = Event(event_type, data)
        self.dispatch(event)


class IdleTracker:
    """
    Tracks user idle time and triggers idle events.
    """
    
    def __init__(self, event_handler, idle_thresholds=None):
        """
        Initialize idle tracker.
        
        Args:
            event_handler: EventHandler to emit idle events to
            idle_thresholds: List of idle durations (seconds) to trigger events at
        """
        self.event_handler = event_handler
        self.idle_thresholds = idle_thresholds or [30, 60, 120, 300]
        self.last_activity_time = time.time()
        self._triggered_thresholds = set()
    
    def mark_activity(self):
        """Mark that user activity occurred."""
        self.last_activity_time = time.time()
        self._triggered_thresholds.clear()
    
    def update(self):
        """Check idle time and emit events if thresholds crossed."""
        idle_duration = time.time() - self.last_activity_time
        
        for threshold in self.idle_thresholds:
            if idle_duration >= threshold and threshold not in self._triggered_thresholds:
                self._triggered_thresholds.add(threshold)
                self.event_handler.emit(
                    EventType.IDLE_TIMEOUT,
                    {"duration": idle_duration}
                )
    
    def get_idle_duration(self):
        """Get current idle duration in seconds."""
        return time.time() - self.last_activity_time


class TypingDetector:
    """
    Detects typing bursts (rapid consecutive keystrokes).
    """
    
    def __init__(self, event_handler, burst_threshold=5, burst_window=2.0):
        """
        Initialize typing detector.
        
        Args:
            event_handler: EventHandler to emit typing events to
            burst_threshold: Number of keystrokes to count as a burst
            burst_window: Time window (seconds) for burst detection
        """
        self.event_handler = event_handler
        self.burst_threshold = burst_threshold
        self.burst_window = burst_window
        self.keystroke_times = []
    
    def on_keystroke(self):
        """Called when a keystroke is detected."""
        current_time = time.time()
        self.keystroke_times.append(current_time)
        
        # Remove old keystrokes outside the window
        self.keystroke_times = [
            t for t in self.keystroke_times
            if current_time - t <= self.burst_window
        ]
        
        # Check if we have a burst
        if len(self.keystroke_times) >= self.burst_threshold:
            self.event_handler.emit(
                EventType.TYPING_BURST,
                {"keystroke_count": len(self.keystroke_times)}
            )
            # Reset to avoid repeated burst events
            self.keystroke_times.clear()


class FocusTracker:
    """
    Tracks window focus state.
    """
    
    def __init__(self, event_handler):
        """
        Initialize focus tracker.
        
        Args:
            event_handler: EventHandler to emit focus events to
        """
        self.event_handler = event_handler
        self.has_focus = True
    
    def set_focus(self, has_focus):
        """
        Update focus state.
        
        Args:
            has_focus: True if window has focus, False otherwise
        """
        if has_focus != self.has_focus:
            self.has_focus = has_focus
            
            if has_focus:
                self.event_handler.emit(EventType.FOCUS_GAINED)
            else:
                self.event_handler.emit(EventType.FOCUS_LOST)


class EventSystem:
    """
    Complete event management system.
    
    Combines all event tracking components into one unified system.
    """
    
    def __init__(self):
        """Initialize event system."""
        self.event_handler = EventHandler()
        self.idle_tracker = IdleTracker(self.event_handler)
        self.typing_detector = TypingDetector(self.event_handler)
        self.focus_tracker = FocusTracker(self.event_handler)
    
    def update(self):
        """Update event trackers (call every frame)."""
        self.idle_tracker.update()
    
    def on_click(self):
        """Handle click event."""
        self.idle_tracker.mark_activity()
        self.event_handler.emit(EventType.CLICK)
    
    def on_keystroke(self):
        """Handle keystroke event."""
        self.idle_tracker.mark_activity()
        self.typing_detector.on_keystroke()
    
    def on_focus_change(self, has_focus):
        """Handle focus change."""
        self.focus_tracker.set_focus(has_focus)
        if has_focus:
            self.idle_tracker.mark_activity()
    
    def trigger_learning_moment(self, duration=10.0):
        """Trigger a learning moment event."""
        self.idle_tracker.mark_activity()
        self.event_handler.emit(
            EventType.LEARNING_MOMENT,
            {"duration": duration}
        )
    
    def add_listener(self, event_type, callback):
        """Add event listener."""
        self.event_handler.add_listener(event_type, callback)
    
    def remove_listener(self, event_type, callback):
        """Remove event listener."""
        self.event_handler.remove_listener(event_type, callback)
