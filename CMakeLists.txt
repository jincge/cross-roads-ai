cmake_minimum_required(VERSION 3.16)
project(cross_road_ai LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Move core library to its own directory
add_subdirectory(src)

add_executable(cross_road_ai WIN32
        main.cpp
)

# Enable C++/CLI for the WinForms UI
set_target_properties(cross_road_ai PROPERTIES
        COMMON_LANGUAGE_RUNTIME ""
        VS_DOTNET_TARGET_FRAMEWORK_VERSION "v4.8"
)

target_compile_options(cross_road_ai PRIVATE /clr)
# File: `CMakeLists.txt` (root) - server subdirectory
add_subdirectory(server)
