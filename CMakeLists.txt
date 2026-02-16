cmake_minimum_required(VERSION 3.16)
project(cross_road_ai LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Move core library to its own directory
add_subdirectory(src)
add_subdirectory(app)
add_subdirectory(server)
