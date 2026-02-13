Feature: ORM-based persistence
  Scenario: Use ORM for data access
    Given the application uses a relational database
    When persisting or retrieving domain objects
    Then database access is performed through an ORM layer instead of raw SQL

  Scenario: Remain database agnostic
    Given the ORM abstracts vendor-specific SQL
    When the database engine changes
    Then the application code continues to work without major rewrites
