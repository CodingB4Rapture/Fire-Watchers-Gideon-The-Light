# Safe Scaling & Refactoring Guide

As *Gideon & The Light* expands beyond Zone 2, follow these practices to maintain code health.

## 1. Centralized Configuration
- **No Magic Numbers**: Use `constants.py` for all gameplay values (e.g., `TREE_HEALTH`, `MAX_FIRE_FUEL`).
- **Zone Config**: Add new zones via `ZoneData` in `zone_manager.py`. Avoid hardcoding unique zone logic in the main loop if possible; use data flags (e.g., `goals`, `wind_chill`) instead.

## 2. Modular Expansion
- **Add, Don't Modify**: When adding a new feature (e.g., a new NPC), extend `npc_manager.py` or add a new class file. Avoid modifying the core `main.py` loop unless absolutely necessary.
- **Layering**: Build new content *on top* of existing systems. For example, a "Sandstorm" should reuse `WeatherSystem` with different parameters, not a new system.

## 3. Safe Refactoring
- **System-by-System**: Refactor one system at a time (e.g., Inventory) and verify before moving to the next.
- **Regression Tests**: Before and after refactoring, run a standard "Survival Test" (Survive 60s, Light Fire, Save/Load) to ensure no regressions.

## 4. Performance
- **Profile First**: If adding heavy visual effects, check FPS. 
- **Object Pooling**: If creating >50 entities (particles/projectiles), implementation pooling or aggressive culling (like in `WeatherSystem`).
