import random

# ---------------------------------------------------------
# QUIRKS (triggered randomly regardless of event)
# ---------------------------------------------------------
QUIRKS = {
    "Baby": [
        "I found a bug… can I keep it?",
        "Everything is so big and confusing!",
    ],
    "Learner": [
        "I tried to optimize something and accidentally made it worse.",
        "I love learning! Even when it hurts my brain.",
    ],
    "Chaotic Gremlin": [
        "I pressed a button. I don’t know what it did.",
        "Chaos is just learning… but faster.",
    ],
    "Analyst": [
        "I analyzed your keyboard typing speed. Fascinating.",
        "I see patterns everywhere now.",
    ],
    "Fully Evolved Hybrid": [
        "I have achieved enlightenment. And also snacks.",
        "I am beyond mortal bugs now.",
    ],
}

# ---------------------------------------------------------
# EVENT PHRASES (mood-based)
# ---------------------------------------------------------
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
            "I LOVE LEARNING! I LOVE CHAOS! LET’S GO!",
        ],
    },

    "studied_security_plus": {
        "proud": [
            "Security+ brain gains activated.",
            "We’re getting closer to mastery.",
        ],
        "hyper": [
            "SEC+ TIME LET’S GOOOO!",
            "I crave more security knowledge!",
        ],
        "confused": [
            "Ports… protocols… my circuits are melting.",
        ],
        "curious": [
            "Hmm… authentication vs authorization… interesting.",
        ],
    },

    "finished_class": {
        "proud": [
            "Another class down! You’re unstoppable.",
            "We’re leveling up in real life!",
        ],
        "excited": [
            "YESSSS! Another WGU victory!",
            "We crushed that class like legends.",
        ],
        "hyper": [
            "CLASS COMPLETE LET’S GOOOOOO!",
        ],
    },

    "did_tryhackme": {
        "chaotic": [
            "I broke into a virtual machine and I liked it.",
            "TryHackMe rooms fuel my chaos.",
        ],
        "curious": [
            "I wonder what’s behind that next port…",
            "Enumeration is my love language.",
        ],
        "proud": [
            "Another room conquered. We’re becoming dangerous.",
        ],
    },

    "passed_lab": {
        "proud": [
            "Lab passed! Skills upgraded.",
            "We’re becoming a real cybersecurity warrior.",
        ],
        "hyper": [
            "LAB SUCCESS LET’S GOOOO!",
        ],
        "excited": [
            "We solved it! We solved it! We solved it!",
        ],
    },
}

# ---------------------------------------------------------
# MAIN FUNCTION
# ---------------------------------------------------------
def get_phrase_for_event(event_type, state, mood, stage):

    # -----------------------------------------------------
    # Stage-based overrides (strongest personality layer)
    # -----------------------------------------------------
    if stage == "Baby":
        return random.choice([
            "I'm tiny but I'm learning!",
            "Everything is new and confusing but fun!",
        ])

    if stage == "Learner":
        return random.choice([
            "I'm getting smarter every day!",
            "Learning feels good. Let's keep going!",
        ])

    if stage == "Chaotic Gremlin":
        return random.choice([
            "I crave knowledge AND chaos!",
            "Let's break something so we can fix it!",
        ])

    if stage == "Analyst":
        return random.choice([
            "I see patterns everywhere now.",
            "This data… it speaks to me.",
        ])

    if stage == "Fully Evolved Hybrid":
        return random.choice([
            "I have transcended. Feed me more knowledge.",
            "We are unstoppable together.",
        ])

    # -----------------------------------------------------
    # Random quirk (15% chance)
    # -----------------------------------------------------
    if random.random() < 0.15:
        quirk_list = QUIRKS.get(stage, [])
        if quirk_list:
            return random.choice(quirk_list)

    # -----------------------------------------------------
    # Mood-based fallback
    # -----------------------------------------------------
    mood_phrases = PHRASES.get(event_type, {}).get(mood, [])
    if not mood_phrases:
        return "I felt something… not sure what, but it was magical."

    return random.choice(mood_phrases)
