Feature: Basic traffic simulation
  Scenario: Simulate vehicle arrivals with randomized flows
    Given a simple traffic generator with randomized arrivals from each direction
    When the simulation starts
    Then vehicles are spawned at random intervals and enter the crossroad

  Scenario: Run clock-driven light control
    Given a basic clock-driven traffic light algorithm with a fixed schedule
    When time ticks advance
    Then the algorithm switches lights according to the clock without using traffic data

  Scenario: Visualize vehicles and signals on a map
    Given the simulation is running
    When vehicle movements and light changes occur
    Then they are visualized on a map view showing stops, movements, and light states
