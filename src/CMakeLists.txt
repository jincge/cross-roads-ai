cmake_minimum_required(VERSION 3.16)

# Define the core library for the project
add_library(cross_road_core STATIC
        ControlAlgorithm.cpp
        DomainModel.cpp
        Intersection.cpp
        KPIReport.cpp
        MapData.cpp
        Playback.cpp
        Recorder.cpp
        RoadApproach.cpp
        SafetyChecker.cpp
        Sensor.cpp
        SignalPhase.cpp
        Simulation.cpp
        TrafficGenerator.cpp
        TrafficLight.cpp
        UIClient.cpp
)

target_include_directories(cross_road_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

# Ensure core uses C++20
set_target_properties(cross_road_core PROPERTIES
  CXX_STANDARD 20
  CXX_STANDARD_REQUIRED ON
)

