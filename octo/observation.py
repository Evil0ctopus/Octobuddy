"""
Safe observation and interaction system for OctoBuddy
Monitors user activity with permission-based controls
"""

import os
import time
import psutil
import threading
from pathlib import Path
from datetime import datetime
from typing import Callable, Optional


class WindowMonitor:
    """Monitor active windows and applications (platform-specific)"""
    
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.current_window = None
        self.window_history = []
        self.callbacks = []
        
        # Import platform-specific modules
        self.platform = os.name
        if self.platform == 'nt':  # Windows
            try:
                import win32gui
                import win32process
                self.win32gui = win32gui
                self.win32process = win32process
                self.platform_available = True
            except ImportError:
                self.platform_available = False
        else:
            self.platform_available = False
            
    def get_active_window(self):
        """Get the currently active window title and process"""
        if not self.enabled or not self.platform_available:
            return None
            
        try:
            if self.platform == 'nt':  # Windows
                window = self.win32gui.GetForegroundWindow()
                title = self.win32gui.GetWindowText(window)
                _, pid = self.win32process.GetWindowThreadProcessId(window)
                
                try:
                    process = psutil.Process(pid)
                    process_name = process.name()
                except:
                    process_name = "Unknown"
                    
                return {
                    "title": title,
                    "process": process_name,
                    "pid": pid,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception:
            return None
            
    def start_monitoring(self, interval=5):
        """Start monitoring in background thread"""
        if not self.enabled or not self.platform_available:
            return
            
        def monitor_loop():
            while self.enabled:
                window_info = self.get_active_window()
                
                if window_info and window_info != self.current_window:
                    self.current_window = window_info
                    self.window_history.append(window_info)
                    
                    # Keep history limited
                    if len(self.window_history) > 100:
                        self.window_history = self.window_history[-100:]
                        
                    # Trigger callbacks
                    for callback in self.callbacks:
                        try:
                            callback(window_info)
                        except:
                            pass
                            
                time.sleep(interval)
                
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self.enabled = False
        
    def add_callback(self, callback: Callable):
        """Add a callback for window changes"""
        self.callbacks.append(callback)
        
    def get_recent_windows(self, limit=10):
        """Get recently active windows"""
        return self.window_history[-limit:]


class ActivityDetector:
    """Detect user activities and events"""
    
    def __init__(self):
        self.detected_activities = []
        self.activity_patterns = {
            # Map process names to activities
            "python.exe": "coding_python",
            "pycharm64.exe": "coding_python",
            "code.exe": "coding",
            "devenv.exe": "coding",
            "chrome.exe": "browsing",
            "firefox.exe": "browsing",
            "msedge.exe": "browsing",
            "teams.exe": "meeting",
            "slack.exe": "chatting",
            "discord.exe": "chatting",
        }
        
        # Keyword detection for window titles
        self.keyword_patterns = {
            "python": "coding_python",
            "visual studio": "coding",
            "github": "coding",
            "stack overflow": "problem_solving",
            "documentation": "learning",
            "tutorial": "learning",
            "tryhackme": "cybersecurity_practice",
            "hackthebox": "cybersecurity_practice",
        }
        
    def detect_activity(self, window_info):
        """Detect activity type from window information"""
        if not window_info:
            return None
            
        process = window_info.get("process", "").lower()
        title = window_info.get("title", "").lower()
        
        # Check process name patterns
        for pattern, activity in self.activity_patterns.items():
            if pattern in process:
                return activity
                
        # Check window title patterns
        for keyword, activity in self.keyword_patterns.items():
            if keyword in title:
                return activity
                
        return "general_work"
        
    def log_activity(self, activity_type, details):
        """Log detected activity"""
        activity = {
            "type": activity_type,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        self.detected_activities.append(activity)
        
        # Keep limited history
        if len(self.detected_activities) > 200:
            self.detected_activities = self.detected_activities[-200:]
            
        return activity


class EventSystem:
    """Event system for tracking user actions and tasks"""
    
    def __init__(self):
        self.events = []
        self.event_handlers = {}
        
    def register_handler(self, event_type, handler: Callable):
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        
    def trigger_event(self, event_type, data=None):
        """Trigger an event"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        self.events.append(event)
        
        # Call handlers
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in event handler: {e}")
                
        return event
        
    def get_recent_events(self, event_type=None, limit=20):
        """Get recent events"""
        events = self.events
        
        if event_type:
            events = [e for e in events if e["type"] == event_type]
            
        return events[-limit:]


class TeachingInterface:
    """Interface for users to teach OctoBuddy new things"""
    
    def __init__(self, brain):
        self.brain = brain
        self.teaching_sessions = []
        
    def teach_fact(self, category, fact):
        """Teach OctoBuddy a new fact"""
        self.brain.learn_from_user(category, fact)
        
        session = {
            "type": "fact",
            "category": category,
            "content": fact,
            "timestamp": datetime.now().isoformat()
        }
        
        self.teaching_sessions.append(session)
        
        return f"I learned about {category}: {fact}"
        
    def teach_skill(self, skill_name, description):
        """Teach OctoBuddy a new skill"""
        self.brain.memory.learn_skill(skill_name, description)
        
        session = {
            "type": "skill",
            "skill_name": skill_name,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        
        self.teaching_sessions.append(session)
        
        return f"I learned a new skill: {skill_name}!"
        
    def teach_behavior(self, trigger, response):
        """Teach OctoBuddy a new behavior pattern"""
        # Store custom behavior
        behavior = {
            "trigger": trigger,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to knowledge base
        if "custom_behaviors" not in self.brain.memory.knowledge:
            self.brain.memory.knowledge["custom_behaviors"] = []
            
        self.brain.memory.knowledge["custom_behaviors"].append(behavior)
        self.brain.memory.save()
        
        session = {
            "type": "behavior",
            "trigger": trigger,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
        self.teaching_sessions.append(session)
        
        return f"I'll remember to {response} when {trigger}!"
        
    def get_teaching_history(self, limit=10):
        """Get recent teaching sessions"""
        return self.teaching_sessions[-limit:]


class ObservationSystem:
    """Complete observation system with permissions"""
    
    def __init__(self, brain, permissions=None):
        self.brain = brain
        
        # Default permissions (all opt-in)
        self.permissions = permissions or {
            "monitor_windows": False,
            "detect_activities": False,
            "track_events": True,
            "learn_from_observation": False
        }
        
        # Initialize components
        self.window_monitor = WindowMonitor(
            enabled=self.permissions["monitor_windows"]
        )
        self.activity_detector = ActivityDetector()
        self.event_system = EventSystem()
        self.teaching_interface = TeachingInterface(brain)
        
        # Set up event handlers
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Set up event handlers"""
        def on_window_change(window_info):
            if self.permissions["detect_activities"]:
                activity = self.activity_detector.detect_activity(window_info)
                if activity:
                    self.activity_detector.log_activity(activity, window_info)
                    
                    # Learn from observation if enabled
                    if self.permissions["learn_from_observation"]:
                        self.brain.process_interaction("observation", 
                                                     f"User is {activity}")
                                                     
        self.window_monitor.add_callback(on_window_change)
        
    def enable_monitoring(self):
        """Enable window monitoring"""
        self.permissions["monitor_windows"] = True
        self.window_monitor.enabled = True
        self.window_monitor.start_monitoring()
        
    def disable_monitoring(self):
        """Disable window monitoring"""
        self.permissions["monitor_windows"] = False
        self.window_monitor.stop_monitoring()
        
    def get_current_context(self):
        """Get current user context"""
        context = {
            "current_window": self.window_monitor.current_window,
            "recent_activities": self.activity_detector.detected_activities[-10:],
            "recent_events": self.event_system.get_recent_events(limit=10)
        }
        return context
