#include "SafetyChecker.h"
#include <unordered_map>
#include <utility>

bool SafetyChecker::validate(const SignalPhase &phase) const {
    int greenCount = 0;
    for (const auto &entry : phase.getStates()) {
        if (entry.second == LightState::Green) {
            ++greenCount;
            if (greenCount > 1) {
                return false; // Disallow multiple greens in this simple safety check.
            }
        }
    }
    return true;
}

SignalPhase SafetyChecker::fallbackPhase(const std::vector<std::string> &approaches) const {
    std::unordered_map<std::string, LightState> states;
    for (const auto &approachId : approaches) {
        states[approachId] = LightState::FlashingAmber;
    }
    return SignalPhase("fallback-flashing-amber", 3, std::move(states));
}
