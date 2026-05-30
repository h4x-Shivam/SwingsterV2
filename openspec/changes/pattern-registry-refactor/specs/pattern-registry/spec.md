## ADDED Requirements

### Requirement: Centralized Pattern Registry
The system SHALL maintain a central registry mapping string keys to pattern instance objects.

#### Scenario: Pattern registration
- **WHEN** the scanning engine or judge agent requests a pattern mode
- **THEN** the system must retrieve the pattern definition from the central registry

### Requirement: Self-Contained Pattern Modules
Each pattern SHALL be encapsulated in its own module class that extends a BasePattern interface.

#### Scenario: Pattern interface implementation
- **WHEN** a pattern is invoked by the engine
- **THEN** it must implement `detect()`, `score()`, and provide `config` and `judge_prompt` attributes.
