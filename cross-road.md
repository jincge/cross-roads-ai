# Crossroads: Traffic Lights at a Crossroad

## 3.1 First Iteration: Basic application
The basic application consists of three components:
- **Simple Traffic Generator:** Simulates vehicle flow approaching and entering a crossroad with randomized arrivals from each direction.
- **Basic Traffic Light Control Algorithm:** Clock-driven logic to switch lights between green and red without using traffic data.
- **Results Visualization on a Map:** Displays vehicle movement, stops, and light changes on a map view to observe flow and congestion impacts.

This setup provides a practical environment to experiment with traffic control logic and visualize strategy impact.

## 3.2 Iteration: Crossroads viewer and editor
- Save each crossroad configuration (e.g., in a database) so layouts are reusable and accessible.

## 3.3 Iteration: Safety design
- Insert a safety checker between control algorithms and traffic lights to enforce consistency of commands.
- Block conflicting signals (e.g., multiple greens) and monitor all light changes to uphold critical safety constraints.

## 3.4 Iteration: Different control algorithms
- Support multiple algorithms (clock-driven, flashing amber "null-control", advanced logic) and allow switching between them.
- Trigger flashing amber automatically on any safety violation and use safe transitional states (all red or flashing amber) when switching.
- Evolve algorithms to use upstream traffic counters for real-time optimization.

## 3.5 Iteration: Key Performance Indicators
A simulation scenario includes:
- The intersection with traffic lights and sensors
- The control algorithm
- Traffic generator configuration options

Define KPIs to quantify control quality and objectively compare algorithms and configurations.

## 3.6 Iteration: Recording and playback
- Record simulation runs for later analysis.
- Provide playback to review behavior and results and refine algorithms based on recorded data.

## 3.7 Iteration: ORM (relational database)
- Refactor to use an ORM layer instead of direct SQL for relational databases, enabling abstraction, reduced boilerplate, and database agnosticism.

## 3.8 Iteration: Crossroads viewer and editor (enhanced)
- Include an editor to design, modify, and select intersection layouts for real-world or hypothetical scenarios.

## 3.9 Iteration: Decoupling of UI
- Allow closing/restarting the UI while the simulation continues, preserving simulator state.
- Support multiple UIs connected to the same simulation.
- Enable running the UI on a different machine from the simulator with appropriate network security.

## 3.10 Iteration: Live Maps
- Load actual map data (e.g., OpenStreetMap or Google Maps) in the UI.
- Refine traffic generators for realistic behavior (e.g., trucks vs. passenger cars).
