# OctoBuddy Installation & Setup Guide

This guide will help you install and configure OctoBuddy on Windows 10/11.

## Prerequisites

- **Python 3.8 or higher** ([Download Python](https://www.python.org/downloads/))
- **Windows 10 or 11** (for full desktop features)
- **pip** (comes with Python)

## Step-by-Step Installation

### 1. Install Python

If you don't have Python installed:

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. ✅ **IMPORTANT**: Check "Add Python to PATH" during installation
4. Click "Install Now"
5. Verify installation:
   ```bash
   python --version
   pip --version
   ```

### 2. Clone or Download OctoBuddy

**Option A: Using Git**
```bash
git clone https://github.com/Evil0ctopus/Octobuddy.git
cd Octobuddy
```

**Option B: Download ZIP**
1. Download the repository as ZIP
2. Extract to a folder (e.g., `C:\OctoBuddy`)
3. Open Command Prompt in that folder

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- PyQt6 (Desktop UI)
- PyYAML (Configuration)
- Pillow (Image handling)
- psutil (Process monitoring)
- pywin32 (Windows integration)
- colorama (Terminal colors)

### 4. First Run

```bash
python octobuddy_desktop.py
```

You should see OctoBuddy appear in the bottom-right corner of your screen!

## Configuration

### Basic Settings

Edit `config.yaml` to customize OctoBuddy:

```yaml
name: "OctoBuddy"
version: "0.1.0"

xp_per_study_event: 10

xp_system:
  max_level: 100
  base_xp: 50
  multiplier: 2

# Moods change based on XP thresholds
moods:
  - name: "sleepy"
    min_xp: 0
    max_xp: 40
  # ... more moods

# Growth stages
stages:
  - name: "Baby"
    min_xp: 0
    max_xp: 100
  # ... more stages
```

### Enabling Observation (Optional)

To enable window/activity monitoring:

```bash
python octobuddy_desktop.py --enable-observation
```

Or enable it from the chat window:
1. Double-click OctoBuddy
2. Type: `enable observation`

**Note**: This requires `pywin32` on Windows. All observation is local and private.

## Features Setup

### Adding Custom Skills

1. Navigate to `expansions/skills/` (created on first run)
2. Create a new Python file (e.g., `my_skill.py`)
3. Use this template:

```python
def skill_info():
    return {
        "name": "my_skill",
        "description": "What this skill does",
        "author": "Your Name",
        "version": "1.0.0"
    }

def execute(context=None):
    # Your skill logic here
    return {
        "success": True,
        "message": "Skill executed!",
        "data": {}
    }
```

4. Execute from chat: `skill my_skill`

### Adding Custom Animations

1. Navigate to `expansions/animations/`
2. Create a JSON file (e.g., `dance.json`):

```json
{
  "name": "dance",
  "description": "OctoBuddy dances",
  "frames": [
    {
      "ascii": "  \\( ^o^ )/\n   __|__",
      "duration_ms": 200
    },
    {
      "ascii": "  /( ^o^ )\\\n   __|__",
      "duration_ms": 200
    }
  ],
  "loop": true
}
```

### Adding Custom Dialogue

1. Navigate to `expansions/dialogue/`
2. Create a JSON file (e.g., `encouragement.json`):

```json
{
  "category": "encouragement",
  "mood_variants": {
    "happy": [
      "You're doing amazing!",
      "Keep up the great work!"
    ],
    "excited": [
      "WOW! You're crushing it!",
      "THIS IS AWESOME!"
    ]
  }
}
```

## Troubleshooting

### OctoBuddy won't start

**Problem**: Module not found errors
**Solution**: 
```bash
pip install -r requirements.txt --upgrade
```

**Problem**: PyQt6 installation fails
**Solution**: 
```bash
# Try installing PyQt6 separately
pip install PyQt6
```

### Window doesn't appear

**Problem**: OctoBuddy runs but no window shows
**Solution**:
- Check if window is off-screen (try moving it with keyboard: Alt+Space → M → Arrow keys)
- Try terminal mode to verify it's working: `python octobuddy_desktop.py --terminal`

### Observation features don't work

**Problem**: Window monitoring not working
**Solution**:
```bash
# Install Windows-specific dependency
pip install pywin32
```

### State file errors

**Problem**: JSON errors in state files
**Solution**:
- Delete `octo_state.json` to reset state
- Delete files in `memory/` folder to reset memory

## Running on Startup (Windows)

To make OctoBuddy start automatically:

### Option 1: Startup Folder

1. Press `Win + R`
2. Type: `shell:startup` and press Enter
3. Create a shortcut to `octobuddy_desktop.py`
4. Edit shortcut properties:
   - Target: `C:\Path\To\Python\python.exe C:\Path\To\Octobuddy\octobuddy_desktop.py`
   - Start in: `C:\Path\To\Octobuddy`

### Option 2: Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Name: "OctoBuddy"
4. Trigger: At log on
5. Action: Start a program
6. Program: `python.exe`
7. Arguments: `C:\Path\To\Octobuddy\octobuddy_desktop.py`
8. Start in: `C:\Path\To\Octobuddy`

## Updates

To update OctoBuddy:

```bash
# If using git
git pull origin main

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## Uninstallation

To remove OctoBuddy:

1. Stop the application
2. Delete the OctoBuddy folder
3. (Optional) Uninstall Python packages:
   ```bash
   pip uninstall PyQt6 pyyaml pillow psutil pywin32 colorama
   ```

## Getting Help

- Check the main [README.md](README.md)
- Review example files in `expansions/` folders
- Open an issue on GitHub

## Performance Tips

- **Memory usage**: OctoBuddy uses ~50-100MB RAM
- **CPU usage**: Minimal when idle, <1% typically
- **Startup time**: 2-5 seconds
- **Observation overhead**: +5-10MB RAM when enabled

## Privacy & Data

- **All data is local**: Nothing is sent over the network
- **State files**: Stored in `memory/` folder and `octo_state.json`
- **Observation data**: Never leaves your computer
- **No telemetry**: No analytics or tracking

## Next Steps

Once installed:

1. ✅ Run OctoBuddy: `python octobuddy_desktop.py`
2. ✅ Double-click to open chat
3. ✅ Try command: `studied_python`
4. ✅ Teach something: `teach python: Functions are reusable code blocks`
5. ✅ Check status: `status`
6. ✅ Explore custom skills in `expansions/skills/`

Enjoy your new AI companion! 🐙
