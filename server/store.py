import uuid

# In-memory data store (Python replacement for server/store.h)
layouts: dict = {}
control_algorithms: dict = {}
simulations: dict = {}


def new_id() -> str:
    return uuid.uuid4().hex


def initialize() -> None:
    # Basic control algorithm definition (mirrors the previous C++ default)
    basic = {
        "name": "basic",
        "mode": "",
        "phases": [
            {"name": "north-south", "durationSeconds": 5, "approachStates": {"north": "Green", "south": "Green"}},
            {"name": "east-west", "durationSeconds": 5, "approachStates": {"east": "Green", "west": "Green"}},
        ],
    }
    control_algorithms["basic"] = basic

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
