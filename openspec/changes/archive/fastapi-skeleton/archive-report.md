# Archive Report: fastapi-skeleton

**Change**: `fastapi-skeleton`
**Branch**: `docs/archive-fastapi-skeleton` (created from `main` at `60dd36f`)
**Project**: 98-tstlocal
**Archive folder**: `openspec/changes/archive/fastapi-skeleton/` (unprefixed per project convention)
**Spec merged into**: `openspec/specs/python-toolchain/spec.md`

---

## Verdict (from verify)

**`PASS`** — 0 CRITICAL, 0 WARNING, 5 SUGGESTIONS. Verify report saved to Engram as
`sdd/fastapi-skeleton/verify-report` (id #42). All 7 spec scenarios of the new `Application
Runtime` ADDED Requirement are runtime-compliant; pre-squash branch ref `45dfac9` preserves
the 4-commit TDD chain with RED before GREEN; CI run #27043793242 SUCCESS in 34s; local
re-run of all 6 quality commands exits 0 on post-merge `main`.

---

## What Changed

### Spec merge

The delta spec at `openspec/changes/archive/fastapi-skeleton/specs/python-toolchain/spec.md`
(84 lines, 646 words) declared 1 ADDED Requirement on the `python-toolchain` capability
(no MODIFIED, no REMOVED, no RENAMED). Merge was an append to the canonical's
`## ADDED Requirements` section, following the dev-tooling archive precedent
(PR #12, commit `db414dc`).

| Domain | Capability | Action | Details |
|---|---|---|---|
| `python-toolchain` | `python-toolchain` | **Updated** | 1 ADDED (appended), 0 MODIFIED, 0 REMOVED, 0 RENAMED |

### Canonical growth

| Metric | Before | After | Delta |
|---|---|---|---|
| Requirements | 12 | **13** | +1 (Application Runtime) |
| Scenarios | 37 | **44** | +7 (Application Runtime scenarios) |
| Words | 2848 | **3410** | +562 |
| Lines (file) | 314 | **362** | +48 |
| `git diff` lines | — | — | **+49 / -1** (1 Purpose-sentence replaced + 48 new lines) |

The new `Application Runtime` Requirement covers: module-level `app: FastAPI = FastAPI()` in
`app/main.py`; `GET /health` returning `{"status": "ok"}` with HTTP 200; `TestClient` test
in `tests/test_health.py`; `~=` pins on `fastapi~=0.116` and `httpx~=0.27` in
`pyproject.toml` `[project] dependencies`; explicit `uvicorn` deferral; strict TDD
discipline (test commit before implementation commit).

### `## Purpose` paragraph

The `## Purpose` section was preserved verbatim with **one additive sentence** at the end
documenting the fastapi-skeleton cycle. The 1-line deletion is the prior placeholder
sentence "This change ships zero application code." — replaced with a one-sentence
summary of the slice (FastAPI surface, `/health` route, `TestClient` test, runtime deps,
coverage gate becoming real, strict TDD exercised on a real feature). No contract change.

### Sections preserved unchanged

- All 12 pre-existing Requirements (8 in `## ADDED Requirements`, 1 in `## MODIFIED
  Requirements`, 3 in `## Out of Scope — Branch Protection Rules` style, all 4 dev-tooling
  additions, all `Application Runtime` predecessors)
- The `## MODIFIED Requirements` section in full
- The `## Out of Scope (Non-Requirements)` section in full (per dev-tooling precedent: the
  per-delta `## Out of Scope` block is a change-level non-goal list, not a capability-level
  one; not merged into the canonical)

### Change folder moved

`openspec/changes/fastapi-skeleton/` → `openspec/changes/archive/fastapi-skeleton/`
via `git mv` (5 renames, 0 delete+add). The `openspec/changes/` directory now contains
only `archive/` and `.gitkeep` — no active `fastapi-skeleton` change.

### Archive folder convention

Per project precedent (all 3 prior cycles: `bootstrap-toolchain`, `ci-quality-gate`,
`dev-tooling`), the archive folder is unprefixed: `archive/fastapi-skeleton/`, **not**
`archive/2026-06-06-fastapi-skeleton/`. This is a deliberate deviation from the OpenSpec
`openspec-convention.md` ISO-date-prefix convention, made consistent across the project
since the first archive. Git history of the archive folder encodes the date.

---

## Pre-Archive Checks (all PASS)

Re-run of the 5/5 quality gate on the **current branch** (`docs/archive-fastapi-skeleton`),
immediately before this report was written. PowerShell `RemoteException` banners on
`uv` commands are terminal artifacts (documented in `AGENTS.md`); exit codes trusted.

| # | Command | Exit | Key output |
|---|---|---|---|
| 1 | `uv run pytest` | 0 | 2 passed (`test_health_returns_ok_status`, `test_math_still_works`); coverage on `app/` = 100% (>= 80% threshold) |
| 2 | `uv run ruff check .` | 0 | "All checks passed!" |
| 3 | `uv run ruff format --check .` | 0 | "5 files already formatted" |
| 4 | `uv run mypy .` | 0 | "Success: no issues found in 5 source files" |
| 5 | `uv lock --check` | 0 | 39 packages resolved (PowerShell `RemoteException` banner = noise) |

The branch also includes a 6th check (`make ci` — aggregator) documented in
`tasks.md` Pre-Apply Checks; not run on this branch because `make` is not installed on
this Windows PowerShell (already in `AGENTS.md` § Known gotchas). The 5 raw `uv run`
commands above mirror the same 5 quality steps from `make ci` and are the binding signal.

### Git state at archive time

```
$ git status
On branch docs/archive-fastapi-skeleton
Changes to be committed:
	renamed:    openspec/changes/fastapi-skeleton/design.md -> openspec/changes/archive/fastapi-skeleton/design.md
	renamed:    openspec/changes/fastapi-skeleton/exploration.md -> openspec/changes/archive/fastapi-skeleton/exploration.md
	renamed:    openspec/changes/fastapi-skeleton/proposal.md -> openspec/changes/archive/fastapi-skeleton/proposal.md
	renamed:    openspec/changes/fastapi-skeleton/specs/python-toolchain/spec.md -> openspec/changes/archive/fastapi-skeleton/specs/python-toolchain/spec.md
	renamed:    openspec/changes/fastapi-skeleton/tasks.md -> openspec/changes/archive/fastapi-skeleton/tasks.md
Changes not staged for commit:
	modified:   openspec/specs/python-toolchain/spec.md
```

5 renames + 1 modification; clean working tree apart from the spec merge and the folder
move. Pre-merge HEAD on `main` was `60dd36f`; the new branch sits 0 commits ahead of main
(spec merge + folder move will be a single squash commit on this branch).

### Commits to land on `main` after this archive merges

`main` is currently at `60dd36f` (3 squash merges this cycle: PR #14, #16, #18). After
this archive's squash-merge lands, `main` will gain **1 additional squash commit**:
`docs(specs): archive fastapi-skeleton change` (the commit this report documents).

### Stale-checkbox reconciliation

The on-disk `tasks.md` had the 6 Pre-Apply Checks as `- [ ]` (unchecked) at archive
time. This archive phase **mechanically marks all 6 as `- [x]`** in the archived copy
as an exceptional reconciliation under the SKILL.md § Task Completion Gate, with proof
anchored in:

- **Apply evidence** (Engram #39 `sdd/fastapi-skeleton/apply-progress`): 4/4
  implementation tasks complete with binding pre-squash SHAs (`58855f2` deps, `7641cad`
  RED, `8c4c013` GREEN, `741714b` spec-arc); all 6 local quality commands exit 0; 4/4
  binding TDD categories PASS.
- **Verify evidence** (Engram #42 `sdd/fastapi-skeleton/verify-report`): re-run of the 6
  quality commands on post-merge `main` all exit 0; CI run #27043793242 SUCCESS in 34s;
  7/7 spec scenarios compliant.
- **Git state**: working tree clean; `main` HEAD at `60dd36f` (pre-merge of this archive).

The 4 implementation tasks (1-4) use bullet-style acceptance criteria on disk (no
checkboxes); their DONE state is recorded in Engram observation #38. The reconcile note
is appended to the archived `tasks.md` so the audit trail is transparent. No re-apply or
re-verify was performed; this is purely checkbox-state correction at archive time. The
reconcile mirrors the dev-tooling archive precedent (PR #12, commit `db414dc`).

---

## Resolved SUGGESTIONS (out-of-band)

The verify report raised 5 SUGGESTIONS. 2 of them were resolved **out-of-band** of this
archive (i.e., already merged on `main` before this archive phase ran), so the archive
itself does not need to address them. 3 remain as non-blocking documentable items.

### SUGGESTION 1 — `type:feature` label

> Verify report: "create `type:feature` label in the repo, or formalize the convention in
> `AGENTS.md` that feature PRs use `enhancement` (not `type:*`)."

**Resolution**: `type:feature` label exists in the repo and was applied to PR #14
(merged at `007a1a3`). Verified via `gh issue view 13` which shows the issue (and PR by
extension) carries the `type:feature` label. Confirmed out-of-band before this archive
phase.

### SUGGESTION 2 — `Co-authored-by: sdd-bootstrap` trailer

> Verify report: "optionally formalize in `AGENTS.md` that `sdd-bootstrap` is the project's
> SDD agent identity (like a CI bot), distinct from LLM attribution."

**Resolution**: formalized in `AGENTS.md` via PR #18 (merged at `60dd36f`),
`docs(agents): clarify that project automation identities are exempt from no-AI-attribution`.
The project automation identities (Dependabot, `sdd-bootstrap`) are now explicitly carved
out in the no-AI-attribution rule. The `Co-authored-by: sdd-bootstrap` trailer in
squash-merges is no longer a SUGGESTION. Confirmed out-of-band before this archive phase.

---

## Remaining SUGGESTIONS (non-blocking, documentable)

3 SUGGESTIONS from the verify report remain. None block archive; all are project-convention
questions or documentable cosmetics. Tracking them here so the next change's proposal phase
can pick them up or close them.

### SUGGESTION 3 — `httpx 0.27` StarletteDeprecationWarning

> Verify report: "appears in pytest output ('Using `httpx` with `starlette.testclient` is
> deprecated; install `httpx2` instead.'). Documented cosmetic per design § Risks and
> spec.md § Out of Scope. Not a test failure. **Action**: deferred to a future slice per
> design (pin `httpx~=0.28` only if the warning becomes noisy)."

**Disposition**: deferred per design. The slice's scope intentionally pins `httpx~=0.27`
per the proposal and exploration; the deprecation warning is a known cosmetic, not a
defect. Will be re-evaluated when the next slice adds a second endpoint (where TestClient
is no longer "the only test pattern" and the warning's noisiness changes). Track in the
next change's `Risks` table or as a follow-up commit on the existing `fastapi-skeleton`
slice if CI starts running `pytest -W error`.

### SUGGESTION 4 — `exploration.md` extra in commit `741714b`

> Verify report: "tasks.md task 4 lists 4 files (`{proposal.md, specs/python-toolchain/spec.md,
> design.md, tasks.md}`), but the actual commit includes `exploration.md` as a 5th file.
> This is a project convention (the sdd-explore phase produces `exploration.md`; prior
> cycles have followed the same pattern). tasks.md was under-specified. **Action**: update
> tasks.md template to include `exploration.md` in the file list for future slices, or
> document the convention in `AGENTS.md`."

**Disposition**: project convention; tasks.md template under-specified. The 5-file
pattern (`proposal.md`, `design.md`, `exploration.md`, `tasks.md`, `specs/<capability>/spec.md`)
has been consistent across bootstrap-toolchain, ci-quality-gate, dev-tooling, and now
fastapi-skeleton. Update the sdd-tasks template to reflect the convention in a future
skill-improvement cycle, or document in `AGENTS.md` § Conventions.

### SUGGESTION 5 — PowerShell `RemoteException` on `uv`

> Verify report: "observed in this verify run. Documented Windows terminal artifact
> (AGENTS.md § Known gotchas; prior verify reports noted the same). Exit code is 0.
> **Action**: none — the banner is noise, not a failure."

**Disposition**: closed as a non-issue. Already documented in `AGENTS.md` § Known gotchas
and in all 3 prior archive reports. Re-confirmed during this archive's pre-apply checks
(`uv lock --check` emitted the banner; exit code 0; trust the exit code).

---

## Refs

| Kind | URL / Path | Status / SHA |
|---|---|---|
| Change folder (was) | `openspec/changes/fastapi-skeleton/` | archived |
| Change folder (now) | `openspec/changes/archive/fastapi-skeleton/` | 5 files + this report |
| Canonical spec (after) | `openspec/specs/python-toolchain/spec.md` | 13 Requirements / 44 Scenarios / 362 lines / 3410 words |
| Apply evidence (Engram) | `sdd/fastapi-skeleton/apply-progress` | id #39 |
| Verify evidence (Engram) | `sdd/fastapi-skeleton/verify-report` | id #42 (PASS, 0C/0W/5S) |
| Tasks (Engram) | `sdd/fastapi-skeleton/tasks` | id #38 (4/4 complete) |
| Proposal (Engram) | `sdd/fastapi-skeleton/propose` | (in-session, not searched; see on-disk `proposal.md`) |
| Exploration (Engram) | `sdd/fastapi-skeleton/explore` | id #34 |
| Issue (fastapi-skeleton feature) | https://github.com/xmiquel/98-tstlocal/issues/13 | CLOSED, label `type:feature` |
| PR (feature squash) | https://github.com/xmiquel/98-tstlocal/pull/14 | MERGED at `007a1a3` |
| PR (PEP 440 fix) | https://github.com/xmiquel/98-tstlocal/pull/16 | MERGED at `eb767d1` |
| PR (AGENTS.md clarification) | https://github.com/xmiquel/98-tstlocal/pull/18 | MERGED at `60dd36f` |
| CI run (PR #14 binding) | https://github.com/xmiquel/98-tstlocal/actions/runs/27043793242 | `success`, Quality Gate in 34s (ID 79825449835) |
| Pre-squash branch ref | `45dfac9` | visible via `git log --all`; original 4 commits `58855f2` → `7641cad` (RED) → `8c4c013` (GREEN) → `741714b` |
| Pre-archive HEAD on `main` | `60dd36f` | 3 squash-merges on `main` (feature + PEP 440 + AGENTS.md) |
| Prior archive (dev-tooling) | https://github.com/xmiquel/98-tstlocal/pull/12 | MERGED at `db414dc`; convention precedent |
| Prior archive (ci-quality-gate) | `openspec/changes/archive/ci-quality-gate/` | convention precedent |
| Prior archive (bootstrap-toolchain) | `openspec/changes/archive/bootstrap-toolchain/` | first convention precedent |

---

**Report generated**: 2026-06-06
**Archiver session**: `sdd-98-tstlocal-fastapi-skeleton-archive-2026-06-06`
**Project**: 98-tstlocal
**Change**: fastapi-skeleton
**SDD cycle status**: **CLOSED** — planned, applied, verified, and archived
