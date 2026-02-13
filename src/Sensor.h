#pragma once

#include <string>

class Sensor {
public:
    explicit Sensor(std::string approachId);

    void observeVehicle();
    int getCount() const;
    void reset();
    const std::string &getApproachId() const;

private:
    std::string approachId;
    int count{0};
};

