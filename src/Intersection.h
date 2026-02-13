#pragma once

#include "RoadApproach.h"
#include "SignalPhase.h"

#include <optional>
#include <string>
#include <vector>

class Intersection {
public:
    explicit Intersection(std::vector<std::string> directions);

    std::vector<RoadApproach> &approaches();
    const std::vector<RoadApproach> &approaches() const;
    std::optional<std::reference_wrapper<RoadApproach>> findApproach(const std::string &direction);
    std::vector<std::string> approachIds() const;
    void applyPhase(const SignalPhase &phase);

private:
    std::vector<RoadApproach> approachList;
};

