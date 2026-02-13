#pragma once

#include "SignalPhase.h"

#include <string>
#include <vector>

class SafetyChecker {
public:
    bool validate(const SignalPhase &phase) const;
    SignalPhase fallbackPhase(const std::vector<std::string> &approaches) const;
};

