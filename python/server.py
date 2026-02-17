"""Flask-based HTTP server that mirrors `server/server.cpp` using the Python domain model.

Run from repo root with:

    python3 python/server.py

The server listens on port 8080 by default to match the C++ server.
"""
import pkgutil
# Backport compatibility helper for pkgutil.get_loader (some stdlib
# builds used by newer Python versions omit this helper). Flask expects
# get_loader to exist; provide a thin shim that returns a loader via
# importlib.spec if available.
if not hasattr(pkgutil, "get_loader"):
    import importlib.util

    def _get_loader(name: str):
        spec = importlib.util.find_spec(name)
        return spec.loader if spec else None

    pkgutil.get_loader = _get_loader

from flask import Flask, jsonify, request, abort
from datetime import datetime

import store
from cross_roads_ai import Intersection, SignalPhase, ControlAlgorithm, SafetyChecker, TrafficGenerator, Simulation, LightState

# Use a stable import name rather than __main__ to avoid pkgutil/importlib
# issues when the script is run directly.
app = Flask("server")


@app.route("/layouts", methods=["GET"])
def get_layouts():
    return jsonify(list(store.layouts.values()))


@app.route("/layouts", methods=["POST"])
def post_layouts():
    try:
        new_layout = request.get_json()
        if not isinstance(new_layout, dict):
            abort(400)
        layout_id = new_layout.get("id", store.new_id())
        new_layout["id"] = layout_id
        store.layouts[layout_id] = new_layout
        return jsonify(new_layout), 201
    except Exception as e:
        return str(e), 400


@app.route("/control-algorithms", methods=["GET"])
def get_algorithms():
    return jsonify(list(store.control_algorithms.values()))


@app.route("/simulations", methods=["POST"])
def create_simulation():
    try:
        body = request.get_json() or {}
        layout_id = body["layoutId"]
        algo_name = body["controlAlgorithmName"]

        if layout_id not in store.layouts or algo_name not in store.control_algorithms:
            abort(404)

        dirs = ["north", "east", "south", "west"]
        intersection = Intersection(dirs)

        phases = []
        phases.append(SignalPhase("north-south", 5, {"north": LightState.Green, "south": LightState.Green}))
        phases.append(SignalPhase("east-west", 5, {"east": LightState.Green, "west": LightState.Green}))

        algorithm = ControlAlgorithm(algo_name, phases)
        safety = SafetyChecker()
        generator = TrafficGenerator(intersection.approachIds())

        sim_obj = Simulation(intersection, algorithm, safety, generator)
        sim_obj.start()

        sim_id = store.new_id()
        server_sim = {
            "id": sim_id,
            "native_sim": sim_obj,
            "running": True,
            "layout": store.layouts[layout_id],
            "controlAlgorithm": store.control_algorithms[algo_name],
        }
        store.simulations[sim_id] = server_sim

        sim_json = {
            "id": sim_id,
            "running": True,
            "layout": store.layouts[layout_id],
            "controlAlgorithm": store.control_algorithms[algo_name],
        }
        return jsonify(sim_json), 201
    except KeyError:
        abort(400)
    except Exception as e:
        return str(e), 400


@app.route("/simulations", methods=["GET"])
def list_simulations():
    result = []
    for sim in store.simulations.values():
        result.append({"id": sim["id"], "running": sim["running"], "layoutId": sim.get("layout", {}).get("id", "")})
    return jsonify(result)


@app.route("/simulations/<sim_id>/step", methods=["POST"])
def step_simulation(sim_id: str):
    if sim_id not in store.simulations:
        abort(404)
    store.simulations[sim_id]["native_sim"].step()
    return "", 200


@app.route("/simulations/<sim_id>", methods=["GET"])
def get_simulation(sim_id: str):
    if sim_id not in store.simulations:
        abort(404)
    sim = store.simulations[sim_id]
    return jsonify({"id": sim_id, "running": sim["running"]})


@app.route("/simulations/<sim_id>/kpis", methods=["GET"])
def get_kpis(sim_id: str):
    if sim_id not in store.simulations:
        abort(404)
    kpis = store.simulations[sim_id]["native_sim"].kpiReport().getMetrics()
    return jsonify({"metrics": kpis})


@app.route("/simulations/<sim_id>/state", methods=["GET"])
def get_simulation_state(sim_id: str):
    """Return current RoadApproach light states, sensor counts and recent SpawnedVehicle list.

    Field names follow the OpenAPI / cross-road.puml terminology (e.g. `sensorCount`).
    """
    if sim_id not in store.simulations:
        abort(404)
    sim = store.simulations[sim_id]["native_sim"]

    approaches = []
    for app_obj in sim.intersection().approaches():
        approaches.append({
            "id": app_obj.direction(),
            "lightState": app_obj.light().getState().name,
            "sensorCount": app_obj.sensor().getCount(),
        })

    recent = []
    for s in sim.recentSpawned():
        recent.append({"approachId": s.approachId, "vehicle": {"type": s.vehicle.type}})

    return jsonify({
        "approaches": approaches,
        "recentSpawned": recent,
        "controlAlgorithm": sim.controlAlgorithm().getName(),
    })


@app.route("/simulations/<sim_id>/control-algorithm", methods=["PUT"])
def set_simulation_control_algorithm(sim_id: str):
    """Switch the active ControlAlgorithm for a running Simulation using OpenAPI.

    Performs a safe transitional phase (fallback) immediately after switching so
    UIs observe a deterministic safety state.
    """
    if sim_id not in store.simulations:
        abort(404)
    data = request.get_json() or {}
    algo_name = data.get("algorithmName")
    mode = data.get("mode", "")
    if not algo_name or algo_name not in store.control_algorithms:
        abort(404)

    sim = store.simulations[sim_id]["native_sim"]

    # Build ControlAlgorithm from the catalog entry
    catalog = store.control_algorithms[algo_name]
    phases = []
    for p in catalog.get("phases", []):
        # approachStates values are strings matching LightState enum names
        states = {k: getattr(LightState, v) for k, v in p.get("approachStates", {}).items()}
        phases.append(SignalPhase(p.get("name", "phase"), p.get("durationSeconds", 1), states))

    new_algo = ControlAlgorithm(algo_name, phases)
    new_algo.setMode(mode)
    # Replace the simulation's algorithm and apply a safety fallback transition
    sim.algorithm = new_algo
    transitional = sim.safety.fallbackPhase(sim.intersection().approachIds())
    sim.intersection().applyPhase(transitional)

    return jsonify({"id": sim_id, "controlAlgorithm": store.control_algorithms[algo_name]}), 200


@app.route("/simulations/<sim_id>/apply-phase", methods=["POST"])
def apply_phase(sim_id: str):
    """Apply a user-provided SignalPhase to the Simulation via the API.

    If the SafetyChecker rejects the requested phase, a fallback phase is applied
    instead and the response indicates the fallback.
    """
    if sim_id not in store.simulations:
        abort(404)
    body = request.get_json() or {}
    try:
        name = body["name"]
        duration = int(body.get("durationSeconds", 1))
        approach_states = {k: getattr(LightState, v) for k, v in body.get("approachStates", {}).items()}
        phase = SignalPhase(name, duration, approach_states)
    except Exception:
        abort(400)

    sim = store.simulations[sim_id]["native_sim"]
    if sim.safety.validate(phase):
        sim.intersection().applyPhase(phase)
        applied = phase.getName()
    else:
        fallback = sim.safety.fallbackPhase(sim.intersection().approachIds())
        sim.intersection().applyPhase(fallback)
        applied = fallback.getName()

    return jsonify({"id": sim_id, "appliedPhase": applied}), 200


@app.route("/maps", methods=["POST"])
def post_maps():
    body = request.get_json() or {}
    if not isinstance(body, dict) or "source" not in body:
        abort(400)
    map_id = body.get("id", store.new_id())
    body["id"] = map_id
    store.map_data[map_id] = body
    return jsonify(body), 201


@app.route("/simulations/<sim_id>", methods=["DELETE"])
def delete_simulation(sim_id: str):
    if sim_id not in store.simulations:
        abort(404)
    sim = store.simulations[sim_id]["native_sim"]
    try:
        sim.stop()
    except Exception:
        pass
    del store.simulations[sim_id]
    return "", 204


@app.route("/simulations/<sim_id>/recordings", methods=["POST"])
def create_recording(sim_id: str):
    if sim_id not in store.simulations:
        abort(404)
    sim = store.simulations[sim_id]["native_sim"]
    events = sim.recorder().events()

    rec_id = store.new_id()
    rec = {"id": rec_id, "simulationId": sim_id, "createdAt": datetime.utcnow().isoformat() + "Z", "events": events}
    store.recordings[rec_id] = rec
    return jsonify({"id": rec_id, "simulationId": sim_id, "createdAt": rec["createdAt"]}), 201


@app.route("/simulations/<sim_id>/recordings", methods=["GET"])
def list_recordings(sim_id: str):
    if sim_id not in store.simulations:
        abort(404)
    result = []
    for r in store.recordings.values():
        if r.get("simulationId") == sim_id:
            result.append({"id": r["id"], "simulationId": r["simulationId"], "createdAt": r["createdAt"]})
    return jsonify(result)


@app.route("/recordings/<rec_id>/playback", methods=["POST"])
def start_playback(rec_id: str):
    if rec_id not in store.recordings:
        abort(404)
    recording = store.recordings[rec_id]
    pb_id = store.new_id()
    pb = {"id": pb_id, "recordingId": rec_id, "position": 0}
    store.playbacks[pb_id] = {"id": pb_id, "recordingId": rec_id, "position": 0, "events": recording.get("events", [])}
    return jsonify(pb), 201


if __name__ == "__main__":
    import os
    store.initialize()
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
