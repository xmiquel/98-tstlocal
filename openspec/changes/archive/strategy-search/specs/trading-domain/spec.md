# Delta for trading-domain

## ADDED Requirements

### Requirement: Strategy CRUD — Name Filter

The `GET /strategies` endpoint SHOULD accept an optional `name` query parameter for case-insensitive substring matching. When `name` is provided, the system MUST return only strategies whose name contains the given value. When omitted, the system MUST return all strategies (backward compatible).

#### Scenario: GET /strategies?name=MACD returns matching strategies

- GIVEN the store contains strategies named "MACD crossover", "RSI divergence", and "Bollinger squeeze"
- WHEN a client sends `GET /strategies?name=MACD`
- THEN the response status is 200 and the JSON body contains exactly "MACD crossover"
- AND strategies without "MACD" in their name are excluded

#### Scenario: GET /strategies?name=NonExistent returns empty list

- GIVEN the store contains strategies with various names
- WHEN a client sends `GET /strategies?name=NonExistent`
- THEN the response status is 200 and the JSON body is `[]`
