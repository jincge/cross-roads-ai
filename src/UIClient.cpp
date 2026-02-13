#include "UIClient.h"

#include <sstream>

bool UIClient::connect() {
    connected = true;
    return connected;
}

void UIClient::disconnect() { connected = false; }

bool UIClient::isConnected() const { return connected; }

std::string UIClient::displayState(const Intersection &intersection) const {
    std::ostringstream oss;
    oss << "UI state:";
    for (const auto &approach : intersection.approaches()) {
        oss << " " << approach.direction() << "=" << static_cast<int>(approach.light().getState());
    }
    return oss.str();
}

