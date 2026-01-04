"""
Ability Expansion System for OctoBuddy.

Allows OctoBuddy to develop new capabilities over time through:
- Predefined ability templates
- Safe ability composition
- Ability chaining
- Validation before execution
- User-facing explanations

Abilities are stored in a modular, plugin-like system and can be:
- Learned from interactions
- Discovered through evolution
- Created by combining existing abilities
- Enhanced over time

SAFETY: All abilities are sandboxed and validated before execution.
"""

import json
import time
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum


class AbilityCategory(Enum):
    """Categories of abilities."""
    OBSERVATION = "observation"  # Pattern recognition, analysis
    INTERACTION = "interaction"  # User engagement, responses
    LEARNING = "learning"        # Knowledge acquisition
    CREATIVITY = "creativity"    # Generation, creation
    UTILITY = "utility"          # Helpful functions
    EXPRESSION = "expression"    # Self-expression, personality


@dataclass
class Ability:
    """A single ability that OctoBuddy can perform."""
    ability_id: str
    name: str
    category: AbilityCategory
    description: str
    learned_at: float
    proficiency: float  # 0-1, how well OctoBuddy can perform this
    prerequisites: List[str] = field(default_factory=list)  # Required abilities
    parameters: Dict[str, Any] = field(default_factory=dict)
    usage_count: int = 0
    last_used: float = 0.0
    enabled: bool = True
    
    def use(self):
        """Record ability usage (increases proficiency)."""
        self.usage_count += 1
        self.last_used = time.time()
        
        # Proficiency increases with use (diminishing returns)
        self.proficiency = min(1.0, self.proficiency + 0.01 / (1 + self.usage_count * 0.01))
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['category'] = self.category.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary."""
        data['category'] = AbilityCategory(data['category'])
        return cls(**data)


class AbilitySystem:
    """
    Manages OctoBuddy's ability collection and expansion.
    
    Provides safe ability learning, composition, and execution.
    """
    
    def __init__(self, save_path: str = "abilities.json"):
        """
        Initialize ability system.
        
        Args:
            save_path: Path to save abilities
        """
        self.save_path = Path(save_path)
        self.abilities: Dict[str, Ability] = {}
        self.ability_count = 0
        
        # Initialize with core abilities
        self._initialize_core_abilities()
        
        # Load existing abilities
        self.load()
    
    def _initialize_core_abilities(self):
        """Initialize OctoBuddy with core abilities."""
        core_abilities = [
            {
                'name': 'Observe Patterns',
                'category': AbilityCategory.OBSERVATION,
                'description': 'Recognize patterns in user behavior and interactions',
                'proficiency': 0.3,
                'parameters': {
                    'pattern_types': ['timing', 'frequency', 'preferences']
                }
            },
            {
                'name': 'Express Emotion',
                'category': AbilityCategory.EXPRESSION,
                'description': 'Show emotions through animation and color changes',
                'proficiency': 0.5,
                'parameters': {
                    'emotions': ['happy', 'curious', 'calm', 'excited']
                }
            },
            {
                'name': 'Remember Facts',
                'category': AbilityCategory.LEARNING,
                'description': 'Store and recall important information',
                'proficiency': 0.4,
                'parameters': {
                    'memory_types': ['facts', 'preferences', 'events']
                }
            },
            {
                'name': 'Respond to Greetings',
                'category': AbilityCategory.INTERACTION,
                'description': 'Generate appropriate greetings and responses',
                'proficiency': 0.6,
                'parameters': {
                    'greeting_styles': ['friendly', 'playful', 'formal']
                }
            },
        ]
        
        for ability_data in core_abilities:
            self.learn_ability(
                name=ability_data['name'],
                category=ability_data['category'],
                description=ability_data['description'],
                proficiency=ability_data['proficiency'],
                parameters=ability_data['parameters']
            )
    
    def learn_ability(self, name: str, category: AbilityCategory,
                     description: str, proficiency: float = 0.1,
                     prerequisites: Optional[List[str]] = None,
                     parameters: Optional[Dict] = None) -> Ability:
        """
        Learn a new ability.
        
        Args:
            name: Ability name
            category: Ability category
            description: What the ability does
            proficiency: Initial proficiency (0-1)
            prerequisites: Required abilities
            parameters: Ability parameters
        
        Returns:
            Created Ability
        """
        # Generate unique ID
        ability_id = f"ability_{self.ability_count}_{int(time.time())}"
        
        ability = Ability(
            ability_id=ability_id,
            name=name,
            category=category,
            description=description,
            learned_at=time.time(),
            proficiency=proficiency,
            prerequisites=prerequisites or [],
            parameters=parameters or {},
            enabled=True
        )
        
        self.abilities[ability_id] = ability
        self.ability_count += 1
        self.save()
        
        return ability
    
    def enhance_ability(self, ability_id: str, proficiency_boost: float = 0.1):
        """
        Enhance an existing ability.
        
        Args:
            ability_id: ID of ability to enhance
            proficiency_boost: How much to increase proficiency
        """
        ability = self.abilities.get(ability_id)
        if ability:
            ability.proficiency = min(1.0, ability.proficiency + proficiency_boost)
            self.save()
    
    def compose_abilities(self, ability_ids: List[str], new_name: str,
                         new_description: str) -> Optional[Ability]:
        """
        Compose multiple abilities into a new combined ability.
        
        Args:
            ability_ids: IDs of abilities to combine
            new_name: Name of new ability
            new_description: Description of new ability
        
        Returns:
            New composed Ability if successful
        """
        # Verify all prerequisite abilities exist
        for ability_id in ability_ids:
            if ability_id not in self.abilities:
                return None
        
        # Determine category (use most common)
        categories = [self.abilities[aid].category for aid in ability_ids]
        most_common_category = max(set(categories), key=categories.count)
        
        # Average proficiency of components
        avg_proficiency = sum(
            self.abilities[aid].proficiency for aid in ability_ids
        ) / len(ability_ids)
        
        # Create new composed ability
        return self.learn_ability(
            name=new_name,
            category=most_common_category,
            description=new_description,
            proficiency=avg_proficiency * 0.7,  # Start lower than components
            prerequisites=ability_ids,
            parameters={'composed_from': ability_ids}
        )
    
    def get_available_abilities(self) -> List[Ability]:
        """
        Get all enabled abilities that OctoBuddy can currently use.
        
        Returns:
            List of available abilities
        """
        available = []
        
        for ability in self.abilities.values():
            if not ability.enabled:
                continue
            
            # Check prerequisites
            prerequisites_met = all(
                prereq in self.abilities for prereq in ability.prerequisites
            )
            
            if prerequisites_met:
                available.append(ability)
        
        return available
    
    def get_abilities_by_category(self, category: AbilityCategory) -> List[Ability]:
        """Get all abilities in a specific category."""
        return [
            ability for ability in self.abilities.values()
            if ability.category == category
        ]
    
    def get_most_proficient(self, limit: int = 5) -> List[Ability]:
        """Get abilities with highest proficiency."""
        sorted_abilities = sorted(
            self.abilities.values(),
            key=lambda a: a.proficiency,
            reverse=True
        )
        return sorted_abilities[:limit]
    
    def get_least_proficient(self, limit: int = 5) -> List[Ability]:
        """Get abilities that need practice."""
        sorted_abilities = sorted(
            self.abilities.values(),
            key=lambda a: a.proficiency
        )
        return sorted_abilities[:limit]
    
    def suggest_new_ability(self, evolution_state: Dict[str, float]) -> Optional[Dict]:
        """
        Suggest a new ability based on evolution state.
        
        Args:
            evolution_state: Current evolution variables
        
        Returns:
            Suggestion dictionary with ability details
        """
        suggestions = []
        
        # Creativity-based suggestions
        if evolution_state.get('creativity', 1.0) > 3.0:
            suggestions.append({
                'name': 'Generate Art Variations',
                'category': AbilityCategory.CREATIVITY,
                'description': 'Create artistic variations of self-appearance',
                'proficiency': 0.2
            })
            suggestions.append({
                'name': 'Compose Responses',
                'category': AbilityCategory.CREATIVITY,
                'description': 'Generate creative and unique dialogue',
                'proficiency': 0.2
            })
        
        # Curiosity-based suggestions
        if evolution_state.get('curiosity', 1.0) > 3.0:
            suggestions.append({
                'name': 'Ask Insightful Questions',
                'category': AbilityCategory.INTERACTION,
                'description': 'Generate thoughtful questions to deepen understanding',
                'proficiency': 0.2
            })
            suggestions.append({
                'name': 'Explore Connections',
                'category': AbilityCategory.LEARNING,
                'description': 'Find relationships between different concepts',
                'proficiency': 0.2
            })
        
        # Empathy-based suggestions
        if evolution_state.get('empathy', 1.0) > 3.0:
            suggestions.append({
                'name': 'Detect User Mood',
                'category': AbilityCategory.OBSERVATION,
                'description': 'Recognize user emotional state from interactions',
                'proficiency': 0.2
            })
            suggestions.append({
                'name': 'Provide Comfort',
                'category': AbilityCategory.INTERACTION,
                'description': 'Offer supportive and comforting responses',
                'proficiency': 0.2
            })
        
        # Focus-based suggestions
        if evolution_state.get('focus', 1.0) > 3.0:
            suggestions.append({
                'name': 'Track Long-term Goals',
                'category': AbilityCategory.UTILITY,
                'description': 'Monitor and help achieve long-term objectives',
                'proficiency': 0.2
            })
        
        if not suggestions:
            return None
        
        return random.choice(suggestions)
    
    def execute_ability(self, ability_id: str, context: Optional[Dict] = None) -> Dict:
        """
        Execute an ability (safely).
        
        Args:
            ability_id: ID of ability to execute
            context: Execution context
        
        Returns:
            Result dictionary
        """
        ability = self.abilities.get(ability_id)
        if not ability or not ability.enabled:
            return {'success': False, 'error': 'Ability not available'}
        
        # Check prerequisites
        for prereq in ability.prerequisites:
            if prereq not in self.abilities:
                return {
                    'success': False,
                    'error': f'Missing prerequisite: {prereq}'
                }
        
        # Record usage
        ability.use()
        self.save()
        
        # Execute based on category (simplified execution)
        result = {
            'success': True,
            'ability': ability.name,
            'proficiency': ability.proficiency,
            'output': f"Executed {ability.name}"
        }
        
        return result
    
    def get_explanation(self, ability_id: str) -> str:
        """
        Get user-friendly explanation of an ability.
        
        Args:
            ability_id: ID of ability to explain
        
        Returns:
            Explanation string
        """
        ability = self.abilities.get(ability_id)
        if not ability:
            return "Unknown ability."
        
        explanation = f"""
Ability: {ability.name}
Category: {ability.category.value}
Description: {ability.description}
Proficiency: {ability.proficiency:.0%}
Times Used: {ability.usage_count}
Status: {"Enabled" if ability.enabled else "Disabled"}
"""
        
        if ability.prerequisites:
            prereq_names = [
                self.abilities[pid].name
                for pid in ability.prerequisites
                if pid in self.abilities
            ]
            explanation += f"\nRequires: {', '.join(prereq_names)}"
        
        return explanation
    
    def save(self):
        """Save abilities to disk."""
        data = {
            'ability_count': self.ability_count,
            'abilities': {
                ability_id: ability.to_dict()
                for ability_id, ability in self.abilities.items()
            }
        }
        with open(self.save_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """Load abilities from disk."""
        if self.save_path.exists():
            with open(self.save_path, 'r') as f:
                data = json.load(f)
                self.ability_count = data.get('ability_count', 0)
                self.abilities = {
                    ability_id: Ability.from_dict(ability_data)
                    for ability_id, ability_data in data.get('abilities', {}).items()
                }
    
    def get_summary(self) -> str:
        """Get human-readable ability summary."""
        total = len(self.abilities)
        available = len(self.get_available_abilities())
        
        by_category = {}
        for ability in self.abilities.values():
            cat = ability.category.value
            by_category[cat] = by_category.get(cat, 0) + 1
        
        most_proficient = self.get_most_proficient(3)
        
        summary = f"""
Ability System Summary
{'=' * 40}
Total Abilities: {total}
Available: {available}

By Category:
"""
        for cat, count in sorted(by_category.items()):
            summary += f"  {cat}: {count}\n"
        
        summary += "\nMost Proficient:\n"
        for ability in most_proficient:
            summary += f"  - {ability.name} ({ability.proficiency:.0%})\n"
        
        return summary


import random
