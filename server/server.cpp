#include "httplib.h"
#include "json.hpp"
#include "store.h"
#include "../src/Simulation.h"
#include "../src/Intersection.h"
#include "../src/ControlAlgorithm.h"
#include "../src/SafetyChecker.h"
#include "../src/TrafficGenerator.h"
#include <iostream>

using json = nlohmann::json;

int main() {
    httplib::Server svr;
    store::initialize();

    // GET /layouts
    svr.Get("/layouts", [](const httplib::Request&, httplib::Response& res) {
        json layout_list = json::array();
        for (const auto& pair : store::layouts) {
            layout_list.push_back(pair.second);
        }
        res.set_content(layout_list.dump(), "application/json");
    });

    // POST /layouts
    svr.Post("/layouts", [](const httplib::Request& req, httplib::Response& res) {
        try {
            json new_layout = json::parse(req.body);
            std::string id = new_layout.value("id", store::new_id());
            new_layout["id"] = id;
            store::layouts[id] = new_layout;
            res.status = 201;
            res.set_content(new_layout.dump(), "application/json");
        } catch (const std::exception& e) {
            res.status = 400;
            res.set_content(e.what(), "text/plain");
        }
    });

    // GET /control-algorithms
    svr.Get("/control-algorithms", [](const httplib::Request&, httplib::Response& res) {
        json algo_list = json::array();
        for (const auto& pair : store::control_algorithms) {
            algo_list.push_back(pair.second);
        }
        res.set_content(algo_list.dump(), "application/json");
    });

    // POST /simulations
    svr.Post("/simulations", [](const httplib::Request& req, httplib::Response& res) {
        try {
            json req_body = json::parse(req.body);
            std::string layout_id = req_body["layoutId"];
            std::string algo_name = req_body["controlAlgorithmName"];

            if (store::layouts.find(layout_id) == store::layouts.end() || store::control_algorithms.find(algo_name) == store::control_algorithms.end()) {
                res.status = 404;
                return;
            }

            // Create native simulation objects from JSON definitions
            std::vector<std::string> dirs = {"north", "east", "south", "west"};
            Intersection intersection(dirs);

            std::vector<SignalPhase> phases;
            // Simplified phase creation
            phases.emplace_back("north-south", 5, std::unordered_map<std::string, LightState>{{"north", LightState::Green}, {"south", LightState::Green}});
            phases.emplace_back("east-west", 5, std::unordered_map<std::string, LightState>{{"east", LightState::Green}, {"west", LightState::Green}});
            ControlAlgorithm algorithm(algo_name, phases);

            SafetyChecker safety;
            TrafficGenerator generator(intersection.approachIds());

            std::string sim_id = store::new_id();
            store::ServerSimulation server_sim;
            server_sim.id = sim_id;
            server_sim.native_sim = Simulation(std::move(intersection), std::move(algorithm), std::move(safety), std::move(generator));
            server_sim.running = true;

            store::simulations[sim_id] = std::move(server_sim);

            json sim_json;
            sim_json["id"] = sim_id;
            sim_json["running"] = true;
            sim_json["layout"] = store::layouts[layout_id];
            sim_json["controlAlgorithm"] = store::control_algorithms[algo_name];

            res.status = 201;
            res.set_content(sim_json.dump(), "application/json");

        } catch (const std::exception& e) {
            res.status = 400;
            res.set_content(e.what(), "text/plain");
        }
    });

    // GET /simulations
    svr.Get("/simulations", [](const httplib::Request&, httplib::Response& res) {
        json sim_list = json::array();
        for (const auto& pair : store::simulations) {
            json s;
            s["id"] = pair.second.id;
            s["running"] = pair.second.running;
            s["layoutId"] = pair.second.native_sim.intersection().approachIds()[0]; // simplified
            sim_list.push_back(s);
        }
        res.set_content(sim_list.dump(), "application/json");
    });

    // POST /simulations/{simulationId}/step
    svr.Post(R"(/simulations/([^/]+)/step)", [](const httplib::Request& req, httplib::Response& res) {
        std::string sim_id = req.matches[1];
        if (store::simulations.find(sim_id) == store::simulations.end()) {
            res.status = 404;
            return;
        }
        store::simulations.at(sim_id).native_sim.step();
        res.status = 200;
    });

    // GET /simulations/{simulationId}
    svr.Get(R"(/simulations/([^/]+))", [](const httplib::Request& req, httplib::Response& res) {
        std::string sim_id = req.matches[1];
        if (store::simulations.find(sim_id) == store::simulations.end()) {
            res.status = 404;
            return;
        }
        // Simplified response
        json sim_json;
        sim_json["id"] = sim_id;
        sim_json["running"] = store::simulations.at(sim_id).running;
        res.set_content(sim_json.dump(), "application/json");
    });

    // GET /simulations/{simulationId}/kpis
    svr.Get(R"(/simulations/([^/]+)/kpis)", [](const httplib::Request& req, httplib::Response& res) {
        std::string sim_id = req.matches[1];
        if (store::simulations.find(sim_id) == store::simulations.end()) {
            res.status = 404;
            return;
        }
        auto& kpis = store::simulations.at(sim_id).native_sim.kpiReport();
        json kpi_json;
        for(const auto& metric : kpis.getMetrics()){
            kpi_json["metrics"][metric.first] = metric.second;
        }
        res.set_content(kpi_json.dump(), "application/json");
    });

    std::cout << "Server starting on http://localhost:8080" << std::endl;
    svr.listen("0.0.0.0", 8080);

    return 0;
}

