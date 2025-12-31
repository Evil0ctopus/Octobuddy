import random

PHRASES = {
    "studied_python": {
        "sleepy": [
            "We did Python… I need a nap now.",
            "My brain is warm. That’s a good sign, right?",
        ],
        "curious": [
            "Loops! Functions! My circuits are tingling.",
            "I almost understand this… which is terrifying and exciting.",
        ],
        "hyper": [
            "PYTHON TIME LET'S GOOOOO!",
            "I learned a function and now I think I'm unstoppable.",
        ],
    },
    # Future events: 'finished_class', 'studied_security_plus', etc.
}

def get_phrase_for_event(event_type, state, mood):
    mood_phrases = PHRASES.get(event_type, {}).get(mood, [])
    if not mood_phrases:
        return "I felt something… not sure what, but it was magical."
    return random.choice(mood_phrases)
