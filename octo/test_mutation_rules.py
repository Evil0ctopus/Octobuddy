"""
Test script for mutation_rules module.

Demonstrates:
1. Data-driven mutation configuration
2. Mutation selection logic
3. Modifier calculation
4. Validation system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mutation_rules import (
    MUTATION_POOL,
    RARITY_WEIGHTS,
    calculate_mutation_chance,
    select_mutation,
    get_mutation_modifiers,
    get_mutation_info,
    get_mutation_display_name,
    list_all_mutations,
    get_mutations_by_rarity,
    validate_mutation_pool,
)
from config import CONFIG


def test_mutation_pool_structure():
    """Test that mutation pool is properly structured."""
    print("=" * 70)
    print("TEST 1: Mutation Pool Structure")
    print("=" * 70)
    
    print(f"\nTotal mutations defined: {len(MUTATION_POOL)}")
    print("\nMutations by rarity:")
    
    for rarity in ["common", "uncommon", "rare", "legendary"]:
        mutations = get_mutations_by_rarity(rarity)
        print(f"  {rarity.capitalize()}: {len(mutations)}")
        for mut_key in mutations:
            info = get_mutation_info(mut_key)
            print(f"    - {info['name']}: {info['description']}")
    
    print()


def test_mutation_validation():
    """Test mutation pool validation."""
    print("=" * 70)
    print("TEST 2: Validation System")
    print("=" * 70)
    
    errors = validate_mutation_pool()
    if errors:
        print("\n❌ Validation errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✅ Mutation pool is valid!")
    print()


def test_mutation_chance_calculation():
    """Test mutation chance scaling."""
    print("=" * 70)
    print("TEST 3: Mutation Chance Calculation")
    print("=" * 70)
    
    test_cases = [
        {"level": 1, "mutations": []},
        {"level": 10, "mutations": []},
        {"level": 50, "mutations": []},
        {"level": 100, "mutations": []},
        {"level": 50, "mutations": ["speed_learner"]},
        {"level": 50, "mutations": ["speed_learner", "chaos_incarnate", "analytical_mind"]},
    ]
    
    for state in test_cases:
        chance = calculate_mutation_chance(state, CONFIG)
        print(f"\nLevel {state['level']}, {len(state.get('mutations', []))} mutations:")
        print(f"  Chance: {chance:.2%}")
    
    print()


def test_mutation_selection():
    """Test weighted mutation selection."""
    print("=" * 70)
    print("TEST 4: Weighted Mutation Selection")
    print("=" * 70)
    
    print("\nRunning 1000 selections to test distribution...")
    
    state = {"mutations": [], "level": 50}
    results = {}
    
    for _ in range(1000):
        mutation_key = select_mutation(state, CONFIG)
        if mutation_key:
            results[mutation_key] = results.get(mutation_key, 0) + 1
    
    print("\nSelection distribution (out of 1000):")
    for rarity in ["common", "uncommon", "rare", "legendary"]:
        mutations = get_mutations_by_rarity(rarity)
        print(f"\n{rarity.capitalize()}:")
        for mut_key in mutations:
            count = results.get(mut_key, 0)
            percentage = (count / 1000) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {get_mutation_display_name(mut_key):25s}: {bar} {count} ({percentage:.1f}%)")
    
    print()


def test_modifier_calculation():
    """Test modifier aggregation."""
    print("=" * 70)
    print("TEST 5: Modifier Aggregation")
    print("=" * 70)
    
    test_cases = [
        {
            "name": "No mutations",
            "state": {"mutations": []},
        },
        {
            "name": "Speed Learner only",
            "state": {"mutations": ["speed_learner"]},
        },
        {
            "name": "Multiple XP modifiers",
            "state": {"mutations": ["speed_learner", "transcendent"]},
        },
        {
            "name": "Chaos build",
            "state": {"mutations": ["chaos_incarnate", "personality_fracture"]},
        },
        {
            "name": "Max power build",
            "state": {"mutations": ["speed_learner", "analytical_mind", "unstoppable", "transcendent"]},
        },
    ]
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        modifiers = get_mutation_modifiers(test_case['state'])
        
        print(f"  XP Modifier: {modifiers['xp_modifier']:.2f}x")
        print(f"  Security XP: {modifiers['xp_modifier_security']:.2f}x")
        print(f"  Milestone XP: {modifiers['xp_modifier_milestone']:.2f}x")
        print(f"  Chaos Factor: {modifiers['chaos_factor']:.2f}x")
        
        if modifiers['mood_influence']:
            print(f"  Mood Influences: {modifiers['mood_influence']}")
        if modifiers['special_flags']:
            print(f"  Special Flags: {', '.join(modifiers['special_flags'])}")
    
    print()


def test_data_driven_extensibility():
    """Test that mutations are purely data-driven."""
    print("=" * 70)
    print("TEST 6: Data-Driven Design")
    print("=" * 70)
    
    print("\nDemonstrating data-driven architecture:")
    print("All mutations are defined as data in MUTATION_POOL.")
    print("No code changes needed to add new mutations!\n")
    
    # Show structure of a mutation
    print("Example mutation structure (speed_learner):")
    import json
    print(json.dumps(MUTATION_POOL["speed_learner"], indent=2))
    
    print("\nTo add a new mutation:")
    print("1. Add entry to MUTATION_POOL dict")
    print("2. Define name, description, rarity")
    print("3. Specify modifiers (xp_modifier, chaos_factor, etc.)")
    print("4. That's it! No code changes needed.")
    
    print("\nThis follows OctoBuddy's architecture:")
    print("✅ Pure data configuration")
    print("✅ Separation of data and logic")
    print("✅ Easy to test and extend")
    print()


def main():
    print("\n" + "=" * 70)
    print("MUTATION RULES MODULE TEST SUITE")
    print("=" * 70)
    print()
    
    tests = [
        test_mutation_pool_structure,
        test_mutation_validation,
        test_mutation_chance_calculation,
        test_mutation_selection,
        test_modifier_calculation,
        test_data_driven_extensibility,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"ERROR in {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("=" * 70)
    print("TESTS COMPLETE")
    print("=" * 70)
    print("\nKey Features:")
    print("✅ Data-driven mutation configuration")
    print("✅ Pure functions for all logic")
    print("✅ Automatic validation on import")
    print("✅ Weighted random selection by rarity")
    print("✅ Modifier aggregation and stacking")
    print("✅ Easy extensibility (just add data)")


if __name__ == "__main__":
    main()
