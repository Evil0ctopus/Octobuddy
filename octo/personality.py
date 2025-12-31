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
        "goofy": [
            "I tried to write code but accidentally wrote a sandwich.",
            "I made a variable named 'wiggle'. I regret nothing.",
        ],
        "chaotic": [
            "I added three loops and now everything is on fire.",
            "I don’t know what this code does but I love it.",
        ],
        "proud": [
            "Look at us learning Python like champions.",
            "I leveled up AND I understand functions. Fear me.",
        ],
        "confused": [
            "Why does this variable exist? Why do *any* of us exist?",
            "I stared at the code and the code stared back.",
        ],
        "excited": [
            "YESSSS PYTHON! FEED ME MORE KNOWLEDGE!",
            "I LOVE LEARNING! I LOVE CHAOS! I LOVE YOU! LET’S GO!",
        ],
    },
}


def get_phrase_for_event(event_type, state, mood):
    mood_phrases = PHRASES.get(event_type, {}).get(mood, [])
    if not mood_phrases:
        return "I felt something… not sure what, but it was magical."
    return random.choice(mood_phrases)
