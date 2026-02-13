#include "SignalPhase.h"
#include <utility>

SignalPhase::SignalPhase(std::string name, int durationSeconds, std::unordered_map<std::string, LightState> states)
    : name(std::move(name)), durationSeconds(durationSeconds), approachStates(std::move(states)) {}

const std::string &SignalPhase::getName() const { return name; }

int SignalPhase::getDurationSeconds() const { return durationSeconds; }

const std::unordered_map<std::string, LightState> &SignalPhase::getStates() const { return approachStates; }

SignalPhase SignalPhase::allRed(const std::vector<std::string> &approaches) {
    std::unordered_map<std::string, LightState> states;
    for (const auto &approachId : approaches) {
        states[approachId] = LightState::AllRed;
    }
    return SignalPhase("all-red", 5, std::move(states));
}
