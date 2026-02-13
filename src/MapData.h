#pragma once

#include <string>

class MapData {
public:
    explicit MapData(std::string source);

    bool load();
    bool isLoaded() const;
    const std::string &getSource() const;

private:
    std::string source;
    bool loaded{false};
};

