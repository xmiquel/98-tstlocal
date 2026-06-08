# Archive Report: strategy-crud

**Change**: `strategy-crud`
**Branch**: `docs/archive-strategy-crud` (created from `main` at `0c56072`)
**Project**: 98-tstlocal
**Archive folder**: `openspec/changes/archive/strategy-crud/` (unprefixed per project convention)
**New capability**: `trading-domain` at `openspec/specs/trading-domain/spec.md`

---

## Verdict (from verify)

**`PASS`** — 0 CRITICAL, 0 WARNING, 0 SUGGESTIONS. Verify report saved to Engram as
`sdd/strategy-crud/verify-report` (id #51). All 9 spec scenarios of the new `Strategy CRUD`
Requirement are runtime-compliant; pre-squash branch ref preserves the 3-commit TDD chain
with RED (`faed91a`) before GREEN (`7d8b5e2`); CI run #27157459203 SUCCESS; local re-run
of all 6 quality commands exits 0 on post-merge `main`.

---

## What Changed

### New capability: trading-domain

The delta spec at `openspec/changes/archive/strategy-crud/specs/trading-domain/spec.md`
(82 lines, 522 words) declared 1 ADDED Requirement on a **new** `trading-domain` capability
(no MODIFIED, no REMOVED, no RENAMED). Since no canonical spec for `trading-domain` existed,
the delta IS the canonical — copied directly to `openspec/specs/trading-domain/spec.md`
with structural adjustments (title renamed to `# Trading Domain`, `## ADDED Requirements`
→ `## Requirements`).

| Domain | Capability | Action | Details |
|--------|-----------|--------|---------|
| `trading-domain` | `trading-domain` | **Created** | 1 Requirement (Strategy CRUD), 9 scenarios |

### Canonical growth

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Capabilities | 1 (`python-toolchain`) | **2** | +1 (`trading-domain`) |
| Requirements (total) | 13 | **14** | +1 (Strategy CRUD) |
| Scenarios (total) | 44 | **53** | +9 (Strategy CRUD scenarios) |
| Words (total) | 3410 | **3930** | +520 (new canonical spec) |

The new `trading-domain` capability introduces:
- `app/schemas.py`: `StrategyCreate` (input) / `Strategy` (output) Pydantic models with UUID
- `app/store.py`: `StrategyStore` in-memory dict store with `list()`/`create()`/`get()`/`delete()`/`clear()`
- `app/main.py`: 4 CRUD endpoints — `GET /strategies`, `POST /strategies` (201), `GET /strategies/{id}` (200/404), `DELETE /strategies/{id}` (204/404)
- `tests/test_strategies.py`: 8 contract tests with `store.clear()` autouse fixture for isolation
- Strict TDD discipline (RED commit `faed91a` before GREEN commit `7d8b5e2`)

### Existing capability untouched

`openspec/specs/python-toolchain/spec.md` is unchanged — 13 Requirements, 44 scenarios,
362 lines, 3410 words. The `strategy-crud` change does not modify the toolchain capability.

### Change folder moved

`openspec/changes/strategy-crud/` → `openspec/changes/archive/strategy-crud/`
via `git mv` (3 renames: `proposal.md`, `tasks.md`, `specs/trading-domain/spec.md`).
The `openspec/changes/` directory now contains only `archive/`, `next-slice-explore/`, and
`.gitkeep` — no active `strategy-crud` change.

### Archive folder convention

Per project precedent (all 4 prior cycles: `bootstrap-toolchain`, `ci-quality-gate`,
`dev-tooling`, `fastapi-skeleton`), the archive folder is unprefixed:
`archive/strategy-crud/`, **not** `archive/2026-06-08-strategy-crud/`. This is a deliberate
deviation from the OpenSpec `openspec-convention.md` ISO-date-prefix convention, made
consistent across the project since the first archive. Git history of the archive folder
encodes the date.

---

## Pre-Archive Checks (all PASS)

Re-run of the 5/5 quality gate on the **current branch** (`docs/archive-strategy-crud`),
immediately before this report was written. PowerShell `RemoteException` banners on
`uv` commands are terminal artifacts (documented in `AGENTS.md`); exit codes trusted.

| # | Command | Exit | Key output |
|---|---|---|---|
| 1 | `uv run pytest` | 0 | 10 passed; coverage on `app/` = 100% (>= 80% threshold) |
| 2 | `uv run ruff check .` | 0 | "All checks passed!" |
| 3 | `uv run ruff format --check .` | 0 | "8 files already formatted" |
| 4 | `uv run mypy .` | 0 | "Success: no issues found in 8 source files" |
| 5 | `uv lock --check` | 0 | 39 packages resolved |

The 5 raw `uv run` commands above mirror the 5 quality steps and are the binding signal.

### Git state at archive time (after branch prep, before commit)

```
$ git status
On branch docs/archive-strategy-crud
Changes to be committed:
    renamed:    openspec/changes/strategy-crud/proposal.md -> openspec/changes/archive/strategy-crud/proposal.md
    renamed:    openspec/changes/strategy-crud/specs/trading-domain/spec.md -> openspec/changes/archive/strategy-crud/specs/trading-domain/spec.md
    renamed:    openspec/changes/strategy-crud/tasks.md -> openspec/changes/archive/strategy-crud/tasks.md
Untracked files:
    openspec/specs/trading-domain/
```

3 renames (staged) + 1 untracked directory (new canonical spec). Clean working tree apart
from the new canonicals and the folder move.

### Task Completion Gate

The on-disk `tasks.md` has all 3 implementation tasks documented with bullet-style
acceptance criteria (no `- [ ]` checkboxes for implementation tasks). The Pre-Apply Checks
section has all 6 items marked `[x]`. Apply progress (Engram #49) confirms 3/3 tasks
complete with binding pre-squash SHAs (`faed91a` RED, `7d8b5e2` GREEN, `2a086ad` spec).
Verify report (Engram #51) confirms PASS with 9/9 scenarios compliant, 10/10 tests
passing, 100% coverage. No stale-checkbox reconciliation needed — no implementation task
checkboxes to reconcile.

### Design phase

Design was **skipped** per orchestrator decision — tasks absorbed the design decisions.
The archive only reflects what exists on disk and in Engram.

---

## Engram Observation References

| Artifact | Engram ID | Notes |
|----------|-----------|-------|
| `sdd/strategy-crud/apply-progress` | #49 | 3/3 tasks complete |
| `sdd/strategy-crud/verify-report` | #51 | PASS — 0 CRITICAL, 0 WARNING, 0 SUGGESTIONS |

---

## Refs

| Kind | URL / Path | Status / SHA |
|---|---|---|
| Change folder (was) | `openspec/changes/strategy-crud/` | archived |
| Change folder (now) | `openspec/changes/archive/strategy-crud/` | 3 files + this report |
| New canonical spec | `openspec/specs/trading-domain/spec.md` | 1 Requirement / 9 scenarios / 83 lines / 520 words |
| Canonical `python-toolchain` | `openspec/specs/python-toolchain/spec.md` | unchanged (13 Requirements / 44 scenarios / 362 lines) |
| Apply evidence (Engram) | `sdd/strategy-crud/apply-progress` | id #49 (3/3 complete) |
| Verify evidence (Engram) | `sdd/strategy-crud/verify-report` | id #51 (PASS, 0C/0W/0S) |
| Issue (strategy-crud feature) | https://github.com/xmiquel/98-tstlocal/issues/21 | CLOSED |
| PR (feature squash) | https://github.com/xmiquel/98-tstlocal/pull/22 | MERGED at `0c56072` |
| CI run (PR #22 binding) | https://github.com/xmiquel/98-tstlocal/actions/runs/27157459203 | `success`, Quality Gate |
| Pre-squash branch ref | `feat/strategy-crud` (deleted) | 3 commits: `faed91a` (RED) → `7d8b5e2` (GREEN) → `2a086ad` (spec) |
| Pre-archive HEAD on `main` | `0c56072` | PR #22 squash on `main` |
| Prior archive (fastapi-skeleton) | `openspec/changes/archive/fastapi-skeleton/` | convention precedent |
| Prior archive (dev-tooling) | `openspec/changes/archive/dev-tooling/` | convention precedent |
| Prior archive (ci-quality-gate) | `openspec/changes/archive/ci-quality-gate/` | convention precedent |
| Prior archive (bootstrap-toolchain) | `openspec/changes/archive/bootstrap-toolchain/` | first convention precedent |

---

**Report generated**: 2026-06-08
**Archiver session**: `sdd-98-tstlocal-strategy-crud-archive-2026-06-08`
**Project**: 98-tstlocal
**Change**: strategy-crud
**SDD cycle status**: **CLOSED** — planned, applied, verified, and archived
