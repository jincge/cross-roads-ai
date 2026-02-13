#pragma once

#include <string>
#include <unordered_map>

class KPIReport {
public:
    void recordMetric(std::string name, double value);
    const std::unordered_map<std::string, double> &metrics() const;

private:
    std::unordered_map<std::string, double> metricValues;
};

