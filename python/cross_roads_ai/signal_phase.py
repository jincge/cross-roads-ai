from typing import Dict
from .light_state import LightState

class SignalPhase:
    def __init__(self, name: str, duration_seconds: float, approach_states: Dict[str, LightState]):
        self._name = name
        self._duration_seconds = duration_seconds
        # approach_states: mapping from approach id -> LightState
        self._approach_states = dict(approach_states)

    def getName(self) -> str:
        return self._name

    def getDurationSeconds(self) -> float:
        return self._duration_seconds

    def approachStates(self) -> Dict[str, LightState]:
        return dict(self._approach_states)
