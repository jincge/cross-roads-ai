from typing import List

class Recorder:
    def __init__(self):
        self._events: List[str] = []

    def recordEvent(self, event: str) -> None:
        self._events.append(event)

    def clear(self) -> None:
        self._events = []

    def events(self) -> List[str]:
        return list(self._events)
