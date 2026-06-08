# Proposal: Strategy Search

## Intent

Users need to find a specific strategy by name without fetching and filtering the full list client-side. Adding an optional `?name=` query parameter to `GET /strategies` enables server-side case-insensitive substring search with zero new dependencies.

## Scope

### In Scope
- `name` query param on `GET /strategies` — `Optional[str]` in FastAPI
- `StrategyStore.list(name_filter: str | None = None)` — case-insensitive `ILIKE` filter
- Test scenarios: empty filter returns all, matching filter returns subset, non-matching returns `[]`, case insensitivity verified

### Out of Scope
- Multi-field search (description, tags)
- Pagination, sorting, fuzzy matching
- Any new endpoint or route

## Capabilities

### New Capabilities
None

### Modified Capabilities
- **trading-domain**: Add search/filter scenario to Strategy CRUD requirement in `openspec/specs/trading-domain/spec.md`. New `name_filter` parameter on `list()`, new `GET /strategies?name=...` scenario.

## Approach

1. Add `name_filter: str | None = None` to `StrategyStore.list()` in `app/store.py`
2. When set, append `.where(StrategyModel.name.ilike(f"%{name_filter}%"))` to the existing select
3. Add `name: str | None = None` query param to `list_strategies()` in `app/main.py`, pass it through to `store.list()`
4. Add scenarios to `openspec/specs/trading-domain/spec.md`
5. Follow strict TDD: test commit first, implementation second

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `app/store.py` | Modified | `list()` gains optional `name_filter` |
| `app/main.py` | Modified | `GET /strategies` accepts `?name=` |
| `openspec/specs/trading-domain/spec.md` | Modified | New filter scenarios added |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| SQL injection via name param | Low | SQLAlchemy ORM parameterizes `ilike` — safe by construction |
| Performance on large datasets | Low | No index needed at this scale; defer to pagination when needed |

## Rollback Plan

Revert the two file changes (`app/store.py` and `app/main.py`) and remove the delta spec additions. No migration needed — parameter is additive and fully backward-compatible.

## Dependencies

None. SQLAlchemy `ilike` is stdlib for this project.

## Success Criteria

- [ ] `GET /strategies?name=trend` returns only strategies with "trend" in their name (case-insensitive)
- [ ] `GET /strategies` (no param) returns all strategies — backward compatible
- [ ] `GET /strategies?name=nonexistent` returns `[]`
- [ ] Test coverage >= 80% on new code paths
