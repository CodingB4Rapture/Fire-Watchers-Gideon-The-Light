# Antigravity AI Collaboration Guidelines

To ensure the stability and integrity of *Gideon & The Light*, all AI-assisted development must adhere to the following principles.

## 1. Clear Instructions Strategy
- **Be Specific**: Cite exact filenames, function names, and variable names.
    - *Bad*: "Fix the tick system."
    - *Good*: "Update `TickSystem.update` in `tick_system.py` to use a 1.0s interval."
- **One Task at a Time**: Isolate changes. Do not mix refactoring with feature addition.

## 2. Constraints & Invariants
The following features are **OFF-LIMITS** for radical AI refactoring:
- **Pixel-Art Rendering**: The procedural matrix system in `matrices.py` must remain. Do not replace with static assets.
- **60 FPS Target**: Any new visual feature must be profiled.
- **Tick-Based Logic**: All survival mechanics (hunger, cold, fuel) must happen in `TickSystem`, never in the frame loop.

## 3. Verify-Confirm Workflow
- **Plan First**: Ask the AI to output an "Implementation Plan" before writing code.
- **Review**: Read the diffs.
- **Confirm**: Only then allow the changes.

## 4. Testing
- Ask the AI to suggest test cases for its own changes.
- Use `debug_mode` to verify changes in a live environment.
