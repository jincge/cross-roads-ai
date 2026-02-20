import os
import sys
from flask import Flask, jsonify, request, abort

# Ensure project root is on path so `cross_roads_ai` imports resolve
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from cross_roads_ai import (
    Intersection,
    SignalPhase,
    ControlAlgorithm,
    SafetyChecker,
    TrafficGenerator,
    Simulation,
    LightState,
)

import server.store as store

app = Flask(__name__)
store.initialize()


@app.route("/layouts", methods=["GET"])
def get_layouts():
    return jsonify(list(store.layouts.values()))


@app.route("/layouts", methods=["POST"])
def post_layouts():
    data = request.get_json()
    if not data:
        abort(400)
    id_ = data.get("id", store.new_id())
    data["id"] = id_
    store.layouts[id_] = data
    return jsonify(data), 201


@app.route("/control-algorithms", methods=["GET"])
def get_algorithms():
    return jsonify(list(store.control_algorithms.values()))


@app.route("/simulations", methods=["POST"])
def create_simulation():
    body = request.get_json()
    if not body:
        abort(400)
    layout_id = body.get("layoutId")
    algo_name = body.get("controlAlgorithmName")
    if layout_id not in store.layouts or algo_name not in store.control_algorithms:
        return ("", 404)

    # Build phases from the control algorithm definition
    algo_def = store.control_algorithms[algo_name]
    phases = []
    for p in algo_def.get("phases", []):
        name = p.get("name")
        dur = float(p.get("durationSeconds", 5))
        approach_states = {}
        for ap, st in p.get("approachStates", {}).items():
            # map string name -> LightState enum
            try:
                approach_states[ap] = LightState[st]
            except Exception:
                approach_states[ap] = LightState.Red
        phases.append(SignalPhase(name, dur, approach_states))

    directions = ["north", "east", "south", "west"]
    intersection = Intersection(directions)
    algorithm = ControlAlgorithm(algo_name, phases)
    algorithm.setMode("fixed-schedule")
    safety = SafetyChecker()
    generator = TrafficGenerator(directions)

    sim = Simulation(intersection, algorithm, safety, generator)
    sim.start()

    sim_id = store.new_id()
    store.simulations[sim_id] = {"id": sim_id, "native_sim": sim, "running": True}

    sim_json = {
        "id": sim_id,
        "running": True,
        "layout": store.layouts[layout_id],
        "controlAlgorithm": store.control_algorithms[algo_name],
    }
    return jsonify(sim_json), 201


@app.route("/simulations", methods=["GET"])
def list_simulations():
    out = []
    for sid, s in store.simulations.items():
        out.append({"id": sid, "running": s.get("running", False), "layoutId": s.get("id")})
    return jsonify(out)


@app.route("/simulations/<sim_id>/step", methods=["POST"])
def step_simulation(sim_id):
    s = store.simulations.get(sim_id)
    if not s:
        return ("", 404)
    s["native_sim"].step()
    return ("", 200)


@app.route("/simulations/<sim_id>", methods=["GET"])
def get_simulation(sim_id):
    s = store.simulations.get(sim_id)
    if not s:
        return ("", 404)
    return jsonify({"id": sim_id, "running": s.get("running", False)})


@app.route("/simulations/<sim_id>/kpis", methods=["GET"])
def get_kpis(sim_id):
    s = store.simulations.get(sim_id)
    if not s:
        return ("", 404)
    metrics = s["native_sim"].kpiReport().getMetrics()
    return jsonify({"metrics": metrics})


if __name__ == "__main__":
    print("Server starting on http://localhost:8080")
    app.run(host="0.0.0.0", port=8080)
