import pytest

from cross_roads_ai import (
    Simulation,
    Intersection,
    ControlAlgorithm,
    SignalPhase,
    SafetyChecker,
    TrafficGenerator,
    Vehicle,
    SpawnedVehicle,
    LightState,
    KPIReport,
)


def make_fixed_generator(spawns):
    gen = TrafficGenerator([s.approachId for s in spawns])
    # replace spawnVehicles with fixed list
    gen.spawnVehicles = lambda: list(spawns)
    return gen


def make_one_shot_generator(spawns):
    gen = TrafficGenerator([s.approachId for s in spawns])
    called = {"done": False}

    def _spawn():
        if not called["done"]:
            called["done"] = True
            return list(spawns)
        return []

    gen.spawnVehicles = _spawn
    return gen


def test_spawn_increments_sensor_and_recent_spawned():
    intersection = Intersection(["north", "south"])
    phase = SignalPhase("north-green", 1, {"north": LightState.Green})
    algo = ControlAlgorithm("test", [phase])
    safety = SafetyChecker()

    spawn = SpawnedVehicle("north", Vehicle("car"))
    gen = make_one_shot_generator([spawn])

    sim = Simulation(intersection, algo, safety, gen)
    sim.start()
    # sensor counts start at 0
    assert intersection.findApproach("north").sensor().getCount() == 0

    sim.step()

    recent = sim.recentSpawned()
    assert len(recent) == 1
    assert recent[0].approachId == "north"

    assert intersection.findApproach("north").sensor().getCount() == 1


def test_safety_prevents_multiple_green_and_uses_fallback():
    intersection = Intersection(["north", "south"])
    # malicious phase: conflicting greens (north and east) should be rejected
    bad = SignalPhase("bad", 1, {"north": LightState.Green, "east": LightState.Green})
    algo = ControlAlgorithm("bad", [bad])
    safety = SafetyChecker()

    gen = make_fixed_generator([])
    sim = Simulation(intersection, algo, safety, gen)
    sim.start()
    sim.step()

    # safety should have selected fallback (FlashingAmber)
    state_n = intersection.findApproach("north").light().getState()
    state_s = intersection.findApproach("south").light().getState()
    assert state_n == LightState.FlashingAmber
    assert state_s == LightState.FlashingAmber


def test_kpi_records_vehicle_count():
    intersection = Intersection(["north", "south"])
    phase = SignalPhase("north-green", 1, {"north": LightState.Green})
    algo = ControlAlgorithm("test", [phase])
    safety = SafetyChecker()

    spawn1 = SpawnedVehicle("north", Vehicle("car"))
    spawn2 = SpawnedVehicle("south", Vehicle("truck"))
    gen = make_fixed_generator([spawn1, spawn2])

    sim = Simulation(intersection, algo, safety, gen)
    sim.start()
    sim.step()

    metrics = sim.kpiReport().getMetrics()
    # vehicle_count metric should equal total sensor counts
    total_sensors = sum(a.sensor().getCount() for a in intersection.approaches())
    assert metrics.get("vehicle_count") == float(total_sensors)


def test_vehicle_stops_on_red_and_continues_on_green():
    # create intersection and algorithm with two phases: all-red then north-green
    intersection = Intersection(["north", "south"])
    all_red = SignalPhase("all-red", 1, {"north": LightState.AllRed, "south": LightState.AllRed})
    north_green = SignalPhase("north-green", 1, {"north": LightState.Green, "south": LightState.Red})
    algo = ControlAlgorithm("staged", [all_red, north_green])
    safety = SafetyChecker()

    spawn = SpawnedVehicle("north", Vehicle("car"))
    gen = make_one_shot_generator([spawn])

    sim = Simulation(intersection, algo, safety, gen)
    sim.start()

    # Step 1: all-red applied -> spawned vehicle should be queued (not observed)
    sim.step()
    assert intersection.findApproach("north").sensor().getCount() == 0
    assert len(sim.recentSpawned()) == 0

    # Step 2: north-green applied -> waiting vehicle should pass and be observed
    sim.step()
    assert intersection.findApproach("north").sensor().getCount() == 1
    recent = sim.recentSpawned()
    assert len(recent) == 1
    assert recent[0].approachId == "north"
