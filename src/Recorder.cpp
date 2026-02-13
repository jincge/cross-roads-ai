#include "Recorder.h"

void Recorder::recordEvent(std::string event) { recordedEvents.push_back(std::move(event)); }

const std::vector<std::string> &Recorder::events() const { return recordedEvents; }

void Recorder::clear() { recordedEvents.clear(); }

