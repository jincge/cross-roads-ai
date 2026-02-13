#pragma once

#include "LightState.h"

#include <string>

class TrafficLight {
public:
    explicit TrafficLight(std::string approachId);

    LightState getState() const;
    void setState(LightState state);
    const std::string &getApproachId() const;

private:
    std::string approachId;
    LightState state{LightState::Red};
};

