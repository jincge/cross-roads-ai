# Cross Road AI

Cross Road AI explores traffic light control at a multi-approach intersection. The project models traffic generators, control algorithms, safety checks, KPIs, and recording/playback, with a simple Qt stub UI while the domain logic lives in C++ classes.

## What you get
- Domain model captured in PlantUML (`cross-road.puml`) and implemented in C++ (`src/DomainModel.*`).
- BDD-style requirements in `features/*.feature`, extracted from `cross-road.md` iterations.
- Stub Qt GUI entry point in `main.cpp` to keep the build runnable.

## Build / Run (Python port)
A complete Python port of the simulation, server and UI is available under `python/`.

Quick start (headless):

```bash
python3 python/main.py
```

Run the Flask server (API):

```bash
python3 python/server.py
```

Run the Qt UI (requires optional GUI deps):

```bash
pip3 install -r python/requirements.txt
python3 python/gui.py
```

(If you still need the original C++ code and CMake build files they remain in the repository, but the recommended workflow is the Python port.)

## Project layout
- `cross-road.md` – iteration notes and high-level requirements.
- `features/` – GitHub-flavored Markdown Gherkin specs for each iteration.
- `src/DomainModel.*` – simulation domain classes (simulation, control, safety, sensors, KPIs, persistence scaffolding).
- `main.cpp` – minimal Qt bootstrap (UI placeholder).
- `cross-road.puml` – domain model diagram you can render with PlantUML.

## Next steps
- Wire the domain model into a real UI and simulation loop.
- Add tests around the domain classes to lock in behaviors from the feature specs.
