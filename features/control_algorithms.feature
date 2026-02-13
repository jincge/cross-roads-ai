Feature: Multiple control algorithms and safe switching
  Scenario: Select control algorithms
    Given multiple control algorithms are available (clock-driven, flashing amber, advanced)
    When an operator selects an algorithm
    Then the chosen algorithm governs the lights

  Scenario: Safe transition between algorithms
    Given an active control algorithm
    When switching to another algorithm
    Then all lights enter a safe transitional state before the new algorithm takes over

  Scenario: Fallback to null-control on violation
    Given the safety checker detects a rule violation
    When the violation occurs
    Then the system automatically enters flashing amber mode until a safe state is restored

  Scenario: Use upstream sensors for optimization
    Given an advanced control algorithm with access to upstream traffic counters
    When live traffic data is received
    Then the algorithm adapts its phases in real time based on the measured flow
