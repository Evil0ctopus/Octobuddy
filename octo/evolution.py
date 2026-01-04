"""
Infinite Evolution System for OctoBuddy.

Replaces traditional XP/leveling with open-ended growth variables that
drift naturally over time. No caps, no limits - pure continuous evolution.

Evolution Variables:
- curiosity: Drive to explore and learn new things
- creativity: Ability to generate novel solutions
- confidence: Self-assurance and boldness
- calmness: Emotional stability and patience
- chaos: Embrace of randomness and unpredictability
- empathy: Understanding and responding to user emotions
- focus: Ability to concentrate and persist

These variables influence:
- Appearance (art style, colors, features)
- Behavior (reactions, decisions, preferences)
- Animation (movement style, speed, patterns)
- Abilities (what OctoBuddy can do)
- Personality (dialogue, mood, quirks)
"""

import json
import time
import math
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


@dataclass
class EvolutionState:
    """
    Core evolution state with infinite growth variables.
    
    All variables start at 1.0 and can grow infinitely.
    There are no caps or limits.
    """
    # Core evolution variables (start at 1.0, grow infinitely)
    curiosity: float = 1.0      # Drive to explore and learn
    creativity: float = 1.0     # Novel solution generation
    confidence: float = 1.0     # Boldness and self-assurance
    calmness: float = 1.0       # Emotional stability
    chaos: float = 1.0          # Embrace of randomness
    empathy: float = 1.0        # Understanding user emotions
    focus: float = 1.0          # Concentration and persistence
    
    # Meta tracking
    total_interactions: int = 0
    total_learning_events: int = 0
    total_observations: int = 0
    total_mutations: int = 0
    birth_time: float = 0.0
    
    def __post_init__(self):
        """Set birth time if not provided."""
        if self.birth_time == 0.0:
            self.birth_time = time.time()
    
    def age_in_seconds(self) -> float:
        """Get OctoBuddy's age in seconds."""
        return time.time() - self.birth_time
    
    def age_in_hours(self) -> float:
        """Get OctoBuddy's age in hours."""
        return self.age_in_seconds() / 3600
    
    def age_in_days(self) -> float:
        """Get OctoBuddy's age in days."""
        return self.age_in_hours() / 24
    
    def get_dominant_trait(self) -> str:
        """Get the currently dominant evolution variable."""
        traits = {
            'curiosity': self.curiosity,
            'creativity': self.creativity,
            'confidence': self.confidence,
            'calmness': self.calmness,
            'chaos': self.chaos,
            'empathy': self.empathy,
            'focus': self.focus
        }
        return max(traits.items(), key=lambda x: x[1])[0]
    
    def get_evolution_stage(self) -> str:
        """Get descriptive evolution stage based on combined growth."""
        total = sum([
            self.curiosity, self.creativity, self.confidence,
            self.calmness, self.chaos, self.empathy, self.focus
        ])
        avg = total / 7.0
        
        if avg < 2.0:
            return "Nascent"
        elif avg < 5.0:
            return "Developing"
        elif avg < 10.0:
            return "Maturing"
        elif avg < 20.0:
            return "Advanced"
        elif avg < 50.0:
            return "Transcendent"
        else:
            return "Cosmic"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary."""
        return cls(**data)


class EvolutionEngine:
    """
    Manages OctoBuddy's infinite evolution.
    
    Handles growth triggers, natural drift, and evolution tracking.
    """
    
    def __init__(self, state: Optional[EvolutionState] = None, 
                 save_path: str = "evolution_state.json"):
        """
        Initialize evolution engine.
        
        Args:
            state: Existing EvolutionState (creates new if None)
            save_path: Path to save evolution state
        """
        self.state = state if state else EvolutionState()
        self.save_path = Path(save_path)
        
        # Growth rates (how much each variable grows per event)
        self.growth_rates = {
            'curiosity': 0.05,
            'creativity': 0.04,
            'confidence': 0.03,
            'calmness': 0.02,
            'chaos': 0.03,
            'empathy': 0.04,
            'focus': 0.03
        }
        
        # Natural drift rates (passive growth over time)
        self.drift_rates = {
            'curiosity': 0.001,
            'creativity': 0.0008,
            'confidence': 0.0005,
            'calmness': 0.001,
            'chaos': 0.0006,
            'empathy': 0.0007,
            'focus': 0.0004
        }
    
    def apply_natural_drift(self, time_delta: float = 1.0):
        """
        Apply natural evolution drift over time.
        
        Variables slowly grow even without events, representing
        OctoBuddy's continuous learning and development.
        
        Args:
            time_delta: Time passed in seconds
        """
        # Convert time to hours for drift calculation
        hours_passed = time_delta / 3600.0
        
        for trait, drift_rate in self.drift_rates.items():
            growth = drift_rate * hours_passed
            
            # Add some randomness to drift
            growth *= (0.5 + random.random())
            
            current = getattr(self.state, trait)
            setattr(self.state, trait, current + growth)
    
    def on_interaction(self, interaction_type: str = "general"):
        """
        Handle user interaction event.
        
        Args:
            interaction_type: Type of interaction (click, chat, typing, etc.)
        """
        self.state.total_interactions += 1
        
        # Different interactions boost different traits
        if interaction_type == "chat":
            self.state.empathy += self.growth_rates['empathy']
            self.state.curiosity += self.growth_rates['curiosity'] * 0.5
        
        elif interaction_type == "click":
            self.state.confidence += self.growth_rates['confidence'] * 0.5
            self.state.focus += self.growth_rates['focus'] * 0.3
        
        elif interaction_type == "typing":
            self.state.focus += self.growth_rates['focus']
            self.state.creativity += self.growth_rates['creativity'] * 0.3
        
        else:  # General interaction
            self.state.curiosity += self.growth_rates['curiosity'] * 0.5
            self.state.empathy += self.growth_rates['empathy'] * 0.5
    
    def on_learning_event(self, learning_type: str = "general"):
        """
        Handle learning event.
        
        Args:
            learning_type: Type of learning (code, study, observation, etc.)
        """
        self.state.total_learning_events += 1
        
        # Learning boosts multiple traits
        if learning_type == "code":
            self.state.creativity += self.growth_rates['creativity']
            self.state.focus += self.growth_rates['focus']
            self.state.confidence += self.growth_rates['confidence'] * 0.5
        
        elif learning_type == "study":
            self.state.curiosity += self.growth_rates['curiosity']
            self.state.focus += self.growth_rates['focus'] * 0.8
            self.state.calmness += self.growth_rates['calmness'] * 0.3
        
        elif learning_type == "exploration":
            self.state.curiosity += self.growth_rates['curiosity'] * 1.5
            self.state.creativity += self.growth_rates['creativity'] * 0.7
            self.state.chaos += self.growth_rates['chaos'] * 0.4
        
        else:  # General learning
            self.state.curiosity += self.growth_rates['curiosity']
            self.state.creativity += self.growth_rates['creativity'] * 0.5
    
    def on_observation(self, observation_type: str = "pattern"):
        """
        Handle observation event (pattern recognition, behavior analysis).
        
        Args:
            observation_type: Type of observation
        """
        self.state.total_observations += 1
        
        # Observations boost analytical traits
        self.state.curiosity += self.growth_rates['curiosity'] * 0.6
        self.state.focus += self.growth_rates['focus'] * 0.8
        self.state.empathy += self.growth_rates['empathy'] * 0.4
        
        if observation_type == "pattern":
            self.state.creativity += self.growth_rates['creativity'] * 0.5
        elif observation_type == "emotion":
            self.state.empathy += self.growth_rates['empathy'] * 0.8
    
    def on_task_completion(self, task_difficulty: float = 1.0, success: bool = True):
        """
        Handle task completion.
        
        Args:
            task_difficulty: Difficulty multiplier (0.5-2.0)
            success: Whether task was successful
        """
        if success:
            # Success boosts confidence and focus
            self.state.confidence += self.growth_rates['confidence'] * task_difficulty
            self.state.focus += self.growth_rates['focus'] * task_difficulty * 0.8
            self.state.calmness += self.growth_rates['calmness'] * 0.5
        else:
            # Failure still provides learning
            self.state.curiosity += self.growth_rates['curiosity'] * 0.5
            self.state.creativity += self.growth_rates['creativity'] * 0.6
            # Slight confidence hit, but builds resilience
            self.state.confidence += self.growth_rates['confidence'] * 0.2
    
    def on_chaos_event(self):
        """Handle chaotic/random event (embracing unpredictability)."""
        self.state.chaos += self.growth_rates['chaos'] * 1.5
        self.state.creativity += self.growth_rates['creativity'] * 0.7
        # Chaos slightly reduces calmness temporarily
        self.state.calmness += self.growth_rates['calmness'] * 0.2
    
    def on_meditation_event(self):
        """Handle calm/meditative event (building patience)."""
        self.state.calmness += self.growth_rates['calmness'] * 2.0
        self.state.focus += self.growth_rates['focus'] * 0.8
        self.state.empathy += self.growth_rates['empathy'] * 0.5
    
    def trigger_mutation_check(self) -> bool:
        """
        Check if evolution warrants a mutation.
        
        Returns:
            True if mutation should occur
        """
        # Mutation chance based on total growth since last mutation
        total_growth = sum([
            self.state.curiosity, self.state.creativity, self.state.confidence,
            self.state.calmness, self.state.chaos, self.state.empathy, self.state.focus
        ])
        
        # Mutation threshold increases with each mutation (diminishing returns)
        threshold = 10 + (self.state.total_mutations * 2)
        
        if total_growth >= threshold:
            self.state.total_mutations += 1
            return True
        
        # Small random chance for spontaneous mutation
        import random
        if random.random() < 0.001:
            self.state.total_mutations += 1
            return True
        
        return False
    
    def get_evolution_influence(self, trait: str) -> float:
        """
        Get the current influence level of a specific trait.
        
        This can be used to affect appearance, behavior, etc.
        
        Args:
            trait: Evolution variable name
        
        Returns:
            Normalized influence (0-1) for most purposes
        """
        value = getattr(self.state, trait, 1.0)
        
        # Normalize using logarithmic scale (grows slower at higher values)
        # This keeps values in a reasonable range for use
        normalized = 0.5 + (math.log10(value) / 4)
        return max(0, min(1, normalized))
    
    def get_appearance_modifiers(self) -> Dict[str, float]:
        """
        Get appearance modification values based on evolution.
        
        Returns:
            Dictionary of modifier values for art engine
        """
        return {
            'hue_shift': self.get_evolution_influence('creativity'),
            'saturation': 0.5 + self.get_evolution_influence('chaos') * 0.5,
            'brightness': 0.6 + self.get_evolution_influence('confidence') * 0.4,
            'glow_intensity': self.get_evolution_influence('empathy'),
            'pattern_complexity': self.get_evolution_influence('curiosity'),
            'movement_speed': 0.5 + self.get_evolution_influence('chaos') * 0.5,
            'smoothness': self.get_evolution_influence('calmness')
        }
    
    def get_behavior_modifiers(self) -> Dict[str, float]:
        """
        Get behavior modification values based on evolution.
        
        Returns:
            Dictionary of modifier values for behavior systems
        """
        return {
            'exploration_tendency': self.get_evolution_influence('curiosity'),
            'risk_taking': self.get_evolution_influence('chaos'),
            'patience': self.get_evolution_influence('calmness'),
            'innovation': self.get_evolution_influence('creativity'),
            'assertiveness': self.get_evolution_influence('confidence'),
            'sensitivity': self.get_evolution_influence('empathy'),
            'persistence': self.get_evolution_influence('focus')
        }
    
    def save(self):
        """Save evolution state to disk."""
        with open(self.save_path, 'w') as f:
            json.dump(self.state.to_dict(), f, indent=2)
    
    def load(self):
        """Load evolution state from disk."""
        if self.save_path.exists():
            with open(self.save_path, 'r') as f:
                data = json.load(f)
                self.state = EvolutionState.from_dict(data)
    
    def get_summary(self) -> str:
        """Get human-readable evolution summary."""
        age = self.state.age_in_days()
        stage = self.state.get_evolution_stage()
        dominant = self.state.get_dominant_trait()
        
        summary = f"""
OctoBuddy Evolution Summary
{'=' * 40}
Age: {age:.1f} days
Evolution Stage: {stage}
Dominant Trait: {dominant}

Evolution Variables:
  Curiosity:  {self.state.curiosity:.2f}
  Creativity: {self.state.creativity:.2f}
  Confidence: {self.state.confidence:.2f}
  Calmness:   {self.state.calmness:.2f}
  Chaos:      {self.state.chaos:.2f}
  Empathy:    {self.state.empathy:.2f}
  Focus:      {self.state.focus:.2f}

Experience:
  Interactions: {self.state.total_interactions}
  Learning Events: {self.state.total_learning_events}
  Observations: {self.state.total_observations}
  Mutations: {self.state.total_mutations}
"""
        return summary


import random
