Feature: Recording and playback
  Scenario: Record simulation runs
    Given a running simulation
    When recording is enabled
    Then the run’s events are stored for later analysis

  Scenario: Replay simulations
    Given a recorded run
    When playback is started
    Then the simulation is replayed to review behavior and results

