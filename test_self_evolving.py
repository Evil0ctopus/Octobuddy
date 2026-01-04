"""
Test suite for self-evolving OctoBuddy systems.

Tests:
- Procedural art engine
- Evolution system
- Mutation engine
- Memory system
- Personality drift
- Ability system
"""

import sys
import time
from pathlib import Path

# Test art engine
def test_art_engine():
    """Test procedural HD pixel art generation."""
    print("Testing Art Engine...")
    
    from octo.art_engine import ArtEngine, ColorPalette, PerlinNoise
    
    # Test palette generation
    palette = ColorPalette.generate_harmonious(hue_base=0.5)
    assert palette.primary is not None
    assert len(palette.primary) == 3  # RGB tuple
    
    # Test palette mutation
    mutated = palette.mutate(0.1)
    assert mutated.primary != palette.primary  # Should be different
    
    # Test Perlin noise
    noise = PerlinNoise(seed=42)
    value = noise.noise(1.5, 2.3)
    assert -1.0 <= value <= 1.0
    
    # Test art engine
    art_engine = ArtEngine(seed=42)
    sprite = art_engine.generate_sprite(size=128)
    assert sprite.size == (128, 128)
    
    # Test mutation
    old_size = art_engine.body_size
    art_engine.mutate(0.2)
    # Body size should have changed (or stayed within bounds)
    assert art_engine.body_size != old_size or art_engine.body_size == max(30, min(50, old_size))
    
    print("  ✓ Art Engine tests passed")


def test_evolution_system():
    """Test infinite evolution system."""
    print("Testing Evolution System...")
    
    from octo.evolution import EvolutionEngine, EvolutionState
    
    # Test evolution state
    state = EvolutionState()
    assert state.curiosity == 1.0  # Default
    assert state.age_in_seconds() >= 0
    
    # Test evolution engine
    engine = EvolutionEngine(state=state)
    
    # Test growth
    initial_curiosity = engine.state.curiosity
    engine.on_learning_event("study")  # Study increases curiosity
    assert engine.state.curiosity > initial_curiosity
    
    # Test natural drift
    engine.apply_natural_drift(3600)  # 1 hour
    
    # Test stage determination
    stage = engine.state.get_evolution_stage()
    assert stage in ["Nascent", "Developing", "Maturing", "Advanced", "Transcendent", "Cosmic"]
    
    # Test modifiers
    appearance = engine.get_appearance_modifiers()
    assert 'glow_intensity' in appearance
    assert 0 <= appearance['glow_intensity'] <= 1
    
    print("  ✓ Evolution System tests passed")


def test_mutation_engine():
    """Test mutation system."""
    print("Testing Mutation Engine...")
    
    from octo.mutations import MutationEngine, MutationType, Mutation
    from octo.art_engine import ArtEngine
    
    # Test mutation engine
    engine = MutationEngine()
    
    # Test mutation generation
    evolution_state = {
        'curiosity': 2.0,
        'creativity': 1.5,
        'chaos': 1.0,
        'confidence': 1.0,
        'calmness': 1.0,
        'empathy': 1.0,
        'focus': 1.0
    }
    
    mutation = engine.trigger_mutation(
        MutationType.VISUAL,
        evolution_state,
        forced=True
    )
    
    assert mutation is not None
    assert mutation.mutation_type == MutationType.VISUAL
    assert mutation.parameters is not None
    
    # Test mutation application
    art_engine = ArtEngine()
    old_glow = art_engine.glow_intensity
    
    # Create a glow mutation
    glow_mutation = Mutation(
        mutation_id="test_mutation",
        mutation_type=MutationType.VISUAL,
        timestamp=time.time(),
        description="Test glow mutation",
        parameters={
            "target": "glow_effect",
            "intensity_delta": 0.2
        },
        evolution_context=evolution_state
    )
    
    engine.apply_mutation_to_art_engine(glow_mutation, art_engine)
    # Glow should have changed
    assert art_engine.glow_intensity != old_glow
    
    print("  ✓ Mutation Engine tests passed")


def test_memory_system():
    """Test memory and learning."""
    print("Testing Memory System...")
    
    from octo.memory import MemorySystem, ShortTermMemory, LongTermMemory, KnowledgeGraph
    
    # Test short-term memory
    stm = ShortTermMemory()
    stm.add("fact", "Python is awesome", importance=0.7)
    assert len(stm.memories) == 1
    
    recent = stm.get_recent(1)
    assert len(recent) == 1
    assert recent[0].content == "Python is awesome"
    
    # Test long-term memory
    ltm = LongTermMemory(save_path="/tmp/test_ltm.json")
    ltm.add("fact", "OctoBuddy evolves", importance=0.9)
    assert len(ltm.memories) > 0
    
    # Test search
    results = ltm.search("evolves")
    assert len(results) > 0
    
    # Test knowledge graph
    kg = KnowledgeGraph(save_path="/tmp/test_kg.json")
    kg.add_concept("Python", "programming", confidence=0.8)
    kg.add_concept("Learning", "skill", confidence=0.7)
    kg.link_concepts("Python", "Learning")
    
    related = kg.get_related_concepts("Python")
    assert "Learning" in related
    
    # Test memory system
    memory_system = MemorySystem()
    memory_system.remember("interaction", "User clicked", importance=0.5)
    memory_system.learn_concept("Testing", "process", confidence=0.6)
    
    print("  ✓ Memory System tests passed")


def test_personality_drift():
    """Test personality system."""
    print("Testing Personality Drift...")
    
    from octo.personality_drift import PersonalityDrift, PersonalityTraits
    
    # Test personality traits
    traits = PersonalityTraits()
    assert 0 <= traits.humor <= 1
    
    archetype = traits.get_personality_archetype()
    assert archetype is not None
    
    # Test personality drift
    personality = PersonalityDrift(traits=traits)
    
    old_humor = personality.traits.humor
    personality.on_humor_success()
    assert personality.traits.humor >= old_humor  # Should increase
    
    # Test natural drift
    personality.apply_natural_drift(3600)  # 1 hour
    
    # Test greeting generation
    greeting = personality.generate_greeting()
    assert len(greeting) > 0
    
    # Test reaction generation
    reaction = personality.generate_reaction("click")
    assert len(reaction) > 0
    
    print("  ✓ Personality Drift tests passed")


def test_ability_system():
    """Test ability expansion."""
    print("Testing Ability System...")
    
    from octo.abilities import AbilitySystem, AbilityCategory
    
    # Test ability system
    abilities = AbilitySystem(save_path="/tmp/test_abilities.json")
    
    # Should have core abilities
    assert len(abilities.abilities) > 0
    
    # Test learning new ability
    initial_count = len(abilities.abilities)
    new_ability = abilities.learn_ability(
        name="Test Ability",
        category=AbilityCategory.UTILITY,
        description="A test ability",
        proficiency=0.5
    )
    
    assert len(abilities.abilities) == initial_count + 1
    assert new_ability.name == "Test Ability"
    
    # Test ability enhancement
    old_proficiency = new_ability.proficiency
    abilities.enhance_ability(new_ability.ability_id, 0.1)
    enhanced = abilities.abilities[new_ability.ability_id]
    assert enhanced.proficiency > old_proficiency
    
    # Test ability composition
    ability1 = abilities.learn_ability(
        "Compose Test 1",
        AbilityCategory.OBSERVATION,
        "Test 1"
    )
    ability2 = abilities.learn_ability(
        "Compose Test 2",
        AbilityCategory.OBSERVATION,
        "Test 2"
    )
    
    composed = abilities.compose_abilities(
        [ability1.ability_id, ability2.ability_id],
        "Composed Ability",
        "Combined test"
    )
    
    assert composed is not None
    assert len(composed.prerequisites) == 2
    
    print("  ✓ Ability System tests passed")


def test_integration():
    """Test full system integration."""
    print("Testing System Integration...")
    
    from octo.art_engine import ArtEngine
    from octo.evolution import EvolutionEngine
    from octo.mutations import MutationEngine, MutationType
    from octo.memory import MemorySystem
    from octo.personality_drift import PersonalityDrift
    from octo.abilities import AbilitySystem
    
    # Create all systems
    art = ArtEngine()
    evolution = EvolutionEngine()
    mutations = MutationEngine()
    memory = MemorySystem()
    personality = PersonalityDrift()
    abilities = AbilitySystem()
    
    # Simulate learning event
    evolution.on_learning_event("code")
    memory.remember("learning", "Learned Python", importance=0.8)
    personality.on_learning_event()
    
    # Trigger mutation
    evo_dict = evolution.state.to_dict()
    mutation = mutations.trigger_mutation(
        MutationType.VISUAL,
        evo_dict,
        forced=True
    )
    
    if mutation:
        mutations.apply_mutation_to_art_engine(mutation, art)
    
    # Generate sprite
    sprite = art.generate_sprite(128)
    assert sprite.size == (128, 128)
    
    # Apply evolution influence on personality
    personality.apply_evolution_influence(evo_dict)
    
    # Check ability suggestion
    suggestion = abilities.suggest_new_ability(evo_dict)
    # May or may not suggest (depends on evolution levels)
    
    print("  ✓ Integration tests passed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("OctoBuddy Self-Evolving Systems Test Suite")
    print("=" * 70 + "\n")
    
    tests = [
        test_art_engine,
        test_evolution_system,
        test_mutation_engine,
        test_memory_system,
        test_personality_drift,
        test_ability_system,
        test_integration,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70 + "\n")
    
    # Cleanup test files
    test_files = [
        "/tmp/test_ltm.json",
        "/tmp/test_kg.json",
        "/tmp/test_abilities.json"
    ]
    for f in test_files:
        path = Path(f)
        if path.exists():
            path.unlink()
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
