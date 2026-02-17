class Sensor:
    def __init__(self):
        self._count = 0

    def observeVehicle(self) -> None:
        self._count += 1

    def getCount(self) -> int:
        return self._count

    def clear(self) -> None:
        self._count = 0
