#include "KPIReport.h"

void KPIReport::recordMetric(std::string name, double value) { metricValues[std::move(name)] = value; }

const std::unordered_map<std::string, double> &KPIReport::metrics() const { return metricValues; }

