cmake_minimum_required(VERSION 3.16)

# App executable (Win32/CLR) — use the original project target name
add_executable(cross_road_ai WIN32
    main.cpp
)

# Keep include dir so existing ../src includes work
target_include_directories(cross_road_ai PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/..)

# Enable C++/CLI for the WinForms UI
set_target_properties(cross_road_ai PROPERTIES
    COMMON_LANGUAGE_RUNTIME ""
    VS_DOTNET_TARGET_FRAMEWORK_VERSION "v4.8"
)

target_compile_options(cross_road_ai PRIVATE /clr)

# Link against the core library
target_link_libraries(cross_road_ai PRIVATE cross_road_core)
