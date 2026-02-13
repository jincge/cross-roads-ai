#pragma once

#include "Sensor.h"
#include "TrafficLight.h"

#include <string>

class RoadApproach {
public:
    explicit RoadApproach(std::string direction);

    TrafficLight &light();
    Sensor &sensor();
    const TrafficLight &light() const;
    const Sensor &sensor() const;
    const std::string &direction() const;

private:
    std::string directionId;
    TrafficLight trafficLight;
    Sensor vehicleSensor;
};

