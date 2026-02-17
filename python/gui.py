import random
import sys
from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (QApplication, QLabel, QVBoxLayout, QWidget)

import requests

from src import (
    Intersection,
    SignalPhase,
    ControlAlgorithm,
    SafetyChecker,
    TrafficGenerator,
    Simulation,
)
from src.light_state import LightState


def lightColor(state: LightState) -> QColor:
    if state == LightState.Green:
        return QColor(0, 180, 0)
    if state == LightState.Amber:
        return QColor(255, 170, 0)
    if state == LightState.FlashingAmber:
        return QColor(255, 200, 0)
    # AllRed / Red
    return QColor(200, 0, 0)


def lightName(state: LightState) -> str:
    return state.name


def isGreen(state: LightState) -> bool:
    return state == LightState.Green


@dataclass
class RenderVehicle:
    approach: str
    position: float
    stopped: bool = False
    type: str = "car"


class MapView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(520, 520)
        self.lightStates: dict[str, LightState] = {}
        self.vehicles: list[RenderVehicle] = []
        self.laneLength = 200.0
        self.stopLineDistance = 45.0
        self.speed = 75.0

    def setLights(self, states: dict):
        self.lightStates = dict(states)

    def addSpawnedVehicles(self, spawned, spawnProbability: float):
        for spawn in spawned:
            if random.random() > spawnProbability:
                continue
            # Support both server-returned dicts and local SpawnedVehicle objects
            if isinstance(spawn, dict):
                approach = spawn.get("approachId")
                vtype = spawn.get("vehicle", {}).get("type", "car")
            else:
                approach = spawn.approachId
                vtype = spawn.vehicle.type
            v = RenderVehicle(approach=approach, position=0.0, type=vtype)
            self.vehicles.append(v)

    def advance(self, dtSeconds: float):
        stopPos = self.laneLength - self.stopLineDistance
        totalPath = self.laneLength * 2.0
        move = self.speed * dtSeconds

        for v in self.vehicles:
            state = self.lightStates.get(v.approach, LightState.AllRed)
            if (not isGreen(state)) and v.position < stopPos:
                if v.position + move >= stopPos:
                    v.position = stopPos
                    v.stopped = True
                else:
                    v.position += move
                    v.stopped = False
            else:
                v.position += move
                v.stopped = False

        self.vehicles = [veh for veh in self.vehicles if veh.position <= totalPath]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillRect(self.rect(), QColor(25, 25, 25))

        center = self.rect().center()
        roadWidth = 70.0
        laneOffset = 16.0

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(60, 60, 60))
        painter.drawRect(QRectF(center.x() - roadWidth / 2.0, self.rect().top(), roadWidth, self.rect().height()))
        painter.drawRect(QRectF(self.rect().left(), center.y() - roadWidth / 2.0, self.rect().width(), roadWidth))

        stopPen = QPen(QColor(240, 240, 240))
        stopPen.setWidth(3)
        painter.setPen(stopPen)
        painter.drawLine(QPointF(center.x() - roadWidth / 2.0, center.y() - self.stopLineDistance),
                         QPointF(center.x() + roadWidth / 2.0, center.y() - self.stopLineDistance))
        painter.drawLine(QPointF(center.x() - roadWidth / 2.0, center.y() + self.stopLineDistance),
                         QPointF(center.x() + roadWidth / 2.0, center.y() + self.stopLineDistance))
        painter.drawLine(QPointF(center.x() - self.stopLineDistance, center.y() - roadWidth / 2.0),
                         QPointF(center.x() - self.stopLineDistance, center.y() + roadWidth / 2.0))
        painter.drawLine(QPointF(center.x() + self.stopLineDistance, center.y() - roadWidth / 2.0),
                         QPointF(center.x() + self.stopLineDistance, center.y() + roadWidth / 2.0))

        self._drawLight(painter, "north", QPointF(center.x() - laneOffset, center.y() - self.stopLineDistance - 18.0))
        self._drawLight(painter, "south", QPointF(center.x() + laneOffset, center.y() + self.stopLineDistance + 18.0))
        self._drawLight(painter, "west", QPointF(center.x() - self.stopLineDistance - 18.0, center.y() + laneOffset))
        self._drawLight(painter, "east", QPointF(center.x() + self.stopLineDistance + 18.0, center.y() - laneOffset))

        for veh in self.vehicles:
            color = QColor(140, 140, 220) if veh.type == "truck" else QColor(80, 170, 255)
            painter.setBrush(color)
            vehiclePen = QPen(QColor(255, 80, 80) if veh.stopped else QColor(30, 30, 30))
            vehiclePen.setWidth(2)
            painter.setPen(vehiclePen)
            pos = self._vehiclePosition(center, laneOffset, veh)
            painter.drawEllipse(pos, 6.0, 6.0)

    def _vehiclePosition(self, center, laneOffset, vehicle: RenderVehicle) -> QPointF:
        if vehicle.approach == "north":
            return QPointF(center.x() - laneOffset, center.y() - self.laneLength + vehicle.position)
        if vehicle.approach == "south":
            return QPointF(center.x() + laneOffset, center.y() + self.laneLength - vehicle.position)
        if vehicle.approach == "east":
            return QPointF(center.x() + self.laneLength - vehicle.position, center.y() - laneOffset)
        return QPointF(center.x() - self.laneLength + vehicle.position, center.y() + laneOffset)

    def _drawLight(self, painter, approach: str, pos: QPointF) -> None:
        state = self.lightStates.get(approach, LightState.AllRed)
        painter.setBrush(lightColor(state))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(pos, 6.5, 6.5)


class SimulationWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Local simulation (fallback)
        self.simulation = self.buildSimulation()

        # Remote server settings
        self.server_url = "http://localhost:8080"
        self.remote_sim_id = None
        self.remote_mode = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.phaseLabel = QLabel("Phase: --", self)
        self.phaseLabel.setStyleSheet("color: white; font-weight: bold;")
        self.spawnLabel = QLabel("Spawns: --", self)
        self.spawnLabel.setStyleSheet("color: white;")
        self.countsLabel = QLabel("Counts: --", self)
        self.countsLabel.setStyleSheet("color: white;")

        layout.addWidget(self.phaseLabel)
        layout.addWidget(self.spawnLabel)
        layout.addWidget(self.countsLabel)

        self.mapView = MapView(self)
        layout.addWidget(self.mapView, 1)

        self.setWindowTitle("Cross-Roads AI Simulation")
        self.setStyleSheet("background-color: #1c1c1c;")

        # Try to connect to a local Flask server and create a remote simulation.
        try:
            self._connect_remote()
            self.remote_mode = True
            print(f"Connected to remote simulation: {self.remote_sim_id}")
        except Exception:
            # keep local simulation if remote unavailable
            self.remote_mode = False

        self.updateLights()
        self.updateLabels([])

        self.stepTimer = QTimer(self)
        self.stepTimer.timeout.connect(self._on_step)
        self.stepTimer.start(1000)

        self.animationTimer = QTimer(self)
        self.animationTimer.timeout.connect(self._on_animate)
        self.animationTimer.start(50)

    def buildSimulation(self) -> Simulation:
        directions = ["north", "south", "east", "west"]
        intersection = Intersection(directions)

        phases = []
        phases.append(SignalPhase("north-green", 5, {"north": LightState.Green}))
        phases.append(SignalPhase("east-green", 5, {"east": LightState.Green}))
        phases.append(SignalPhase("south-green", 5, {"south": LightState.Green}))
        phases.append(SignalPhase("west-green", 5, {"west": LightState.Green}))

        algorithm = ControlAlgorithm("clock-driven", phases)
        algorithm.setMode("fixed-schedule")

        safety = SafetyChecker()
        generator = TrafficGenerator(directions)
        generator.setArrivalPattern("randomized")

        sim = Simulation(intersection, algorithm, safety, generator)
        sim.start()
        return sim

    def _on_step(self):
        self.simulation.step()
        self.updateLights()

        spawned = self.simulation.recentSpawned()
        spawnProbability = random.uniform(0.3, 0.9)
        self.mapView.addSpawnedVehicles(spawned, spawnProbability)
        self.updateLabels(spawned)

    def _on_animate(self):
        self.mapView.advance(0.05)
        self.mapView.update()

    def updateLights(self):
        states = {}
        for approach in self.simulation.intersection().approaches():
            states[approach.direction()] = approach.light().getState()
        self.mapView.setLights(states)

    def updateLabels(self, spawned):
        parts = []
        for approach in self.simulation.intersection().approaches():
            direction = approach.direction()
            light = lightName(approach.light().getState())
            parts.append(f"{direction}={approach.sensor().getCount()} ({light})")

        self.phaseLabel.setText("Phase: " + self.simulation.controlAlgorithm().getName())
        self.spawnLabel.setText(f"Spawns: {len(spawned)} in last tick")
        self.countsLabel.setText("Counts: " + " | ".join(parts))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimulationWindow()
    window.resize(700, 760)
    window.show()
    sys.exit(app.exec())
