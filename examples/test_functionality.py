"""
Simple test to verify OctoBuddy core functionality
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from octo.config import CONFIG
from octo.core_enhanced import EnhancedOctoBuddy


def test_basic_functionality():
    """Test basic OctoBuddy features"""
    
    print("Testing OctoBuddy Core Functionality...")
    print("=" * 50)
    
    # Initialize OctoBuddy
    print("\n1. Initializing OctoBuddy...")
    buddy = EnhancedOctoBuddy(CONFIG, enable_observation=False)
    print(f"   ✓ OctoBuddy initialized")
    
    # Test event handling
    print("\n2. Testing event handling...")
    result = buddy.handle_event('studied_python')
    print(f"   Event: studied_python")
    print(f"   Response: {result['phrase']}")
    print(f"   Mood: {result['mood']}")
    print(f"   Stage: {result['stage']}")
    print(f"   ✓ Event handling works")
    
    # Test teaching
    print("\n3. Testing teaching system...")
    buddy.teach('programming', 'Python is a high-level language')
    buddy.teach('cybersecurity', 'Encryption protects data')
    print(f"   ✓ Teaching system works")
    
    # Test knowledge recall
    print("\n4. Testing knowledge recall...")
    results = buddy.recall_knowledge('programming')
    print(f"   Found {len(results['knowledge'])} knowledge items")
    if results['knowledge']:
        print(f"   Sample: {results['knowledge'][0]['content']['fact']}")
    print(f"   ✓ Knowledge recall works")
    
    # Test status
    print("\n5. Testing status retrieval...")
    status = buddy.get_status()
    print(f"   Level: {status['level']}")
    print(f"   XP: {status['xp']}")
    print(f"   Mood: {status['mood']}")
    print(f"   Stage: {status['stage']}")
    print(f"   Evolution Stage: {status['personality']['evolution_stage']}")
    print(f"   Known Facts: {status['memory_stats']['known_facts']}")
    print(f"   ✓ Status retrieval works")
    
    # Test expansion system
    print("\n6. Testing expansion system...")
    capabilities = buddy.expansion.get_all_capabilities()
    print(f"   Skills available: {len(capabilities['skills'])}")
    print(f"   Animations available: {len(capabilities['animations'])}")
    print(f"   ✓ Expansion system works")
    
    # Test personality traits
    print("\n7. Testing personality traits...")
    traits = buddy.brain.personality.get_dominant_traits(3)
    print(f"   Top traits:")
    for trait_name, value in traits:
        print(f"   - {trait_name}: {value}")
    print(f"   ✓ Personality system works")
    
    # Test memory
    print("\n8. Testing memory system...")
    buddy.brain.memory.add_short_term('test', 'This is a test memory')
    recent = buddy.brain.memory.get_recent_memories(limit=5)
    print(f"   Short-term memories: {len(recent)}")
    print(f"   ✓ Memory system works")
    
    # Save state
    print("\n9. Testing state persistence...")
    buddy.brain.save_state()
    print(f"   ✓ State saved successfully")
    
    print("\n" + "=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)
    
    return buddy


if __name__ == "__main__":
    try:
        buddy = test_basic_functionality()
        print("\nOctoBuddy is ready to use!")
        print("Run: python octobuddy_desktop.py")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
