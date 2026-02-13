Feature: Live maps and realistic traffic generation
  Scenario: Load live map data
    Given access to map sources such as OpenStreetMap or Google Maps
    When the UI loads a scenario
    Then actual map data is displayed in the UI for the crossing

  Scenario: Refine generators with vehicle types
    Given traffic generators support different vehicle characteristics
    When trucks and passenger cars are generated
    Then their differing behaviors are reflected in the simulation

