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
        # arrival patterns:
        # - randomized: each approach has a modest chance to spawn one vehicle
        # - heavy: high chance per approach and occasionally multiple vehicles
        # - jam: continuous stream (many vehicles per approach)
        if self._arrival_pattern == "heavy":
            for a in self._approach_ids:
                if self._rng.random() < 0.9:
                    # 1 or 2 vehicles in quick succession
                    for _ in range(self._rng.randint(1, 2)):
                        spawned.append(SpawnedVehicle(a, Vehicle("car")))
            return spawned

        if self._arrival_pattern == "jam":
            for a in self._approach_ids:
                # spawn 2-4 vehicles per tick for jam
                for _ in range(self._rng.randint(2, 4)):
                    spawned.append(SpawnedVehicle(a, Vehicle("car")))
            return spawned

        # default randomized spawns: each approach has a small chance to spawn one vehicle
        for a in self._approach_ids:
            if self._rng.random() < 0.25:
                spawned.append(SpawnedVehicle(a, Vehicle("car")))
        return spawned
