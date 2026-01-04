# Copilot instructions for the OctoBuddy codebase

## Big picture

- OctoBuddy is a Python project under `octo/` that implements an evolving companion rendered in the terminal.
- Logic (evolution, personality, state) is kept separate from presentation (terminal UI) to allow future UIs (pixel art, desktop companion) to plug into the same core.
- Data flows from configuration (`config.yaml`) into `octo/config.py`, then through a `state`/`config` pair passed into core, brain, storage, personality, and UI layers.

## Key modules

- `octo/core.py`: Orchestrates the main control flow. Reads config/state, calls evolution logic in `brain.py`, personality in `personality.py`, and rendering in `ui_terminal.py`.
- `octo/brain.py`: Contains evolution and stage/behavior decision logic. Keep this focused on *what* state should be, not *how* it is displayed.
- `octo/config.py`: Loads and normalizes configuration from `config.yaml`. Add new evolution/effect parameters here instead of hardcoding constants.
- `octo/storage.py`: Handles loading/saving persistent state. Add new persistent fields here and thread them through the `state` object.
- `octo/personality.py`: Defines phrases, quirks, and personality mapping. Centralize text and behavior mappings here rather than scattering strings.
- `octo/ui_terminal.py`: Renders OctoBuddy in the terminal (ASCII art, status, etc.). Keep this focused on output only; call into `brain`/`personality` for decisions.
- `octo/mutation_rules.py`: Data-driven mutation definitions and selection logic. All mutation configuration lives here as pure data structures.
- `octo/evolution_engine.py`: Implements mutations, personality drift, and evolution triggers. Pure functions that transform state based on activity patterns.
- `octo/pixel_art.py`: Procedural 128x128 pixel renderer. Pure function that generates visuals from state without modifying it. Evolution-aware (mutations/drift affect appearance).

## Conventions and patterns

- Prefer **small, composable functions** that accept `(state, config)` rather than large classes with hidden state.
- Use **pure functions** for decisions (e.g., choosing stage, mood, next action) and apply side effects (printing, file IO) at the edges in `core` or UI modules.
- When adding new features, follow the pattern:
  - **Config**: add knobs/flags to `config.yaml` and wire them in `octo/config.py`.
  - **State**: persist new fields in `octo/storage.py` and pass through `state`.
  - **Logic**: implement decision/evolution logic in `octo/brain.py` or a new logic module.
  - **Personality**: extend `octo/personality.py` for new moods/phrases.
  - **UI**: render changes in `octo/ui_terminal.py` or a new UI module.

## Extension examples

- **New evolution mechanic** (e.g., "curiosity" stat):
  - Add fields to `config.yaml` and `octo/config.py`.
  - Store and update in `octo/storage.py` / `state`.
  - Use it in decision logic in `octo/brain.py`.
  - Visualize it in `octo/ui_terminal.py`.

- **New personality feature** (e.g., reaction to an event):
  - Add phrase sets/mappings in `octo/personality.py`.
  - Call personality helpers from `core.py` or `brain.py` instead of inlining messages.

- **New mutation** (recommended approach):
  - Add entry to `MUTATION_POOL` in `octo/mutation_rules.py` (data only, no code).
  - Define name, description, rarity, and modifiers.
  - Add visual effects in `octo/pixel_art.py` if desired.
  - Add phrases in `octo/personality.py` if desired.

## How to read the codebase

To understand control flow, read in this order:

1. `octo/core.py` – main loop and orchestration  
2. `octo/config.py` – how configuration is shaped  
3. `octo/storage.py` – how state is persisted  
4. `octo/brain.py` – evolution and decision logic  
5. `octo/personality.py` – personality surface area  
6. `octo/ui_terminal.py` – current UI rendering
7. `octo/evolution_engine.py` – advanced evolution mechanics (mutations, drift, triggers)
8. `octo/pixel_art.py` – procedural visual rendering from state
