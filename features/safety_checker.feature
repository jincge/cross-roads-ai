Feature: Safety checker for light commands
  Scenario: Enforce safe light commands
    Given a safety checker between control algorithms and traffic lights
    When a control algorithm issues light commands
    Then conflicting or unsafe combinations are blocked and safety rules are enforced

  Scenario: Automatic safe mode on violation
    Given the system is running with active safety checks
    When the safety checker detects a rule violation
    Then the lights fall back to a safe mode (e.g., all flashing amber) until safety is restored

