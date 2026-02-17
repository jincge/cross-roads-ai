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

import store
from src import Intersection, SignalPhase, ControlAlgorithm, SafetyChecker, TrafficGenerator, Simulation
from src.light_state import LightState

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
    """Return current approach light states, sensor counts and recent spawned vehicles."""
    if sim_id not in store.simulations:
        abort(404)
    sim = store.simulations[sim_id]["native_sim"]

    approaches = []
    for app_obj in sim.intersection().approaches():
        approaches.append({
            "id": app_obj.direction(),
            "lightState": app_obj.light().getState().name,
            "count": app_obj.sensor().getCount(),
        })

    recent = []
    for s in sim.recentSpawned():
        recent.append({"approachId": s.approachId, "vehicle": {"type": s.vehicle.type}})

    return jsonify({
        "approaches": approaches,
        "recentSpawned": recent,
        "controlAlgorithm": sim.controlAlgorithm().getName(),
    })


if __name__ == "__main__":
    store.initialize()
    app.run(host="0.0.0.0", port=8080)
