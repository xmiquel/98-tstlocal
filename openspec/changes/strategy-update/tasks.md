# Tasks: Strategy Update Endpoint

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~40 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-on-risk |
| Chain strategy | size-exception |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Full PUT endpoint + tests | Single PR | TDD: RED commit → GREEN commit; base = main |

## Phase 1: Core Implementation

- [x] 1.1 Write RED test: add 4 update scenarios to `tests/test_strategies.py` — store.update success, store.update KeyError, PUT 200, PUT 404
- [x] 1.2 Implement GREEN: add `StrategyUpdate` to `app/schemas.py`, `update()` to `app/store.py`, PUT route to `app/main.py` — make all 4 tests pass
- [x] 1.3 Verify spec delta: confirm `openspec/changes/strategy-update/specs/trading-domain/spec.md` update scenarios match the implementation
