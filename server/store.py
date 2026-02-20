"""In-memory store for server resources (layouts, algorithms, simulations, recordings, maps).
This module provides simple CRUD helpers used by `app.py`.
"""
from typing import Dict, Any
import uuid
import time

layouts: Dict[str, Dict[str, Any]] = {}
control_algorithms: Dict[str, Dict[str, Any]] = {}
simulations: Dict[str, Dict[str, Any]] = {}
recordings: Dict[str, Dict[str, Any]] = {}
maps: Dict[str, Dict[str, Any]] = {}


def new_id() -> str:
    return uuid.uuid4().hex


def initialize() -> None:
    # default algorithm (mirror of previous defaults)
    basic = {
        "name": "basic",
        "mode": "",
        "phases": [
            {"name": "north-south", "durationSeconds": 5, "approachStates": {"north": "Green", "south": "Green"}},
            {"name": "east-west", "durationSeconds": 5, "approachStates": {"east": "Green", "west": "Green"}},
        ],
    }
    control_algorithms[basic["name"]] = basic

    # flashing amber algorithm (all approaches flash amber)
    flashing_amber = {
        "name": "flashing-amber",
        "mode": "flashing",
        "phases": [
            {
                "name": "flashing",
                "durationSeconds": 1,
                "approachStates": {"north": "FlashingAmber", "south": "FlashingAmber", "east": "FlashingAmber", "west": "FlashingAmber"},
            }
        ],
    }
    control_algorithms[flashing_amber["name"]] = flashing_amber

    # advanced adaptive algorithm (placeholder with more phases)
    advanced = {
        "name": "advanced",
        "mode": "adaptive",
        "phases": [
            {"name": "north-south-green", "durationSeconds": 8, "approachStates": {"north": "Green", "south": "Green", "east": "Red", "west": "Red"}},
            {"name": "all-red", "durationSeconds": 2, "approachStates": {"north": "Red", "south": "Red", "east": "Red", "west": "Red"}},
            {"name": "east-west-green", "durationSeconds": 8, "approachStates": {"east": "Green", "west": "Green", "north": "Red", "south": "Red"}},
        ],
    }
    control_algorithms[advanced["name"]] = advanced

    # default layout
    default_layout = {
        "id": "default",
        "name": "Standard 4-way",
        "description": "Default 4-way intersection",
        "intersection": {
            "id": "intersection-1",
            "approaches": [
                {"id": "north", "lightState": "Red", "sensorCount": 0},
                {"id": "south", "lightState": "Red", "sensorCount": 0},
                {"id": "east", "lightState": "Red", "sensorCount": 0},
                {"id": "west", "lightState": "Red", "sensorCount": 0},
            ],
        },
    }
    layouts[default_layout["id"]] = default_layout


# Generic CRUD helpers

def list_resources(store_dict: Dict[str, Dict]) -> list:
    return list(store_dict.values())


def get_resource(store_dict: Dict[str, Dict], resource_id: str):
    return store_dict.get(resource_id)


def create_resource(store_dict: Dict[str, Dict], data: Dict) -> Dict:
    rid = data.get("id", new_id())
    data["id"] = rid
    store_dict[rid] = data
    return data


def update_resource(store_dict: Dict[str, Dict], resource_id: str, data: Dict) -> Dict:
    if resource_id not in store_dict:
        return None
    data["id"] = resource_id
    store_dict[resource_id] = data
    return data


def delete_resource(store_dict: Dict[str, Dict], resource_id: str) -> bool:
    return store_dict.pop(resource_id, None) is not None
