#pragma once

#include <string>
#include <vector>

class Recorder {
public:
    void recordEvent(std::string event);
    const std::vector<std::string> &events() const;
    void clear();

private:
    std::vector<std::string> recordedEvents;
};

