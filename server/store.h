#pragma once
#include "httplib.h"
#include "json.hpp"
#include "../src/Simulation.h"
#include <string>
#include <vector>
#include <map>

using json = nlohmann::json;

// In-memory data store
namespace store {
    // Simple simulation state for the server
    struct ServerSimulation {
        std::string id;
        Simulation native_sim;
        bool running = false;
    };

    inline std::map<std::string, json> layouts;
    inline std::map<std::string, json> control_algorithms;
    inline std::map<std::string, ServerSimulation> simulations;

    inline std::string new_id() {
        return std::to_string(rand());
    }

    inline void initialize() {
        json basic_algo;
        basic_algo["name"] = "basic";
        basic_algo["mode"] = "";
        basic_algo["phases"] = json::array({
            {{"name", "north-south"}, {"durationSeconds", 5}, {"approachStates", {{"north", "Green"}, {"south", "Green"}}}},
            {{"name", "east-west"}, {"durationSeconds", 5}, {"approachStates", {{"east", "Green"}, {"west", "Green"}}}}
        });
        control_algorithms["basic"] = basic_algo;

        json default_layout;
        default_layout["id"] = "default";
        default_layout["name"] = "Standard 4-way";
        default_layout["intersection"]["id"] = "intersection-1";
        default_layout["intersection"]["approaches"] = json::array({
            {{"id", "north"}, {"lightState", "Red"}},
            {{"id", "south"}, {"lightState", "Red"}},
            {{"id", "east"}, {"lightState", "Red"}},
            {{"id", "west"}, {"lightState", "Red"}}
        });
        layouts["default"] = default_layout;
    }
}

