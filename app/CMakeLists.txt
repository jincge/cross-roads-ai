cmake_minimum_required(VERSION 3.16)

project(cross_road_ai_app)

# Enable Qt MOC/UIC/RCC
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

# App executable — native Qt application
add_executable(cross_road_ai
    main.cpp
)

# Keep include dir so existing ../src includes work
target_include_directories(cross_road_ai PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/..)

# Find Qt6 Widgets
find_package(Qt6 REQUIRED COMPONENTS Widgets)

# Link against Qt and the core library
target_link_libraries(cross_road_ai PRIVATE Qt6::Widgets cross_road_core)

target_compile_features(cross_road_ai PRIVATE cxx_std_17)
