Feature: KPI measurement
  Scenario: Compute KPIs for a scenario
    Given an intersection with sensors, a control algorithm, and traffic generator settings
    When a simulation run completes
    Then KPIs expressing control quality are calculated and reported

