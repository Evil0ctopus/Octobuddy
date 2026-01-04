"""
Mutation Engine for OctoBuddy.

Manages safe, cumulative mutations that evolve OctoBuddy's appearance,
behavior, personality, and abilities over time.

Mutations are:
- Small and incremental
- Safe and sandboxed
- Cumulative (build on each other)
- Triggered by learning, interaction, and evolution
- Reversible if needed

Mutation Types:
- Visual mutations (color, shape, patterns, effects)
- Behavioral mutations (movement style, reactions, preferences)
- Personality mutations (traits, dialogue, mood tendencies)
- Ability mutations (new skills, enhanced capabilities)
"""

import json
import time
import random
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from enum import Enum


class MutationType(Enum):
    """Types of mutations that can occur."""
    VISUAL = "visual"
    BEHAVIORAL = "behavioral"
    PERSONALITY = "personality"
    ABILITY = "ability"


@dataclass
class Mutation:
    """Record of a single mutation event."""
    mutation_id: str
    mutation_type: MutationType
    timestamp: float
    description: str
    parameters: Dict[str, Any]
    evolution_context: Dict[str, float]  # Evolution state at time of mutation
    reversible: bool = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['mutation_type'] = self.mutation_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary."""
        data['mutation_type'] = MutationType(data['mutation_type'])
        return cls(**data)


class MutationEngine:
    """
    Manages OctoBuddy's mutation system.
    
    Mutations are triggered by evolution events and apply safe,
    incremental changes to various aspects of OctoBuddy.
    """
    
    def __init__(self, save_path: str = "mutation_history.json"):
        """
        Initialize mutation engine.
        
        Args:
            save_path: Path to save mutation history
        """
        self.save_path = Path(save_path)
        self.mutation_history: List[Mutation] = []
        self.mutation_count = 0
        
        # Mutation strength (how much each mutation changes things)
        self.base_mutation_strength = 0.15
        
        # Load existing history if available
        self.load()
    
    def trigger_mutation(self, mutation_type: MutationType, 
                        evolution_state: Dict[str, float],
                        forced: bool = False) -> Optional[Mutation]:
        """
        Trigger a mutation based on evolution state.
        
        Args:
            mutation_type: Type of mutation to trigger
            evolution_state: Current evolution variable values
            forced: Force mutation even if probability check fails
        
        Returns:
            Mutation object if mutation occurred, None otherwise
        """
        # Probability check (unless forced)
        if not forced:
            # Higher chaos = more frequent mutations
            mutation_chance = 0.3 + (evolution_state.get('chaos', 1.0) * 0.05)
            if random.random() > mutation_chance:
                return None
        
        # Generate mutation based on type
        if mutation_type == MutationType.VISUAL:
            mutation = self._generate_visual_mutation(evolution_state)
        elif mutation_type == MutationType.BEHAVIORAL:
            mutation = self._generate_behavioral_mutation(evolution_state)
        elif mutation_type == MutationType.PERSONALITY:
            mutation = self._generate_personality_mutation(evolution_state)
        elif mutation_type == MutationType.ABILITY:
            mutation = self._generate_ability_mutation(evolution_state)
        else:
            return None
        
        # Record mutation
        self.mutation_history.append(mutation)
        self.mutation_count += 1
        self.save()
        
        return mutation
    
    def _generate_visual_mutation(self, evolution_state: Dict[str, float]) -> Mutation:
        """Generate a visual appearance mutation."""
        mutation_id = f"visual_{self.mutation_count}_{int(time.time())}"
        
        # Choose what to mutate based on evolution traits
        creativity = evolution_state.get('creativity', 1.0)
        chaos = evolution_state.get('chaos', 1.0)
        
        mutation_options = [
            ("palette", "Color palette shift"),
            ("shading", "Shading style change"),
            ("body_shape", "Body shape modification"),
            ("tentacle_style", "Tentacle appearance change"),
            ("eye_style", "Eye appearance modification"),
            ("glow_effect", "Glow/aura intensity change"),
            ("pattern", "Pattern/marking addition or change"),
        ]
        
        # Weight options by evolution traits
        if creativity > 2.0:
            mutation_options.extend([
                ("pattern", "Complex pattern generation"),
                ("shading", "Advanced shading technique"),
            ])
        
        if chaos > 2.0:
            mutation_options.extend([
                ("palette", "Chaotic color shift"),
                ("body_shape", "Asymmetric variation"),
            ])
        
        mutation_target, description = random.choice(mutation_options)
        
        # Generate mutation parameters
        strength = self.base_mutation_strength * (1 + chaos * 0.1)
        
        parameters = {
            "target": mutation_target,
            "strength": strength
        }
        
        # Add specific parameters based on target
        if mutation_target == "palette":
            parameters["hue_shift"] = random.uniform(-0.1, 0.1) * strength * 10
            parameters["saturation_shift"] = random.uniform(-0.1, 0.1) * strength
            parameters["brightness_shift"] = random.uniform(-0.1, 0.1) * strength
        
        elif mutation_target == "shading":
            parameters["shading_style"] = random.choice([
                "flat", "soft", "dithered", "specular"
            ])
        
        elif mutation_target == "body_shape":
            parameters["size_delta"] = random.uniform(-3, 3) * strength
            parameters["roundness_delta"] = random.uniform(-0.1, 0.1) * strength
        
        elif mutation_target == "tentacle_style":
            parameters["length_delta"] = random.uniform(-5, 5) * strength
            parameters["thickness_delta"] = random.uniform(-1, 1) * strength
            parameters["curvature_delta"] = random.uniform(-0.2, 0.2) * strength
        
        elif mutation_target == "eye_style":
            parameters["size_delta"] = random.uniform(-2, 2) * strength
            parameters["pupil_size_delta"] = random.uniform(-1, 1) * strength
        
        elif mutation_target == "glow_effect":
            parameters["intensity_delta"] = random.uniform(-0.2, 0.2) * strength
        
        elif mutation_target == "pattern":
            parameters["pattern_style"] = random.choice([
                "stripes", "spots", "runes", "veins", "none"
            ])
        
        return Mutation(
            mutation_id=mutation_id,
            mutation_type=MutationType.VISUAL,
            timestamp=time.time(),
            description=description,
            parameters=parameters,
            evolution_context=evolution_state.copy(),
            reversible=True
        )
    
    def _generate_behavioral_mutation(self, evolution_state: Dict[str, float]) -> Mutation:
        """Generate a behavioral mutation."""
        mutation_id = f"behavioral_{self.mutation_count}_{int(time.time())}"
        
        confidence = evolution_state.get('confidence', 1.0)
        curiosity = evolution_state.get('curiosity', 1.0)
        calmness = evolution_state.get('calmness', 1.0)
        
        mutation_options = [
            ("movement_style", "Movement pattern change"),
            ("interaction_preference", "Interaction style shift"),
            ("idle_behavior", "Idle animation variation"),
            ("reaction_speed", "Reaction timing adjustment"),
            ("cursor_tracking", "Cursor tracking behavior change"),
        ]
        
        mutation_target, description = random.choice(mutation_options)
        
        strength = self.base_mutation_strength * (1 + curiosity * 0.1)
        
        parameters = {
            "target": mutation_target,
            "strength": strength
        }
        
        if mutation_target == "movement_style":
            parameters["speed_multiplier"] = 0.8 + random.random() * 0.4
            parameters["amplitude_multiplier"] = 0.7 + random.random() * 0.6
        
        elif mutation_target == "interaction_preference":
            parameters["curiosity_bias"] = random.uniform(-0.1, 0.1) * strength
            parameters["boldness"] = confidence / 5.0
        
        elif mutation_target == "idle_behavior":
            parameters["sway_frequency"] = random.uniform(0.8, 1.2)
            parameters["fidget_chance"] = random.uniform(0.05, 0.2)
        
        elif mutation_target == "reaction_speed":
            parameters["response_delay"] = random.uniform(0.1, 0.5) / calmness
        
        elif mutation_target == "cursor_tracking":
            parameters["tracking_intensity"] = curiosity / 5.0
            parameters["smooth_factor"] = calmness / 3.0
        
        return Mutation(
            mutation_id=mutation_id,
            mutation_type=MutationType.BEHAVIORAL,
            timestamp=time.time(),
            description=description,
            parameters=parameters,
            evolution_context=evolution_state.copy(),
            reversible=True
        )
    
    def _generate_personality_mutation(self, evolution_state: Dict[str, float]) -> Mutation:
        """Generate a personality trait mutation."""
        mutation_id = f"personality_{self.mutation_count}_{int(time.time())}"
        
        empathy = evolution_state.get('empathy', 1.0)
        creativity = evolution_state.get('creativity', 1.0)
        
        mutation_options = [
            ("dialogue_style", "Dialogue tone shift"),
            ("humor_level", "Humor tendency change"),
            ("formality", "Formality level adjustment"),
            ("expressiveness", "Emotional expressiveness change"),
            ("curiosity_expression", "Question-asking tendency"),
        ]
        
        mutation_target, description = random.choice(mutation_options)
        
        strength = self.base_mutation_strength
        
        parameters = {
            "target": mutation_target,
            "strength": strength
        }
        
        if mutation_target == "dialogue_style":
            styles = ["casual", "formal", "quirky", "wise", "playful", "focused"]
            parameters["style"] = random.choice(styles)
        
        elif mutation_target == "humor_level":
            parameters["humor_frequency"] = random.uniform(0.1, 0.5)
            parameters["humor_type"] = random.choice(["puns", "observations", "absurd", "dry"])
        
        elif mutation_target == "formality":
            parameters["formality_level"] = random.uniform(0.3, 0.9)
        
        elif mutation_target == "expressiveness":
            parameters["emotion_intensity"] = empathy / 3.0
            parameters["expression_frequency"] = random.uniform(0.2, 0.8)
        
        elif mutation_target == "curiosity_expression":
            parameters["question_frequency"] = evolution_state.get('curiosity', 1.0) / 5.0
        
        return Mutation(
            mutation_id=mutation_id,
            mutation_type=MutationType.PERSONALITY,
            timestamp=time.time(),
            description=description,
            parameters=parameters,
            evolution_context=evolution_state.copy(),
            reversible=True
        )
    
    def _generate_ability_mutation(self, evolution_state: Dict[str, float]) -> Mutation:
        """Generate a new ability or enhance existing one."""
        mutation_id = f"ability_{self.mutation_count}_{int(time.time())}"
        
        focus = evolution_state.get('focus', 1.0)
        creativity = evolution_state.get('creativity', 1.0)
        
        # Abilities that can be learned/enhanced
        ability_options = [
            ("pattern_recognition", "Enhanced pattern recognition"),
            ("memory_recall", "Improved memory systems"),
            ("prediction", "Better predictive modeling"),
            ("adaptation", "Faster adaptation to user patterns"),
            ("synthesis", "Information synthesis capability"),
        ]
        
        ability_target, description = random.choice(ability_options)
        
        parameters = {
            "ability": ability_target,
            "level": 1 + (self.mutation_count * 0.1),
            "effectiveness": focus / 5.0 + creativity / 10.0
        }
        
        return Mutation(
            mutation_id=mutation_id,
            mutation_type=MutationType.ABILITY,
            timestamp=time.time(),
            description=description,
            parameters=parameters,
            evolution_context=evolution_state.copy(),
            reversible=False  # Abilities generally don't reverse
        )
    
    def apply_mutation_to_art_engine(self, mutation: Mutation, art_engine):
        """
        Apply a visual mutation to the art engine.
        
        Args:
            mutation: Mutation to apply
            art_engine: ArtEngine instance to modify
        """
        if mutation.mutation_type != MutationType.VISUAL:
            return
        
        params = mutation.parameters
        target = params.get("target")
        strength = params.get("strength", 0.15)
        
        if target == "palette":
            # Mutate palette
            art_engine.palette = art_engine.palette.mutate(strength)
        
        elif target == "shading":
            art_engine.shading_style = params.get("shading_style", "soft")
        
        elif target == "body_shape":
            art_engine.body_size += params.get("size_delta", 0)
            art_engine.body_roundness += params.get("roundness_delta", 0)
            # Clamp values
            art_engine.body_size = max(30, min(50, art_engine.body_size))
            art_engine.body_roundness = max(0.7, min(1.0, art_engine.body_roundness))
        
        elif target == "tentacle_style":
            art_engine.tentacle_length += params.get("length_delta", 0)
            art_engine.tentacle_thickness += params.get("thickness_delta", 0)
            art_engine.tentacle_curvature += params.get("curvature_delta", 0)
            # Clamp values
            art_engine.tentacle_length = max(25, min(45, art_engine.tentacle_length))
            art_engine.tentacle_thickness = max(4, min(10, art_engine.tentacle_thickness))
            art_engine.tentacle_curvature = max(0, min(1, art_engine.tentacle_curvature))
        
        elif target == "eye_style":
            art_engine.eye_size += params.get("size_delta", 0)
            art_engine.pupil_size += params.get("pupil_size_delta", 0)
            # Clamp values
            art_engine.eye_size = max(8, min(16, art_engine.eye_size))
            art_engine.pupil_size = max(4, min(8, art_engine.pupil_size))
        
        elif target == "glow_effect":
            art_engine.glow_intensity += params.get("intensity_delta", 0)
            art_engine.glow_intensity = max(0, min(1, art_engine.glow_intensity))
        
        elif target == "pattern":
            art_engine.marking_style = params.get("pattern_style", "none")
    
    def get_mutation_summary(self) -> str:
        """Get human-readable mutation history summary."""
        if not self.mutation_history:
            return "No mutations yet."
        
        visual = sum(1 for m in self.mutation_history if m.mutation_type == MutationType.VISUAL)
        behavioral = sum(1 for m in self.mutation_history if m.mutation_type == MutationType.BEHAVIORAL)
        personality = sum(1 for m in self.mutation_history if m.mutation_type == MutationType.PERSONALITY)
        ability = sum(1 for m in self.mutation_history if m.mutation_type == MutationType.ABILITY)
        
        recent = self.mutation_history[-5:] if len(self.mutation_history) > 5 else self.mutation_history
        
        summary = f"""
Mutation History Summary
{'=' * 40}
Total Mutations: {self.mutation_count}
  Visual: {visual}
  Behavioral: {behavioral}
  Personality: {personality}
  Ability: {ability}

Recent Mutations:
"""
        for mutation in recent:
            summary += f"  - {mutation.description} ({mutation.mutation_type.value})\n"
        
        return summary
    
    def save(self):
        """Save mutation history to disk."""
        data = [m.to_dict() for m in self.mutation_history]
        with open(self.save_path, 'w') as f:
            json.dump({
                'mutation_count': self.mutation_count,
                'mutations': data
            }, f, indent=2)
    
    def load(self):
        """Load mutation history from disk."""
        if self.save_path.exists():
            with open(self.save_path, 'r') as f:
                data = json.load(f)
                self.mutation_count = data.get('mutation_count', 0)
                self.mutation_history = [
                    Mutation.from_dict(m) for m in data.get('mutations', [])
                ]
