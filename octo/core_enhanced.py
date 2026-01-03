"""
Enhanced Core System for OctoBuddy
Integrates all subsystems: AI brain, observation, expansion, and UI
"""

import random
from pathlib import Path
from .storage import load_state, save_state
from .brain import update_state_from_event, get_mood, get_stage
from .personality import get_phrase_for_event
from .ai_brain import EnhancedBrain
from .observation import ObservationSystem
from .expansion import ExpansionSystem


class EnhancedOctoBuddy:
    """
    Enhanced OctoBuddy with full AI capabilities
    - Advanced brain with memory and learning
    - Observation and interaction systems
    - Self-expansion capabilities
    - Desktop UI integration
    """
    
    def __init__(self, config, enable_observation=False):
        self.config = config
        self.state = load_state()
        
        # Initialize advanced systems
        self.brain = EnhancedBrain()
        self.expansion = ExpansionSystem()
        
        # Initialize observation system with permissions
        self.observation = ObservationSystem(
            self.brain,
            permissions={
                "monitor_windows": enable_observation,
                "detect_activities": enable_observation,
                "track_events": True,
                "learn_from_observation": False  # User must opt-in
            }
        )
        
        # UI reference (set externally)
        self.ui = None
        
        # Start observation if enabled
        if enable_observation:
            self.observation.window_monitor.start_monitoring()
            
    def handle_event(self, event_type, data=None):
        """
        Handle an event (study, achievement, etc.)
        Now with AI brain integration
        """
        # Update state using existing system
        self.state = update_state_from_event(self.state, event_type, data, self.config)
        
        # Get current mood and stage
        mood = get_mood(self.state, self.config)
        stage = get_stage(self.state, self.config)
        
        # Process through AI brain
        self.brain.process_interaction(
            "study_event" if "studied" in event_type else "event",
            f"{event_type}: {data}" if data else event_type
        )
        
        # Check for personality evolution
        if self.brain.personality.evolve():
            phrase = f"I feel different... I think I'm evolving! I'm at evolution stage {self.brain.personality.traits['evolution_stage']} now!"
        else:
            # Get phrase (enhanced with brain context)
            phrase = get_phrase_for_event(event_type, self.state, mood, stage)
            phrase = self.brain.generate_contextual_response(event_type, phrase)
            
        # Check for custom skills that might react to this event
        self._check_custom_reactions(event_type)
        
        # Save state
        save_state(self.state)
        self.brain.save_state()
        
        # Update UI if available
        if self.ui:
            self.ui.update_state(self.state, mood, stage)
            self.ui.set_phrase(phrase)
            
        return {
            "state": self.state,
            "mood": mood,
            "stage": stage,
            "phrase": phrase
        }
        
    def _check_custom_reactions(self, event_type):
        """Check if any custom behaviors should trigger"""
        custom_behaviors = self.brain.memory.knowledge.get("custom_behaviors", [])
        
        for behavior in custom_behaviors:
            if behavior["trigger"].lower() in event_type.lower():
                # Execute the custom behavior
                if self.ui:
                    self.ui.set_phrase(behavior["response"])
                    
    def teach(self, category, content):
        """
        Teach OctoBuddy something new
        Returns a response message
        """
        result = self.observation.teaching_interface.teach_fact(category, content)
        
        # Update personality
        self.brain.personality.update_trait("intelligence", 0.2, f"learned about {category}")
        self.brain.save_state()
        
        if self.ui:
            self.ui.set_phrase(f"Thanks for teaching me about {category}! I'll remember that!")
            
        return result
        
    def add_skill(self, skill_name, skill_code):
        """Add a new skill to OctoBuddy"""
        result = self.expansion.add_skill(skill_name, skill_code)
        
        if result:
            self.brain.memory.learn_skill(
                skill_name,
                f"Custom skill: {skill_name}"
            )
            self.brain.save_state()
            
            if self.ui:
                self.ui.set_phrase(f"I learned a new skill: {skill_name}! I can use it now!")
                
            return {"success": True, "message": f"Skill {skill_name} added successfully"}
        else:
            return {"success": False, "message": "Failed to add skill (validation failed)"}
            
    def execute_skill(self, skill_name, context=None):
        """Execute a custom skill"""
        # Prepare context
        if context is None:
            context = {}
            
        context.update({
            "state": self.state,
            "mood": get_mood(self.state, self.config),
            "stage": get_stage(self.state, self.config),
            "user_name": self.state.get("name", "friend")
        })
        
        # Execute skill
        result = self.expansion.skills.execute_skill(skill_name, context)
        
        if result.get("success"):
            # Update UI with result
            if self.ui and "message" in result:
                self.ui.set_phrase(result["message"])
                
        return result
        
    def recall_knowledge(self, query):
        """Recall knowledge related to a query"""
        results = self.brain.recall_related(query)
        return results
        
    def get_status(self):
        """Get comprehensive status information"""
        mood = get_mood(self.state, self.config)
        stage = get_stage(self.state, self.config)
        dominant_traits = self.brain.personality.get_dominant_traits(3)
        
        return {
            "xp": self.state.get("xp", 0),
            "level": self.state.get("level", 1),
            "mood": mood,
            "stage": stage,
            "personality": {
                "evolution_stage": self.brain.personality.traits["evolution_stage"],
                "dominant_traits": dominant_traits
            },
            "capabilities": self.expansion.get_all_capabilities(),
            "memory_stats": {
                "short_term_memories": len(self.brain.memory.short_term),
                "long_term_memories": len(self.brain.memory.long_term["memories"]),
                "important_events": len(self.brain.memory.long_term["important_events"]),
                "known_facts": sum(len(facts) for facts in self.brain.memory.knowledge["facts"].values()),
                "learned_skills": len(self.brain.memory.knowledge["learned_skills"])
            }
        }
        
    def enable_observation(self):
        """Enable observation/monitoring (requires user permission)"""
        self.observation.enable_monitoring()
        
        if self.ui:
            self.ui.set_phrase("I'm now observing your activity to help you better! You can disable this anytime.")
            
    def disable_observation(self):
        """Disable observation/monitoring"""
        self.observation.disable_monitoring()
        
        if self.ui:
            self.ui.set_phrase("Observation disabled. I'll just hang out here!")
            
    def get_context(self):
        """Get current context (what user is doing)"""
        return self.observation.get_current_context()
        
    def idle_update(self):
        """
        Called periodically when idle
        OctoBuddy can initiate interactions based on observations
        """
        # Random thoughts
        if random.random() < 0.1:  # 10% chance
            thoughts = [
                "I wonder what you're working on...",
                "Do you need any help?",
                "I'm here if you need me!",
                "Learning is fun! *wiggles*",
                "I've been thinking about what you taught me...",
            ]
            
            thought = random.choice(thoughts)
            
            if self.ui:
                self.ui.set_phrase(thought)
                
        # Check context and maybe comment
        if self.observation.permissions["monitor_windows"]:
            context = self.observation.get_current_context()
            current_window = context.get("current_window")
            
            if current_window and random.random() < 0.05:  # 5% chance
                # Make a relevant comment
                title = current_window.get("title", "").lower()
                
                if "python" in title:
                    comment = "Ooh, Python! That's my favorite!"
                elif "code" in title or "visual studio" in title:
                    comment = "Coding time! You're doing great!"
                elif "github" in title:
                    comment = "GitHub! I love seeing code evolve!"
                elif "stack overflow" in title:
                    comment = "Stack Overflow saves the day again!"
                else:
                    comment = "Interesting work you're doing!"
                    
                if self.ui:
                    self.ui.set_phrase(comment)
                    
    def shutdown(self):
        """Graceful shutdown"""
        # Save everything
        save_state(self.state)
        self.brain.save_state()
        
        # Stop observation
        self.observation.disable_monitoring()
        
        if self.ui:
            self.ui.set_phrase("Goodbye! See you next time! 🐙")
