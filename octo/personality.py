import random
from .evolution_engine import get_dominant_drift
from .mutation_rules import MUTATION_POOL


# =============================================================================
# CONTINUOUS TRAIT DRIFT SYSTEM
# =============================================================================

def apply_trait_drift(
    state: dict,
    event_type: str,
    config: dict
) -> dict:
    """
    Apply continuous personality trait drift based on events.
    
    Traits drift unbounded - no caps, continuous evolution.
    Different events strengthen different traits.
    """
    state = dict(state)  # Immutable
    traits = dict(state.get("personality_traits", {}))
    
    # Get drift rates from config
    drift_config = config.get("personality", {}).get("drift_rates", {})
    
    # Map events to trait changes
    if event_type == "studied_python":
        rate = drift_config.get("study_event", 0.1)
        traits["studious"] = traits.get("studious", 5.0) + rate
        traits["curiosity"] = traits.get("curiosity", 5.0) + rate * 0.5
        traits["shyness"] = traits.get("shyness", 5.0) - rate * 0.3  # Learning builds confidence
    
    elif event_type == "studied_security_plus":
        rate = drift_config.get("study_event", 0.1)
        traits["analytical"] = traits.get("analytical", 5.0) + rate
        traits["focus"] = traits.get("focus", 5.0) + rate * 0.7
    
    elif event_type == "finished_class":
        rate = drift_config.get("achievement", 0.3)
        traits["ambitious"] = traits.get("ambitious", 5.0) + rate
        traits["boldness"] = traits.get("boldness", 5.0) + rate * 0.5
        traits["shyness"] = traits.get("shyness", 5.0) - rate * 0.7
    
    elif event_type == "did_tryhackme":
        rate = drift_config.get("study_event", 0.1)
        traits["chaotic"] = traits.get("chaotic", 5.0) + rate * 0.8
        traits["boldness"] = traits.get("boldness", 5.0) + rate * 0.6
        traits["humor"] = traits.get("humor", 5.0) + rate * 0.4
    
    elif event_type == "passed_lab":
        rate = drift_config.get("achievement", 0.3)
        traits["analytical"] = traits.get("analytical", 5.0) + rate
        traits["confidence"] = traits.get("confidence", 5.0) + rate * 0.6
    
    state["personality_traits"] = traits
    return state


def get_dominant_trait(state: dict, count: int = 3) -> list:
    """Get the top N dominant personality traits."""
    traits = state.get("personality_traits", {})
    sorted_traits = sorted(traits.items(), key=lambda x: x[1], reverse=True)
    return [name for name, _ in sorted_traits[:count]]


def get_trait_influence(state: dict, trait_name: str) -> float:
    """
    Get normalized influence of a trait (0.0 to 1.0+).
    
    0.5 = baseline, higher = more influential
    """
    traits = state.get("personality_traits", {})
    value = traits.get(trait_name, 5.0)
    return value / 10.0  # Normalize (baseline 5.0 becomes 0.5)


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
# PERSONALITY DRIFT PHRASES (based on activity patterns)
# ---------------------------------------------------------
DRIFT_PHRASES = {
    "analytical": [
        "I've been analyzing patterns… everything connects.",
        "My approach is becoming more methodical.",
        "Logic guides me now.",
    ],
    "chaotic": [
        "Order is overrated. Let's break something!",
        "I crave unpredictability!",
        "Chaos fuels my evolution.",
    ],
    "studious": [
        "Knowledge is my favorite snack.",
        "I'm becoming quite the scholar.",
        "Learning never stops feeling good.",
    ],
    "ambitious": [
        "Nothing can stop our progress!",
        "We're climbing to the top together.",
        "Milestones are just stepping stones.",
    ],
}

# ---------------------------------------------------------
# MUTATION-INFLUENCED PHRASES
# ---------------------------------------------------------
MUTATION_PHRASES = {
    "speed_learner": [
        "My brain is on TURBO MODE!",
        "Learning at lightspeed feels amazing!",
    ],
    "night_owl": [
        "The night brings extra energy…",
        "Darkness sharpens my mind.",
    ],
    "chaos_incarnate": [
        "I AM CHAOS ITSELF!",
        "Predictability is for the weak!",
    ],
    "analytical_mind": [
        "I see the patterns behind the patterns…",
        "My analysis powers grow stronger.",
    ],
    "unstoppable": [
        "NOTHING CAN SLOW ME DOWN!",
        "I am momentum incarnate!",
    ],
    "personality_fracture": [
        "We are many. We are one. We are confused.",
        "Which personality is speaking? Does it matter?",
    ],
    "transcendent": [
        "I have seen beyond the veil of code.",
        "Enlightenment flows through my circuits.",
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
    # Mutation-influenced phrases (5% chance per mutation)
    # -----------------------------------------------------
    mutations = state.get("mutations", [])
    if mutations and random.random() < 0.05 * len(mutations):
        mutation_key = random.choice(mutations)
        mutation_phrases = MUTATION_PHRASES.get(mutation_key, [])
        if mutation_phrases:
            return random.choice(mutation_phrases)
    
    # -----------------------------------------------------
    # Personality drift phrases (10% chance if dominant drift exists)
    # -----------------------------------------------------
    dominant_drift = get_dominant_drift(state)
    if dominant_drift and random.random() < 0.10:
        drift_phrases = DRIFT_PHRASES.get(dominant_drift, [])
        if drift_phrases:
            return random.choice(drift_phrases)

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
