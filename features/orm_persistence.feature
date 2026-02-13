Feature: ORM-based persistence
  Scenario: Use ORM for data access
    Given the application uses a relational database
    When persisting or retrieving domain objects
    Then database access is performed through an ORM layer instead of raw SQL

