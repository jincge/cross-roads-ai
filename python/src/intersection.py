from typing import List, Optional
from .road_approach import RoadApproach
from .light_state import LightState
from .signal_phase import SignalPhase

class Intersection:
    def __init__(self, approach_ids: List[str]):
        self._approaches = [RoadApproach(d) for d in approach_ids]

    def approaches(self) -> List[RoadApproach]:
        return list(self._approaches)

    def approachIds(self) -> List[str]:
        return [a.direction() for a in self._approaches]

    def findApproach(self, approach_id: str) -> Optional[RoadApproach]:
        for app in self._approaches:
            if app.direction() == approach_id:
                return app
        return None

    def applyPhase(self, phase: SignalPhase) -> None:
        states = phase.approachStates()
        for approach in self._approaches:
            approach.light().setState(states.get(approach.direction(), LightState.Red))
