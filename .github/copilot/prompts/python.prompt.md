# Sync prompt — C++ → Python port

Purpose
- Keep the `python/` port in sync with the native C++ implementation in `src/`, `app/` and `server/`.
- Used by human reviewers or automation (Copilot/CI) to translate, validate, and smoke-test changes.

Goal
- Produce a Python module that preserves the C++ public API and behaviour, runs the headless runner, exposes the same HTTP surface, and (optionally) provides the Qt UI.

Instructions (step-by-step)
1. Detect changes
   - Diff C++ sources (`src/**/*.cpp`, `src/**/*.h`, `app/*.cpp`, `server/*.cpp`).
2. Map files
   - For each changed C++ file, identify the corresponding `python/src/<module>.py`.
   - If missing, add a new Python module with the same public API.
3. Translate code
   - Preserve class names and public method names where possible (e.g. `Simulation.step()`, `TrafficLight.getState()`).
   - Prefer Pythonic idioms but keep signatures compatible with existing GUI/server code.
4. Maintain behaviour
   - Reproduce algorithms and side-effects (sensors, kpis, recorder events).
   - Keep deterministic behavior for tests; where randomness exists, use injected RNG if needed.
5. Update server & GUI
   - Ensure `python/server.py` mirrors `server/server.cpp` endpoints and JSON shapes.
   - Ensure `python/gui.py` mirrors `app/main.cpp` rendering and labels.
6. Dependencies & docs
   - Add required packages to `python/requirements.txt`.
   - Update `python/README.md` with run/test instructions.
7. Tests & smoke checks
   - Add or update unit/integration tests under `python/tests/`.
   - Smoke-run:
     - `python3 python/main.py` (headless)
     - `python3 python/server.py` (Flask server on :8080)
     - `python3 python/gui.py` (PySide6 UI)
     - API checks: `curl -s localhost:8080/layouts`, `POST /simulations`, `POST /simulations/{id}/step`, `GET /simulations/{id}/kpis`, `GET /simulations/{id}/state`.
8. Commit message & changelog
   - Use `sync(python): <short description>` and list translated files.
   - If behaviour differs, document the reason in the PR description and CHANGELOG.

Quick prompt (for assistant/automation)
- "Translate changed C++ files in `src/`, `app/`, and `server/` into `python/src/`, preserving public APIs and JSON shapes; add/update tests; run `python/main.py`, `python/server.py`, and `python/gui.py` smoke checks; update `python/requirements.txt` and `python/README.md`; create a `sync(python): ...` commit with a short changelog entry." 

Commands to run locally
```bash
# run headless smoke test
python3 python/main.py

# start Flask server
python3 python/server.py

# run Qt GUI (requires PySide6)
python3 python/gui.py

# run tests (if present)
pytest python/tests -q
```

Notes & expectations
- Public APIs should remain stable to reduce downstream changes in the GUI/server layers.
- When exact porting is impossible, prefer a minimal, well-documented behavioural change and add unit tests to lock the new behavior.
- Keep translations small and reviewable (one logical C++ -> Python mapping per PR).

Checklist (PR template)
- [ ] All changed C++ files have corresponding Python updates
- [ ] Python unit tests added/updated
- [ ] Smoke tests for `main.py`, `server.py`, `gui.py` pass
- [ ] `python/requirements.txt` and `python/README.md` updated
- [ ] Commit message follows `sync(python): ...` convention
