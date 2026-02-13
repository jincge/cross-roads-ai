#include "Playback.h"

Playback::Playback(std::vector<std::string> events) : events(std::move(events)) {}

std::optional<std::string> Playback::next() {
    if (position >= events.size()) {
        return std::nullopt;
    }
    return events[position++];
}

void Playback::reset() { position = 0; }

