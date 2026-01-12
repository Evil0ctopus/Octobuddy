import os
import time
from colorama import Fore, Style, init

# Import evolution engine for decision-making (not rendering)
from .evolution_engine import get_dominant_drift, get_evolution_summary
from .mutation_rules import get_mutation_display_name

init(autoreset=True)

# ---------------------------------------------------------
# TWO-FRAME ANIMATED FACES (wiggle + blink)
# ---------------------------------------------------------
FACES = {
    "sleepy": ["( -.- ) zZ", "( -.- ) ..."],
    "curious": ["( o.O )", "( O.o )"],
    "hyper": ["( ^o^ )/", "\\( ^o^ )"],
    "goofy": ["( @v@ )", "( @.@ )"],
    "chaotic": ["( >:D )", "( >XD )"],
    "proud": ["( ^‿^ )", "( ^▿^ )"],
    "confused": ["( ?_? )", "( ?.? )"],
    "excited": ["( ^O^ )!!", "( ^0^ )!!"],
}

DEFAULT_FACE = ["( ^~^ )", "( ^-^ )"]

# ---------------------------------------------------------
# EVOLUTION ASCII ART WITH FACE SLOT
# ---------------------------------------------------------
EVOLUTION_ART = {
    "Baby": [
        "    .-.",
        "   /   \\",
        "   |=| ",
        "  [FACE_HERE]",
        "  __|__",
    ],
    "Learner": [
        "    .-.",
        "   /   \\",
        "   |=|]───┐",
        "  [FACE_HERE]",
        "   / |    |",
    ],
    "Chaotic Gremlin": [
        r"   \\\|||///",
        "     ^   ^",
        "   [FACE_HERE]",
        r"    /|  ^  |\\" ,
        "     |  V  |",
    ],
    "Analyst": [
        r"    /\_/\\" ,
        "   /     \\",
        "   [FACE_HERE]",
        r"   /|===|\\" ,
    ],
    "Hybrid": [
        r"     /\___/\\" ,
        "   .=|     |=.",
        "   [FACE_HERE]",
        r"   /|  ===  |\\" ,
    ],
}

DEFAULT_EVOLUTION = ["[FACE_HERE]"]

# ---------------------------------------------------------
# MOOD-BASED ANIMATION LENGTH
# ---------------------------------------------------------
ANIMATION_LENGTH = {
    "sleepy": 2,
    "curious": 4,
    "hyper": 8,
    "goofy": 4,
    "chaotic": 10,
    "proud": 4,
    "confused": 3,
    "excited": 8,
}

# ---------------------------------------------------------
# NEON MOOD COLOR PALETTE
# ---------------------------------------------------------
MOOD_COLORS = {
    "sleepy":   {"frame": Fore.BLUE,      "text": Fore.CYAN},
    "curious":  {"frame": Fore.CYAN,      "text": Fore.GREEN},
    "hyper":    {"frame": Fore.YELLOW,    "text": Fore.GREEN},
    "goofy":    {"frame": Fore.MAGENTA,   "text": Fore.YELLOW},
    "chaotic":  {"frame": Fore.MAGENTA,   "text": Fore.RED},
    "proud":    {"frame": Fore.YELLOW,    "text": Fore.WHITE},
    "confused": {"frame": Fore.MAGENTA,   "text": Fore.CYAN},
    "excited":  {"frame": Fore.MAGENTA,   "text": Fore.YELLOW},
}

DEFAULT_COLORS = {"frame": Fore.CYAN, "text": Fore.WHITE}

# ---------------------------------------------------------
# PERSONALITY DRIFT COLOR ACCENTS
# ---------------------------------------------------------
DRIFT_COLORS = {
    "analytical": Fore.BLUE,
    "chaotic": Fore.MAGENTA,
    "studious": Fore.GREEN,
    "ambitious": Fore.YELLOW,
}

# ---------------------------------------------------------
# EVOLUTION INFO RENDERING
# ---------------------------------------------------------
def render_mutations(state, color):
    """Render mutation badges if any exist."""
    mutations = state.get("mutations", [])
    if not mutations:
        return
    
    print()
    print(color + "Mutations:" + Style.RESET_ALL)
    for mutation_key in mutations[:3]:  # Show max 3 to avoid clutter
        name = get_mutation_display_name(mutation_key)
        print(Fore.MAGENTA + f"  ⚡ {name}")
    
    if len(mutations) > 3:
        print(Fore.MAGENTA + f"  + {len(mutations) - 3} more...")


def render_personality_drift(state, color):
    """Render personality drift indicator if dominant drift exists."""
    dominant = get_dominant_drift(state)
    if not dominant:
        return
    
    drift_values = state.get("personality_drift", {})
    drift_percentage = drift_values.get(dominant, 0)
    
    drift_color = DRIFT_COLORS.get(dominant, Fore.WHITE)
    bar_length = int(drift_percentage * 20)
    bar = "█" * bar_length
    
    print()
    print(color + "Personality:" + Style.RESET_ALL)
    print(drift_color + f"  {dominant.capitalize()} {bar} {drift_percentage:.0%}")


def render_evolution_triggers(state, color):
    """Render evolution trigger badges if any exist."""
    triggers = state.get("evolution_triggers", [])
    if not triggers:
        return
    
    print()
    print(color + "Achievements:" + Style.RESET_ALL)
    for trigger in triggers[:2]:  # Show max 2
        print(Fore.YELLOW + f"  🌟 {trigger.replace('_', ' ').title()}")
    
    if len(triggers) > 2:
        print(Fore.YELLOW + f"  + {len(triggers) - 2} more...")

# ---------------------------------------------------------
# CLEAR SCREEN
# ---------------------------------------------------------
def clear():
    os.system("cls" if os.name == "nt" else "clear")

# ---------------------------------------------------------
# MAIN RENDER FUNCTION WITH EVOLUTION + FACE SLOT + ANIMATION
# ---------------------------------------------------------
def render(state, mood, stage, phrase):
    config = state["config"]

    frames = FACES.get(mood, DEFAULT_FACE)
    cycles = ANIMATION_LENGTH.get(mood, 4)
    colors = MOOD_COLORS.get(mood, DEFAULT_COLORS)
    evo_art = EVOLUTION_ART.get(stage, DEFAULT_EVOLUTION)

    frame_color = colors["frame"]
    text_color = colors["text"]

    # Animation cycles
    for _ in range(cycles):
        for frame in frames:
            clear()

            print(frame_color + "========================================")
            print(text_color + "      < OctoBuddy Terminal Interface >")
            print(frame_color + "========================================" + Style.RESET_ALL)

            # Evolution body with face slot replaced
            for line in evo_art:
                if "[FACE_HERE]" in line:
                    print(text_color + "   " + line.replace("[FACE_HERE]", frame))
                else:
                    print(text_color + "   " + line)

            print(text_color + f"   Stage : {stage}")
            print(text_color + f"   Mood  : {mood}")
            print()
            
            # Show evolution info during animation (mutations, drift, triggers)
            render_mutations(state, frame_color)
            render_personality_drift(state, frame_color)
            render_evolution_triggers(state, frame_color)
            print()

            print(frame_color + "----------------------------------------" + Style.RESET_ALL)
            print(text_color + phrase)
            print(frame_color + "========================================" + Style.RESET_ALL)

            time.sleep(0.10)

    # Final static frame
    clear()

    print(frame_color + "========================================")
    print(text_color + "      < OctoBuddy Terminal Interface >")
    print(frame_color + "========================================" + Style.RESET_ALL)

    for line in evo_art:
        if "[FACE_HERE]" in line:
            print(text_color + "   " + line.replace("[FACE_HERE]", frames[0]))
        else:
            print(text_color + "   " + line)

    print(text_color + f"   Stage : {stage}")
    print(text_color + f"   Mood  : {mood}")
    print()
    
    # Show evolution info in final frame
    render_mutations(state, frame_color)
    render_personality_drift(state, frame_color)
    render_evolution_triggers(state, frame_color)
    print()

    print(frame_color + "----------------------------------------" + Style.RESET_ALL)
    print(text_color + phrase)
    print(frame_color + "========================================" + Style.RESET_ALL)
