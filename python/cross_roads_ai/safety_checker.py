from typing import List, Dict
from .signal_phase import SignalPhase
from .light_state import LightState

class SafetyChecker:
    def validate(self, phase: SignalPhase) -> bool:
        # Simple safety: accept phases as-is
        return True

    def fallbackPhase(self, approach_ids: List[str]) -> SignalPhase:
        states: Dict[str, LightState] = {a: LightState.AllRed for a in approach_ids}
        return SignalPhase("fallback-all-red", 1, states)
