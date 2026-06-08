# Archive Report: strategy-search

**Change**: `strategy-search`
**Branch**: `docs/archive-strategy-search` (created from `main` at `4b15de9`)
**Project**: 98-tstlocal
**Archive folder**: `openspec/changes/archive/strategy-search/` (unprefixed per project convention)
**Modified capability**: `trading-domain` at `openspec/specs/trading-domain/spec.md`

---

## Verdict (from verify)

**`PASS`** — 5/5 gates pass (24 tests, ruff, mypy, lock). The Name Filter requirement was
implemented via a backward-compatible `name` query parameter on `GET /strategies` using
SQLAlchemy `.ilike()`. Squash-merge commit `4b15de9` confirms all quality checks pass.

---

## What Changed

### Modified capability: trading-domain — Name Filter (ADDED to existing Strategy CRUD)

The delta spec at `openspec/changes/archive/strategy-search/specs/trading-domain/spec.md`
declared 1 ADDED Requirement on the existing `Strategy CRUD` capability. The canonical
spec already existed with `Strategy CRUD` (11 scenarios) and `Data Persistence` (4 scenarios).
The delta appended a new `Strategy CRUD — Name Filter` requirement with 2 scenarios
covering matching and non-matching filter cases.

| Domain | Capability | Action | Details |
|--------|-----------|--------|---------|
| `trading-domain` | `Strategy CRUD — Name Filter` | **Added** | +1 Requirement with 2 scenarios (`GET /strategies?name=…`) |

### Canonical growth

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Requirements | 2 (Strategy CRUD, Data Persistence) | **3** (+Name Filter) | +1 |
| Scenarios | 15 | **17** | +2 |
| Domain spec total lines | 145 | **144** | (minor — Out of Scope unchanged) |

The 2 new Name Filter scenarios cover the search contract:

1. **GET /strategies?name=MACD returns matching strategies** — case-insensitive substring filter returns subset
2. **GET /strategies?name=NonExistent returns empty list** — no match returns `[]`

### Implementation artifacts

- `app/main.py`: Modified — added `name: str | None = None` query param to `list_strategies()`
- `app/store.py`: Modified — added `name_filter: str | None = None` to `list()`, appends `.where(StrategyModel.name.ilike(...))` when set
- `tests/test_strategies.py`: Added 2 filter tests (`test_list_strategies_filters_by_name`, `test_list_strategies_no_match_returns_empty`)
- `openspec/specs/trading-domain/spec.md`: Added Name Filter requirement + 2 scenarios (Phase 4 task completed during apply)

### Existing capabilities untouched

`openspec/specs/python-toolchain/spec.md` is unchanged — 13 Requirements, unchanged.
Only `trading-domain` was modified.

### Change folder moved

`openspec/changes/strategy-search/` → `openspec/changes/archive/strategy-search/`
via `git mv` for tracked files (tasks.md) and copy+add for untracked SDD artifacts
(proposal.md, design.md, specs/trading-domain/spec.md). The `openspec/changes/` directory
now contains only `archive/`, `next-slice-explore/`, and `.gitkeep` — no active
`strategy-search` change.

### Archive folder convention

Per project precedent (all prior cycles), the archive folder is unprefixed:
`archive/strategy-search/`, **not** `archive/YYYY-MM-DD-strategy-search/`. Git history
of the archive folder encodes the date.

---

## Pre-Archive Checks

| # | Check | Result | Details |
|---|-------|--------|---------|
| 1 | **Task Completion Gate** | ✅ PASS | On-disk `tasks.md` has all 4 implementation tasks `[x]`. No stale unchecked tasks. |
| 2 | **Canonical spec updated** | ✅ PASS | `openspec/specs/trading-domain/spec.md` — Name Filter requirement appended after Data Persistence with 2 scenarios. This was done during Phase 4 of apply. |
| 3 | **Delta spec preserved** | ✅ PASS | Archived `openspec/changes/archive/strategy-search/specs/trading-domain/spec.md` contains the full delta spec with the ADDED Requirements section. |
| 4 | **All artifacts archived** | ✅ PASS | 4 files archived: `proposal.md`, `design.md`, `specs/trading-domain/spec.md`, `tasks.md`. Plus this `archive-report.md`. |
| 5 | **Active directory clean** | ✅ PASS | `openspec/changes/strategy-search/` no longer exists. |
| 6 | **Verification passed** | ✅ PASS | 5/5 gates pass per user context (24 tests, ruff, mypy, lock). No verify-report.md artifact persisted (local generation only). |

### Task Completion Gate Detail

The on-disk `tasks.md` at `openspec/changes/archive/strategy-search/tasks.md` has all
4 implementation tasks marked `[x]`. All 4 phases (Store Layer, Route Layer, Tests,
Spec Sync) are complete. No stale-checkbox reconciliation needed — the on-disk artifact
is correct.

---

## Engram Observation References

| Artifact | Engram ID | Notes |
|----------|-----------|-------|
| `sdd/strategy-search/proposal` | *(not stored in Engram)* | On-disk at `archive/strategy-search/proposal.md` |
| `sdd/strategy-search/spec` | *(not stored in Engram)* | On-disk at `archive/strategy-search/specs/trading-domain/spec.md` |
| `sdd/strategy-search/design` | *(not stored in Engram)* | On-disk at `archive/strategy-search/design.md` |
| `sdd/strategy-search/tasks` | *(not stored in Engram)* | On-disk at `archive/strategy-search/tasks.md` |
| `sdd/strategy-search/verify-report` | *(not stored in Engram)* | 5/5 gates pass per user context — no local artifact persisted |
| `sdd/strategy-search/archive-report` | *(this save)* | This archive report |

---

## Refs

| Kind | URL / Path | Status / SHA |
|------|-----------|--------------|
| Change folder (was) | `openspec/changes/strategy-search/` | archived |
| Change folder (now) | `openspec/changes/archive/strategy-search/` | 5 files (4 artifacts + this report) |
| Canonical spec (updated) | `openspec/specs/trading-domain/spec.md` | 3 Requirements / 17 scenarios / 144 lines |
| PR (feature squash) | https://github.com/xmiquel/98-tstlocal/pull/41 | MERGED at `4b15de9` |
| Pre-squash branch ref | `feat/strategy-search` (deleted) | TDD cycle confirmed |

---

**Report generated**: 2026-06-08
**Project**: 98-tstlocal
**Change**: strategy-search
**SDD cycle status**: **CLOSED** — planned, designed, applied, verified, and archived
