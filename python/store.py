"""In-memory store for the Python Flask server (port of `server/store.h`).

This mirrors the minimal data used by the C++ server: layouts, control algorithms
and an in-memory simulation registry.
"""
import uuid
from typing import Dict

layouts: Dict[str, dict] = {}
control_algorithms: Dict[str, dict] = {}
simulations: Dict[str, dict] = {}


def new_id() -> str:
    return uuid.uuid4().hex


def initialize() -> None:
    # Control algorithm: "basic"
    basic_algo = {
        "name": "basic",
        "mode": "",
        "phases": [
            {
                "name": "north-south",
                "durationSeconds": 5,
                "approachStates": {"north": "Green", "south": "Green"},
            },
            {
                "name": "east-west",
                "durationSeconds": 5,
                "approachStates": {"east": "Green", "west": "Green"},
            },
        ],
    }
    control_algorithms["basic"] = basic_algo

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
