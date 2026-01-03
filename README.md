# OctoBuddy (working title)

OctoBuddy is a cute, funny, slightly chaotic creature–AI hybrid that learns and grows with me as I study cybersecurity, Python, and WGU courses.

Inspired by projects like Pwnagotchi (agent loop, plugins, personality), but focused entirely on **safe, legal learning**. OctoBuddy acts as a study companion, XP tracker, and code-explaining buddy as it evolves alongside my skills.

## Features

- **XP Tracking System**: Earn XP through various study and learning activities
- **Dynamic Leveling**: Progress through 100 levels with escalating XP requirements
- **Mood System**: 8 different moods based on your XP (sleepy, curious, hyper, goofy, chaotic, proud, confused, excited)
- **Evolution Stages**: Watch OctoBuddy evolve through 5 stages:
  - Baby (0-100 XP)
  - Learner (100-300 XP)
  - Chaotic Gremlin (300-600 XP)
  - Analyst (600-1000 XP)
  - Fully Evolved Hybrid (1000+ XP)
- **Animated Terminal UI**: Colorful, animated ASCII art with mood-based colors
- **Persistent State**: Your progress is saved between sessions
- **Personality System**: Random quirks and event-specific reactions

## Supported Events

OctoBuddy tracks various learning activities, each awarding different amounts of XP:

- `studied_python` - Basic Python study session (base XP)
- `studied_security_plus` - Security+ certification study (2x XP)
- `finished_class` - Completed a WGU class (10x XP)
- `did_tryhackme` - Completed a TryHackMe room (3x XP)
- `passed_lab` - Passed a lab or practical exercise (5x XP)
- `bug_bounty` - Found and reported a vulnerability (8x XP)
- `ctf_challenge` - Solved a CTF challenge (6x XP)
- `code_review` - Reviewed code or learned from others' code (4x XP)
- `read_documentation` - Read technical documentation (2x XP)

## Early goals

- Track study sessions and earned XP
- Show mood, level, and evolving personality
- React to events (studied Python, finished a class, etc.)
- Run in the terminal at first, then expand to richer UIs
- Eventually:
  - Help explain code I give it
  - Evolve new abilities as I learn new skills (Security+, bug bounties, CTFs)

## Run locally

```bash
pip install -r requirements.txt
python examples/demo_run.py
```

## Usage Examples

Run with specific events:

```bash
# Basic Python study
python examples/demo_run.py studied_python

# Security+ study session
python examples/demo_run.py studied_security_plus

# Completed a CTF challenge
python examples/demo_run.py ctf_challenge

# Found a bug bounty
python examples/demo_run.py bug_bounty

# Code review
python examples/demo_run.py code_review
```

