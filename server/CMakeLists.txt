# Ensure the core library is available before creating the server target
if (NOT TARGET cross_road_core)
  message(FATAL_ERROR "cross_road_core target must be defined before adding the server subdirectory")
endif()

# Require C++20 for the server target
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)

FetchContent_Declare(
  httplib
  GIT_REPOSITORY https://github.com/yhirose/cpp-httplib.git
  GIT_TAG v0.15.3
)
FetchContent_MakeAvailable(httplib)

FetchContent_Declare(
  json
  GIT_REPOSITORY https://github.com/nlohmann/json.git
  GIT_TAG v3.11.3
)
FetchContent_MakeAvailable(json)

add_executable(cross_road_server
  server.cpp
)

# Use the include locations provided by the fetched projects. Some projects
# expose headers at the source root while others under an `include/` subfolder.
# Keep both locations so compilation finds the headers reliably.
target_include_directories(cross_road_server PUBLIC
  ${httplib_SOURCE_DIR}
  ${httplib_SOURCE_DIR}/include
  ${json_SOURCE_DIR}/include
)

# Ensure the server compiles with C++20 like the core library
set_target_properties(cross_road_server PROPERTIES
  CXX_STANDARD 20
  CXX_STANDARD_REQUIRED ON
)

target_link_libraries(cross_road_server PRIVATE
  cross_road_core
)