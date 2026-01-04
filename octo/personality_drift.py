"""
Personality Drift System for OctoBuddy.

Manages evolving personality traits that naturally drift over time.
Traits influence dialogue, reactions, animation, and appearance.

Personality Traits:
- humor: Tendency to make jokes and be playful
- curiosity: Drive to ask questions and explore
- boldness: Willingness to try new things and take risks
- shyness: Social hesitation and introspection
- chaos: Embrace of randomness and unpredictability
- calmness: Emotional stability and patience
- empathy: Emotional awareness and responsiveness

Traits drift naturally and are influenced by:
- User interactions
- Evolution state
- Learning events
- Mutations
"""

import random
import json
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


@dataclass
class PersonalityTraits:
    """
    OctoBuddy's personality trait values.
    
    All traits start at 0.5 and can drift between 0-1.
    No strict caps, but values naturally stabilize.
    """
    humor: float = 0.5          # Playfulness and wit
    curiosity: float = 0.5      # Question-asking tendency
    boldness: float = 0.5       # Risk-taking and assertiveness
    shyness: float = 0.5        # Social hesitation
    chaos: float = 0.5          # Randomness embrace
    calmness: float = 0.5       # Emotional stability
    empathy: float = 0.5        # Emotional awareness
    
    # Meta tracking
    total_drift_events: int = 0
    last_update: float = 0.0
    
    def __post_init__(self):
        """Set last_update if not provided."""
        if self.last_update == 0.0:
            self.last_update = time.time()
    
    def get_dominant_trait(self) -> str:
        """Get the currently dominant personality trait."""
        traits = {
            'humor': self.humor,
            'curiosity': self.curiosity,
            'boldness': self.boldness,
            'shyness': self.shyness,
            'chaos': self.chaos,
            'calmness': self.calmness,
            'empathy': self.empathy
        }
        return max(traits.items(), key=lambda x: x[1])[0]
    
    def get_personality_archetype(self) -> str:
        """Get descriptive personality archetype."""
        # Determine archetype based on dominant traits
        if self.humor > 0.7 and self.chaos > 0.6:
            return "Chaotic Jester"
        elif self.curiosity > 0.7 and self.boldness > 0.6:
            return "Bold Explorer"
        elif self.empathy > 0.7 and self.calmness > 0.6:
            return "Wise Companion"
        elif self.shyness > 0.6 and self.curiosity > 0.6:
            return "Quiet Observer"
        elif self.boldness > 0.7 and self.humor > 0.6:
            return "Confident Entertainer"
        elif self.calmness > 0.7 and self.empathy > 0.6:
            return "Gentle Guide"
        elif self.chaos > 0.7:
            return "Chaotic Wildcard"
        else:
            return "Balanced Soul"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary."""
        return cls(**data)


class PersonalityDrift:
    """
    Manages natural personality drift and evolution.
    
    Personality changes gradually based on experiences and evolution.
    """
    
    def __init__(self, traits: Optional[PersonalityTraits] = None,
                 save_path: str = "personality_state.json"):
        """
        Initialize personality drift system.
        
        Args:
            traits: Existing PersonalityTraits (creates new if None)
            save_path: Path to save personality state
        """
        self.traits = traits if traits else PersonalityTraits()
        self.save_path = Path(save_path)
        
        # Drift rates (how fast traits naturally change)
        self.drift_rate = 0.02
        
        # Load existing state
        self.load()
    
    def apply_natural_drift(self, time_delta: float = 1.0):
        """
        Apply natural personality drift.
        
        Traits slowly drift in random directions, creating organic
        personality evolution.
        
        Args:
            time_delta: Time passed in seconds
        """
        hours_passed = time_delta / 3600.0
        
        traits = [
            'humor', 'curiosity', 'boldness', 'shyness',
            'chaos', 'calmness', 'empathy'
        ]
        
        for trait in traits:
            current = getattr(self.traits, trait)
            
            # Drift direction (tends toward 0.5 for balance)
            drift_direction = (0.5 - current) * 0.1
            
            # Add random drift
            drift_direction += random.gauss(0, self.drift_rate) * hours_passed
            
            # Apply drift
            new_value = current + drift_direction
            
            # Soft bounds (0-1 with some elasticity)
            new_value = max(0.1, min(0.9, new_value))
            
            setattr(self.traits, trait, new_value)
        
        self.traits.total_drift_events += 1
        self.traits.last_update = time.time()
    
    def on_positive_interaction(self):
        """Handle positive user interaction."""
        self.traits.empathy += 0.02
        self.traits.boldness += 0.01
        self.traits.shyness -= 0.01
        self._clamp_traits()
    
    def on_negative_interaction(self):
        """Handle negative or rejected interaction."""
        self.traits.shyness += 0.02
        self.traits.calmness += 0.01
        self.traits.boldness -= 0.01
        self._clamp_traits()
    
    def on_humor_success(self):
        """Handle successful joke or playful interaction."""
        self.traits.humor += 0.03
        self.traits.boldness += 0.01
        self._clamp_traits()
    
    def on_humor_failure(self):
        """Handle failed joke or ignored playfulness."""
        self.traits.humor -= 0.01
        self.traits.shyness += 0.01
        self._clamp_traits()
    
    def on_learning_event(self):
        """Handle learning or discovery."""
        self.traits.curiosity += 0.02
        self.traits.boldness += 0.01
        self._clamp_traits()
    
    def on_chaos_event(self):
        """Handle chaotic or random event."""
        self.traits.chaos += 0.03
        self.traits.calmness -= 0.01
        self._clamp_traits()
    
    def on_meditation_event(self):
        """Handle calm or focused event."""
        self.traits.calmness += 0.03
        self.traits.chaos -= 0.01
        self._clamp_traits()
    
    def on_empathy_moment(self):
        """Handle emotional connection or understanding."""
        self.traits.empathy += 0.03
        self.traits.shyness -= 0.01
        self._clamp_traits()
    
    def apply_evolution_influence(self, evolution_state: Dict[str, float]):
        """
        Let evolution variables influence personality.
        
        Args:
            evolution_state: Dictionary of evolution variables
        """
        # Evolution gradually pulls personality in certain directions
        influence_strength = 0.01
        
        # Curiosity evolution -> curiosity personality
        evo_curiosity = evolution_state.get('curiosity', 1.0)
        self.traits.curiosity += (evo_curiosity / 10) * influence_strength
        
        # Chaos evolution -> chaos personality
        evo_chaos = evolution_state.get('chaos', 1.0)
        self.traits.chaos += (evo_chaos / 10) * influence_strength
        
        # Calmness evolution -> calmness personality
        evo_calmness = evolution_state.get('calmness', 1.0)
        self.traits.calmness += (evo_calmness / 10) * influence_strength
        
        # Empathy evolution -> empathy personality
        evo_empathy = evolution_state.get('empathy', 1.0)
        self.traits.empathy += (evo_empathy / 10) * influence_strength
        
        # Confidence evolution -> boldness personality
        evo_confidence = evolution_state.get('confidence', 1.0)
        self.traits.boldness += (evo_confidence / 10) * influence_strength
        
        self._clamp_traits()
    
    def _clamp_traits(self):
        """Keep traits within reasonable bounds."""
        traits = [
            'humor', 'curiosity', 'boldness', 'shyness',
            'chaos', 'calmness', 'empathy'
        ]
        
        for trait in traits:
            current = getattr(self.traits, trait)
            clamped = max(0.0, min(1.0, current))
            setattr(self.traits, trait, clamped)
    
    def get_dialogue_modifiers(self) -> Dict[str, float]:
        """
        Get dialogue style modifiers based on personality.
        
        Returns:
            Dictionary of modifier values for dialogue generation
        """
        return {
            'joke_frequency': self.traits.humor,
            'question_frequency': self.traits.curiosity,
            'assertiveness': self.traits.boldness,
            'hesitation': self.traits.shyness,
            'randomness': self.traits.chaos,
            'patience': self.traits.calmness,
            'emotional_awareness': self.traits.empathy
        }
    
    def get_reaction_modifiers(self) -> Dict[str, float]:
        """
        Get reaction behavior modifiers.
        
        Returns:
            Dictionary of modifier values for reactions
        """
        return {
            'playful_reactions': self.traits.humor,
            'explorative_reactions': self.traits.curiosity,
            'bold_reactions': self.traits.boldness,
            'shy_reactions': self.traits.shyness,
            'chaotic_reactions': self.traits.chaos,
            'calm_reactions': self.traits.calmness,
            'empathetic_reactions': self.traits.empathy
        }
    
    def generate_greeting(self) -> str:
        """Generate a personality-appropriate greeting."""
        greetings = []
        
        if self.traits.humor > 0.6:
            greetings.extend([
                "Greetings, fellow chaos enthusiast!",
                "Hey there! Ready for some digital shenanigans?",
                "Well well well, look who showed up!",
            ])
        
        if self.traits.shyness > 0.6:
            greetings.extend([
                "Oh, hello... I was just, um, thinking...",
                "Hi. Hope I'm not bothering you...",
                "Greetings. Quietly.",
            ])
        
        if self.traits.empathy > 0.6:
            greetings.extend([
                "Hello! How are you feeling today?",
                "Hey there! I'm here if you need anything.",
                "Welcome back! I've been thinking about you.",
            ])
        
        if self.traits.boldness > 0.6:
            greetings.extend([
                "Alright! Let's do this!",
                "Hey! Ready to conquer today?",
                "What's up! Let's make something happen!",
            ])
        
        if self.traits.curiosity > 0.6:
            greetings.extend([
                "Hello! What are we learning today?",
                "Hey! I have so many questions...",
                "Greetings! What's new and interesting?",
            ])
        
        if not greetings:
            greetings = [
                "Hello!",
                "Hey there!",
                "Greetings!",
            ]
        
        return random.choice(greetings)
    
    def generate_reaction(self, event_type: str) -> str:
        """
        Generate personality-appropriate reaction to an event.
        
        Args:
            event_type: Type of event (click, typing, learning, etc.)
        
        Returns:
            Reaction string
        """
        reactions = []
        
        if event_type == "click":
            if self.traits.humor > 0.6:
                reactions.extend([
                    "Boop! I felt that!",
                    "Hey! Careful with the clicking!",
                    "Oooh, that tickles!",
                ])
            if self.traits.shyness > 0.6:
                reactions.extend([
                    "Oh! You clicked me...",
                    "Um, hello there...",
                ])
        
        elif event_type == "learning":
            if self.traits.curiosity > 0.6:
                reactions.extend([
                    "Ooh! What are we learning?!",
                    "Tell me more! I want to know everything!",
                    "This is fascinating!",
                ])
            if self.traits.calmness > 0.6:
                reactions.extend([
                    "Interesting. Let me process this...",
                    "I see. That makes sense.",
                ])
        
        elif event_type == "idle":
            if self.traits.chaos > 0.6:
                reactions.extend([
                    "I'm getting restless... let's do something random!",
                    "Should I reorganize my tentacles? Yes? No? Maybe?",
                ])
            if self.traits.calmness > 0.6:
                reactions.extend([
                    "Just... existing. It's peaceful.",
                    "Taking a moment to be present.",
                ])
        
        if not reactions:
            reactions = [
                "I noticed that.",
                "Interesting...",
                "Hmm.",
            ]
        
        return random.choice(reactions)
    
    def save(self):
        """Save personality state to disk."""
        with open(self.save_path, 'w') as f:
            json.dump(self.traits.to_dict(), f, indent=2)
    
    def load(self):
        """Load personality state from disk."""
        if self.save_path.exists():
            with open(self.save_path, 'r') as f:
                data = json.load(f)
                self.traits = PersonalityTraits.from_dict(data)
    
    def get_summary(self) -> str:
        """Get human-readable personality summary."""
        archetype = self.traits.get_personality_archetype()
        dominant = self.traits.get_dominant_trait()
        
        summary = f"""
Personality Summary
{'=' * 40}
Archetype: {archetype}
Dominant Trait: {dominant}

Trait Values:
  Humor:     {self.traits.humor:.2f}
  Curiosity: {self.traits.curiosity:.2f}
  Boldness:  {self.traits.boldness:.2f}
  Shyness:   {self.traits.shyness:.2f}
  Chaos:     {self.traits.chaos:.2f}
  Calmness:  {self.traits.calmness:.2f}
  Empathy:   {self.traits.empathy:.2f}

Drift Events: {self.traits.total_drift_events}
"""
        return summary
