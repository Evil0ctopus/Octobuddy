import time
import random

def render(state, mood, stage, phrase):
    face = build_face(mood, stage)

    print("=" * 40)

    # 20% chance to animate the face
    if random.random() < 0.20:
        animate_face(face)
    else:
        print(face)

    print(f"Name : {state.get('name', 'OctoBuddy')}")
    print(f"XP   : {state.get('xp', 0)}")
    print(f"Level: {state.get('level', 1)}")
    print(f"Stage: {stage}")
    print(f"Mood : {mood}")
    print("-" * 40)
    print(phrase)
    print("=" * 40)


def animate_face(face):
    animations = [
        [face, face.replace("(", "(~"), face.replace(")", "~)")],  # wiggle
        [face, face.replace("•", "o"), face],  # blink
        [face, face + " ✨", face],  # sparkle
    ]

    frames = random.choice(animations)

    for f in frames:
        print("\r" + f, end="")
        time.sleep(0.15)

    print()  # move to next line


def build_face(mood, stage):
    # Stage-based overrides
    if stage == "Baby":
        return "(•ᴗ•)ﾉ"
    if stage == "Learner":
        return "(^o^)/"
    if stage == "Chaotic Gremlin":
        return "(>_<)🔥"
    if stage == "Analyst":
        return "(•̀ᴗ•́)و"
    if stage == "Fully Evolved Hybrid":
        return "＼(≧▽≦)／✨"

    # Fallback to mood-based faces
    faces = {
        "sleepy": "(-_-) zZ",
        "curious": "(o_O)?",
        "hyper": "(^o^)/!!!",
        "goofy": "(ᵔᴥᵔ)",
        "chaotic": "(>_<)🔥",
        "proud": "(•̀ᴗ•́)و ̑̑",
        "confused": "(⊙_☉)",
        "excited": "＼(≧▽≦)／",
    }
    return faces.get(mood, "(•_•)")

