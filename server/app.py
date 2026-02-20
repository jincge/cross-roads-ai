import os
import sys
import time
from flask import Flask, jsonify, request, abort

# Expose repo root so `cross_roads_ai` imports resolve
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


# ---- Layouts (CRUD) ----
@app.route("/layouts", methods=["GET"])
def list_layouts():
    # return layout summaries
    out = [{"id": l["id"], "name": l.get("name", "")} for l in store.list_resources(store.layouts)]
    return jsonify(out)


@app.route("/layouts", methods=["POST"])
def create_layout():
    data = request.get_json(force=True)
    if not data:
        abort(400)
    created = store.create_resource(store.layouts, data)
    return jsonify(created), 201


@app.route("/layouts/<layout_id>", methods=["GET"])
def get_layout(layout_id):
    l = store.get_resource(store.layouts, layout_id)
    if not l:
        return ("", 404)
    return jsonify(l)


@app.route("/layouts/<layout_id>", methods=["PUT"])
def update_layout(layout_id):
    data = request.get_json(force=True)
    if not data:
        abort(400)
    updated = store.update_resource(store.layouts, layout_id, data)
    if not updated:
        return ("", 404)
    return jsonify(updated)


# ---- Control Algorithms (read-only catalog) ----
@app.route("/control-algorithms", methods=["GET"])
def list_algorithms():
    return jsonify(store.list_resources(store.control_algorithms))


# ---- Simulations ----
@app.route("/simulations", methods=["POST"])
def create_simulation():
    body = request.get_json(force=True)
    if not body:
        abort(400)
    layout_id = body.get("layoutId")
    algo_name = body.get("controlAlgorithmName")
    arrival_pattern = body.get("arrivalPattern")

    if layout_id not in store.layouts or algo_name not in store.control_algorithms:
        return ("", 404)

    # build phases from stored algorithm definition
    algo_def = store.control_algorithms[algo_name]
    phases = []
    for p in algo_def.get("phases", []):
        name = p.get("name")
        dur = float(p.get("durationSeconds", 5))
        approach_states = {}
        for ap, st in p.get("approachStates", {}).items():
            try:
                approach_states[ap] = LightState[st]
            except Exception:
                approach_states[ap] = LightState.Red
        phases.append(SignalPhase(name, dur, approach_states))

    directions = [a["id"] for a in store.layouts[layout_id]["intersection"]["approaches"]]
    intersection = Intersection(directions)
    algorithm = ControlAlgorithm(algo_name, phases)
    algorithm.setMode(body.get("controlMode", "fixed-schedule"))
    safety = SafetyChecker()
    generator = TrafficGenerator(directions)
    if arrival_pattern:
        generator.setArrivalPattern(arrival_pattern)

    sim = Simulation(intersection, algorithm, safety, generator)
    sim.start()

    sim_id = store.new_id()
    store.simulations[sim_id] = {
        "id": sim_id,
        "native_sim": sim,
        "running": True,
        "layoutId": layout_id,
        "createdAt": time.time(),
        "recordings": [],
    }

    sim_json = {
        "id": sim_id,
        "running": True,
        "layout": store.layouts[layout_id],
        "controlAlgorithm": store.control_algorithms[algo_name],
        "generator": {"arrivalPattern": arrival_pattern or "randomized", "spawnTrucks": False},
        "kpis": {"metrics": {}},
    }
    return jsonify(sim_json), 201


@app.route("/simulations", methods=["GET"])
def list_simulations():
    out = []
    for sid, s in store.simulations.items():
        out.append({"id": sid, "running": s.get("running", False), "layoutId": s.get("layoutId")})
    return jsonify(out)


@app.route("/simulations/<sim_id>", methods=["GET"])
def get_simulation(sim_id):
    s = store.get_resource(store.simulations, sim_id)
    if not s:
        return ("", 404)
    # build response
    layout = store.layouts.get(s.get("layoutId"))
    algo = None
    algoname = s["native_sim"].controlAlgorithm().getName()
    algo = store.control_algorithms.get(algoname)
    gen = {"arrivalPattern": getattr(s["native_sim"].generator, "_arrival_pattern", "randomized"), "spawnTrucks": False}
    kpis = {"metrics": s["native_sim"].kpiReport().getMetrics()}
    return jsonify({"id": sim_id, "running": s.get("running", False), "layout": layout, "controlAlgorithm": algo, "generator": gen, "kpis": kpis})


@app.route("/simulations/<sim_id>", methods=["DELETE"])
def delete_simulation(sim_id):
    s = store.get_resource(store.simulations, sim_id)
    if not s:
        return ("", 404)
    # attempt to stop
    try:
        s["native_sim"].stop()
    except Exception:
        pass
    store.delete_resource(store.simulations, sim_id)
    return ("", 204)


@app.route("/simulations/<sim_id>/step", methods=["POST"])
def step_simulation(sim_id):
    s = store.get_resource(store.simulations, sim_id)
    if not s:
        return ("", 404)
    s["native_sim"].step()
    # return current simulation state summary
    return get_simulation(sim_id)


@app.route("/simulations/<sim_id>/control-algorithm", methods=["PUT"])
def switch_control_algorithm(sim_id):
    s = store.get_resource(store.simulations, sim_id)
    if not s:
        return ("", 404)
    body = request.get_json(force=True)
    if not body or "algorithmName" not in body:
        abort(400)
    algo_name = body["algorithmName"]
    mode = body.get("mode")
    if algo_name not in store.control_algorithms:
        return ("", 404)
    # construct new algorithm and assign to running sim
    algo_def = store.control_algorithms[algo_name]
    phases = []
    for p in algo_def.get("phases", []):
        name = p.get("name")
        dur = float(p.get("durationSeconds", 5))
        approach_states = {}
        for ap, st in p.get("approachStates", {}).items():
            try:
                approach_states[ap] = LightState[st]
            except Exception:
                approach_states[ap] = LightState.Red
        phases.append(SignalPhase(name, dur, approach_states))
    new_algo = ControlAlgorithm(algo_name, phases)
    if mode:
        new_algo.setMode(mode)
    # apply with safe transition: use safety.validate on first phase
    chosen = new_algo.nextPhase()
    chosenPhase = chosen if s["native_sim"].safety.validate(chosen) else s["native_sim"].safety.fallbackPhase(s["native_sim"].intersection().approachIds())
    s["native_sim"]._currentPhase = chosenPhase
    s["native_sim"].algorithm = new_algo
    return get_simulation(sim_id)


# ---- KPIs ----
@app.route("/simulations/<sim_id>/kpis", methods=["GET"])
def get_kpis(sim_id):
    s = store.get_resource(store.simulations, sim_id)
    if not s:
        return ("", 404)
    metrics = s["native_sim"].kpiReport().getMetrics()
    return jsonify({"metrics": metrics})


# ---- Recordings (simple snapshot of recorder events) ----
@app.route("/simulations/<sim_id>/recordings", methods=["POST"])
def create_recording(sim_id):
    s = store.get_resource(store.simulations, sim_id)
    if not s:
        return ("", 404)
    rid = store.new_id()
    rec = {"id": rid, "simulationId": sim_id, "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    # store recorder events if available
    try:
        events = s["native_sim"].recorder().events()
        rec["events"] = list(events)
    except Exception:
        rec["events"] = []
    store.recordings[rid] = rec
    # link to simulation
    s.setdefault("recordings", []).append(rid)
    return jsonify(rec), 201


@app.route("/simulations/<sim_id>/recordings", methods=["GET"])
def list_recordings(sim_id):
    s = store.get_resource(store.simulations, sim_id)
    if not s:
        return ("", 404)
    recs = [store.recordings[rid] for rid in s.get("recordings", []) if rid in store.recordings]
    return jsonify(recs)


@app.route("/recordings/<rec_id>/playback", methods=["POST"])
def start_playback(rec_id):
    rec = store.get_resource(store.recordings, rec_id)
    if not rec:
        return ("", 404)
    # create a simple playback token object
    pbid = store.new_id()
    pb = {"id": pbid, "recordingId": rec_id, "position": 0}
    # store transiently (not persisted beyond memory)
    store.recordings[rec_id].setdefault("playbacks", []).append(pb)
    return jsonify(pb), 201


# ---- Maps ----
@app.route("/maps", methods=["POST"])
def load_map():
    data = request.get_json(force=True)
    if not data or "source" not in data:
        abort(400)
    mid = store.new_id()
    data["id"] = mid
    data.setdefault("loaded", True)
    store.maps[mid] = data
    return jsonify(data), 201


if __name__ == "__main__":
    print("Server (Flask) starting on http://0.0.0.0:8080")
    app.run(host="0.0.0.0", port=8080)
