#include "RoadApproach.h"

RoadApproach::RoadApproach(std::string direction)
    : directionId(std::move(direction)), trafficLight(directionId), vehicleSensor(directionId) {}

TrafficLight &RoadApproach::light() { return trafficLight; }

Sensor &RoadApproach::sensor() { return vehicleSensor; }

const TrafficLight &RoadApproach::light() const { return trafficLight; }

const Sensor &RoadApproach::sensor() const { return vehicleSensor; }

const std::string &RoadApproach::direction() const { return directionId; }

