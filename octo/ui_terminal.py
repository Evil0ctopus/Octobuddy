import os
import time
from colorama import Fore, Style, init

init(autoreset=True)

# ---------------------------------------------------------
# TWO-FRAME ANIMATED FACES (wiggle + blink)
# ---------------------------------------------------------
FACES = {
    "sleepy": [
        "( -.- ) zZ",
        "( -.- ) ...",
    ],
    "curious": [
        "( o.O )",
        "( O.o )",
    ],
    "hyper": [
        "( ^o^ )/",
        "\\( ^o^ )",
    ],
    "goofy": [
        "( @v@ )",
        "( @.@ )",
    ],
    "chaotic": [
        "( >:D )",
        "( >XD )",
    ],
    "proud": [
        "( ^‿^ )",
        "( ^▿^ )",
    ],
    "confused": [
        "( ?_? )",
        "( ?.? )",
    ],
    "excited": [
        "( ^O^ )!!",
        "( ^0^ )!!",
    ],
}

DEFAULT_FACE = ["( ^~^ )", "( ^-^ )"]

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
# XP BAR (always green)
# ---------------------------------------------------------
def xp_bar(xp, level, config):
    levels = sorted(config["xp_levels"], key=lambda x: x["threshold"])
    current = next((lv for lv in levels if lv["level"] == level), None)
    next_lv = next((lv for lv in levels if lv["level"] == level + 1), None)

    if not next_lv:
        return "[ MAX LEVEL ]"

    min_xp = current["threshold"]
    max_xp = next_lv["threshold"]

    progress = (xp - min_xp) / (max_xp - min_xp)
    progress = max(0, min(progress, 1))

    filled = int(progress * 20)
    empty = 20 - filled

    return "[" + Fore.GREEN + "#" * filled + Style.RESET_ALL + "-" * empty + "]"

# ---------------------------------------------------------
# CLEAR SCREEN
# ---------------------------------------------------------
def clear():
    os.system("cls" if os.name == "nt" else "clear")

# ---------------------------------------------------------
# MAIN RENDER FUNCTION WITH NEON COLORS + ANIMATION
# ---------------------------------------------------------
def render(state, mood, stage, phrase):
    xp = state.get("xp", 0)
    level = state.get("level", 1)
    config = state["config"]

    frames = FACES.get(mood, DEFAULT_FACE)
    cycles = ANIMATION_LENGTH.get(mood, 4)
    colors = MOOD_COLORS.get(mood, DEFAULT_COLORS)

    frame_color = colors["frame"]
    text_color = colors["text"]

    # Animation cycles
    for _ in range(cycles):
        for frame in frames:
            clear()

            print(frame_color + "========================================")
            print(text_color + "      < OctoBuddy Terminal Interface >")
            print(frame_color + "========================================" + Style.RESET_ALL)

            # Creature display
            print(text_color + f"   {frame}")
            print(text_color + f"   Stage : {stage}")
            print(text_color + f"   Mood  : {mood}")
            print()

            # XP bar (always green)
            print(Fore.YELLOW + f"XP   : {xp}")
            print(Fore.YELLOW + f"Level: {level}")
            print(Fore.YELLOW + f"Prog : {xp_bar(xp, level, config)}")
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

    print(text_color + f"   {frames[0]}")
    print(text_color + f"   Stage : {stage}")
    print(text_color + f"   Mood  : {mood}")
    print()

    print(Fore.YELLOW + f"XP   : {xp}")
    print(Fore.YELLOW + f"Level: {level}")
    print(Fore.YELLOW + f"Prog : {xp_bar(xp, level, config)}")
    print()

    print(frame_color + "----------------------------------------" + Style.RESET_ALL)
    print(text_color + phrase)
    print(frame_color + "========================================" + Style.RESET_ALL)
