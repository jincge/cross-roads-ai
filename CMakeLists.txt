cmake_minimum_required(VERSION 3.16)
project(cross_road_ai LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(cross_road_core STATIC
        src/ControlAlgorithm.cpp
        src/DomainModel.cpp
        src/Intersection.cpp
        src/KPIReport.cpp
        src/MapData.cpp
        src/Playback.cpp
        src/Recorder.cpp
        src/RoadApproach.cpp
        src/SafetyChecker.cpp
        src/Sensor.cpp
        src/SignalPhase.cpp
        src/Simulation.cpp
        src/TrafficGenerator.cpp
        src/TrafficLight.cpp
        src/UIClient.cpp
)
target_include_directories(cross_road_core PUBLIC src)

add_executable(cross_road_ai WIN32
        main.cpp
)

# Enable C++/CLI for the WinForms UI
set_target_properties(cross_road_ai PROPERTIES
        COMMON_LANGUAGE_RUNTIME ""
        VS_DOTNET_TARGET_FRAMEWORK_VERSION "v4.8"
)

target_compile_options(cross_road_ai PRIVATE /clr)

target_link_libraries(cross_road_ai PRIVATE
        cross_road_core
        System.Windows.Forms
        System.Drawing
)
