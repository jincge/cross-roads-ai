from dataclasses import dataclass


@dataclass
class RenderVehicle:
    approach: str
    position: float
    stopped: bool = False
    type: str = "car"
    collided: bool = False
    explosion_timer: float = 0.0
    explosion_duration: float = 0.0
