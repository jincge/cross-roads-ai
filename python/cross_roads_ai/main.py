from . import (
    Intersection,
    SignalPhase,
    ControlAlgorithm,
    SafetyChecker,
    TrafficGenerator,
    Simulation,
)
from .light_state import LightState


def build_simulation() -> Simulation:
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
