def render(state, mood, phrase):
    face = build_face(mood)
    print("=" * 40)
    print(face)
    print(f"Name : {state.get('name', 'OctoBuddy')}")
    print(f"XP   : {state.get('xp', 0)}")
    print(f"Level: {state.get('level', 1)}")
    print(f"Mood : {mood}")
    print("-" * 40)
    print(phrase)
    print("=" * 40)

def build_face(mood):
    if mood == "sleepy":
        return "(-_-) zZ"
    if mood == "curious":
        return "(o_O)?"
    if mood == "hyper":
        return "(^o^)/!!!"
    return "(•_•)"
