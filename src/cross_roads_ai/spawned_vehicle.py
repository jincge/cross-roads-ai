from dataclasses import dataclass
from .vehicle import Vehicle


@dataclass
class SpawnedVehicle:
    approachId: str
    vehicle: Vehicle
