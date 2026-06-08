# Proposal: Strategy Update Endpoint

## Intent

Complete the Strategy CRUD interface by adding the missing UPDATE operation (`PUT /strategies/{id}`). Currently strategies can be created, listed, retrieved, and deleted — but not modified. This gap forces clients to delete-and-recreate, losing `created_at` timestamps and exposing an inconsistent API.

## Scope

### In Scope
- Add `update(id, data)` to `StrategyStore` in `app/store.py`
- Add `PUT /strategies/{id}` route that replaces all strategy fields
- Add `StrategyUpdate` model reusing `StrategyCreate` fields
- Tests: store update success/missing + route 200/404 scenarios
- Delta spec: add UPDATE scenario to trading-domain spec

### Out of Scope
- PATCH (partial update) — deferred for a later change
- Validation beyond type checking — follows existing patterns
- Persistence layer — still in-memory store
- Custom error types — uses existing `KeyError` → 404 pattern

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `trading-domain`: add UPDATE to the Strategy CRUD requirement — `PUT /strategies/{id}` with 200 (success) and 404 (non-existent id) scenarios

## Approach

1. Add `StrategyUpdate(BaseModel)` to schemas — same fields as `StrategyCreate`
2. Add `update(id, strategy_data)` to `StrategyStore` — raises `KeyError` if id not found
3. Add `PUT /strategies/{id}` route — returns updated strategy (200) or 404
4. Write tests: store update (success, missing) + route (200, 404)
5. Strict TDD: test commit precedes implementation commit

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `app/schemas.py` | Modified | Add `StrategyUpdate` model |
| `app/store.py` | Modified | Add `update(id, data)` method |
| `app/main.py` | Modified | Add `PUT /strategies/{id}` route |
| `tests/test_strategies.py` | Modified | Add update scenarios |
| `openspec/specs/trading-domain/spec.md` | Modified | Add UPDATE scenario |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| PUT overwrites fields client omits | Low | Full-replacement semantics are standard for PUT; PATCH explicitly deferred |

## Rollback Plan

Revert the feature commit. Changes are additive with no migration — revert is safe.

## Dependencies

None.

## Success Criteria

- [ ] `PUT /strategies/{id}` returns 200 + updated strategy body
- [ ] `PUT /strategies/{non-existent-id}` returns 404
- [ ] Existing GET/POST/DELETE tests pass unchanged
- [ ] `make ci` passes (ruff, mypy, pytest ≥ 80% coverage)
