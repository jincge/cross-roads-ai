# Cross Road AI

Cross Road AI explores traffic light control at a multi-approach intersection. The project models traffic generators, control algorithms, safety checks, KPIs, and recording/playback, with a simple Qt stub UI while the domain logic lives in C++ classes.

## What you get
- Domain model captured in PlantUML (`cross-road.puml`) and implemented in C++ (`src/DomainModel.*`).
- BDD-style requirements in `features/*.feature`, extracted from `cross-road.md` iterations.
- Stub Qt GUI entry point in `main.cpp` to keep the build runnable.

## Building (CMake + Qt)
Prerequisites: CMake, a C++20 compiler, and Qt5 or Qt6 development files on your PATH/CMAKE_PREFIX_PATH.

```powershell
cmake -B cmake-build-debug -S .
cmake --build cmake-build-debug
```

## Project layout
- `cross-road.md` – iteration notes and high-level requirements.
- `features/` – GitHub-flavored Markdown Gherkin specs for each iteration.
- `src/DomainModel.*` – simulation domain classes (simulation, control, safety, sensors, KPIs, persistence scaffolding).
- `main.cpp` – minimal Qt bootstrap (UI placeholder).
- `cross-road.puml` – domain model diagram you can render with PlantUML.

## Next steps
- Wire the domain model into a real UI and simulation loop.
- Add tests around the domain classes to lock in behaviors from the feature specs.
