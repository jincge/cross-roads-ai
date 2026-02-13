#pragma once

#include "Intersection.h"

#include <string>

class UIClient {
public:
    bool connect();
    void disconnect();
    bool isConnected() const;
    std::string displayState(const Intersection &intersection) const;

private:
    bool connected{false};
};

