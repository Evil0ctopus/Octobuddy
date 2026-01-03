"""
Advanced AI Brain System for OctoBuddy
Includes long-term memory, short-term memory, learning, and knowledge management
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta


class Memory:
    """Memory system with short-term and long-term storage"""
    
    def __init__(self, storage_path="memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Short-term memory (current session, volatile)
        self.short_term = []
        self.short_term_limit = 50  # Keep last 50 interactions
        
        # Long-term memory (persistent)
        self.long_term_file = self.storage_path / "long_term_memory.json"
        self.long_term = self._load_long_term()
        
        # Knowledge base (facts, learned information)
        self.knowledge_file = self.storage_path / "knowledge_base.json"
        self.knowledge = self._load_knowledge()
        
    def _load_long_term(self):
        """Load long-term memory from disk"""
        if self.long_term_file.exists():
            try:
                with open(self.long_term_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {"memories": [], "important_events": []}
        return {"memories": [], "important_events": []}
        
    def _load_knowledge(self):
        """Load knowledge base from disk"""
        if self.knowledge_file.exists():
            try:
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {"facts": {}, "learned_skills": [], "user_preferences": {}}
        return {"facts": {}, "learned_skills": [], "user_preferences": {}}
        
    def save(self):
        """Save memory to disk"""
        with open(self.long_term_file, 'w', encoding='utf-8') as f:
            json.dump(self.long_term, f, indent=2)
            
        with open(self.knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, indent=2)
            
    def add_short_term(self, memory_type, content, metadata=None):
        """Add to short-term memory"""
        memory = {
            "type": memory_type,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.short_term.append(memory)
        
        # Keep only recent memories
        if len(self.short_term) > self.short_term_limit:
            self.short_term = self.short_term[-self.short_term_limit:]
            
    def add_long_term(self, memory_type, content, importance=5):
        """Add to long-term memory (importance: 1-10)"""
        memory = {
            "type": memory_type,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "importance": importance
        }
        
        # Important events get special treatment
        if importance >= 8:
            self.long_term["important_events"].append(memory)
        else:
            self.long_term["memories"].append(memory)
            
        self.save()
        
    def learn_fact(self, category, fact, source="user"):
        """Learn a new fact"""
        if category not in self.knowledge["facts"]:
            self.knowledge["facts"][category] = []
            
        fact_entry = {
            "fact": fact,
            "source": source,
            "learned_at": datetime.now().isoformat(),
            "confidence": 1.0 if source == "user" else 0.5
        }
        
        self.knowledge["facts"][category].append(fact_entry)
        self.save()
        
    def get_facts(self, category=None):
        """Retrieve learned facts"""
        if category:
            return self.knowledge["facts"].get(category, [])
        return self.knowledge["facts"]
        
    def learn_skill(self, skill_name, description):
        """Learn a new skill or ability"""
        skill = {
            "name": skill_name,
            "description": description,
            "learned_at": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        self.knowledge["learned_skills"].append(skill)
        self.save()
        
    def get_recent_memories(self, memory_type=None, limit=10):
        """Get recent short-term memories"""
        memories = self.short_term
        
        if memory_type:
            memories = [m for m in memories if m["type"] == memory_type]
            
        return memories[-limit:]
        
    def search_knowledge(self, query):
        """Search knowledge base for relevant information"""
        query_lower = query.lower()
        results = []
        
        # Search facts
        for category, facts in self.knowledge["facts"].items():
            for fact in facts:
                if query_lower in fact["fact"].lower() or query_lower in category.lower():
                    results.append({"type": "fact", "category": category, "content": fact})
                    
        # Search skills
        for skill in self.knowledge["learned_skills"]:
            if query_lower in skill["name"].lower() or query_lower in skill["description"].lower():
                results.append({"type": "skill", "content": skill})
                
        return results


class PersonalityTraits:
    """Dynamic personality system that evolves over time"""
    
    def __init__(self, storage_path="memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.traits_file = self.storage_path / "personality_traits.json"
        self.traits = self._load_traits()
        
    def _load_traits(self):
        """Load personality traits from disk"""
        if self.traits_file.exists():
            try:
                with open(self.traits_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return self._default_traits()
        return self._default_traits()
        
    def _default_traits(self):
        """Default personality traits (0-10 scale)"""
        return {
            "curiosity": 7,
            "playfulness": 8,
            "helpfulness": 9,
            "chaos_level": 5,
            "seriousness": 4,
            "humor": 8,
            "empathy": 7,
            "intelligence": 5,  # Grows with learning
            "confidence": 5,    # Grows with achievements
            "social": 6,
            "evolution_stage": 1,  # Personality evolution stage
            "traits_history": []  # Track how traits change over time
        }
        
    def save(self):
        """Save personality traits to disk"""
        with open(self.traits_file, 'w', encoding='utf-8') as f:
            json.dump(self.traits, f, indent=2)
            
    def update_trait(self, trait_name, delta, reason=""):
        """Update a personality trait (delta: -10 to +10)"""
        if trait_name in self.traits and isinstance(self.traits[trait_name], (int, float)):
            old_value = self.traits[trait_name]
            new_value = max(0, min(10, old_value + delta))
            self.traits[trait_name] = new_value
            
            # Record change in history
            change = {
                "trait": trait_name,
                "old_value": old_value,
                "new_value": new_value,
                "delta": delta,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            }
            self.traits["traits_history"].append(change)
            
            self.save()
            
    def get_dominant_traits(self, top_n=3):
        """Get the most dominant personality traits"""
        trait_values = [(k, v) for k, v in self.traits.items() 
                       if isinstance(v, (int, float))]
        sorted_traits = sorted(trait_values, key=lambda x: x[1], reverse=True)
        return sorted_traits[:top_n]
        
    def evolve(self, trigger="time"):
        """Evolve personality based on experiences"""
        stage = self.traits["evolution_stage"]
        
        # Evolution criteria
        if stage < 5:  # Max evolution stage
            # Check if ready to evolve
            intelligence = self.traits["intelligence"]
            confidence = self.traits["confidence"]
            
            if intelligence >= stage * 2 and confidence >= stage * 2:
                self.traits["evolution_stage"] = stage + 1
                
                # Evolution changes personality slightly
                self.update_trait("intelligence", 1, "personality evolution")
                self.update_trait("confidence", 1, "personality evolution")
                
                self.save()
                return True
                
        return False


class EnhancedBrain:
    """Enhanced AI brain with memory, learning, and personality"""
    
    def __init__(self):
        self.memory = Memory()
        self.personality = PersonalityTraits()
        
        # Context awareness
        self.current_context = {
            "active_tasks": [],
            "recent_interactions": [],
            "environment": {}
        }
        
    def process_interaction(self, interaction_type, content, user_input=None):
        """Process an interaction and learn from it"""
        # Add to short-term memory
        self.memory.add_short_term(interaction_type, content, {
            "user_input": user_input
        })
        
        # Update context
        self.current_context["recent_interactions"].append({
            "type": interaction_type,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only recent interactions
        if len(self.current_context["recent_interactions"]) > 20:
            self.current_context["recent_interactions"] = \
                self.current_context["recent_interactions"][-20:]
                
        # Learn and adapt personality based on interaction type
        if interaction_type == "study_event":
            self.personality.update_trait("intelligence", 0.1, "studying")
        elif interaction_type == "achievement":
            self.personality.update_trait("confidence", 0.2, "achievement")
            self.memory.add_long_term("achievement", content, importance=8)
        elif interaction_type == "teaching":
            self.personality.update_trait("intelligence", 0.15, "being taught")
            self.personality.update_trait("curiosity", 0.1, "learning new things")
            
    def learn_from_user(self, category, fact):
        """Learn a fact from the user"""
        self.memory.learn_fact(category, fact, source="user")
        self.personality.update_trait("intelligence", 0.2, f"learned about {category}")
        
    def recall_related(self, query):
        """Recall memories and knowledge related to a query"""
        # Search knowledge
        knowledge_results = self.memory.search_knowledge(query)
        
        # Search recent memories
        recent = self.memory.get_recent_memories(limit=20)
        memory_results = [m for m in recent 
                         if query.lower() in m["content"].lower()]
        
        return {
            "knowledge": knowledge_results,
            "memories": memory_results
        }
        
    def generate_contextual_response(self, event_type, base_phrase):
        """Generate a response based on current context and personality"""
        # Get dominant traits
        dominant = self.personality.get_dominant_traits(3)
        
        # Modify response based on personality
        if dominant[0][0] == "playfulness" and dominant[0][1] > 7:
            # Add playful element
            playful_additions = [" *wiggles*", " 🐙", " (^‿^)", "!"]
            base_phrase += playful_additions[hash(base_phrase) % len(playful_additions)]
            
        if self.personality.traits["chaos_level"] > 7:
            # Occasionally add chaotic element
            import random
            if random.random() < 0.3:
                base_phrase = base_phrase.upper()
                
        return base_phrase
        
    def save_state(self):
        """Save all brain state"""
        self.memory.save()
        self.personality.save()
