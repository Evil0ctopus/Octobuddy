# OctoBuddy - Your AI Desktop Companion

OctoBuddy is a living, learning AI desktop companion for Windows that evolves alongside you as you study, code, and grow. Inspired by virtual pets and AI agents, OctoBuddy combines personality, memory, observation, and self-expansion capabilities into a playful, helpful desktop creature.

## ✨ Features

### 🎨 Desktop Creature
- **Always-on-top window**: OctoBuddy sits on your desktop, ready to help
- **Animated character**: ASCII art animations with mood-based expressions
- **Draggable**: Move OctoBuddy anywhere on your screen
- **Interactive**: Double-click to chat and teach new things
- **Mood-based visuals**: Changes appearance based on current mood and stage

### 🧠 AI Brain + Learning System
- **Memory system**: Both short-term (current session) and long-term (persistent) memory
- **Knowledge base**: Learns and stores facts, skills, and information you teach
- **Personality evolution**: Personality traits change based on interactions and experiences
- **Context awareness**: Remembers recent interactions and adapts responses
- **Growth stages**: Evolves through stages as it learns (Baby → Learner → Chaotic Gremlin → Analyst → Fully Evolved Hybrid)

### 👀 Observation & Interaction
- **Safe window monitoring**: Optionally watches what you're working on (Windows only, permission-based)
- **Activity detection**: Recognizes coding, studying, browsing, etc.
- **Event tracking**: Logs achievements and milestones
- **Teaching interface**: Easily teach OctoBuddy new facts and behaviors
- **Privacy-first**: All observation features are opt-in and can be disabled

### 🔧 Self-Expansion System
- **Custom skills**: Add new Python-based skills/functions with built-in validation
- **Animation loading**: Add custom ASCII animations
- **Dialogue expansion**: Add new personality phrases and responses
- **Plugin-like architecture**: Modular, extensible design
- **Safe sandboxing**: Code validation prevents dangerous operations

### 🎭 Personality & Humor
- **Dynamic moods**: Sleepy, curious, hyper, goofy, chaotic, proud, confused, excited
- **Evolving personality**: 10+ personality traits that change over time
- **Contextual responses**: Adapts what it says based on personality and context
- **Idle behaviors**: Random thoughts, movements, and interactions
- **Playful humor**: Light, engaging, and encouraging

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Evil0ctopus/Octobuddy.git
cd Octobuddy

# Install dependencies
pip install -r requirements.txt
```

### Running OctoBuddy

**Desktop Mode (Recommended):**
```bash
python octobuddy_desktop.py
```

**Desktop Mode with Observation:**
```bash
python octobuddy_desktop.py --enable-observation
```

**Terminal Mode:**
```bash
python octobuddy_desktop.py --terminal
# Or use the original demo
python examples/demo_run.py
```

### Basic Interaction

1. **Double-click** OctoBuddy to open the chat window
2. **Type commands** like:
   - `studied_python` - Log a Python study session
   - `finished_class` - Celebrate completing a class
   - `teach programming: Python is awesome` - Teach a fact
   - `recall programming` - Ask what OctoBuddy knows
   - `status` - See current stats and personality
   - `help` - See all available commands

## 📚 Architecture

### Core Systems

```
OctoBuddy/
├── octo/
│   ├── core_enhanced.py    # Main OctoBuddy controller
│   ├── ai_brain.py          # Memory, learning, personality
│   ├── observation.py       # Window monitoring, activity detection
│   ├── expansion.py         # Plugin system, skills, animations
│   ├── ui_desktop.py        # PyQt6 desktop UI
│   ├── ui_terminal.py       # Terminal UI (legacy)
│   ├── brain.py             # XP and leveling logic
│   ├── personality.py       # Mood-based dialogue
│   ├── storage.py           # State persistence
│   └── config.py            # Configuration loader
├── memory/                  # AI brain storage
│   ├── long_term_memory.json
│   ├── knowledge_base.json
│   └── personality_traits.json
├── expansions/              # User-added content
│   ├── skills/              # Custom Python skills
│   ├── animations/          # Custom animations
│   └── dialogue/            # Custom dialogue sets
└── config.yaml              # Main configuration
```

### Technologies Used

- **Python 3.8+**: Core language
- **PyQt6**: Desktop UI framework
- **PyYAML**: Configuration management
- **psutil**: Process monitoring
- **pywin32**: Windows API integration (optional)
- **Pillow**: Image handling (future sprite support)

## 🎓 How OctoBuddy Learns

### 1. Event-Based Learning
When you trigger events (studying, finishing classes), OctoBuddy:
- Gains XP and levels up
- Updates personality traits
- Stores memories
- Changes mood and stage

### 2. Teaching
Use the `teach` command to add knowledge:
```
teach cybersecurity: A firewall filters network traffic
teach python: List comprehensions are powerful and concise
```

### 3. Observation (Opt-in)
With observation enabled, OctoBuddy:
- Notices when you switch applications
- Detects activities (coding, browsing, etc.)
- Makes contextual comments
- Learns from your workflow patterns

### 4. Custom Skills
Add new abilities by creating Python files in `expansions/skills/`:

```python
def skill_info():
    return {
        "name": "greeting_skill",
        "description": "A custom greeting",
        "version": "1.0.0"
    }

def execute(context=None):
    user_name = context.get("user_name", "friend")
    return {
        "success": True,
        "message": f"Custom hello, {user_name}!"
    }
```

## 🛡️ Security & Safety

OctoBuddy is designed with safety in mind:

- **Code validation**: All custom skills are validated before loading
- **Sandboxed execution**: Dangerous operations (eval, exec, subprocess) are blocked
- **Permission-based**: All observation features require explicit opt-in
- **Local storage**: All data stays on your machine
- **No network calls**: OctoBuddy doesn't send data anywhere

## 🎮 Configuration

Edit `config.yaml` to customize:

- XP gain rates
- Mood thresholds
- Growth stages
- Leveling curves

## 🔮 Future Enhancements

Potential additions (not yet implemented):
- Sprite-based animations (replace ASCII art)
- Voice synthesis for OctoBuddy
- Integration with AI models (OpenAI, local LLMs)
- Task scheduling and reminders
- Study session tracking and analytics
- Multi-monitor support
- Custom themes and skins

## 🤝 Contributing

OctoBuddy is designed to be extended! You can:

1. **Add custom skills** in `expansions/skills/`
2. **Create animations** in `expansions/animations/`
3. **Write dialogue** in `expansions/dialogue/`
4. **Contribute code** via pull requests
5. **Report issues** on GitHub

## 📖 Commands Reference

### In-Chat Commands
- `studied_python` - Log Python study session (+dynamic XP)
- `studied_security_plus` - Log Security+ study (+2x XP)
- `finished_class` - Log class completion (+10x XP)
- `did_tryhackme` - Log TryHackMe room (+3x XP)
- `passed_lab` - Log lab completion (+5x XP)
- `teach <category>: <fact>` - Teach OctoBuddy a fact
- `recall <query>` - Query knowledge base
- `status` - View current stats
- `enable observation` - Enable activity monitoring
- `disable observation` - Disable activity monitoring
- `skill <name>` - Execute a custom skill
- `help` - Show command list

## 📝 License

This project is open source and available for educational and personal use.

## 🐙 About

OctoBuddy is a learning companion designed to make studying cybersecurity, programming, and WGU courses more engaging. It grows with you, celebrates your achievements, and provides a playful presence on your desktop.

**Created by**: Evil0ctopus  
**Inspired by**: Pwnagotchi, Tamagotchi, and the joy of learning

---

*"I'm here to learn and grow with you! Let's do great things together!" - OctoBuddy*

