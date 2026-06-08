# Tasks: Strategy Search

## Review Workload Forecast

| Field | Value |
|---|---|
| Estimated changed lines | ~15-25 |
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
|---|---|---|---|
| 1 | Full filter feature + tests | Single PR | ~20 lines, single concern, one commit |

## Phase 1: Store Layer

- [x] 1.1 Modify `app/store.py` — add `name_filter: str | None = None` to `list()`, append `.where(StrategyModel.name.ilike(...))` when set

## Phase 2: Route Layer

- [x] 2.1 Modify `app/main.py` — add `name: str | None = None` query param to `list_strategies()`, pass to `store.list()`

## Phase 3: Tests

- [x] 3.1 Add `test_list_strategies_filters_by_name()` — creates 3 strategies, `GET /strategies?name=MACD` returns only the matching one
- [x] 3.2 Add `test_list_strategies_no_match_returns_empty()` — `GET /strategies?name=NonExistent` returns `[]`
- [x] 3.3 Verify existing list tests pass unchanged

## Phase 4: Spec Sync

- [x] 4.1 Add Name Filter requirement + 2 scenarios to `openspec/specs/trading-domain/spec.md`
