import random
from .storage import load_state, save_state
from .brain import update_state_from_event, get_mood, get_stage
from .personality import get_phrase_for_event
from .ui_terminal import render
from .evolution_engine import process_evolution_cycle
from . import memory


def handle_event(state, event_type, data=None):
    """
    Handle an event and update state.
    
    Pure function that processes events through the evolution system.
    
    Args:
        state: Current state dict
        event_type: Event identifier (e.g., 'studied_python')
        data: Optional event data
    
    Returns:
        Updated state dict
    """
    config = state.get("config")
    if not config:
        from .config import load_config
        config = load_config()
        state = {**state, "config": config}
    
    # Update state from event (activity tracking)
    state = update_state_from_event(state, event_type, data, config)
    
    # Run evolution cycle (variables, mutations, drift, triggers)
    state = process_evolution_cycle(state, config, event_type)
    
    # Remember event in memory system
    memory.remember_event(event_type, data or {}, config)
    
    return state


class OctoBuddy:
    def __init__(self, config):
        self.config = config
        self.state = load_state()
        self.state["config"] = config  # Attach config to state
        
        # Initialize memory system
        memory.initialize_memory()

    def handle_event(self, event_type, data=None):
        """Apply an event (e.g., 'studied_python', 'finished_course')."""
        # Use pure function
        self.state = handle_event(self.state, event_type, data)

        mood = get_mood(self.state, self.config)
        stage = get_stage(self.state, self.config)
        
        # Check for evolution events to announce
        evolution_events = self.state.get("last_evolution_events", [])
        if evolution_events:
            for event_type_evo, event_data in evolution_events:
                if event_type_evo == "mutation":
                    phrase = f"⚡ MUTATION ACQUIRED: {event_data}! ⚡"
                    render({**self.state, "config": self.config}, mood, stage, phrase)
                    
                    # Record appearance milestone
                    memory.record_appearance_milestone(self.state, f"Mutation: {event_data}")
                    
                elif event_type_evo == "evolution_trigger":
                    phrase = f"🌟 EVOLUTION TRIGGER: {event_data.upper()}! 🌟"
                    render({**self.state, "config": self.config}, mood, stage, phrase)
                    
                    # Record appearance milestone
                    memory.record_appearance_milestone(self.state, f"Trigger: {event_data}")
            
            # Clear evolution events after displaying
            self.state["last_evolution_events"] = []

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
