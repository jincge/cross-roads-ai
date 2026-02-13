#include "TrafficGenerator.h"
#include <utility>

TrafficGenerator::TrafficGenerator(std::vector<std::string> approachIds)
    : approachIds(std::move(approachIds)) {}

void TrafficGenerator::setArrivalPattern(std::string pattern) { arrivalPattern = std::move(pattern); }

const std::string &TrafficGenerator::getArrivalPattern() const { return arrivalPattern; }

std::vector<SpawnedVehicle> TrafficGenerator::spawnVehicles() {
    std::vector<SpawnedVehicle> spawned;
    for (const auto &approachId : approachIds) {
        Vehicle vehicle{spawnTrucks ? "truck" : "car"};
        spawned.push_back({approachId, vehicle});
    }
    spawnTrucks = !spawnTrucks;
    return spawned;
}
