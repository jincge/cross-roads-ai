from dataclasses import dataclass

@dataclass
class Vehicle:
    type: str = "car"


@dataclass
class SpawnedVehicle:
    approachId: str
    vehicle: Vehicle
