#pragma once

#include <optional>
#include <string>
#include <vector>

class Playback {
public:
    explicit Playback(std::vector<std::string> events = {});

    std::optional<std::string> next();
    void reset();

private:
    std::vector<std::string> events;
    std::size_t position{0};
};

