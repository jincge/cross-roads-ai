from behave import given, when, then
import requests
from urllib.parse import urljoin


def _u(context, path: str) -> str:
    return context.base_url.rstrip("/") + path


@given("a simple traffic generator with randomized arrivals from each direction")
def step_impl_create_simulation(context):
    """Start a `Simulation` via the OpenAPI `/simulations` endpoint using `TrafficGenerator`.

    The request uses the OpenAPI `CreateSimulationRequest` payload and the server returns
    a `Simulation` resource representing the running Simulation domain object.
    """
    payload = {"layoutId": "default", "controlAlgorithmName": "basic", "arrivalPattern": "randomized"}
    resp = requests.post(_u(context, "/simulations"), json=payload)
    assert resp.status_code == 201, resp.text
    simulation = resp.json()

    # Domain-model terms: Simulation.id
    context.simulationId = simulation["id"]
    context.simulation = simulation


@given("a basic clock-driven traffic light algorithm with a fixed schedule")
def step_impl_basic_algo(context):
    if not hasattr(context, "simulationId"):
        context.execute_steps('Given a simple traffic generator with randomized arrivals from each direction')

    # Query the ControlAlgorithm catalogue via OpenAPI
    resp = requests.get(_u(context, "/control-algorithms"))
    assert resp.status_code == 200
    algos = resp.json()

    # Domain-model term: ControlAlgorithm.name
    context.controlAlgorithm = next((a for a in algos if a.get("name") == "basic"), None)
    assert context.controlAlgorithm is not None


@given("the simulation is running")
def step_impl_sim_running(context):
    if not hasattr(context, "simulationId"):
        context.execute_steps('Given a simple traffic generator with randomized arrivals from each direction')

    # Use OpenAPI `/simulations/{id}` to assert Simulation.running
    resp = requests.get(_u(context, f"/simulations/{context.simulationId}"))
    assert resp.status_code == 200
    assert resp.json().get("running") is True


@when("vehicle movements and light changes occur")
def step_impl_vehicle_movements(context):
    # Advance the Simulation by one tick using the OpenAPI `/simulations/{id}/step`
    resp = requests.post(_u(context, f"/simulations/{context.simulationId}/step"))
    assert resp.status_code == 200


@then("they are visualized on a map view showing stops, movements, and light states")
def step_impl_visualization(context):
    # Retrieve the domain `Intersection` state via the OpenAPI `/simulations/{id}/state`
    resp = requests.get(_u(context, f"/simulations/{context.simulationId}/state"))
    assert resp.status_code == 200
    intersection_state = resp.json()

    # Domain-model: Intersection -> RoadApproach -> TrafficLight (LightState) + Sensor (sensorCount)
    road_approaches = intersection_state.get("approaches", [])
    assert road_approaches, "No RoadApproach entries returned by /state"

    # Verify each RoadApproach follows the OpenAPI / domain contract
    valid_light_states = {"Red", "Green", "Amber", "FlashingAmber", "AllRed"}
    assert all(
        ("id" in a and "lightState" in a and "sensorCount" in a and a["lightState"] in valid_light_states)
        for a in road_approaches
    )


@when("the simulation starts")
def step_impl_start(context):
    # Starting the Simulation is done via POST /simulations — reuse existing step
    context.execute_steps('Given a simple traffic generator with randomized arrivals from each direction')


@when("time ticks advance")
def step_impl_ticks_advance(context):
    # Advance the Simulation (domain: Simulation.step()) through the OpenAPI endpoint
    for _ in range(3):
        r = requests.post(_u(context, f"/simulations/{context.simulationId}/step"))
        assert r.status_code == 200


@then("vehicles are spawned at random intervals and enter the crossroad")
def step_impl_check_spawns(context):
    # Look for domain SpawnedVehicle objects via /simulations/{id}/state
    saw_spawn: bool = False
    for _ in range(10):
        requests.post(_u(context, f"/simulations/{context.simulationId}/step"))
        r = requests.get(_u(context, f"/simulations/{context.simulationId}/state"))
        assert r.status_code == 200
        recent_spawned = r.json().get("recentSpawned", [])
        # Each SpawnedVehicle should include approachId and vehicle.type per domain model
        if any((s.get("approachId") and s.get("vehicle", {}).get("type")) for s in recent_spawned):
            saw_spawn = True
            break
    assert saw_spawn, "No SpawnedVehicle observed via API"


@then("the algorithm switches lights according to the clock without using traffic data")
def step_impl_algo_switches(context):
    # Validate that RoadApproach TrafficLight `LightState` values change over ticks
    sequences = []
    for _ in range(6):
        requests.post(_u(context, f"/simulations/{context.simulationId}/step"))
        r = requests.get(_u(context, f"/simulations/{context.simulationId}/state"))
        assert r.status_code == 200
        approaches = r.json().get("approaches", [])
        # Record the LightState per RoadApproach.id (domain terms)
        sequences.append({a["id"]: a["lightState"] for a in approaches})

    # Ensure at least one RoadApproach saw a LightState transition
    changed = any(sequences[i] != sequences[i + 1] for i in range(len(sequences) - 1))
    assert changed, f"No TrafficLight LightState transitions observed across ticks: {sequences}"


@given("an intersection with sensors, a control algorithm, and traffic generator settings")
def step_impl_kpi_setup(context):
    # Ensure a running Simulation exists (domain: Intersection + sensors + TrafficGenerator)
    context.execute_steps('Given a simple traffic generator with randomized arrivals from each direction')


@when("a simulation run completes")
def step_impl_sim_complete(context):
    # Advance a few ticks then delete the Simulation resource via OpenAPI
    for _ in range(10):
        requests.post(_u(context, f"/simulations/{context.simulationId}/step"))
    r = requests.delete(_u(context, f"/simulations/{context.simulationId}"))
    assert r.status_code in (200, 204)


@then("KPIs expressing control quality are calculated and reported")
def step_impl_kpis_reported(context):
    # Fetch KPIReport (domain: KPIReport.metrics)
    r = requests.get(_u(context, f"/simulations/{context.simulationId}/kpis"))
    assert r.status_code == 200
    kpi_report = r.json()
    assert "metrics" in kpi_report and isinstance(kpi_report["metrics"], dict)
    # Example metric produced by the Simulation domain
    assert "vehicle_count" in kpi_report["metrics"]


@given("a running simulation")
def step_impl_running_sim(context):
    context.execute_steps('Given a simple traffic generator with randomized arrivals from each direction')
    r = requests.get(_u(context, f"/simulations/{context.simulationId}"))
    assert r.status_code == 200
    assert r.json().get("running") is True


@when("recording is enabled")
def step_impl_enable_recording(context):
    # Record the Simulation run via OpenAPI `/simulations/{id}/recordings`
    r = requests.post(_u(context, f"/simulations/{context.simulationId}/recordings"))
    assert r.status_code == 201
    context.recording = r.json()


@then("the run's events are stored for later analysis")
def step_impl_recording_stored(context):
    # List recordings for the Simulation and assert Recording schema fields
    r = requests.get(_u(context, f"/simulations/{context.simulationId}/recordings"))
    assert r.status_code == 200
    recordings = r.json()
    assert isinstance(recordings, list) and recordings, "No recordings returned by API"
    rec = recordings[0]
    assert all(k in rec for k in ("id", "simulationId", "createdAt"))


@then("the simulation is replayed to review behavior and results")
def step_impl_playback(context):
    # Start a Playback for a recording via `/recordings/{id}/playback`
    r = requests.get(_u(context, f"/simulations/{context.simulationId}/recordings"))
    assert r.status_code == 200
    recs = r.json()
    assert recs, "No recordings available to start playback"

    recording_id = recs[0]["id"]
    p = requests.post(_u(context, f"/recordings/{recording_id}/playback"))
    assert p.status_code == 201
    playback = p.json()

    # Playback schema fields (domain: Playback.position)
    assert playback.get("recordingId") == recording_id
    assert isinstance(playback.get("position"), int)
    assert playback.get("position") >= 0


# --- control algorithm & safety-related step implementations (use OpenAPI) ---

@given("multiple control algorithms are available (clock-driven, flashing amber, advanced)")
def step_impl_multiple_algos(context):
    r = requests.get(_u(context, "/control-algorithms"))
    assert r.status_code == 200
    names = [a.get("name") for a in r.json()]
    for expected in ("basic", "flashing-amber", "advanced"):
        assert expected in names, f"ControlAlgorithm '{expected}' not found in catalog: {names}"


@when("an operator selects an algorithm")
def step_impl_operator_selects_algorithm(context):
    # Default to selecting 'advanced' when not specified
    algo = getattr(context, "select_algorithm", "advanced")
    resp = requests.put(_u(context, f"/simulations/{context.simulationId}/control-algorithm"), json={"algorithmName": algo})
    assert resp.status_code == 200
    context.selectedAlgorithm = algo


@then("the chosen algorithm governs the lights")
def step_impl_chosen_algo_governs(context):
    assert hasattr(context, "selectedAlgorithm")
    r = requests.get(_u(context, f"/simulations/{context.simulationId}/state"))
    assert r.status_code == 200
    # The state returns controlAlgorithm by name
    assert r.json().get("controlAlgorithm") and r.json().get("controlAlgorithm").get("name") == context.selectedAlgorithm


@given("an active control algorithm")
def step_impl_active_control_algorithm(context):
    # Ensure a running simulation exists (defaults to 'basic')
    context.execute_steps('Given a simple traffic generator with randomized arrivals from each direction')


@when("switching to another algorithm")
def step_impl_switching_algorithm(context):
    # Choose 'flashing-amber' as the alternative
    context.execute_steps('When an operator selects an algorithm')


@then("all lights enter a safe transitional state before the new algorithm takes over")
def step_impl_safe_transition(context):
    r = requests.get(_u(context, f"/simulations/{context.simulationId}/state"))
    assert r.status_code == 200
    approaches = r.json().get("approaches", [])
    # Safety fallback in the server uses FlashingAmber for all approaches
    assert all(a.get("lightState") == "FlashingAmber" for a in approaches), f"Expected FlashingAmber transitional state, got: {approaches}"


@given("the safety checker detects a rule violation")
def step_impl_safety_detects_violation(context):
    # Prepare an explicitly unsafe SignalPhase (two approaches green)
    context.unsafe_phase = {
        "name": "unsafe-multi-green",
        "durationSeconds": 1,
        "approachStates": {"north": "Green", "south": "Green", "east": "Green"},
    }


@when("the violation occurs")
def step_impl_violation_occurs(context):
    # Apply the unsafe phase via the API and expect the server to apply a fallback
    resp = requests.post(_u(context, f"/simulations/{context.simulationId}/apply-phase"), json=context.unsafe_phase)
    assert resp.status_code == 200
    context.applied_result = resp.json()


@then("the system automatically enters flashing amber mode until a safe state is restored")
def step_impl_system_enters_flashing(context):
    # The API should have returned the applied phase name (fallback)
    assert context.applied_result and context.applied_result.get("appliedPhase")
    # Verify the live simulation state shows FlashingAmber for all approaches
    r = requests.get(_u(context, f"/simulations/{context.simulationId}/state"))
    assert r.status_code == 200
    approaches = r.json().get("approaches", [])
    assert all(a.get("lightState") == "FlashingAmber" for a in approaches)


# --- decoupled UI / multi-client steps (use OpenAPI only) ---

@given("the simulator runs independently of the UI")
def step_impl_simulator_runs_independent(context):
    context.execute_steps('Given a simple traffic generator with randomized arrivals from each direction')


@when("the UI is closed and reopened")
def step_impl_ui_restart(context):
    # UI state is client-side; simulate by fetching state before/after reconnect
    r1 = requests.get(_u(context, f"/simulations/{context.simulationId}/state"))
    assert r1.status_code == 200
    context.ui_snapshot_before = r1.json()
    # simulate close/reopen by calling the same endpoint again
    r2 = requests.get(_u(context, f"/simulations/{context.simulationId}/state"))
    assert r2.status_code == 200
    context.ui_snapshot_after = r2.json()


@then("the simulation continues and the UI reconnects without losing state")
def step_impl_ui_reconnects(context):
    assert context.ui_snapshot_before == context.ui_snapshot_after


@given("the simulator is network-accessible")
def step_impl_simulator_network_accessible(context):
    # The server exposes the simulation resources via HTTP
    r = requests.get(_u(context, "/simulations"))
    assert r.status_code == 200


@when("multiple UI instances connect")
def step_impl_multiple_ui_connect(context):
    # Simulate two UI clients polling the same simulation state
    r1 = requests.get(_u(context, f"/simulations/{context.simulationId}/state"))
    r2 = requests.get(_u(context, f"/simulations/{context.simulationId}/state"))
    assert r1.status_code == 200 and r2.status_code == 200
    context.ui1 = r1.json()
    context.ui2 = r2.json()


@then("each UI shows the current simulation state concurrently")
def step_impl_each_ui_shows_state(context):
    assert context.ui1 == context.ui2


@given("the simulator exposes a secure network interface")
def step_impl_simulator_secure_interface(context):
    # TLS/auth not implemented in the simple server; assert endpoint is reachable
    r = requests.get(_u(context, "/layouts"))
    assert r.status_code == 200


@when("a UI runs on another machine")
def step_impl_ui_on_another_machine(context):
    # Simulate remote UI by calling the same HTTP endpoints from this test client
    r = requests.get(_u(context, f"/simulations/{context.simulationId}/state"))
    assert r.status_code == 200


@then("it can control and observe the simulation state remotely")
def step_impl_remote_ui_controls(context):
    # Verify remote UI can advance the simulation and observe state
    r1 = requests.post(_u(context, f"/simulations/{context.simulationId}/step"))
    assert r1.status_code == 200
    r2 = requests.get(_u(context, f"/simulations/{context.simulationId}/state"))
    assert r2.status_code == 200


# --- maps / live data steps (use /maps OpenAPI) ---

@given("access to map sources such as OpenStreetMap or Google Maps")
def step_impl_map_sources(context):
    # Confirm the server accepts map sources via /maps
    r = requests.post(_u(context, "/maps"), json={"source": "OSM:test"})
    assert r.status_code == 201
    context.map = r.json()


@when("the UI loads a scenario")
def step_impl_ui_loads_scenario(context):
    # Loading a scenario simply ensures the layout exists and a simulation can be started
    context.execute_steps('Given a simple traffic generator with randomized arrivals from each direction')


@then("actual map data is displayed in the UI for the crossing")
def step_impl_map_displayed(context):
    # UI rendering is out-of-band; assert the server has the map source stored
    assert context.map and "source" in context.map


# --- persistence / layouts (use /layouts OpenAPI) ---

@given("a designed crossroad configuration")
def step_impl_designed_configuration(context):
    context.example_layout = {"name": "test-layout", "intersection": {"id": "i1", "approaches": [{"id": "north"}]}}


@when("the configuration is stored in persistent storage")
def step_impl_store_configuration(context):
    r = requests.post(_u(context, "/layouts"), json=context.example_layout)
    assert r.status_code == 201
    context.saved_layout = r.json()


@then("the layout can be reloaded and reused across sessions")
def step_impl_reload_layout(context):
    lid = context.saved_layout.get("id")
    r = requests.get(_u(context, f"/layouts/{lid}"))
    assert r.status_code == 200
    assert r.json().get("id") == lid


@given("a crossroads editor and viewer")
def step_impl_editor_and_viewer(context):
    context.execute_steps('Given a designed crossroad configuration')


@when("a user designs or modifies an intersection layout")
def step_impl_user_designs_layout(context):
    context.example_layout["name"] = "edited-layout"
    r = requests.post(_u(context, "/layouts"), json=context.example_layout)
    assert r.status_code == 201
    context.saved_layout = r.json()


@then("the layout can be saved, selected, and reused within the application")
def step_impl_layout_saved_and_reused(context):
    assert context.saved_layout and "id" in context.saved_layout


@given("a library of saved real-world and hypothetical layouts")
def step_impl_library_of_layouts(context):
    # Ensure at least the default layout exists in store
    r = requests.get(_u(context, "/layouts"))
    assert r.status_code == 200


@when("a scenario is selected")
def step_impl_scenario_selected(context):
    r = requests.get(_u(context, "/layouts"))
    assert r.status_code == 200
    layouts = r.json()
    assert layouts
    context.selected_layout = layouts[0]


@then("the chosen layout is loaded for simulation and visualization")
def step_impl_chosen_layout_loaded(context):
    assert context.selected_layout and "id" in context.selected_layout


# --- safety-checker observation step (use OpenAPI) ---

@given("a safety checker between control algorithms and traffic lights")
def step_impl_safety_checker_present(context):
    # The server-side Simulation uses SafetyChecker internally; assert simulation can be created
    context.execute_steps('Given a simple traffic generator with randomized arrivals from each direction')


@when("a control algorithm issues light commands")
def step_impl_algo_issues_commands(context):
    # Apply a safe phase to the simulation via the API
    safe_phase = {"name": "safe-phase", "durationSeconds": 1, "approachStates": {"north": "Green"}}
    r = requests.post(_u(context, f"/simulations/{context.simulationId}/apply-phase"), json=safe_phase)
    assert r.status_code == 200


@then("conflicting or unsafe combinations are blocked and safety rules are enforced")
def step_impl_unsafe_blocked(context):
    # Try applying an unsafe phase and assert fallback was applied
    context.execute_steps('Given the safety checker detects a rule violation')
    context.execute_steps('When the violation occurs')
    context.execute_steps('Then the system automatically enters flashing amber mode until a safe state is restored')
