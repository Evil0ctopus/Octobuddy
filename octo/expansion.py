"""
Self-Expansion System for OctoBuddy
Allows safe loading of new skills, animations, dialogue, and plugins
"""

import os
import sys
import json
import importlib
import importlib.util
from pathlib import Path
from typing import Callable, Dict, Any
import ast
import re


class SkillLoader:
    """Safely load and manage custom skills/functions"""
    
    def __init__(self, skills_dir="skills"):
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(exist_ok=True)
        
        self.loaded_skills = {}
        self.skill_metadata = {}
        
        # Create example skill if directory is empty
        if not list(self.skills_dir.glob("*.py")):
            self._create_example_skill()
            
    def _create_example_skill(self):
        """Create an example skill to demonstrate the system"""
        example_skill = '''"""
Example OctoBuddy Skill
This is a template for creating custom skills
"""

def skill_info():
    """Return skill metadata"""
    return {
        "name": "example_greeting",
        "description": "A simple greeting skill",
        "author": "OctoBuddy",
        "version": "1.0.0"
    }

def execute(context=None):
    """
    Execute the skill
    
    Args:
        context: Dictionary with current state, user input, etc.
        
    Returns:
        Dictionary with results
    """
    user_name = context.get("user_name", "friend") if context else "friend"
    
    return {
        "success": True,
        "message": f"Hello {user_name}! This is a custom skill!",
        "data": {"greeted": True}
    }
'''
        
        example_path = self.skills_dir / "example_greeting.py"
        with open(example_path, 'w', encoding='utf-8') as f:
            f.write(example_skill)
            
    def load_skill(self, skill_name):
        """Load a skill module"""
        skill_path = self.skills_dir / f"{skill_name}.py"
        
        if not skill_path.exists():
            return None
            
        try:
            # Validate the skill file before loading
            if not self._validate_skill_file(skill_path):
                print(f"Skill {skill_name} failed validation")
                return None
                
            # Load the module
            spec = importlib.util.spec_from_file_location(skill_name, skill_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get skill info
            if hasattr(module, 'skill_info'):
                info = module.skill_info()
                self.skill_metadata[skill_name] = info
                
            # Store the skill
            self.loaded_skills[skill_name] = module
            
            return module
            
        except Exception as e:
            print(f"Error loading skill {skill_name}: {e}")
            return None
            
    def _validate_skill_file(self, filepath):
        """Validate that a skill file is safe to load"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
                
            # Parse the AST to check for dangerous operations
            tree = ast.parse(code)
            
            # List of dangerous functions/modules to avoid
            dangerous_imports = ['os.system', 'subprocess', 'eval', 'exec', '__import__']
            
            for node in ast.walk(tree):
                # Check imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if any(danger in alias.name for danger in ['subprocess', 'os.system']):
                            print(f"Dangerous import detected: {alias.name}")
                            return False
                            
                # Check function calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['eval', 'exec', '__import__']:
                            print(f"Dangerous function call detected: {node.func.id}")
                            return False
                            
            return True
            
        except Exception as e:
            print(f"Validation error: {e}")
            return False
            
    def execute_skill(self, skill_name, context=None):
        """Execute a loaded skill"""
        if skill_name not in self.loaded_skills:
            # Try to load it
            if not self.load_skill(skill_name):
                return {"success": False, "error": "Skill not found"}
                
        skill = self.loaded_skills[skill_name]
        
        if not hasattr(skill, 'execute'):
            return {"success": False, "error": "Skill missing execute function"}
            
        try:
            result = skill.execute(context)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def list_skills(self):
        """List all available skills"""
        skills = []
        
        for skill_file in self.skills_dir.glob("*.py"):
            skill_name = skill_file.stem
            
            if skill_name not in self.loaded_skills:
                self.load_skill(skill_name)
                
            metadata = self.skill_metadata.get(skill_name, {
                "name": skill_name,
                "description": "No description available"
            })
            
            skills.append(metadata)
            
        return skills


class AnimationLoader:
    """Load custom animations and sprite sheets"""
    
    def __init__(self, animations_dir="animations"):
        self.animations_dir = Path(animations_dir)
        self.animations_dir.mkdir(exist_ok=True)
        
        self.loaded_animations = {}
        
        # Create example animation if directory is empty
        if not list(self.animations_dir.glob("*.json")):
            self._create_example_animation()
            
    def _create_example_animation(self):
        """Create an example animation definition"""
        example_anim = {
            "name": "wave",
            "description": "OctoBuddy waves hello",
            "frames": [
                {
                    "ascii": "    ( ^‿^ )/\n   __|__",
                    "duration_ms": 200
                },
                {
                    "ascii": "   \\( ^‿^ )\n   __|__",
                    "duration_ms": 200
                },
                {
                    "ascii": "    ( ^‿^ )/\n   __|__",
                    "duration_ms": 200
                }
            ],
            "loop": False
        }
        
        example_path = self.animations_dir / "wave.json"
        with open(example_path, 'w', encoding='utf-8') as f:
            json.dump(example_anim, f, indent=2)
            
    def load_animation(self, animation_name):
        """Load an animation definition"""
        anim_path = self.animations_dir / f"{animation_name}.json"
        
        if not anim_path.exists():
            return None
            
        try:
            with open(anim_path, 'r', encoding='utf-8') as f:
                animation = json.load(f)
                
            self.loaded_animations[animation_name] = animation
            return animation
            
        except Exception as e:
            print(f"Error loading animation {animation_name}: {e}")
            return None
            
    def get_animation(self, animation_name):
        """Get a loaded animation"""
        if animation_name not in self.loaded_animations:
            return self.load_animation(animation_name)
        return self.loaded_animations[animation_name]
        
    def list_animations(self):
        """List all available animations"""
        animations = []
        
        for anim_file in self.animations_dir.glob("*.json"):
            anim_name = anim_file.stem
            
            if anim_name not in self.loaded_animations:
                self.load_animation(anim_name)
                
            if anim_name in self.loaded_animations:
                anim = self.loaded_animations[anim_name]
                animations.append({
                    "name": anim_name,
                    "description": anim.get("description", "No description")
                })
                
        return animations


class DialogueExpander:
    """Expand OctoBuddy's dialogue and personality expressions"""
    
    def __init__(self, dialogue_dir="dialogue"):
        self.dialogue_dir = Path(dialogue_dir)
        self.dialogue_dir.mkdir(exist_ok=True)
        
        self.dialogue_sets = {}
        
        # Create example dialogue set
        if not list(self.dialogue_dir.glob("*.json")):
            self._create_example_dialogue()
            
    def _create_example_dialogue(self):
        """Create example dialogue set"""
        example_dialogue = {
            "category": "greetings",
            "mood_variants": {
                "happy": [
                    "Hey there! Ready to learn something awesome?",
                    "Hi! I'm so excited to see you!",
                    "Hello friend! Let's do great things today!"
                ],
                "sleepy": [
                    "Oh... hi there... *yawn*",
                    "Hello... I was just resting my circuits...",
                    "Hey... nice to see you..."
                ],
                "excited": [
                    "HI HI HI! You're here! YES!",
                    "HELLO! I've been waiting! Let's GO!",
                    "YOU'RE BACK! This is the best day ever!"
                ]
            }
        }
        
        example_path = self.dialogue_dir / "greetings.json"
        with open(example_path, 'w', encoding='utf-8') as f:
            json.dump(example_dialogue, f, indent=2)
            
    def load_dialogue_set(self, category):
        """Load a dialogue set"""
        dialogue_path = self.dialogue_dir / f"{category}.json"
        
        if not dialogue_path.exists():
            return None
            
        try:
            with open(dialogue_path, 'r', encoding='utf-8') as f:
                dialogue = json.load(f)
                
            self.dialogue_sets[category] = dialogue
            return dialogue
            
        except Exception as e:
            print(f"Error loading dialogue {category}: {e}")
            return None
            
    def get_dialogue(self, category, mood=None):
        """Get dialogue for a category and mood"""
        if category not in self.dialogue_sets:
            if not self.load_dialogue_set(category):
                return None
                
        dialogue_set = self.dialogue_sets[category]
        
        if mood and "mood_variants" in dialogue_set:
            variants = dialogue_set["mood_variants"].get(mood, [])
            if variants:
                import random
                return random.choice(variants)
                
        # Fallback to generic
        if "generic" in dialogue_set:
            import random
            return random.choice(dialogue_set["generic"])
            
        return None
        
    def add_dialogue(self, category, mood, phrase):
        """Add a new dialogue phrase"""
        if category not in self.dialogue_sets:
            self.dialogue_sets[category] = {
                "category": category,
                "mood_variants": {}
            }
            
        if mood not in self.dialogue_sets[category]["mood_variants"]:
            self.dialogue_sets[category]["mood_variants"][mood] = []
            
        self.dialogue_sets[category]["mood_variants"][mood].append(phrase)
        
        # Save to file
        dialogue_path = self.dialogue_dir / f"{category}.json"
        with open(dialogue_path, 'w', encoding='utf-8') as f:
            json.dump(self.dialogue_sets[category], f, indent=2)


class ExpansionSystem:
    """Complete self-expansion system for OctoBuddy"""
    
    def __init__(self, base_dir="expansions"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Initialize subsystems
        self.skills = SkillLoader(self.base_dir / "skills")
        self.animations = AnimationLoader(self.base_dir / "animations")
        self.dialogue = DialogueExpander(self.base_dir / "dialogue")
        
    def add_skill(self, skill_name, skill_code):
        """Add a new skill (with validation)"""
        skill_path = self.skills.skills_dir / f"{skill_name}.py"
        
        # Save the skill
        with open(skill_path, 'w', encoding='utf-8') as f:
            f.write(skill_code)
            
        # Try to load it
        return self.skills.load_skill(skill_name)
        
    def add_animation(self, animation_name, frames, loop=False):
        """Add a new animation"""
        animation_def = {
            "name": animation_name,
            "description": f"Custom animation: {animation_name}",
            "frames": frames,
            "loop": loop
        }
        
        anim_path = self.animations.animations_dir / f"{animation_name}.json"
        with open(anim_path, 'w', encoding='utf-8') as f:
            json.dump(animation_def, f, indent=2)
            
        return self.animations.load_animation(animation_name)
        
    def get_all_capabilities(self):
        """Get all current capabilities"""
        return {
            "skills": self.skills.list_skills(),
            "animations": self.animations.list_animations(),
            "dialogue_categories": list(self.dialogue.dialogue_sets.keys())
        }
