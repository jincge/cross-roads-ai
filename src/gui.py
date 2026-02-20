import random
import sys
from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (QApplication, QLabel, QVBoxLayout, QWidget, QComboBox, QCheckBox, QHBoxLayout)
import os
import json

import requests

from cross_roads_ai import (
    Intersection,
    SignalPhase,
    ControlAlgorithm,
    SafetyChecker,
    TrafficGenerator,
    Simulation,
    LightState,
)


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
    collided: bool = False
    explosion_timer: float = 0.0
    explosion_duration: float = 0.0


class MapView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # visual scaling factor (scale drawing by this amount)
        self.visual_scale = 2.0
        self.setMinimumSize(int(520 * self.visual_scale), int(520 * self.visual_scale))
        self.lightStates: dict[str, LightState] = {}
        self.vehicles: list[RenderVehicle] = []
        self.laneLength = 200.0
        self.stopLineDistance = 45.0
        self.speed = 75.0
        self.style = "dark"
        self.showOverlays = True
        self.flash_on = False
        self._flash_acc = 0

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
        # move vehicles toward stop line / through intersection while enforcing
        # a minimum following gap so vehicles on the same approach never overlap
        # minimum gap is 1.5x the vehicle length (use base lengths for types)
        CAR_LENGTH = 10.0
        TRUCK_LENGTH = 14.0
        # group vehicles by approach
        by_approach: dict[str, list[RenderVehicle]] = {}
        for v in self.vehicles:
            by_approach.setdefault(v.approach, []).append(v)

        # compute intended positions then clamp followers behind leaders
        intended_pos: dict[int, float] = {}
        intended_stopped: dict[int, bool] = {}

        for approach, vehicles in by_approach.items():
            # sort so leader (closest to intersection) is first
            vehicles.sort(key=lambda x: x.position, reverse=True)
            leader_pos = None
            state = self.lightStates.get(approach, LightState.AllRed)
            for v in vehicles:
                if isGreen(state):
                    intended = v.position + move
                    stopped = False
                else:
                    if v.position < stopPos:
                        if v.position + move >= stopPos:
                            intended = stopPos
                            stopped = True
                        else:
                            intended = v.position + move
                            stopped = False
                    else:
                        intended = stopPos
                        stopped = True

                # clamp behind leader to maintain min_gap (1.5x follower length)
                if leader_pos is not None:
                    follower_len = TRUCK_LENGTH if v.type == "truck" else CAR_LENGTH
                    min_gap_for_v = 2.5 * follower_len
                    max_allowed = leader_pos - min_gap_for_v
                    if intended > max_allowed:
                        intended = max_allowed
                        stopped = True

                # keep within bounds
                if intended < 0:
                    intended = 0.0

                intended_pos[id(v)] = intended
                intended_stopped[id(v)] = stopped
                leader_pos = intended

        # apply computed positions
        for v in self.vehicles:
            key = id(v)
            if key in intended_pos:
                v.position = intended_pos[key]
                v.stopped = intended_stopped.get(key, False)

        # Prevent perpendicular vehicles from entering the intersection
        # center zone: vehicles whose position is within this radius are considered
        # to be in the intersection. If two vehicles from perpendicular approaches
        # would both be in the zone, block the one with lower priority (further
        # from the center) by clamping it to the stop line.
        center_pos = self.laneLength
        zone_radius = 8.0
        ns = {"north", "south"}
        ew = {"east", "west"}

        # For each vehicle that intends to enter the center, check for conflicts
        for v in list(self.vehicles):
            intended = intended_pos.get(id(v), v.position)
            if abs(intended - center_pos) <= zone_radius:
                conflict = False
                for u in self.vehicles:
                    if u is v:
                        continue
                    # only consider perpendicular approaches
                    if (v.approach in ns and u.approach in ns) or (v.approach in ew and u.approach in ew):
                        continue
                    u_current_in = abs(u.position - center_pos) <= zone_radius
                    u_intended = intended_pos.get(id(u), u.position)
                    u_intended_in = abs(u_intended - center_pos) <= zone_radius
                    if u_current_in:
                        # someone already in the intersection; block v
                        conflict = True
                        break
                    if u_intended_in:
                        # both intend to enter: allow the one closer to center (higher intended)
                        if u_intended > intended:
                            conflict = True
                            break
                if conflict:
                    # clamp v to stop line and mark stopped
                    key = id(v)
                    intended_pos[key] = min(intended_pos.get(key, v.position), stopPos)
                    intended_stopped[key] = True

        # apply trimming: remove vehicles that have completed their path
        self.vehicles = [veh for veh in self.vehicles if veh.position <= totalPath]

    def tickFlash(self, dt_ms: int):
        # update flashing state (toggle ~500ms)
        self._flash_acc += dt_ms
        if self._flash_acc >= 500:
            self._flash_acc = 0
            self.flash_on = not self.flash_on

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # Apply visual scaling so the entire scene is drawn larger
        scale = getattr(self, "visual_scale", 1.0)
        painter.save()
        # compute a logical center that compensates for the scale transform
        center = QPointF(self.rect().center().x() / scale, self.rect().center().y() / scale)
        painter.scale(scale, scale)

        # Background per style
        if self.style == "light":
            painter.fillRect(self.rect(), QColor(240, 240, 240))
        elif self.style == "satellite":
            painter.fillRect(self.rect(), QColor(30, 30, 30))
        else:
            painter.fillRect(self.rect(), QColor(25, 25, 25))

        # `center` is computed above to account for scaling
        # style-aware colors
        if self.style == "light":
            roadBrush = QColor(220, 220, 220)
            laneColor = QColor(200, 200, 200)
            bgColor = QColor(240, 240, 240)
        elif self.style == "osm":
            # OSM-like: light road, green surroundings
            roadBrush = QColor(235, 235, 220)
            laneColor = QColor(200, 200, 180)
            bgColor = QColor(200, 230, 190)
        elif self.style == "google":
            # Google satellite-like: darker, with subtle contrast
            roadBrush = QColor(48, 48, 48)
            laneColor = QColor(140, 140, 140)
            bgColor = QColor(20, 20, 20)
        else:
            roadBrush = QColor(60, 60, 60)
            laneColor = QColor(100, 100, 100)
            bgColor = QColor(25, 25, 25)

        roadWidth = 70.0
        laneOffset = 16.0

        painter.setPen(Qt.NoPen)
        painter.setBrush(roadBrush)
        painter.drawRect(QRectF(center.x() - roadWidth / 2.0, self.rect().top(), roadWidth, self.rect().height()))
        painter.drawRect(QRectF(self.rect().left(), center.y() - roadWidth / 2.0, self.rect().width(), roadWidth))

        stopPen = QPen(laneColor)
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

        # place traffic lights just outside the road edges
        roadHalf = roadWidth / 2.0
        edge_offset = 10.0

        north_pos = QPointF(center.x() - roadHalf - edge_offset, center.y() - self.stopLineDistance - 18.0)
        south_pos = QPointF(center.x() + roadHalf + edge_offset, center.y() + self.stopLineDistance + 18.0)
        west_pos = QPointF(center.x() - self.stopLineDistance - 18.0, center.y() + roadHalf + edge_offset)
        east_pos = QPointF(center.x() + self.stopLineDistance + 18.0, center.y() - roadHalf - edge_offset)

        self._drawLight(painter, "north", north_pos)
        self._drawLight(painter, "south", south_pos)
        self._drawLight(painter, "west", west_pos)
        self._drawLight(painter, "east", east_pos)

        for veh in self.vehicles:
            # pick base color by style and type
            if self.style == "light":
                base_truck = QColor(180, 120, 100)
                base_car = QColor(70, 110, 170)
            else:
                base_truck = QColor(160, 120, 100)
                base_car = QColor(80, 170, 255)

            base = base_truck if veh.type == "truck" else base_car
            outline = QColor(20, 20, 20)

            painter.setPen(QPen(outline, 1))
            pos = self._vehiclePosition(center, laneOffset, veh)

            # dimensions
            if veh.type == "truck":
                body_w = 28.0
                body_h = 14.0
            else:
                body_w = 18.0
                body_h = 10.0

            # vertical orientation (north/south)
            if veh.approach in ("north", "south"):
                w = body_w * 0.6
                h = body_h * 1.6
                cx = pos.x()
                cy = pos.y()

                if veh.type == "truck":
                    # truck: cab (front) + cargo box
                    cab_h = h * 0.45
                    cargo_h = h - cab_h - 1
                    cab_rect = QRectF(cx - w / 2.0, cy - h / 2.0, w, cab_h)
                    cargo_rect = QRectF(cx - w / 2.0, cy - h / 2.0 + cab_h + 1, w, cargo_h)

                    painter.setBrush(base)
                    painter.drawRect(cab_rect)
                    painter.drawRect(cargo_rect)

                    # windows on cab
                    painter.setBrush(QColor(200, 230, 250, 220))
                    win = QRectF(cab_rect.left() + 1.5, cab_rect.top() + 1.5, cab_rect.width() - 3.0, cab_rect.height() - 3.0)
                    painter.drawRect(win)

                    # wheels
                    painter.setBrush(QColor(20, 20, 20))
                    painter.drawEllipse(QPointF(cab_rect.left() + 2.8, cab_rect.bottom() + 2.0), 2.8, 2.8)
                    painter.drawEllipse(QPointF(cab_rect.right() - 2.8, cab_rect.bottom() + 2.0), 2.8, 2.8)
                    painter.drawEllipse(QPointF(cargo_rect.left() + 3.8, cargo_rect.bottom() + 2.0), 2.8, 2.8)
                    painter.drawEllipse(QPointF(cargo_rect.right() - 3.8, cargo_rect.bottom() + 2.0), 2.8, 2.8)

                    # lights
                    if veh.approach == "north":
                        # facing downwards: headlights at bottom
                        painter.setBrush(QColor(255, 230, 170))
                        painter.drawEllipse(QPointF(cab_rect.center().x() - 6, cab_rect.bottom()), 1.6, 1.6)
                        painter.drawEllipse(QPointF(cab_rect.center().x() + 6, cab_rect.bottom()), 1.6, 1.6)
                    else:
                        # facing upwards: tail lights at top
                        painter.setBrush(QColor(220, 40, 40))
                        painter.drawEllipse(QPointF(cargo_rect.center().x() - 6, cargo_rect.top()), 1.6, 1.6)
                        painter.drawEllipse(QPointF(cargo_rect.center().x() + 6, cargo_rect.top()), 1.6, 1.6)
                else:
                    # car: stylized sedan shape
                    rect = QRectF(cx - body_w / 2.0, cy - body_h / 2.0, body_w, body_h)
                    painter.setBrush(base)
                    painter.drawRoundedRect(rect, 3.0, 3.0)

                    # roof/window
                    painter.setBrush(QColor(200, 225, 245, 220))
                    roof = QRectF(rect.left() + 1.5, rect.top() + 1.0, rect.width() - 3.0, rect.height() * 0.5)
                    painter.drawRoundedRect(roof, 2.0, 2.0)

                    # wheels
                    painter.setBrush(QColor(20, 20, 20))
                    painter.drawEllipse(QPointF(rect.left() + 3.5, rect.bottom() - 1.5), 2.4, 2.4)
                    painter.drawEllipse(QPointF(rect.right() - 3.5, rect.bottom() - 1.5), 2.4, 2.4)

                    # lights
                    if veh.approach == "north":
                        painter.setBrush(QColor(255, 230, 170))
                        painter.drawEllipse(QPointF(rect.center().x() - 5, rect.bottom()), 1.4, 1.4)
                        painter.drawEllipse(QPointF(rect.center().x() + 5, rect.bottom()), 1.4, 1.4)
                    else:
                        painter.setBrush(QColor(220, 40, 40))
                        painter.drawEllipse(QPointF(rect.center().x() - 5, rect.top()), 1.4, 1.4)
                        painter.drawEllipse(QPointF(rect.center().x() + 5, rect.top()), 1.4, 1.4)

            else:
                # horizontal orientation (east/west)
                cx = pos.x()
                cy = pos.y()
                if veh.type == "truck":
                    # truck: cab left, cargo right (horizontal)
                    cab_w = body_w * 0.45
                    cargo_w = body_w - cab_w - 1
                    cab_rect = QRectF(cx - body_w / 2.0, cy - body_h / 2.0, cab_w, body_h)
                    cargo_rect = QRectF(cab_rect.right() + 1, cy - body_h / 2.0, cargo_w, body_h)

                    painter.setBrush(base)
                    painter.drawRect(cab_rect)
                    painter.drawRect(cargo_rect)

                    painter.setBrush(QColor(200, 230, 250, 220))
                    win = QRectF(cab_rect.left() + 1.5, cab_rect.top() + 1.5, cab_rect.width() - 3.0, cab_rect.height() - 3.0)
                    painter.drawRect(win)

                    painter.setBrush(QColor(20, 20, 20))
                    painter.drawEllipse(QPointF(cab_rect.left() + 3.0, cab_rect.bottom() + 2.0), 2.8, 2.8)
                    painter.drawEllipse(QPointF(cargo_rect.left() + 4.5, cargo_rect.bottom() + 2.0), 2.8, 2.8)
                    painter.drawEllipse(QPointF(cargo_rect.right() - 4.5, cargo_rect.bottom() + 2.0), 2.8, 2.8)

                    # lights
                    if veh.approach == "east":
                        painter.setBrush(QColor(255, 230, 170))
                        painter.drawEllipse(QPointF(cargo_rect.right(), cargo_rect.center().y() - 4), 1.6, 1.6)
                    else:
                        painter.setBrush(QColor(220, 40, 40))
                        painter.drawEllipse(QPointF(cab_rect.left(), cab_rect.center().y() - 4), 1.6, 1.6)
                else:
                    rect = QRectF(cx - body_w / 2.0, cy - body_h / 2.0, body_w, body_h)
                    painter.setBrush(base)
                    painter.drawRoundedRect(rect, 3.0, 3.0)

                    painter.setBrush(QColor(200, 225, 245, 220))
                    roof = QRectF(rect.left() + 1.5, rect.top() + 1.0, rect.width() * 0.55, rect.height() - 2.5)
                    painter.drawRect(roof)
