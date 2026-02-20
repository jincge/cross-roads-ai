#include "TrafficLight.h"

TrafficLight::TrafficLight(std::string approachId) : approachId(std::move(approachId)) {}

LightState TrafficLight::getState() const { return state; }

void TrafficLight::setState(LightState newState) { state = newState; }

const std::string &TrafficLight::getApproachId() const { return approachId; }

