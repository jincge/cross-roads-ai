#pragma once

#include "LightState.h"

#include <string>
#include <unordered_map>
#include <vector>

class SignalPhase {
public:
    SignalPhase(std::string name, int durationSeconds, std::unordered_map<std::string, LightState> states);

    const std::string &getName() const;
    int getDurationSeconds() const;
    const std::unordered_map<std::string, LightState> &getStates() const;

    static SignalPhase allRed(const std::vector<std::string> &approaches);

private:
    std::string name;
    int durationSeconds;
    std::unordered_map<std::string, LightState> approachStates;
};

