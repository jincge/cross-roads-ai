Sync prompt — C++ → Python port

Purpose
- Keep the `python/` port in sync with the native C++ implementation in `src/`, `app/` and `server/`.
- Used by human reviewers or automation (Copilot/CI) to translate, validate, and smoke-test changes.

Goal
- Produce a Python module that preserves the C++ public API and behaviour, runs the headless runner, exposes the same HTTP surface, and (optionally) provides the Qt UI.

Quick instructions
- Detect changed C++ sources under `src/**/*.cpp`, `src/**/*.h`, `app/*.cpp`, `server/*.cpp`.
- For each changed C++ file, ensure a corresponding Python module exists (prefer `python/src/<module>.py` or `src/cross_roads_ai/<module>.py`).
- Preserve public class and method names where possible; keep JSON shapes stable for server endpoints.
- Add/update unit tests and smoke checks: `python3 python/main.py`, `python3 python/server.py`, `python3 python/gui.py`.
- Update `python/requirements.txt` and `python/README.md` and use commit message `sync(python): <summary>`.

See `.github/copilot/prompts/python.prompt.md` for full step-by-step instructions.
