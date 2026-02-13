Feature: Persisted crossroad layouts
  Scenario: Save and load layouts
    Given a designed crossroad configuration
    When the configuration is stored in persistent storage
    Then the layout can be reloaded and reused across sessions

  Scenario: Edit and manage crossings
    Given a crossroads editor and viewer
    When a user designs or modifies an intersection layout
    Then the layout can be saved, selected, and reused within the application

  Scenario: Choose layouts for scenarios
    Given a library of saved real-world and hypothetical layouts
    When a scenario is selected
    Then the chosen layout is loaded for simulation and visualization
