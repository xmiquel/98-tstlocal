# Archive Report — dev-tooling

**Change**: `dev-tooling`
**Branch**: `main`
**Merge commit SHA**: `7ccd19fbf3868630a0b7172bbfb0197190c9c12c`
**Merge base**: `de49bf9` (ci-quality-gate archive HEAD)
**Dates**: proposed 2026-06-05 · verified 2026-06-05 · archived 2026-06-05
**Session**: `sdd-98-tstlocal-dev-tooling-2026-06-05`
**Project**: 98-tstlocal
**Archive folder**: `openspec/changes/archive/dev-tooling/`
**Spec merged into**: `openspec/specs/python-toolchain/spec.md`

---

## 1. Executive Summary

The `dev-tooling` change shipped **4 new files** (`.github/dependabot.yml`, `.pre-commit-config.yaml`, `Makefile`, `AGENTS.md`) and modified **3 files** (`pyproject.toml`, `README.md`, `uv.lock`), totaling **+313/-91** across **7 files**. The squash-merge is on `main` at `7ccd19f` (PR #8 MERGED, issue #7 CLOSED, branch `chore/dev-tooling` deleted on remote). The binding CI run on the PR branch (run #27032809386, `windows-latest`, 25s) was GREEN with the Quality Gate check exiting 0 in every step, and **all 28 spec scenarios** (3 MODIFIED + 4 ADDED requirements) are structurally compliant. The delta spec was merged into the canonical `python-toolchain` spec with full-replacement of 3 MODIFIED requirements and append of 4 ADDED requirements, growing the canonical from **1341 → 2848 words** and **158 → 314 lines** (12 Requirements total, 37 Scenarios total). The verdict was `WARN` (0 CRITICAL, 1 WARNING, 6 SUGGESTION) and the change is **archived with warnings**; the 1 WARNING is the pre-known USER setup step (`gh repo edit --enable-auto-merge`) — the change itself is correct and complete.

**Operational highlight**: Dependabot opened **PRs #9 and #10** within 2 minutes of the squash-merge (PR #9 for `actions/checkout` and `astral-sh/setup-uv`; PR #10 for the python-deps group with 5 updates). The `dependencies` label was auto-created on first run. The change is fully operational end-to-end — auto-merge is the only deferred step (USER action, documented in the proposal).

---

## 2. Final State

| Item | Value |
|---|---|
| Files in commit | 7 (4 new + 3 modified: `pyproject.toml`, `README.md`, `uv.lock`) |
| Source files modified (Python code) | 0 |
| New config / docs files | 4 (`.github/dependabot.yml`, `.pre-commit-config.yaml`, `Makefile`, `AGENTS.md`) |
| Modified non-source files | 2 (`pyproject.toml`, `README.md`); `uv.lock` regenerated |
| Squash commit on `main` | `7ccd19fbf3868630a0b7172bbfb0197190c9c12c` |
| PR | https://github.com/xmiquel/98-tstlocal/pull/8 — MERGED, base `main`, head `chore/dev-tooling`, label `type:chore` |
| Issue | https://github.com/xmiquel/98-tstlocal/issues/7 — CLOSED, label `status:approved` |
| CI run (binding, on PR) | https://github.com/xmiquel/98-tstlocal/actions/runs/27032809386 — `success`, Quality Gate in 25s (ID 79789145035); 8/8 user-defined steps exit 0 |
| CI run (Dependabot actions) | run #27032897589, `success`, 34s (gated by Quality Gate) |
| CI run (Dependabot python-deps) | run #27032942001, `success`, 32s (gated by Quality Gate) |
| Branch protection | Configured on `main`, required check `Quality Gate` (strict: true, enforce_admins: true) — per Engram #20/#23 |
| Working tree | Clean of source changes at archive time; only the change folder (now archived) was untracked |
| Local re-run of CI commands | All 6 exit 0 (pytest, ruff check, ruff format --check, mypy, uv lock --check, uv sync --frozen) + `uv run pre-commit run --all-files` exit 0 |
| Local re-run (archive-time sanity) | `uv run pytest` exit 0, 1 passed, coverage 100% ≥ 80% threshold |
| Line delta | **+313 / -91** across 7 files (squash commit stat) |

---

## 3. Spec Merge Summary

Delta spec at `openspec/changes/archive/dev-tooling/specs/python-toolchain/spec.md` declared 3 MODIFIED + 4 ADDED Requirements on the `python-toolchain` capability. Merge was a surgical full-replacement per the OpenSpec MODIFIED convention, with ADDED Requirements appended to the canonical's `## ADDED Requirements` section regardless of where the requirement currently lives in the canonical (per project precedent from `ci-quality-gate` archive — match by name, not by section).

| Domain | Capability | Action | Details |
|---|---|---|---|
| `python-toolchain` | `python-toolchain` | **Updated** | 3 MODIFIED (full-replacement), 4 ADDED (appended), 0 REMOVED, 0 RENAMED |

### Word and line counts

| Artifact | Words | Lines | Δ vs. canonical |
|---|---|---|---|
| Canonical spec (before merge) | 1341 | 158 | — |
| Delta spec (source) | 2099 | 234 | — |
| Canonical spec (after merge) | **2848** | **314** | **+1507 words, +156 lines** |

### Requirements changed

| # | Requirement | Action | In canonical section | Scenarios before → after |
|---|---|---|---|---|
| 1 | Toolchain Pinning and Lockfile | **REPLACED** (MODIFIED) | `## ADDED Requirements` | 3 → 5 (added "Dev-dependency pins use compatible-release specifier", "Dependabot tracks dev-dependency version bumps") |
| 2 | Code Quality (Lint, Format, Type Check) | **REPLACED** (MODIFIED) | `## ADDED Requirements` | 2 → 6 (added 4 pre-commit scenarios: ruff-format, ruff, mypy, bypass) |
| 3 | Test Runner and Coverage Gate | **REPLACED** (MODIFIED) | `## MODIFIED Requirements` | 2 → 4 (added "Make target `make test`", "Make target `make ci`") |
| 4 | Dependabot | **APPENDED** (ADDED) | `## ADDED Requirements` | new, 3 scenarios |
| 5 | Pre-commit Hooks | **APPENDED** (ADDED) | `## ADDED Requirements` | new, 3 scenarios |
| 6 | Makefile Targets | **APPENDED** (ADDED) | `## ADDED Requirements` | new, 3 scenarios |
| 7 | AGENTS.md | **APPENDED** (ADDED) | `## ADDED Requirements` | new, 4 scenarios |
| — | OpenSpec Strict TDD Mode | UNCHANGED | `## ADDED Requirements` | preserved as-is, 1 scenario |
| — | GGA Python Mode | UNCHANGED | `## ADDED Requirements` | preserved as-is, 1 scenario |
| — | Repository Hygiene | UNCHANGED | `## ADDED Requirements` | preserved as-is, 1 scenario |
| — | Continuous Integration Workflow | UNCHANGED | `## ADDED Requirements` | preserved as-is, 5 scenarios |
| — | Out of Scope — Branch Protection Rules | UNCHANGED | `## ADDED Requirements` | preserved as-is, 1 scenario |

**Canonical totals after merge**: **12 Requirements** (7 in `## ADDED Requirements` preserved/replaced, 4 new in `## ADDED Requirements` appended, 1 in `## MODIFIED Requirements` replaced) and **37 Scenarios** (9 preserved from previous changes, 15 contributed by MODIFIED replacements, 13 contributed by ADDED appends).

### Normalization notes

- **Heading levels**: canonical uses `##` for top-level sections and `### Requirement: <name>` / `#### Scenario: <name>` for content; delta uses the same hierarchy. **No normalization needed.**
- **Scenario body style**: delta uses `**GIVEN**` / `**WHEN**` / `**THEN**` (bolded, no bullets) with blank lines between scenarios. Canonical uses `- GIVEN` / `- WHEN` / `- THEN` (bulleted) with blank lines between scenarios. **Normalized all delta content (both MODIFIED and ADDED blocks) to canonical's bulleted style** for consistency across the entire file. Both styles parse identically as Markdown and are visually equivalent after a soft wrap; the bulleted form matches the rest of the canonical.
- **`> Satisfies: ...` lines**: present in all 7 delta Requirement blocks (3 MODIFIED + 4 ADDED). **Preserved in the canonical** as part of the requirement documentation. These are an OpenSpec convention for tracking which scenarios each block satisfies.
- **`(Previously: ...)` notes**: preserved in all 3 MODIFIED blocks. They are part of the delta's MODIFIED body and document what changed in this cycle (the change-of-record marker for the transition to `~=` pins, pre-commit hooks, and Makefile wrappers).
- **Historical `> 2026-06-05 — MODIFIED:` meta-commentary**: not present in the current canonical; no action needed.
- **`## Purpose` section**: preserved verbatim with **one additive sentence** documenting the dev-tooling cycle (pre-commit, Makefile, Dependabot, AGENTS.md, `~=` pins). The additive sentence lives at the end of the existing paragraph and does not modify the contract.
- **Sections preserved unchanged**: `## ADDED Requirements` (existing entries OpenSpec Strict TDD Mode / GGA Python Mode / Repository Hygiene / Continuous Integration Workflow / Out of Scope — Branch Protection Rules), `## Out of Scope (Non-Requirements)`.
- **Section split preserved**: `## ADDED Requirements` and `## MODIFIED Requirements` are kept as separate top-level sections per the precedent set by the `bootstrap-toolchain` archive and the `ci-quality-gate` archive. **OpenSpec merges by requirement name, not by section** — so the 4 ADDED requirements from this delta are appended to canonical's `## ADDED Requirements` even though 1 of the MODIFIED requirements lives in canonical's `## MODIFIED Requirements`. This matches the precedent.

### Sections not added to canonical

- `## REMOVED Requirements` — delta declares None.
- `## RENAMED Requirements` — delta declares None.
- A consolidated "future dev-tooling follow-ups" section — the 6 SUGGESTIONs from the verify report are tracked in this archive-report's § Outstanding Follow-Ups, not in the canonical spec.

---

## 4. Artifacts Preserved

The archive folder contains **5 files** (4 from the change + 1 archive report). All files match the `openspec-convention.md` archive structure.

| File | Purpose | Source | Notes |
|---|---|---|---|
| `proposal.md` | Change proposal (intent, scope, approach, risks, rollback) | sdd-propose | 102 lines |
| `tasks.md` | 16/16 implementation tasks (reconciled at archive time) + archive-time reconciliation note | sdd-tasks, sdd-apply, sdd-archive | See § 6 for the archive-time reconciliation explanation |
| `specs/python-toolchain/spec.md` | Delta spec that drove the canonical merge | sdd-spec | 234 lines, 2099 words |
| `verify-report.md` | Full verify report (30 commands, 28/28 scenarios compliant, TDD matrix) | sdd-verify | 423 lines |
| `archive-report.md` | This file | sdd-archive | — |

### Archive folder note (convention adherence)

Per project precedent (both `bootstrap-toolchain` and `ci-quality-gate` archives use the **unprefixed** form), the archive folder name is **`openspec/changes/archive/dev-tooling/`** (no `YYYY-MM-DD-` prefix). This is a **deliberate deviation from the OpenSpec convention** in `skills/_shared/openspec-convention.md` which uses `archive/YYYY-MM-DD-{change-name}/`. The deviation is acceptable and consistent because:

1. The `bootstrap-toolchain` archive (the first cycle on this repo) established the no-prefix pattern.
2. The `ci-quality-gate` archive (the second cycle) followed the same pattern.
3. The verify report's § 11 recommendation suggested `archive/2026-06-05-dev-tooling/`, but this is overridden by the project precedent per the orchestrator's explicit instruction.
4. Git history of the archive folder (`git log --follow openspec/changes/archive/dev-tooling/`) encodes the date; the folder name itself is a stable, date-free identifier.

The SKILL.md `## Rules` rule "Use ISO date format (YYYY-MM-DD) for archive folder prefix" is overridden by the project convention in this case. The deviation is transparent and documented here so reviewers can verify the choice.

---

## 5. Engram Observation Lineage

The following Engram observations were created during this SDD cycle and are preserved as historical record (none deleted by archive):

| ID | Title | Purpose |
|---|---|---|
| #25 | `sdd/dev-tooling/proposal` | Change proposal (sdd-propose output) |
| #26 | `sdd/dev-tooling/spec` | Delta spec (sdd-spec output) |
| #27 | `sdd/dev-tooling/tasks` | Task breakdown (sdd-tasks output) |
| #28 | `sdd/dev-tooling/apply-progress` | Apply evidence (6 commits, branch/PR/CI run URLs, 4/4 binding TDD categories PASS, sub-agent recovery note) |
| #29 | `sdd/dev-tooling/verify-report` | Verify evidence (30 checks, 28/28 scenarios compliant, full spec compliance matrix, WARN verdict) |
| (this save) | `sdd/dev-tooling/archive-report` | This closure record (sdd-archive output) |

The apply-progress (#28) and verify-report (#29) observations are kept as historical record per the SKILL.md and the orchestrator's instruction ("do NOT delete them"). The cycle is closed: 6 observations trace the full `propose → spec → tasks → apply → verify → archive` flow.

---

## 6. Archive-Time Stale-Checkbox Reconciliation

The sdd-apply phase completed all 6 implementation commits on `chore/dev-tooling` (squash-merged to `main` as `7ccd19f` via PR #8) but **did not persist task-checkbox state to the on-disk `tasks.md`** — the file kept the original `- [ ]` checkboxes while the in-memory todos were all marked done.

This archive phase **mechanically marks all 16 task checkboxes as completed** in the archived `tasks.md` as an exceptional reconciliation under the SKILL.md § Task Completion Gate, with proof anchored in:

- **Apply evidence** (Engram #28): 6 commits with the expected hashes (`a63c195`, `f899fb7`, `0d7bb76`, `be2830a`, `8d41dfc`, `043485b`), 4/4 binding TDD categories PASS, all 6 local quality commands exit 0
- **Verify evidence** (Engram #29): 16/16 implementation tasks complete, 28/28 spec scenarios compliant, CI run #27032809386 SUCCESS, 7 files / +313/-91 on `main` at `7ccd19f`
- **Git state** (working tree, both `git rev-parse HEAD` and `git rev-parse origin/main` = `7ccd19f`)

The reconciliation note is appended to the archived `tasks.md` so the audit trail is transparent. **No re-apply or re-verify was performed**; this is purely checkbox-state correction based on binding TDD and post-merge evidence. The orphaned in-memory todo state from the apply phase did not propagate to the persisted artifact, and the archive sub-agent performs the mechanical fix per the SKILL.md "exceptional mechanical reconciliation with proof" provision.

---

## 7. Verdict and Recommendation

**Final verdict**: `WARN` (0 CRITICAL, 1 WARNING, 6 SUGGESTION)
**Recommendation**: `archive-with-warnings` (executed — change is now archived)

The 1 WARNING and 6 SUGGESTIONs are triaged below.

---

## 8. Outstanding Follow-Ups

### WARNING (USER action — out-of-band of the change)

1. **Auto-merge not yet enabled at the repo level** — `gh pr view 9` and `gh pr view 10` both return `autoMergeRequest: null`. Dependabot PRs #9 and #10 are opening, passing the Quality Gate, and stalling open instead of auto-merging. The repo setting `gh repo edit xmiquel/98-tstlocal --enable-auto-merge` was documented in the proposal § User Setup Steps (line 101) as a 1-time USER action. **Action**: USER should run the one-line setup step. Once enabled, the already-open Dependabot PRs #9 and #10 will auto-merge on the next Quality Gate re-run, and future Dependabot PRs will auto-merge immediately on CI green. This is environmental, not a defect of the change.

### SUGGESTIONs (deferred to future changes)

These 6 SUGGESTIONs from the verify report are nice-to-have improvements, scoped to potential future changes:

1. **`make` is not installed on this Windows system** — `make ci` is unavailable locally. The 6 raw commands are the fallback. **Action**: optional — document in `AGENTS.md` § Known gotchas that `make` is not pre-installed on Windows and the 6 raw commands are the fallback.
2. **`.pre-commit-config.yaml` `rev: v0.6.9` is not tracked by Dependabot** — Dependabot's `github-actions` ecosystem only tracks GitHub Actions, not external pre-commit hook revisions. **Action**: optional — consider adding a `pre-commit` ecosystem to dependabot (Dependabot gained pre-commit ecosystem support in late 2024) OR accepting manual `rev` bumps.
3. **No CI job for `pre-commit run --all-files`** — by design, pre-commit is local-only. **Action**: optional — add a `pre-commit` job to the CI workflow as defense-in-depth.
4. **No `make setup` target** — a one-time setup target combining `uv sync` + `uv run pre-commit install` would streamline onboarding. **Action**: optional — add `setup:` target to Makefile.
5. **No `CONTRIBUTING.md`** — all conventions live in `AGENTS.md` (AI-focused). **Action**: optional — create `CONTRIBUTING.md` and reference `AGENTS.md` for AI-specific concerns.
6. **PowerShell `RemoteException` artifact** — observed in `uv run pytest`, `uv lock --check`, and `uv sync --frozen` outputs. This is the documented Windows terminal artifact (already in `AGENTS.md` § Known gotchas). **Action**: none — exit codes are 0, the banners are noise.

---

## 9. Operational Evidence (Dependabot post-merge)

Within 2 minutes of the squash-merge to `main`, Dependabot opened 2 PRs against the repo:

- **PR #9** https://github.com/xmiquel/98-tstlocal/pull/9 — `chore(deps): bump the actions group with 2 updates` (Dependabot github-actions ecosystem)
- **PR #10** https://github.com/xmiquel/98-tstlocal/pull/10 — `chore(deps-dev): bump the python-deps group with 5 updates` (Dependabot uv ecosystem)

Both PRs triggered the binding Quality Gate CI check, which passed (runs #27032897589 and #27032942001 respectively, 34s and 32s). Both PRs remain OPEN because the repo's auto-merge setting is not yet enabled (see § 8 WARNING #1). The `dependencies` label was **auto-created by Dependabot on its first run** — the pre-create step in the proposal § User Setup Steps was not required.

**Operational confirmation** that the Dependabot config is correct, the 8-step quality gate is the contract, and the change is end-to-end functional. The auto-merge activation is a 1-line USER setup step, not a defect.

---

## 10. Cross-References

| Kind | URL / Path |
|---|---|
| GitHub PR | https://github.com/xmiquel/98-tstlocal/pull/8 |
| GitHub CI run (PR) | https://github.com/xmiquel/98-tstlocal/actions/runs/27032809386 |
| GitHub CI run (Dependabot actions) | https://github.com/xmiquel/98-tstlocal/actions/runs/27032897589 |
| GitHub CI run (Dependabot python-deps) | https://github.com/xmiquel/98-tstlocal/actions/runs/27032942001 |
| GitHub Issue | https://github.com/xmiquel/98-tstlocal/issues/7 |
| Dependabot PR (actions) | https://github.com/xmiquel/98-tstlocal/pull/9 |
| Dependabot PR (python-deps) | https://github.com/xmiquel/98-tstlocal/pull/10 |
| Canonical spec (merged) | `openspec/specs/python-toolchain/spec.md` (2848 words, 314 lines) |
| Archived delta spec | `openspec/changes/archive/dev-tooling/specs/python-toolchain/spec.md` |
| Apply evidence (Engram) | `#28` — `sdd/dev-tooling/apply-progress` |
| Verify evidence (Engram) | `#29` — `sdd/dev-tooling/verify-report` |
| Proposal (Engram) | `#25` — `sdd/dev-tooling/proposal` |
| Spec (Engram) | `#26` — `sdd/dev-tooling/spec` |
| Tasks (Engram) | `#27` — `sdd/dev-tooling/tasks` |
| Previous archive report (Engram) | `#24` — `sdd/ci-quality-gate/archive-report` |
| First archive report (Engram) | `#12` — `sdd/bootstrap-toolchain/archive-report` |
| Merge commit on main | `7ccd19fbf3868630a0b7172bbfb0197190c9c12c` |

---

**Report generated**: 2026-06-05
**Archiver session**: `sdd-98-tstlocal-dev-tooling-2026-06-05`
**Project**: 98-tstlocal
**Change**: dev-tooling
**SDD cycle status**: **CLOSED** — planned, applied, verified, and archived
