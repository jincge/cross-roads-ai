#pragma once

#include "SignalPhase.h"

#include <cstddef>
#include <string>
#include <vector>

class ControlAlgorithm {
public:
    ControlAlgorithm(std::string name, std::vector<SignalPhase> phases);

    const std::string &getName() const;
    void setMode(std::string modeName);
    const std::string &getMode() const;
    const SignalPhase &nextPhase();
    void reset();

private:
    std::string name;
    std::string mode;
    std::vector<SignalPhase> phases;
    std::size_t currentPhase{0};
};

