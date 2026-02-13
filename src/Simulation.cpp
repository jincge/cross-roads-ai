#include "Simulation.h"

#include <numeric>
#include <sstream>

Simulation::Simulation(Intersection intersection, ControlAlgorithm algorithm, SafetyChecker safetyChecker, TrafficGenerator generator)
    : simulationIntersection(std::move(intersection)),
      algorithm(std::move(algorithm)),
      safety(std::move(safetyChecker)),
      generator(std::move(generator)) {}

void Simulation::start() {
    running = true;
    runRecorder.clear();
    kpis.recordMetric("runtime_seconds", 0.0);
}

void Simulation::stop() { running = false; }

bool Simulation::isRunning() const { return running; }

void Simulation::step() {
    if (!running) {
        return;
    }

    auto spawned = generator.spawnVehicles();
    for (const auto &spawn : spawned) {
        auto approach = simulationIntersection.findApproach(spawn.approachId);
        if (approach.has_value()) {
            approach->get().sensor().observeVehicle();
        }
    }

    const SignalPhase &phase = algorithm.nextPhase();
    SignalPhase chosenPhase = safety.validate(phase)
                                 ? phase
                                 : safety.fallbackPhase(simulationIntersection.approachIds());

    simulationIntersection.applyPhase(chosenPhase);

    std::ostringstream oss;
    oss << "Phase:" << chosenPhase.getName() << " Vehicles:" << spawned.size();
    runRecorder.recordEvent(oss.str());

    const auto &approachesRef = simulationIntersection.approaches();
    const double vehicleCount = std::accumulate(
        approachesRef.begin(), approachesRef.end(), 0.0,
        [](double acc, const RoadApproach &approach) { return acc + approach.sensor().getCount(); });
    kpis.recordMetric("vehicle_count", vehicleCount);
}

Intersection &Simulation::intersection() { return simulationIntersection; }

ControlAlgorithm &Simulation::controlAlgorithm() { return algorithm; }

KPIReport &Simulation::kpiReport() { return kpis; }

Recorder &Simulation::recorder() { return runRecorder; }

Playback Simulation::playback() const { return Playback(runRecorder.events()); }

