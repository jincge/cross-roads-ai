#pragma once

#include "ControlAlgorithm.h"
#include "Intersection.h"
#include "KPIReport.h"
#include "Playback.h"
#include "Recorder.h"
#include "SafetyChecker.h"
#include "TrafficGenerator.h"

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

private:
    bool running{false};
    Intersection simulationIntersection;
    ControlAlgorithm algorithm;
    SafetyChecker safety;
    TrafficGenerator generator;
    KPIReport kpis;
    Recorder runRecorder;
};

