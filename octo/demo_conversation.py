"""
Demo script to test OctoBuddy's conversation engine.

This demonstrates the new conversation features:
- Message analysis (tone, emotion, topics, keywords)
- Personality-based responses
- Follow-up questions (30% chance)
- Learning from dialogue (vocabulary, phrases, style, grammar)
- Personality drift based on conversation style
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from octo.config import load_config
from octo.storage import load_state
from octo.brain import get_mood
from octo.personality import get_dominant_trait


def simulate_conversation():
    """Simulate a conversation to show the engine's capabilities."""
    
    print("=" * 60)
    print("🐙 OctoBuddy Conversation Engine Demo")
    print("=" * 60)
    
    # Load config and state
    config = load_config()
    state = load_state()
    
    # Get current personality
    mood = get_mood(state, config)
    traits = get_dominant_trait(state, 3)
    
    print(f"\nOctoBuddy's current mood: {mood}")
    print(f"Dominant personality traits: {', '.join(traits)}")
    print("\n" + "-" * 60)
    
    # Example conversations
    test_messages = [
        "Hello OctoBuddy!",
        "I'm working on a really complex algorithm for my project.",
        "I'm feeling a bit anxious about my exam tomorrow.",
        "Do you think machine learning is the future?",
        "Wow this is awesome! I just finished my code!",
        "Can you help me understand recursion?",
        "I'm so tired from work today...",
        "What do you like to learn about?"
    ]
    
    print("\nTest Conversations:")
    print("-" * 60)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n[{i}] User: {message}")
        
        # Simulate what the conversation engine would do
        print("    Analysis:")
        
        # Detect tone
        msg_lower = message.lower()
        if "!" in message or any(w in msg_lower for w in ["awesome", "great", "amazing"]):
            print("      - Tone: excited")
        elif "?" in message:
            print("      - Tone: questioning")
        elif any(w in msg_lower for w in ["sad", "anxious", "tired"]):
            print("      - Tone: negative")
        else:
            print("      - Tone: neutral")
        
        # Detect topics
        topics = []
        if any(w in msg_lower for w in ["algorithm", "code", "machine learning", "recursion"]):
            topics.append("programming")
        if any(w in msg_lower for w in ["learn", "understand", "exam"]):
            topics.append("learning")
        if any(w in msg_lower for w in ["work", "project"]):
            topics.append("work")
        
        if topics:
            print(f"      - Topics: {', '.join(topics)}")
        
        # Detect emotion
        if "anxious" in msg_lower or "worried" in msg_lower:
            print("      - Emotion: anxious")
        elif "tired" in msg_lower:
            print("      - Emotion: tired/sad")
        
        print("    → OctoBuddy would:")
        print("      1. Learn vocabulary from your message")
        print("      2. Extract phrases and grammar patterns")
        print("      3. Detect your writing style (formal/casual/technical)")
        print("      4. Apply personality drift if needed")
        print("      5. Generate a contextual response")
        print("      6. Maybe ask a follow-up question (30% chance)")
    
    print("\n" + "=" * 60)
    print("Memory Storage:")
    print("=" * 60)
    print("\nThe conversation engine saves to:")
    print("  - memory/words.json (learned vocabulary)")
    print("  - memory/phrases.json (common phrases)")
    print("  - memory/style.json (writing style metrics)")
    print("  - memory/grammar.json (grammar patterns)")
    print("  - memory/personality_history.json (drift over time)")
    
    print("\n" + "=" * 60)
    print("Personality Drift Examples:")
    print("=" * 60)
    print("\nFormal/Technical speech → increases 'analytical' and 'studious'")
    print("Casual/Slang speech → increases 'humor' and 'chaotic'")
    print("Emotional speech → increases 'boldness'")
    print("Many questions → increases 'curiosity'")
    
    print("\n" + "=" * 60)
    print("Follow-up Question Examples:")
    print("=" * 60)
    print("\nOctoBuddy might ask:")
    print("  - 'How are you feeling about that?'")
    print("  - 'Should I learn more about that topic?'")
    print("  - 'Want me to remember that?'")
    print("  - 'What made you think about that?'")
    print("  - 'Tell me more?'")
    print("  - 'What do you think?'")
    
    print("\n" + "=" * 60)
    print("✓ Conversation engine ready!")
    print("=" * 60)


if __name__ == "__main__":
    simulate_conversation()
