#pragma once

#include <cstddef>
#include <functional>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

enum class LightState { Red, Green, Amber, FlashingAmber, AllRed };

struct Vehicle {
    std::string type;
};

struct SpawnedVehicle {
    std::string approachId;
    Vehicle vehicle;
};

class SignalPhase {
public:
    SignalPhase(std::string name, int durationSeconds, std::unordered_map<std::string, LightState> states);

    const std::string &getName() const;
    int getDurationSeconds() const;
    const std::unordered_map<std::string, LightState> &getStates() const;

    static SignalPhase allRed(const std::vector<std::string> &approaches);

private:
    std::string name;
    int durationSeconds;
    std::unordered_map<std::string, LightState> approachStates;
};

class TrafficLight {
public:
    explicit TrafficLight(std::string approachId);

    LightState getState() const;
    void setState(LightState state);
    const std::string &getApproachId() const;

private:
    std::string approachId;
    LightState state{LightState::Red};
};

class Sensor {
public:
    explicit Sensor(std::string approachId);

    void observeVehicle();
    int getCount() const;
    void reset();
    const std::string &getApproachId() const;

private:
    std::string approachId;
    int count{0};
};

class RoadApproach {
public:
    explicit RoadApproach(std::string direction);

    TrafficLight &light();
    Sensor &sensor();
    const TrafficLight &light() const;
    const Sensor &sensor() const;
    const std::string &direction() const;

private:
    std::string directionId;
    TrafficLight trafficLight;
    Sensor vehicleSensor;
};

class ControlAlgorithm {
public:
    ControlAlgorithm(std::string name, std::vector<SignalPhase> phases);

    const std::string &getName() const;
    void setMode(std::string modeName);
    const std::string &getMode() const;
    const SignalPhase &nextPhase();
    void reset();

private:
    std::string name;
    std::string mode;
    std::vector<SignalPhase> phases;
    std::size_t currentPhase{0};
};

class SafetyChecker {
public:
    bool validate(const SignalPhase &phase) const;
    SignalPhase fallbackPhase(const std::vector<std::string> &approaches) const;
};

class TrafficGenerator {
public:
    explicit TrafficGenerator(std::vector<std::string> approachIds);

    void setArrivalPattern(std::string pattern);
    const std::string &getArrivalPattern() const;
    std::vector<SpawnedVehicle> spawnVehicles();

private:
    std::vector<std::string> approachIds;
    std::string arrivalPattern{"randomized"};
    bool spawnTrucks{false};
};

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

class KPIReport {
public:
    void recordMetric(std::string name, double value);
    const std::unordered_map<std::string, double> &metrics() const;

private:
    std::unordered_map<std::string, double> metricValues;
};

class Recorder {
public:
    void recordEvent(std::string event);
    const std::vector<std::string> &events() const;
    void clear();

private:
    std::vector<std::string> recordedEvents;
};

class Playback {
public:
    explicit Playback(std::vector<std::string> events = {});

    std::optional<std::string> next();
    void reset();

private:
    std::vector<std::string> events;
    std::size_t position{0};
};

class MapData {
public:
    explicit MapData(std::string source);

    bool load();
    bool isLoaded() const;
    const std::string &getSource() const;

private:
    std::string source;
    bool loaded{false};
};

class UIClient {
public:
    bool connect();
    void disconnect();
    bool isConnected() const;
    std::string displayState(const Intersection &intersection) const;

private:
    bool connected{false};
};

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

