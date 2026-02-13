#include "Sensor.h"

Sensor::Sensor(std::string approachId) : approachId(std::move(approachId)) {}

void Sensor::observeVehicle() { ++count; }

int Sensor::getCount() const { return count; }

void Sensor::reset() { count = 0; }

const std::string &Sensor::getApproachId() const { return approachId; }

