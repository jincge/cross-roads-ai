from dataclasses import dataclass


@dataclass
class Vehicle:
    type: str = "car"
    # turn can be 'straight', 'left', or 'right'
    turn: str = "straight"
