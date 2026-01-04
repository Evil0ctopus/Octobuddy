# 🐙 OctoBuddy - Self-Evolving Desktop Companion

OctoBuddy is a fully autonomous AI creature that lives on your Windows desktop, continuously evolving based on your activities, interactions, and its own learning journey.

## ✨ Features

### 🧬 Infinite Evolution System
- **No XP or Levels** - Evolution is continuous and unbounded
- **7 Evolution Variables**: curiosity, creativity, confidence, calmness, chaos, empathy, focus
- **Open-ended Growth** - Variables drift infinitely based on activities
- **Variable Interactions** - Variables affect each other dynamically

### 🎨 Procedural HD Pixel Art
- **128x128 Resolution** - High-quality procedural rendering
- **Evolution-Aware** - Appearance changes with mutations, drift, and mood
- **Dynamic Colors** - Palette shifts based on personality and stage
- **Real-time Rendering** - Smooth 30 FPS animation

### 🧪 Mutation Engine
- **Activity-Driven** - Mutations triggered by learning and milestones
- **7 Unique Mutations** - From Speed Learner to Transcendent
- **Rarity System** - Common, Uncommon, Rare, Legendary mutations
- **Cumulative Effects** - Mutations stack and compound

### 🎭 Personality Drift
- **7 Continuous Traits**: humor, boldness, shyness, analytical, chaotic, studious, ambitious
- **No Caps** - Traits drift infinitely based on behavior
- **Event-Responsive** - Every action shapes personality
- **Dynamic Phrases** - Dialogue adapts to current traits

### ⚡ Ability Expansion System
- **Plugin Architecture** - New abilities can be added dynamically
- **Prerequisite System** - Abilities unlock based on mutations, traits, and triggers
- **Cost System** - Abilities consume evolution variables
- **Built-in Abilities**: Analyze Pattern, Creative Burst, Chaos Mode

### 🎬 Procedural Animation
- **Spring Physics** - Realistic tentacle movement
- **Mood-Based Motion** - Speed and amplitude vary with evolution vars
- **Cursor Tracking** - Eyes and tentacles follow your mouse
- **Event Reactions** - Celebrates achievements, reacts to mutations
- **Idle Fidgeting** - Continuous subtle movement

### 🧠 Memory & Learning
- **Short-term Memory** - Recent events and interactions
- **Long-term Memory** - User preferences and patterns
- **Personality Memory** - Historical trait evolution
- **Appearance Memory** - Visual evolution milestones
- **Ability Memory** - Usage tracking and statistics

### � Drag-and-Drop Learning
- **File Learning Zone** - Drop files to teach OctoBuddy
- **Multi-Format Support** - .txt, .md, .rtf, .json, .pdf (with PyPDF2)
- **Vocabulary Extraction** - Learns new words and frequencies
- **Phrase Learning** - Captures bigrams and trigrams
- **Style Analysis** - Detects sentence length, punctuation patterns
- **Grammar Detection** - Identifies passive voice, contractions, complexity
- **Personality Drift** - Formal text → analytical, Casual → humorous, Technical → studious
- **Memory Persistence** - Saves learned content to `memory/` folder
- **Visual Feedback** - Shows learning progress via speech bubbles
### 💬 Conversation Engine
- **Message Analysis** - Detects tone, emotion, topics, and keywords
- **Contextual Responses** - Replies based on personality, mood, and learned vocabulary
- **Follow-up Questions** - Sometimes asks questions to continue dialogue (30% chance)
- **Dialogue Learning** - Learns vocabulary, phrases, style, and grammar from conversations
- **Personality Drift** - Speech patterns influence OctoBuddy's personality over time
- **Empathetic Responses** - Detects and responds to emotions (happy, sad, angry, anxious)
- **Topic Awareness** - Recognizes programming, learning, work, and personal topics
- **Natural Responses** - Short, creature-like replies (not long paragraphs)
- **Memory Integration** - Uses learned vocabulary for more natural conversations
### �🖥️ Windows Desktop UI
- **Always-On-Top** - Stays visible across all apps
- **Transparent Background** - Seamless desktop integration
- **Click & Drag** - Move OctoBuddy anywhere
- **Right-Click Menu** - Feed, pet, use abilities, view stats
- **30 FPS Rendering** - Smooth, responsive animation

## 📦 Installation

### Prerequisites

- **Python 3.8+**
- **Windows 10/11**

### Dependencies

Install required packages:

```powershell
pip install PyQt5 numpy pyyaml colorama
```

Or install all dependencies at once:

```powershell
pip install -r requirements.txt
```

### Setup

1. Clone or download this repository
2. Navigate to the `octo` directory
3. Run the companion:

```powershell
python main.py
```

## 🚀 Usage

### Desktop Companion Mode (Default)

Launch the visual desktop companion:

```powershell
python main.py
```

**Controls:**
- **Left-click & drag**: Move OctoBuddy around the screen
- **Right-click**: Open context menu
  - 📊 **Info**: View current stage, mood, mutations
  - ⚡ **Abilities**: Execute available abilities
  - 🍔 **Feed**: Increase happiness, trigger evolution
  - 👋 **Pet**: Social interaction, boost empathy
  - � **Talk**: Chat with OctoBuddy (personality-based responses)
  - 🚪 **Quit**: Close companion (auto-saves)
- **Drag & Drop Files**: Drop text files onto the blue zone to teach OctoBuddy
  - Supported formats: `.txt`, `.md`, `.rtf`, `.json`, `.pdf`
  - OctoBuddy learns vocabulary, phrases, writing style, and grammar
  - Personality drifts based on content (formal/casual/technical)
  - All learned content saved to `memory/` folder

### Terminal Mode (Legacy)

Run in terminal for testing:

```powershell
python main.py --terminal
```

Interactive menu for triggering events manually.

### Test Mode

Run system tests to verify everything works:

```powershell
python main.py --test
```

## 📁 Project Structure

```
octo/
├── abilities/              # Ability expansion system
│   └── __init__.py        # Built-in abilities + registry
├── desktop/               # Desktop UI package
│   ├── __init__.py
│   └── companion.py       # PyQt5 desktop window
├── memory/                # Persistent memory storage (created at runtime)
│   ├── short_term.json
│   ├── long_term.json
│   ├── personality_history.json
│   ├── appearance_history.json
│   └── ability_memory.json
├── animation.py           # Procedural animation engine
├── brain.py               # Decision logic (mood, stage)
├── config.py              # Configuration loader
├── config.yaml            # Central configuration file
├── core.py                # Main orchestration
├── evolution_engine.py    # Evolution system orchestration
├── main.py                # Entry point
├── memory.py              # Memory & learning system
├── mutation_rules.py      # Data-driven mutation definitions
├── personality.py         # Personality trait system
├── pixel_art.py           # Procedural renderer
├── storage.py             # State persistence
└── ui_terminal.py         # Terminal UI (legacy)
```

## ⚙️ Configuration

Edit `config.yaml` to customize OctoBuddy:

### Evolution Variables

```yaml
evolution:
  defaults:
    curiosity: 5.0
    creativity: 5.0
    # ... adjust starting values
  
  drift_rates:
    learning_event: 0.1    # How much variables change per event
    milestone_event: 0.5   # Bigger changes for milestones
```

### Personality Traits

```yaml
personality:
  defaults:
    humor: 5.0
    boldness: 5.0
    # ... adjust starting values
  
  drift_rates:
    study_event: 0.1
    achievement: 0.3
```

### Animation Settings

```yaml
animation:
  tentacle_physics:
    spring_constant: 0.5   # Springiness
    damping: 0.8          # Resistance
  
  idle_fidget:
    frequency: 2.0        # Movements per second
    amplitude: 5.0        # Movement size
```

### Desktop UI

```yaml
desktop:
  window_size: 128
  framerate: 30
  start_position: "bottom_right"  # or "top_left", "center", etc.
```

## 🎮 Triggering Evolution

OctoBuddy evolves through activities:

### Learning Events
- **Study Python** - Boosts curiosity, focus, studiousness
- **Study Security+** - Boosts focus, analytical traits
- **TryHackMe Rooms** - Boosts chaos, boldness, creativity

### Milestones
- **Finish Class** - Major boost to confidence, ambition
- **Pass Lab** - Boost confidence, analytical thinking

### Interactions
- **Feed** - Increases happiness, triggers evolution cycle
- **Pet** - Boosts empathy, calmness

### Abilities
- **Analyze Pattern** - Costs focus, boosts analytical trait
- **Creative Burst** - Costs calmness, massively boosts creativity
- **Chaos Mode** - Costs calmness, embraces unpredictability

## 📊 Evolution Mechanics

### Mutation Chances

Mutations occur randomly based on total activity:
- **Base Chance**: 0.5%
- **Activity Scaling**: +0.009% per activity point
- **Max Chance**: 5%
- **Diminishing Returns**: Each mutation reduces future chance by 10%

### Evolution Triggers

Special achievements unlock permanent evolution stages:
- **Ascension**: 500+ total activity + 3 mutations
- **Chaos Master**: 50+ TryHackMe rooms + Chaos Incarnate mutation
- **Scholar**: 10+ classes finished + analytical drift >0.5
- **Hybrid Form**: Balanced personality drift across all traits

### Stage Progression

Based on total activity and personality drift:
- **Baby** (<10 activity)
- **Learner** (10-50 activity)
- **Specialist** (50-150 activity) - Chaotic Gremlin or Analyst based on drift
- **Advanced** (150-300 activity)
- **Fully Evolved Hybrid** (300+ activity or special triggers)

## 🧬 Extending OctoBuddy

### Adding New Abilities

Create a Python file in `abilities/` directory:

```python
from octo.abilities import ability

@ability(
    name="my_ability",
    description="Does something cool",
    cost={"focus": 2.0},
    prerequisites={"traits": {"curiosity": 10.0}}
)
def my_ability_impl(context):
    # Implementation
    return {
        "message": "Success!",
        "data": {...},
        "state_changes": {...}
    }
```

### Adding New Mutations

Edit `mutation_rules.py` and add to `MUTATION_POOL`:

```python
"my_mutation": {
    "name": "My Mutation",
    "description": "Custom effect",
    "rarity": "uncommon",
    "modifiers": {
        "chaos_factor": 1.5,
    },
}
```

### Adding New Events

Events are defined in `brain.py` and `personality.py`. Add new event types to:
1. `update_state_from_event()` in `brain.py`
2. `apply_trait_drift()` in `personality.py`
3. `apply_evolution_var_drift()` in `evolution_engine.py`
4. `PHRASES` dict in `personality.py`

## 🐛 Troubleshooting

### PyQt5 Installation Issues

If PyQt5 fails to install:

```powershell
pip install PyQt5 --prefer-binary
```

### Window Not Appearing

Check if OctoBuddy is hidden behind other windows - it should be always-on-top. Try:
1. Close all other windows
2. Check taskbar for OctoBuddy (should not appear there)
3. Re-run `python main.py`

### State Corruption

If state becomes corrupted:

```powershell
# Delete state file to reset
Remove-Item octo_state.json

# Or run tests to verify
python main.py --test
```

### Memory Directory Issues

Memory system creates `memory/` directory automatically. If you get permission errors, manually create it:

```powershell
New-Item -ItemType Directory -Path memory
```

## 📝 Architecture Notes

OctoBuddy follows strict architectural principles from `.github/copilot-instructions.md`:

- **Logic/Presentation Separation**: Decision logic in `brain.py`, rendering in `pixel_art.py`/`ui_terminal.py`
- **Pure Functions**: All core functions accept `(state, config)` and return new state
- **Immutable State**: State is shallow-copied before modification
- **Data-Driven**: Mutations, abilities, and configuration defined as data, not code
- **Explicit Flow**: `core.py` orchestrates, modules don't call each other directly

## 🤝 Contributing

OctoBuddy is designed to be extensible:

1. **New abilities**: Add to `abilities/` directory
2. **New mutations**: Edit `mutation_rules.py`
3. **New visual effects**: Edit `pixel_art.py`
4. **New personality traits**: Edit `personality.py`
5. **New event types**: Edit `brain.py`, `personality.py`, `evolution_engine.py`

Follow the existing patterns and maintain logic/presentation separation.

## 📜 License

MIT License - Free to use, modify, and distribute.

## 🙏 Acknowledgments

Built with:
- **PyQt5** - Desktop UI framework
- **NumPy** - Pixel art rendering
- **PyYAML** - Configuration management
- **Colorama** - Terminal colors

---

**Enjoy your journey with OctoBuddy! 🐙✨**

*Remember: OctoBuddy evolves with you. Every study session, every achievement, every interaction shapes its personality and appearance. There are no limits to how far it can grow.*
