from src import (
    Intersection,
    SignalPhase,
    ControlAlgorithm,
    SafetyChecker,
    TrafficGenerator,
    Simulation,
    LightState,
)


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


if __name__ == "__main__":
    sim = build_simulation()
    print("Starting headless simulation (5 steps)")
    for i in range(5):
        sim.step()
        print(
            f"step={i+1} phase={sim.controlAlgorithm().getName()} spawns={len(sim.recentSpawned())} vehicle_count={sim.kpiReport().getMetrics().get('vehicle_count')}"
        )
