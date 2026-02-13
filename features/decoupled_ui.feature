Feature: Decoupled UI and simulator
  Scenario: Restart UI without stopping simulation
    Given the simulator runs independently of the UI
    When the UI is closed and reopened
    Then the simulation continues and the UI reconnects without losing state

  Scenario: Multiple UIs per simulation
    Given the simulator is network-accessible
    When multiple UI instances connect
    Then each UI shows the current simulation state concurrently

  Scenario: Remote UI
    Given the simulator exposes a secure network interface
    When a UI runs on another machine
    Then it can control and observe the simulation state remotely

