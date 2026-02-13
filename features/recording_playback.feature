Feature: Recording and playback
  Scenario: Record simulation runs
    Given a running simulation
    When recording is enabled
    Then the run's events are stored for later analysis

  Scenario: Replay simulations
    Given a recorded run
    When playback is started
    Then the simulation is replayed to review behavior and results

  Scenario: Use recordings to refine algorithms
    Given past recordings of simulation runs
    When control strategies are adjusted based on playback observations
    Then new runs can be compared to verify improvements
