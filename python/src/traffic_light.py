from .light_state import LightState

class TrafficLight:
    def __init__(self, approachId: str):
        self._approachId = approachId
        self._state = LightState.Red

    def getState(self) -> LightState:
        return self._state

    def setState(self, state: LightState) -> None:
        self._state = state

    def getApproachId(self) -> str:
        return self._approachId
