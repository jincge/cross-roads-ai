# Python port of Cross-Roads AI (partial)

This folder contains a Python port of the core simulation domain model from the C++ `src/` directory.

- `python/src/` — Python modules mirroring the C++ domain classes (Simulation, Intersection, TrafficLight, etc.)
- `python/main.py` — headless runner (smoke test)
- `python/requirements.txt` — optional dependencies (Flask for server; PySide6 commented)

Quick test (run from repo root):

```bash
python3 python/main.py
```

Run the Qt GUI (requires PySide6):

```bash
pip3 install -r python/requirements.txt
python3 python/gui.py
```
