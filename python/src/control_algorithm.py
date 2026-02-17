from typing import List
from .signal_phase import SignalPhase

class ControlAlgorithm:
    def __init__(self, name: str, phases: List[SignalPhase]):
        self._name = name
        self._phases = list(phases)
        self._index = 0
        self._mode = ""

    def nextPhase(self) -> SignalPhase:
        if not self._phases:
            raise RuntimeError("No phases available")
        phase = self._phases[self._index]
        self._index = (self._index + 1) % len(self._phases)
        return phase

    def getName(self) -> str:
        return self._name

    def setMode(self, mode: str) -> None:
        self._mode = mode

    def mode(self) -> str:
        return self._mode
