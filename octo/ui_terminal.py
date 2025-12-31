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
# XP BAR (cyber‑style)
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
# MAIN RENDER FUNCTION WITH ANIMATION
# ---------------------------------------------------------
def render(state, mood, stage, phrase):
    xp = state.get("xp", 0)
    level = state.get("level", 1)
    config = state["config"]

    frames = FACES.get(mood, DEFAULT_FACE)

    # Play 2-frame animation
    for frame in frames:
        clear()

        print(Fore.CYAN + "========================================")
        print(Fore.MAGENTA + "      < OctoBuddy Terminal Interface >")
        print(Fore.CYAN + "========================================" + Style.RESET_ALL)

        # Creature display
        print(Fore.GREEN + f"   {frame}")
        print(Fore.GREEN + f"   Stage : {stage}")
        print(Fore.GREEN + f"   Mood  : {mood}")
        print()

        # XP bar
        print(Fore.YELLOW + f"XP   : {xp}")
        print(Fore.YELLOW + f"Level: {level}")
        print(Fore.YELLOW + f"Prog : {xp_bar(xp, level, config)}")
        print()

        print(Fore.CYAN + "----------------------------------------" + Style.RESET_ALL)

        print(Fore.WHITE + phrase)
        print(Fore.CYAN + "========================================" + Style.RESET_ALL)

        time.sleep(0.12)  # smooth animation timing

