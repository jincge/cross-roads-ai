"""In-memory store for the Python Flask server (port of `server/store.h`).

This mirrors the minimal data used by the C++ server: layouts, control algorithms
and an in-memory simulation registry.
"""
import uuid
import os
import json
from typing import Dict

layouts: Dict[str, dict] = {}
control_algorithms: Dict[str, dict] = {}
simulations: Dict[str, dict] = {}
map_data: Dict[str, dict] = {}
recordings: Dict[str, dict] = {}
playbacks: Dict[str, dict] = {}
recordings: Dict[str, dict] = {}
playbacks: Dict[str, dict] = {}


def new_id() -> str:
    return uuid.uuid4().hex


def initialize() -> None:
    # Read timings from optional config file `python/store_config.json`
    def _read_timings():
        defaults = {"green_seconds": 60, "amber_seconds": 10, "all_red_seconds": 120, "force_all_red": True}
        cfg_path = os.path.join(os.path.dirname(__file__), "store_config.json")
        try:
            if os.path.exists(cfg_path):
                with open(cfg_path, "r") as f:
                    cfg = json.load(f)
                timings = cfg.get("timings", {})
                for k in ("green_seconds", "amber_seconds", "all_red_seconds", "force_all_red"):
                    if k in cfg:
                        timings[k] = cfg[k]
                res = dict(defaults)
                res.update(timings)
                return res
        except Exception:
            pass
        return dict(defaults)

    timings = _read_timings()
    green = int(timings.get("green_seconds", 60))
    amber = int(timings.get("amber_seconds", 10))
    all_red = int(timings.get("all_red_seconds", 120))
    force_all_red = bool(timings.get("force_all_red", True))

    # Control algorithm: "basic" (NS/EW half-cycle synchronized)
    phases = [
        {"name": "ns-green", "durationSeconds": green, "approachStates": {"north": "Green", "south": "Green"}},
        {"name": "ns-amber", "durationSeconds": amber, "approachStates": {"north": "Amber", "south": "Amber"}},
    ]
    if force_all_red:
        phases.append({"name": "all-red", "durationSeconds": all_red, "approachStates": {"north": "AllRed", "south": "AllRed", "east": "AllRed", "west": "AllRed"}})
    phases.extend([
        {"name": "ew-green", "durationSeconds": green, "approachStates": {"east": "Green", "west": "Green"}},
        {"name": "ew-amber", "durationSeconds": amber, "approachStates": {"east": "Amber", "west": "Amber"}},
    ])
    if force_all_red:
        phases.append({"name": "all-red", "durationSeconds": all_red, "approachStates": {"north": "AllRed", "south": "AllRed", "east": "AllRed", "west": "AllRed"}})

    basic_algo = {"name": "basic", "mode": "", "phases": phases}
    control_algorithms["basic"] = basic_algo

    # Control algorithm: "flashing-amber" (failsafe / manual mode)
    flashing = {
        "name": "flashing-amber",
        "mode": "failsafe",
        "phases": [
            {
                "name": "flashing-amber",
                "durationSeconds": 3,
                "approachStates": {"north": "FlashingAmber", "south": "FlashingAmber", "east": "FlashingAmber", "west": "FlashingAmber"},
            }
        ],
    }
    control_algorithms["flashing-amber"] = flashing

    # Control algorithm: "advanced" (placeholder for adaptive/optimized modes)
    advanced = {
        "name": "advanced",
        "mode": "adaptive",
        "phases": [
            {"name": "ns-green-adaptive", "durationSeconds": 60, "approachStates": {"north": "Green", "south": "Green"}},
            {"name": "ns-amber-adaptive", "durationSeconds": 10, "approachStates": {"north": "Amber", "south": "Amber"}},
            {"name": "all-red", "durationSeconds": 120, "approachStates": {"north": "AllRed", "south": "AllRed", "east": "AllRed", "west": "AllRed"}},
            {"name": "ew-green-adaptive", "durationSeconds": 60, "approachStates": {"east": "Green", "west": "Green"}},
            {"name": "ew-amber-adaptive", "durationSeconds": 10, "approachStates": {"east": "Amber", "west": "Amber"}},
            {"name": "all-red", "durationSeconds": 120, "approachStates": {"north": "AllRed", "south": "AllRed", "east": "AllRed", "west": "AllRed"}},
        ],
    }
    control_algorithms["advanced"] = advanced

    # Default layout
    default_layout = {
        "id": "default",
        "name": "Standard 4-way",
        "intersection": {
            "id": "intersection-1",
            "approaches": [
                {"id": "north", "lightState": "Red"},
                {"id": "south", "lightState": "Red"},
                {"id": "east", "lightState": "Red"},
                {"id": "west", "lightState": "Red"},
            ],
        },
    }
    layouts["default"] = default_layout
