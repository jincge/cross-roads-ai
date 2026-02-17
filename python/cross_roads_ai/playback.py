from typing import List

class Playback:
    def __init__(self, events: List[str]):
        self._events = list(events)

    def events(self) -> List[str]:
        return list(self._events)
