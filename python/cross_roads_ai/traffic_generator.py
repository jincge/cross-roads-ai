import random
from typing import List
from .vehicle import Vehicle, SpawnedVehicle

class TrafficGenerator:
    def __init__(self, approach_ids: List[str]):
        self._approach_ids = list(approach_ids)
        self._arrival_pattern = "randomized"
        self._rng = random.Random()

    def setArrivalPattern(self, pattern: str) -> None:
        self._arrival_pattern = pattern

    def spawnVehicles(self) -> List[SpawnedVehicle]:
        spawned = []
        # simple randomized spawns: each approach has a small chance to spawn one vehicle
        for a in self._approach_ids:
            if self._rng.random() < 0.25:
                spawned.append(SpawnedVehicle(a, Vehicle("car")))
        return spawned
