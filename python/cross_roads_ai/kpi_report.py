from typing import Dict

class KPIReport:
    def __init__(self):
        self._metrics: Dict[str, float] = {}

    def recordMetric(self, name: str, value: float) -> None:
        self._metrics[name] = value

    def getMetrics(self) -> Dict[str, float]:
        return dict(self._metrics)
