# Archive Report: frontend-crud-forms

**Change**: `frontend-crud-forms`
**Branch**: `feat/frontend-crud-forms` (created from `main`, pushed, PR #45, squash-merged)
**Project**: 98-tstlocal
**Archive folder**: `openspec/changes/archive/frontend-crud-forms/` (unprefixed per project convention)
**Modified capability**: `frontend` at `openspec/specs/frontend/spec.md`

---

## Verdict

**`PASS`** — All tasks complete, CI green, PR squash-merged at `b968d76`.
Verification gates confirmed:
| Gate | Result |
|------|--------|
| Tests | 36 passing (29 existing + 7 new) |
| Coverage | 97% |
| ruff | clean |
| mypy | clean |
| lock | clean |

---

## What Changed

### Modified capability: frontend — Strategy CRUD Forms (DELTA MERGE)

The delta spec at `openspec/changes/frontend-crud-forms/specs/frontend/spec.md` was merged
into the canonical `openspec/specs/frontend/spec.md` as a new **Requirement: Strategy CRUD Forms**
with 6 scenarios.

| Domain | Capability | Action | Details |
|--------|-----------|--------|---------|
| `frontend` | `Strategy CRUD Forms` | **Added** (delta merge) | +1 Requirement with 6 scenarios (create/edit/delete forms) |

### Spec correction applied during archive

The delta spec's scenario #5 originally read `DELETE /strategies/{id}` (JSON endpoint, 204).
During archive merge, this was corrected to `DELETE /strategies/{id}/html` with status 200,
matching the implementation — because 204 has no body for HTMX swap.

### Out of Scope cleanup

The outdated deferred-CRUD line ("HTMX form submission, swap mechanics, and CRUD operations
are deferred to subsequent frontend slices") was removed from the canonical spec's Out of
Scope section, since CRUD operations are now implemented.

### Canonical spec delta

| Metric | Before | After |
|--------|--------|-------|
| Requirements | 1 (Strategy List Page) | 2 (+ Strategy CRUD Forms) |
| Scenarios | 4 | 10 (+6 CRUD scenarios) |
| Domain spec total lines | 55 | 102 |
| Out of Scope items | 5 (forms, CRUD, pagination, sorting, search) | 3 (pagination, sorting, search) |

The 6 scenarios cover the CRUD contract:

1. **GET /strategies/new renders create form** — empty form with name/description inputs
2. **POST /strategies/html creates strategy and returns list partial** — HTMX form create
3. **GET /strategies/{id}/edit renders pre-filled edit form** — pre-filled form from store
4. **PUT /strategies/{id}/html updates strategy and returns updated list** — HTMX form update
5. **DELETE /strategies/{id}/html via HTMX removes strategy** — HTMX delete with list swap
6. **POST /strategies/html with empty name rejects submission** — validation error display

### Existing capabilities unchanged

`openspec/specs/python-toolchain/spec.md` and `openspec/specs/trading-domain/spec.md`
are untouched — 0 modifications to existing specs.

### Implementation artifacts (from merged PR #45, b968d76)

- `app/main.py`: Modified — added `Form`, `ValidationError` imports; added CRUD HTML routes (`/strategies/new`, `POST /strategies/html`, `GET {id}/edit`, `PUT {id}/html`, `DELETE {id}/html`)
- `app/schemas.py`: Modified — added `min_length=1` validation on strategy `name` field
- `templates/strategies/form.html`: New — shared create/edit form with pre-fill, error display, HTMX wiring
- `templates/strategies/list.html`: Modified — added `<th>Actions</th>` column, edit link, delete button with HTMX attributes
- `pyproject.toml`: Modified — added `python-multipart~=0.0` dependency
- `uv.lock`: Updated — python-multipart 0.0.32 resolved
- `tests/test_pages.py`: Modified — added 7 integration tests (form render, create, edit, delete, validation, button attributes)

### Change folder moved

`openspec/changes/frontend-crud-forms/` → `openspec/changes/archive/frontend-crud-forms/`
via `git mv` (5 items: `design.md`, `proposal.md`, `specs/frontend/spec.md`, `tasks.md`, and this `archive-report.md`).
The `openspec/changes/` directory no longer contains an active `frontend-crud-forms` change.

### Archive folder convention

Per project precedent (all prior cycles), the archive folder is unprefixed:
`archive/frontend-crud-forms/`, **not** `archive/YYYY-MM-DD-frontend-crud-forms/`. Git history
of the archive folder encodes the date.

---

## Pre-Archive Checks (5/5 PASS)

| # | Check | Result | Details |
|---|-------|--------|---------|
| 1 | **Task Completion Gate** | ✅ PASS | On-disk `tasks.md` has all 16 implementation tasks `[x]`. CI green. |
| 2 | **Canonical spec updated** | ✅ PASS | `openspec/specs/frontend/spec.md` — Strategy CRUD Forms requirement merged with 6 scenarios. Scenario #5 corrected to `/html` route. |
| 3 | **Delta spec preserved** | ✅ PASS | Archived `openspec/changes/archive/frontend-crud-forms/specs/frontend/spec.md` contains the original delta spec. |
| 4 | **All artifacts archived** | ✅ PASS | 5 items archived: `design.md`, `proposal.md`, `tasks.md`, `specs/frontend/spec.md`, `archive-report.md`. |
| 5 | **Active directory clean** | ✅ PASS | `openspec/changes/frontend-crud-forms/` no longer exists. |

### Task Completion Gate Detail

The on-disk `tasks.md` at `openspec/changes/archive/frontend-crud-forms/tasks.md` has all
16 implementation tasks marked `[x]` across 4 phases (Templates, Routes, Tests, Verify).
No stale-checkbox reconciliation needed — the on-disk artifact is correct. CI passed on the
squash-merged commit.

---

## Spec Correction Detail

During delta merge into the canonical spec, one intentional correction was applied:

| Delta spec (as written) | Canonical spec (after merge) | Rationale |
|------------------------|------------------------------|-----------|
| Scenario #5: `DELETE /strategies/{id}`, status 204 or 200 | `DELETE /strategies/{id}/html`, status 200 | JSON endpoint returns 204 with no body — HTMX cannot swap. The implementation uses `DELETE /strategies/{id}/html` returning 200 with the updated list. |
| Scenario #5: asserts "204 or 200" | asserts "200" | Only 200 is correct for the HTML route. |

This is a spec correction, not a deviation. The design document (design.md §Spec Deviation)
flagged this issue before implementation.

---

## Engram Observation References

No Engram observations were created for this change's SDD artifacts during the main SDD cycle.
The archive report is persisted to Engram as `sdd/frontend-crud-forms/archive-report` for
cross-session recovery.

---

## Refs

| Kind | URL / Path | Status / SHA |
|------|-----------|--------------|
| Change folder (was) | `openspec/changes/frontend-crud-forms/` | archived |
| Change folder (now) | `openspec/changes/archive/frontend-crud-forms/` | 5 items + this report |
| Canonical spec (updated) | `openspec/specs/frontend/spec.md` | 2 Requirements / 10 scenarios / 102 lines |
| PR (feature squash) | https://github.com/xmiquel/98-tstlocal/pull/45 | MERGED at `b968d76` |
| Squash-merge commit | `b968d769a7c93ccc4e9a8f34084fbbf99734eee2` | Fast-forward to `main` |

---

**Report generated**: 2026-06-09
**Project**: 98-tstlocal
**Change**: frontend-crud-forms
**SDD cycle status**: **CLOSED** — proposed, designed, implemented, verified, and archived
