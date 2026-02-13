#include "ControlAlgorithm.h"
#include <utility>

ControlAlgorithm::ControlAlgorithm(std::string name, std::vector<SignalPhase> phases)
    : name(std::move(name)), phases(std::move(phases)) {
    if (this->phases.empty()) {
        this->phases.emplace_back("all-red", 5, std::unordered_map<std::string, LightState>{});
    }
}

const std::string &ControlAlgorithm::getName() const { return name; }

void ControlAlgorithm::setMode(std::string modeName) { mode = std::move(modeName); }

const std::string &ControlAlgorithm::getMode() const { return mode; }

const SignalPhase &ControlAlgorithm::nextPhase() {
    const auto &phase = phases[currentPhase];
    currentPhase = (currentPhase + 1) % phases.size();
    return phase;
}

void ControlAlgorithm::reset() { currentPhase = 0; }
