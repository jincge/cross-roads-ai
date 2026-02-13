#pragma once

#include <string>

struct Vehicle {
    std::string type;
};

struct SpawnedVehicle {
    std::string approachId;
    Vehicle vehicle;
};

