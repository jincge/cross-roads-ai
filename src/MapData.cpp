#include "MapData.h"

MapData::MapData(std::string source) : source(std::move(source)) {}

bool MapData::load() {
    loaded = !source.empty();
    return loaded;
}

bool MapData::isLoaded() const { return loaded; }

const std::string &MapData::getSource() const { return source; }

