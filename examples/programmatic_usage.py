"""
Example: Programmatic interaction with OctoBuddy
Shows how to create custom integrations and automations
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from octo.config import CONFIG
from octo.core_enhanced import EnhancedOctoBuddy


def example_study_session():
    """Example: Automated study session tracking"""
    
    print("=== OctoBuddy Study Session Example ===\n")
    
    # Initialize OctoBuddy
    buddy = EnhancedOctoBuddy(CONFIG, enable_observation=False)
    
    # Start study session
    print("📚 Starting Python study session...")
    result = buddy.handle_event('studied_python')
    print(f"OctoBuddy says: {result['phrase']}\n")
    
    # Teach some facts while studying
    print("📝 Teaching OctoBuddy about what we learned...")
    buddy.teach('python', 'List comprehensions are concise and powerful')
    buddy.teach('python', 'Decorators modify function behavior')
    buddy.teach('python', 'Context managers handle resources safely')
    print("✓ OctoBuddy learned 3 new facts!\n")
    
    # Finish another study session
    print("📚 Continuing studies...")
    result = buddy.handle_event('studied_python')
    print(f"OctoBuddy says: {result['phrase']}\n")
    
    # Check what OctoBuddy remembers
    print("🧠 Checking what OctoBuddy knows about Python...")
    knowledge = buddy.recall_knowledge('python')
    print(f"Found {len(knowledge['knowledge'])} knowledge items about Python:")
    for item in knowledge['knowledge'][:3]:
        if item['type'] == 'fact':
            print(f"  - {item['content']['fact']}")
    print()
    
    # Get final status
    status = buddy.get_status()
    print("📊 Session Summary:")
    print(f"  Level: {status['level']}")
    print(f"  XP: {status['xp']}")
    print(f"  Mood: {status['mood']}")
    print(f"  Stage: {status['stage']}")
    print(f"  Total Facts Learned: {status['memory_stats']['known_facts']}")
    print(f"  Personality Evolution: Stage {status['personality']['evolution_stage']}")
    print("\n✅ Study session complete!")


def example_achievement_tracking():
    """Example: Track achievements and milestones"""
    
    print("\n=== OctoBuddy Achievement Tracking ===\n")
    
    buddy = EnhancedOctoBuddy(CONFIG)
    
    # Complete a major milestone
    print("🎓 Finished a class!")
    result = buddy.handle_event('finished_class')
    print(f"OctoBuddy says: {result['phrase']}\n")
    
    # This is a big achievement - add to long-term memory
    buddy.brain.memory.add_long_term(
        "achievement",
        "Completed Advanced Python Programming class",
        importance=9  # High importance
    )
    
    print("✓ Achievement recorded in long-term memory!")
    
    # Check personality changes
    traits = buddy.brain.personality.get_dominant_traits(5)
    print("\n🎭 Current personality traits:")
    for trait_name, value in traits:
        print(f"  {trait_name}: {value}/10")


def example_custom_skill():
    """Example: Using custom skills"""
    
    print("\n=== OctoBuddy Custom Skills ===\n")
    
    buddy = EnhancedOctoBuddy(CONFIG)
    
    # List available skills
    skills = buddy.expansion.skills.list_skills()
    print(f"Available skills: {len(skills)}")
    for skill in skills:
        print(f"  - {skill['name']}: {skill['description']}")
    print()
    
    # Execute a skill
    if skills:
        skill_name = skills[0]['name']
        print(f"Executing skill: {skill_name}")
        result = buddy.execute_skill(skill_name)
        if result['success']:
            print(f"✓ {result['message']}")
        else:
            print(f"✗ Error: {result.get('error', 'Unknown')}")


def example_personality_evolution():
    """Example: Watching personality evolve"""
    
    print("\n=== OctoBuddy Personality Evolution ===\n")
    
    buddy = EnhancedOctoBuddy(CONFIG)
    
    print("Initial personality:")
    traits = buddy.brain.personality.get_dominant_traits(3)
    for trait_name, value in traits:
        print(f"  {trait_name}: {value}")
    print()
    
    # Simulate learning journey
    print("Simulating learning journey...")
    for i in range(5):
        buddy.handle_event('studied_python')
        buddy.teach('programming', f'Concept {i+1} learned')
    
    print("\nAfter learning:")
    traits = buddy.brain.personality.get_dominant_traits(3)
    for trait_name, value in traits:
        print(f"  {trait_name}: {value}")
    
    # Check evolution
    evo_stage = buddy.brain.personality.traits['evolution_stage']
    print(f"\nEvolution stage: {evo_stage}")


if __name__ == "__main__":
    try:
        # Run all examples
        example_study_session()
        example_achievement_tracking()
        example_custom_skill()
        example_personality_evolution()
        
        print("\n" + "="*50)
        print("All examples completed successfully!")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
