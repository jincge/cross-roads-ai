#include "DomainModel.h"

#include <numeric>
#include <sstream>
#include <utility>

SignalPhase::SignalPhase(std::string name, int durationSeconds, std::unordered_map<std::string, LightState> states)
    : name(std::move(name)), durationSeconds(durationSeconds), approachStates(std::move(states)) {}

const std::string &SignalPhase::getName() const { return name; }

int SignalPhase::getDurationSeconds() const { return durationSeconds; }

const std::unordered_map<std::string, LightState> &SignalPhase::getStates() const { return approachStates; }

SignalPhase SignalPhase::allRed(const std::vector<std::string> &approaches) {
    std::unordered_map<std::string, LightState> states;
    for (const auto &approachId : approaches) {
        states[approachId] = LightState::AllRed;
    }
    return SignalPhase("all-red", 5, std::move(states));
}

TrafficLight::TrafficLight(std::string approachId) : approachId(std::move(approachId)) {}

LightState TrafficLight::getState() const { return state; }

void TrafficLight::setState(LightState newState) { state = newState; }

const std::string &TrafficLight::getApproachId() const { return approachId; }

Sensor::Sensor(std::string approachId) : approachId(std::move(approachId)) {}

void Sensor::observeVehicle() { ++count; }

int Sensor::getCount() const { return count; }

void Sensor::reset() { count = 0; }

const std::string &Sensor::getApproachId() const { return approachId; }

RoadApproach::RoadApproach(std::string direction)
    : directionId(std::move(direction)), trafficLight(directionId), vehicleSensor(directionId) {}

TrafficLight &RoadApproach::light() { return trafficLight; }

Sensor &RoadApproach::sensor() { return vehicleSensor; }

const TrafficLight &RoadApproach::light() const { return trafficLight; }

const Sensor &RoadApproach::sensor() const { return vehicleSensor; }

const std::string &RoadApproach::direction() const { return directionId; }

ControlAlgorithm::ControlAlgorithm(std::string name, std::vector<SignalPhase> phases)
    : name(std::move(name)), phases(std::move(phases)) {
    if (this->phases.empty()) {
        this->phases.emplace_back("all-red", 5, std::unordered_map<std::string, LightState>{});
    }
}

const std::string &ControlAlgorithm::getName() const { return name; }

void ControlAlgorithm::setMode(std::string modeName) { mode = std::move(modeName); }

const std::string &ControlAlgorithm::getMode() const { return mode; }

const SignalPhase &ControlAlgorithm::nextPhase() {
    const auto &phase = phases[currentPhase];
    currentPhase = (currentPhase + 1) % phases.size();
    return phase;
}

void ControlAlgorithm::reset() { currentPhase = 0; }

bool SafetyChecker::validate(const SignalPhase &phase) const {
    int greenCount = 0;
    for (const auto &entry : phase.getStates()) {
        if (entry.second == LightState::Green) {
            ++greenCount;
            if (greenCount > 1) {
                return false; // Simple guard: more than one concurrent green is treated as unsafe.
            }
        }
    }
    return true;
}

SignalPhase SafetyChecker::fallbackPhase(const std::vector<std::string> &approaches) const {
    std::unordered_map<std::string, LightState> states;
    for (const auto &approachId : approaches) {
        states[approachId] = LightState::FlashingAmber;
    }
    return SignalPhase("fallback-flashing-amber", 3, std::move(states));
}

TrafficGenerator::TrafficGenerator(std::vector<std::string> approachIds)
    : approachIds(std::move(approachIds)) {}

void TrafficGenerator::setArrivalPattern(std::string pattern) { arrivalPattern = std::move(pattern); }

const std::string &TrafficGenerator::getArrivalPattern() const { return arrivalPattern; }

std::vector<SpawnedVehicle> TrafficGenerator::spawnVehicles() {
    std::vector<SpawnedVehicle> spawned;
    for (const auto &approachId : approachIds) {
        Vehicle vehicle{spawnTrucks ? "truck" : "car"};
        spawned.push_back({approachId, vehicle});
    }
    spawnTrucks = !spawnTrucks;
    return spawned;
}

Intersection::Intersection(std::vector<std::string> directions) {
    for (auto &direction : directions) {
        approachList.emplace_back(direction);
    }
}

std::vector<RoadApproach> &Intersection::approaches() { return approachList; }

const std::vector<RoadApproach> &Intersection::approaches() const { return approachList; }

std::optional<std::reference_wrapper<RoadApproach>> Intersection::findApproach(const std::string &direction) {
    for (auto &approach : approachList) {
        if (approach.direction() == direction) {
            return approach;
        }
    }
    return std::nullopt;
}

std::vector<std::string> Intersection::approachIds() const {
    std::vector<std::string> ids;
    ids.reserve(approachList.size());
    for (const auto &approach : approachList) {
        ids.push_back(approach.direction());
    }
    return ids;
}

void Intersection::applyPhase(const SignalPhase &phase) {
    for (auto &approach : approachList) {
        const auto &states = phase.getStates();
        const auto match = states.find(approach.direction());
        if (match != states.end()) {
            approach.light().setState(match->second);
        } else {
            approach.light().setState(LightState::AllRed);
        }
    }
}

void KPIReport::recordMetric(std::string name, double value) { metricValues[std::move(name)] = value; }

const std::unordered_map<std::string, double> &KPIReport::metrics() const { return metricValues; }

void Recorder::recordEvent(std::string event) { recordedEvents.push_back(std::move(event)); }

const std::vector<std::string> &Recorder::events() const { return recordedEvents; }

void Recorder::clear() { recordedEvents.clear(); }

Playback::Playback(std::vector<std::string> events) : events(std::move(events)) {}

std::optional<std::string> Playback::next() {
    if (position >= events.size()) {
        return std::nullopt;
    }
    return events[position++];
}

void Playback::reset() { position = 0; }

MapData::MapData(std::string source) : source(std::move(source)) {}

bool MapData::load() {
    loaded = !source.empty();
    return loaded;
}

bool MapData::isLoaded() const { return loaded; }

const std::string &MapData::getSource() const { return source; }

bool UIClient::connect() {
    connected = true;
    return connected;
}

void UIClient::disconnect() { connected = false; }

bool UIClient::isConnected() const { return connected; }

std::string UIClient::displayState(const Intersection &intersection) const {
    std::ostringstream oss;
    oss << "UI state:";
    for (const auto &approach : intersection.approaches()) {
        oss << " " << approach.direction() << "=" << static_cast<int>(approach.light().getState());
    }
    return oss.str();
}

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

