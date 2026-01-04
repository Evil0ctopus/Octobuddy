"""
Memory and Learning System for OctoBuddy.

Manages persistent memory storage and learning capabilities:
- Short-term memory (session-based, temporary)
- Long-term memory (persistent, saved to disk)
- Knowledge graphs (relationships between concepts)
- Personality memory (user preferences, interaction patterns)
- Appearance evolution memory (visual change history)
- Ability memory (learned capabilities)

All memory is stored locally in JSON format.
"""

import json
import time
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict, deque


@dataclass
class MemoryEntry:
    """A single memory entry."""
    memory_id: str
    timestamp: float
    memory_type: str  # fact, interaction, observation, emotion, ability
    content: str
    importance: float  # 0-1, how important this memory is
    context: Dict[str, Any] = field(default_factory=dict)
    access_count: int = 0
    last_accessed: float = 0.0
    
    def __post_init__(self):
        """Set last_accessed to timestamp if not set."""
        if self.last_accessed == 0.0:
            self.last_accessed = self.timestamp
    
    def access(self):
        """Record memory access (strengthens memory)."""
        self.access_count += 1
        self.last_accessed = time.time()
    
    def decay_importance(self, decay_rate=0.01):
        """Reduce importance over time (forgetting)."""
        time_passed = time.time() - self.last_accessed
        days_passed = time_passed / (24 * 3600)
        
        # Memories with high access count decay slower
        decay_multiplier = 1.0 / (1 + self.access_count * 0.1)
        self.importance = max(0.1, self.importance - (decay_rate * days_passed * decay_multiplier))
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary."""
        return cls(**data)


@dataclass
class KnowledgeNode:
    """A node in the knowledge graph."""
    node_id: str
    concept: str
    category: str  # code, security, tool, person, event, etc.
    learned_at: float
    confidence: float  # 0-1, how well understood
    related_nodes: Set[str] = field(default_factory=set)
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['related_nodes'] = list(self.related_nodes)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary."""
        data['related_nodes'] = set(data.get('related_nodes', []))
        return cls(**data)


class ShortTermMemory:
    """
    Session-based memory (cleared between sessions).
    
    Tracks recent interactions, observations, and context.
    """
    
    def __init__(self, max_size=100):
        """
        Initialize short-term memory.
        
        Args:
            max_size: Maximum number of recent memories to keep
        """
        self.memories = deque(maxlen=max_size)
        self.session_start = time.time()
        self.interaction_count = 0
    
    def add(self, memory_type: str, content: str, importance: float = 0.5, 
            context: Optional[Dict] = None):
        """Add a memory to short-term storage."""
        memory = MemoryEntry(
            memory_id=f"stm_{len(self.memories)}_{int(time.time())}",
            timestamp=time.time(),
            memory_type=memory_type,
            content=content,
            importance=importance,
            context=context or {}
        )
        self.memories.append(memory)
        self.interaction_count += 1
    
    def get_recent(self, count=10) -> List[MemoryEntry]:
        """Get most recent memories."""
        return list(self.memories)[-count:]
    
    def get_by_type(self, memory_type: str) -> List[MemoryEntry]:
        """Get all memories of a specific type."""
        return [m for m in self.memories if m.memory_type == memory_type]
    
    def clear(self):
        """Clear all short-term memories."""
        self.memories.clear()
        self.session_start = time.time()
        self.interaction_count = 0


class LongTermMemory:
    """
    Persistent memory storage (saved to disk).
    
    Stores important memories, learned facts, and experiences.
    """
    
    def __init__(self, save_path: str = "long_term_memory.json"):
        """
        Initialize long-term memory.
        
        Args:
            save_path: Path to save memory database
        """
        self.save_path = Path(save_path)
        self.memories: Dict[str, MemoryEntry] = {}
        self.memory_count = 0
        
        # Load existing memories
        self.load()
    
    def add(self, memory_type: str, content: str, importance: float = 0.7,
            context: Optional[Dict] = None) -> MemoryEntry:
        """
        Add a memory to long-term storage.
        
        Args:
            memory_type: Type of memory
            content: Memory content
            importance: How important (0-1)
            context: Additional context
        
        Returns:
            Created MemoryEntry
        """
        memory_id = f"ltm_{self.memory_count}_{int(time.time())}"
        memory = MemoryEntry(
            memory_id=memory_id,
            timestamp=time.time(),
            memory_type=memory_type,
            content=content,
            importance=importance,
            context=context or {}
        )
        
        self.memories[memory_id] = memory
        self.memory_count += 1
        self.save()
        
        return memory
    
    def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """Get a specific memory by ID."""
        memory = self.memories.get(memory_id)
        if memory:
            memory.access()
            self.save()
        return memory
    
    def search(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """Search memories by content (simple substring search)."""
        query_lower = query.lower()
        results = [
            m for m in self.memories.values()
            if query_lower in m.content.lower()
        ]
        
        # Sort by importance and recency
        results.sort(key=lambda m: (m.importance, m.timestamp), reverse=True)
        
        # Access found memories
        for memory in results[:limit]:
            memory.access()
        
        self.save()
        return results[:limit]
    
    def get_by_type(self, memory_type: str, limit: int = 50) -> List[MemoryEntry]:
        """Get memories of a specific type."""
        results = [m for m in self.memories.values() if m.memory_type == memory_type]
        results.sort(key=lambda m: m.timestamp, reverse=True)
        return results[:limit]
    
    def get_most_important(self, limit: int = 20) -> List[MemoryEntry]:
        """Get most important memories."""
        results = sorted(self.memories.values(), key=lambda m: m.importance, reverse=True)
        return results[:limit]
    
    def consolidate_from_short_term(self, short_term: ShortTermMemory, 
                                     threshold: float = 0.6):
        """
        Move important short-term memories to long-term storage.
        
        Args:
            short_term: ShortTermMemory instance
            threshold: Minimum importance to consolidate
        """
        for memory in short_term.memories:
            if memory.importance >= threshold:
                # Add to long-term
                self.add(
                    memory_type=memory.memory_type,
                    content=memory.content,
                    importance=memory.importance,
                    context=memory.context
                )
    
    def apply_decay(self, decay_rate: float = 0.01):
        """Apply decay to all memories (forgetting)."""
        for memory in self.memories.values():
            memory.decay_importance(decay_rate)
        self.save()
    
    def prune_weak_memories(self, threshold: float = 0.2):
        """Remove memories below importance threshold."""
        to_remove = [
            mem_id for mem_id, mem in self.memories.items()
            if mem.importance < threshold
        ]
        
        for mem_id in to_remove:
            del self.memories[mem_id]
        
        if to_remove:
            self.save()
    
    def save(self):
        """Save memories to disk."""
        data = {
            'memory_count': self.memory_count,
            'memories': {
                mem_id: mem.to_dict()
                for mem_id, mem in self.memories.items()
            }
        }
        with open(self.save_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """Load memories from disk."""
        if self.save_path.exists():
            with open(self.save_path, 'r') as f:
                data = json.load(f)
                self.memory_count = data.get('memory_count', 0)
                self.memories = {
                    mem_id: MemoryEntry.from_dict(mem_data)
                    for mem_id, mem_data in data.get('memories', {}).items()
                }


class KnowledgeGraph:
    """
    Graph-based knowledge representation.
    
    Stores concepts and their relationships for learning and reasoning.
    """
    
    def __init__(self, save_path: str = "knowledge_graph.json"):
        """
        Initialize knowledge graph.
        
        Args:
            save_path: Path to save graph data
        """
        self.save_path = Path(save_path)
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.node_count = 0
        
        # Load existing graph
        self.load()
    
    def add_concept(self, concept: str, category: str, 
                   confidence: float = 0.5, properties: Optional[Dict] = None) -> KnowledgeNode:
        """
        Add a concept to the knowledge graph.
        
        Args:
            concept: Name of the concept
            category: Category (code, security, tool, etc.)
            confidence: How well understood (0-1)
            properties: Additional properties
        
        Returns:
            Created KnowledgeNode
        """
        node_id = f"node_{self.node_count}"
        node = KnowledgeNode(
            node_id=node_id,
            concept=concept,
            category=category,
            learned_at=time.time(),
            confidence=confidence,
            properties=properties or {}
        )
        
        self.nodes[node_id] = node
        self.node_count += 1
        self.save()
        
        return node
    
    def link_concepts(self, concept1: str, concept2: str):
        """Create a relationship between two concepts."""
        node1 = self._find_node_by_concept(concept1)
        node2 = self._find_node_by_concept(concept2)
        
        if node1 and node2:
            node1.related_nodes.add(node2.node_id)
            node2.related_nodes.add(node1.node_id)
            self.save()
    
    def _find_node_by_concept(self, concept: str) -> Optional[KnowledgeNode]:
        """Find a node by concept name."""
        for node in self.nodes.values():
            if node.concept.lower() == concept.lower():
                return node
        return None
    
    def get_related_concepts(self, concept: str) -> List[str]:
        """Get concepts related to a given concept."""
        node = self._find_node_by_concept(concept)
        if not node:
            return []
        
        related = []
        for related_id in node.related_nodes:
            related_node = self.nodes.get(related_id)
            if related_node:
                related.append(related_node.concept)
        
        return related
    
    def get_concepts_by_category(self, category: str) -> List[str]:
        """Get all concepts in a category."""
        return [
            node.concept for node in self.nodes.values()
            if node.category == category
        ]
    
    def strengthen_concept(self, concept: str, amount: float = 0.1):
        """Increase confidence in a concept."""
        node = self._find_node_by_concept(concept)
        if node:
            node.confidence = min(1.0, node.confidence + amount)
            self.save()
    
    def save(self):
        """Save knowledge graph to disk."""
        data = {
            'node_count': self.node_count,
            'nodes': {
                node_id: node.to_dict()
                for node_id, node in self.nodes.items()
            }
        }
        with open(self.save_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """Load knowledge graph from disk."""
        if self.save_path.exists():
            with open(self.save_path, 'r') as f:
                data = json.load(f)
                self.node_count = data.get('node_count', 0)
                self.nodes = {
                    node_id: KnowledgeNode.from_dict(node_data)
                    for node_id, node_data in data.get('nodes', {}).items()
                }


class MemorySystem:
    """
    Unified memory management system.
    
    Combines short-term, long-term, and knowledge graph memory.
    """
    
    def __init__(self):
        """Initialize complete memory system."""
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.knowledge = KnowledgeGraph()
    
    def remember(self, memory_type: str, content: str, importance: float = 0.5,
                context: Optional[Dict] = None):
        """
        Store a memory (goes to short-term, may consolidate to long-term).
        
        Args:
            memory_type: Type of memory
            content: Memory content
            importance: Importance level (0-1)
            context: Additional context
        """
        # Add to short-term
        self.short_term.add(memory_type, content, importance, context)
        
        # If very important, also add to long-term immediately
        if importance >= 0.8:
            self.long_term.add(memory_type, content, importance, context)
    
    def learn_concept(self, concept: str, category: str, 
                     confidence: float = 0.5, related_to: Optional[List[str]] = None):
        """
        Learn a new concept and add to knowledge graph.
        
        Args:
            concept: Concept name
            category: Category
            confidence: Understanding level
            related_to: List of related concepts
        """
        # Add to knowledge graph
        self.knowledge.add_concept(concept, category, confidence)
        
        # Link to related concepts
        if related_to:
            for related_concept in related_to:
                self.knowledge.link_concepts(concept, related_concept)
        
        # Also remember as a fact
        self.remember(
            "fact",
            f"Learned about {concept} in {category}",
            importance=0.7,
            context={'concept': concept, 'category': category}
        )
    
    def consolidate_memories(self):
        """Move important short-term memories to long-term storage."""
        self.long_term.consolidate_from_short_term(self.short_term, threshold=0.6)
    
    def end_session(self):
        """Clean up at end of session."""
        # Consolidate important memories
        self.consolidate_memories()
        
        # Clear short-term
        self.short_term.clear()
        
        # Apply decay to long-term
        self.long_term.apply_decay()
        
        # Prune weak memories
        self.long_term.prune_weak_memories()
    
    def get_summary(self) -> str:
        """Get human-readable memory summary."""
        stm_count = len(self.short_term.memories)
        ltm_count = len(self.long_term.memories)
        knowledge_count = len(self.knowledge.nodes)
        
        important_memories = self.long_term.get_most_important(5)
        
        summary = f"""
Memory System Summary
{'=' * 40}
Short-Term Memories: {stm_count}
Long-Term Memories: {ltm_count}
Knowledge Concepts: {knowledge_count}

Most Important Memories:
"""
        for mem in important_memories:
            summary += f"  - {mem.content[:60]}... (importance: {mem.importance:.2f})\n"
        
        return summary
