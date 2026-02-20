from typing import List, Dict
from .signal_phase import SignalPhase
from .light_state import LightState

class SafetyChecker:
    def validate(self, phase: SignalPhase) -> bool:
        # Allow paired opposite directions (north/south or east/west) to be
        # green together, but disallow conflicting greens (e.g., north+east).
        states = phase.approachStates()
        greens = [a for a, s in states.items() if s == LightState.Green]
        if not greens:
            return True

        greens_set = set(greens)
        # simple axis grouping based on common approach ids used in the project
        ns = {"north", "south"}
        ew = {"east", "west"}

        if greens_set.issubset(ns) or greens_set.issubset(ew):
            return True

        return False

    def fallbackPhase(self, approach_ids: List[str]) -> SignalPhase:
        # Fallback to flashing amber for all approaches (matches C++ behaviour)
        states: Dict[str, LightState] = {a: LightState.FlashingAmber for a in approach_ids}
        return SignalPhase("fallback-flashing-amber", 3, states)
