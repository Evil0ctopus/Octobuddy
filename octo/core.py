import random
from .storage import load_state, save_state
from .brain import update_state_from_event, get_mood, get_stage
from .personality import get_phrase_for_event
from .ui_terminal import render

class OctoBuddy:
    def __init__(self, config):
        self.config = config
        self.state = load_state()

    def handle_event(self, event_type, data=None):
        """Apply an event (e.g., 'studied_python', 'finished_course')."""
        self.state = update_state_from_event(self.state, event_type, data, self.config)

        mood = get_mood(self.state, self.config)
        stage = get_stage(self.state, self.config)

        # Random idle thoughts (10% chance)
        if random.random() < 0.10:
            phrase = random.choice([
                "I was just thinking about octopuses…",
                "Do you ever wonder if code dreams?",
                "I feel a strange urge to reorganize your folders.",
                "If I had hands, I would high-five you.",
            ])
            render({**self.state, "config": self.config}, mood, stage, phrase)
            save_state(self.state)
            return

        # Normal event reaction
        phrase = get_phrase_for_event(event_type, self.state, mood, stage)

        render({**self.state, "config": self.config}, mood, stage, phrase)

        save_state(self.state)
