#pragma once

#include "Vehicle.h"

#include <string>
#include <vector>

class TrafficGenerator {
public:
    explicit TrafficGenerator(std::vector<std::string> approachIds);

    void setArrivalPattern(std::string pattern);
    const std::string &getArrivalPattern() const;
    std::vector<SpawnedVehicle> spawnVehicles();

private:
    std::vector<std::string> approachIds;
    std::string arrivalPattern{"randomized"};
    bool spawnTrucks{false};
};

