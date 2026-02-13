#pragma once

#include "ControlAlgorithm.h"
#include "Intersection.h"
#include "KPIReport.h"
#include "Playback.h"
#include "Recorder.h"
#include "SafetyChecker.h"
#include "TrafficGenerator.h"

#include <vector>

class Simulation {
public:
    Simulation(Intersection intersection, ControlAlgorithm algorithm, SafetyChecker safetyChecker, TrafficGenerator generator);

    void start();
    void stop();
    bool isRunning() const;
    void step();

    Intersection &intersection();
    ControlAlgorithm &controlAlgorithm();
    KPIReport &kpiReport();
    Recorder &recorder();
    Playback playback() const;

    // Return the vehicles spawned during the most recent step
    const std::vector<SpawnedVehicle> &recentSpawned() const;

private:
    bool running{false};
    Intersection simulationIntersection;
    ControlAlgorithm algorithm;
    SafetyChecker safety;
    TrafficGenerator generator;
    KPIReport kpis;
    Recorder runRecorder;

    // Vehicles spawned in the last step call
    std::vector<SpawnedVehicle> lastSpawned;
};
