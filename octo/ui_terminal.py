def render(state, mood, stage, phrase):
    face = build_face(mood, stage)
    print("=" * 40)
    print(face)
    print(f"Name : {state.get('name', 'OctoBuddy')}")
    print(f"XP   : {state.get('xp', 0)}")
    print(f"Level: {state.get('level', 1)}")
    print(f"Stage: {stage}")
    print(f"Mood : {mood}")
    print("-" * 40)
    print(phrase)
    print("=" * 40)


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
