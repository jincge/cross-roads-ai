from .traffic_light import TrafficLight
from .sensor import Sensor

class RoadApproach:
    def __init__(self, direction: str):
        self._direction = direction
        self._light = TrafficLight(direction)
        self._sensor = Sensor()

    def direction(self) -> str:
        return self._direction

    def light(self) -> TrafficLight:
        return self._light

    def sensor(self) -> Sensor:
        return self._sensor
