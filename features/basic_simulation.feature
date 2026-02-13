Feature: Basic traffic simulation
  Scenario: Simulate vehicle arrivals
    Given a simple traffic generator with randomized arrivals from each direction
    When the simulation starts
    Then vehicles are spawned at random intervals and enter the crossroad

  Scenario: Clock-driven light control
    Given a basic clock-driven traffic light algorithm
    When time ticks advance
    Then the algorithm switches lights through its fixed schedule without using traffic data

  Scenario: Visualize results
    Given the simulation is running
    When vehicle movements and light changes occur
    Then they are visualized on a map view showing stops, movements, and light states

