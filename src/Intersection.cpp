#include "Intersection.h"

Intersection::Intersection(std::vector<std::string> directions) {
    for (auto &direction : directions) {
        approachList.emplace_back(direction);
    }
}

std::vector<RoadApproach> &Intersection::approaches() { return approachList; }

const std::vector<RoadApproach> &Intersection::approaches() const { return approachList; }

std::optional<std::reference_wrapper<RoadApproach>> Intersection::findApproach(const std::string &direction) {
    for (auto &approach : approachList) {
        if (approach.direction() == direction) {
            return approach;
        }
    }
    return std::nullopt;
}

std::vector<std::string> Intersection::approachIds() const {
    std::vector<std::string> ids;
    ids.reserve(approachList.size());
    for (const auto &approach : approachList) {
        ids.push_back(approach.direction());
    }
    return ids;
}

void Intersection::applyPhase(const SignalPhase &phase) {
    for (auto &approach : approachList) {
        const auto &states = phase.getStates();
        const auto match = states.find(approach.direction());
        if (match != states.end()) {
            approach.light().setState(match->second);
        } else {
            approach.light().setState(LightState::AllRed);
        }
    }
}

