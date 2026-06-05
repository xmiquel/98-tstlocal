# Archive Report — ci-quality-gate

**Change**: `ci-quality-gate`
**Branch**: `main`
**Merge commit SHA**: `36a0b8540c49bc18328f65c26b84417af34467b8`
**Merge base**: `e20b982` (bootstrap-toolchain HEAD)
**Dates**: proposed 2026-06-05 · verified 2026-06-05 · archived 2026-06-05
**Session**: `sdd-98-tstlocal-ci-quality-gate-2026-06-05`
**Project**: 98-tstlocal
**Archive folder**: `openspec/changes/archive/ci-quality-gate/`
**Spec merged into**: `openspec/specs/python-toolchain/spec.md`

---

## 1. Executive Summary

The `ci-quality-gate` change shipped one new file (`.github/workflows/ci.yml`, 72 lines) and modified zero source files. The squash-merge is on `main` at `36a0b85` (PR #4 MERGED, issue #3 CLOSED). The binding CI run on the PR branch (run #27024240896, `windows-latest`, 32s) was GREEN with all 8 user-defined steps exiting 0, and the spec's 13 scenarios are fully covered (8/13 by positive-path runtime tests, 5/13 by mechanism verification — acceptable for a structural config change). The delta spec was merged into the canonical `python-toolchain` spec with full-replacement of 3 MODIFIED requirements and append of 2 ADDED requirements, growing the canonical from 630 to 1240 words. Final verdict was `WARN` (0 CRITICAL, 2 WARNING, 7 SUGGESTION) and the change is archived with warnings; the 2 WARNINGs are environmental (branch protection initially unavailable on Free plan, Node 20 deprecation on the actions) and the 7 SUGGESTIONs are deferred to the future `dev-tooling` change.

## 2. Final State

| Item | Value |
|---|---|
| Files in commit | 1 (`.github/workflows/ci.yml`, +72/-0) |
| Source files modified | 0 |
| `pyproject.toml` / `uv.lock` touched | No |
| Squash commit on `main` | `36a0b8540c49bc18328f65c26b84417af34467b8` |
| PR | https://github.com/xmiquel/98-tstlocal/pull/4 — MERGED, base `main`, head `chore/ci-quality-gate`, label `type:chore` |
| Issue | https://github.com/xmiquel/98-tstlocal/issues/3 — CLOSED, label `status:approved` |
| CI run (binding) | https://github.com/xmiquel/98-tstlocal/actions/runs/27024240896 — `success`, 32s, 8/8 user-defined steps exit 0 |
| CI run (post-merge) | https://github.com/xmiquel/98-tstlocal/actions/runs/27024303652 — `success`, 38s |
| Branch protection | Configured on `main`, required check `Quality Gate` (strict: true, enforce_admins: true) — see WARNING #1 for the visibility prerequisite |
| Working tree | Clean of source changes at archive time; only the change folder (now archived) was untracked |
| Local re-run of CI commands | All 6 exit 0 (pytest, ruff check, ruff format --check, mypy, uv lock --check, uv sync --frozen) |

## 3. Spec Merge Summary

Delta spec at `openspec/changes/archive/ci-quality-gate/specs/python-toolchain/spec.md` declared 3 MODIFIED + 2 ADDED Requirements on the `python-toolchain` capability. Merge was a surgical full-replacement per the OpenSpec MODIFIED convention.

| Domain | Capability | Action | Details |
|---|---|---|---|
| `python-toolchain` | `python-toolchain` | **Updated** | 3 MODIFIED (full-replacement), 2 ADDED (appended), 0 REMOVED, 0 RENAMED |

### Word counts

| Artifact | Words | Lines | Δ vs. canonical |
|---|---|---|---|
| Canonical spec (before merge) | 630 | 87 | — |
| Delta spec (source) | 1024 | 114 | — |
| Canonical spec (after merge) | 1240 | 158 | +610 words, +71 lines |

### Requirements changed

| # | Requirement | Action | In canonical section | New scenario count |
|---|---|---|---|---|
| 1 | Toolchain Pinning and Lockfile | **REPLACED** (MODIFIED) | `## ADDED Requirements` | 2 → 3 (added "Lockfile drift fails CI on a PR") |
| 2 | Code Quality (Lint, Format, Type Check) | **REPLACED** (MODIFIED) | `## ADDED Requirements` | 1 → 2 (added "Lint error fails CI on a PR") |
| 3 | Test Runner and Coverage Gate | **REPLACED** (MODIFIED) | `## MODIFIED Requirements` | 1 → 2 (added "Coverage below 80% fails CI on a PR"); historical `> 2026-06-05 — MODIFIED:` note dropped (it was a meta-commentary from the bootstrap-toolchain change, not part of the requirement) |
| 4 | Continuous Integration Workflow | **APPENDED** (ADDED) | `## ADDED Requirements` | new, 5 scenarios |
| 5 | Out of Scope — Branch Protection Rules | **APPENDED** (ADDED) | `## ADDED Requirements` | new, 1 scenario |
| — | OpenSpec Strict TDD Mode | UNCHANGED | `## ADDED Requirements` | preserved as-is |
| — | GGA Python Mode | UNCHANGED | `## ADDED Requirements` | preserved as-is |
| — | Repository Hygiene | UNCHANGED | `## ADDED Requirements` | preserved as-is |

### Normalization notes

- **Heading levels**: canonical uses `##` for top-level sections and `### Requirement: <name>` / `#### Scenario: <name>` for content; delta uses the same hierarchy. **No normalization needed.**
- **Scenario body style**: delta uses `- GIVEN ...` / `- WHEN ...` / `- THEN ...` on consecutive lines with no blank lines. Canonical uses the same bullets but with blank lines between them. Normalized the MODIFIED/replaced blocks to canonical's style for consistency; the append (ADDED) blocks are kept in delta's style because they sit at the end of the file and matching the rest of the file is the higher-priority concern. (Both styles parse identically as Markdown and are visually equivalent after a soft wrap.)
- **`> Satisfies: ...` lines**: not present in either file. No action needed.
- **`(Previously: ...)` notes**: preserved in the merged file because they are part of the delta's MODIFIED body and document what changed in this cycle. They are the change-of-record marker for the `python-toolchain` capability's transition from local to CI-enforced.
- **Historical `> 2026-06-05 — MODIFIED:` line in canonical's Test Runner requirement**: this was a meta-commentary from the bootstrap-toolchain change recording that `app/__init__.py` was added. It is **not part of the requirement statement** and is dropped from the merged canonical because the MODIFIED convention says the delta contains the entire updated requirement. The history of that note is preserved in the archived bootstrap-toolchain spec.
- **Sections preserved unchanged**: `## Purpose` (with a small additive sentence about CI enforcement), `## Out of Scope (Non-Requirements)`.

### Sections not added to canonical

- `## REMOVED Requirements` — delta declares None.
- `## RENAMED Requirements` — delta declares None.
- A consolidated "dev-tooling follow-ups" section — the 7 SUGGESTIONs are tracked in the bootstrap-toolchain verify-report and will be planned in a future `dev-tooling` change's proposal, not in the canonical spec.

## 4. Artifacts Preserved

The archive folder contains **5 files** (4 from the change + 1 archive report). All files match the `openspec-convention.md` archive structure.

| File | Purpose | Source |
|---|---|---|
| `proposal.md` | Change proposal (intent, scope, approach, risks, rollback) | sdd-propose |
| `tasks.md` | 12/12 implementation tasks complete + 5/5 verification tasks complete | sdd-tasks, sdd-apply, sdd-verify |
| `specs/python-toolchain/spec.md` | Delta spec that drove the canonical merge | sdd-spec |
| `verify-report.md` | Full verify report (33 checks, 13/13 scenarios compliant) | sdd-verify |
| `archive-report.md` | This file | sdd-archive |

### Archive folder note

Per user instruction and the precedent set by the previous `bootstrap-toolchain` archive (which also has no date prefix), the archive folder name is `archive/ci-quality-gate/` (no `YYYY-MM-DD-` prefix). This is a **deviation from the OpenSpec convention** (`archive/YYYY-MM-DD-{change-name}/`). The deviation is acceptable because (a) the previous archive established the pattern on this repo, (b) git history of the archive folder already encodes the date, and (c) the user explicitly specified the no-prefix path.

## 5. Engram Observation Lineage

The following Engram observations were created during this SDD cycle and are preserved as historical record (none deleted by archive):

| ID | Title | Purpose |
|---|---|---|
| #19 | `sdd/ci-quality-gate/tasks` | Task breakdown (sdd-tasks output) |
| #20 | `Branch protection configured on main` | USER follow-up resolution (configures branch protection on `main` requiring "Quality Gate" status check) |
| #21 | `sdd/ci-quality-gate/apply-progress` | Apply evidence (branch/commit/PR/CI run URLs, TDD cycle) |
| #22 | `sdd/ci-quality-gate/verify-report` | Verify evidence (33 checks, 13/13 scenarios, full spec compliance matrix) |
| #23 | `architecture/repo-visibility` | Decision: public repo to unlock branch protection on Free plan |
| (this save) | `sdd/ci-quality-gate/archive-report` | This closure record (sdd-archive output) |

## 6. Verdict and Recommendation

**Final verdict**: `WARN` (0 CRITICAL, 2 WARNING, 7 SUGGESTION)
**Recommendation**: `archive-with-warnings` (executed — change is now archived)

The 2 WARNINGs and 7 SUGGESTIONs are triaged below.

## 7. Outstanding Follow-Ups

### WARNINGs (should be triaged at the start of the next change)

1. **Branch protection prerequisite (environmental, resolved)** — `gh api …/branches/main/protection` initially returned HTTP 403 on GitHub Free plan. Resolved by making the repo public on 2026-06-05 (decision #23). Branch protection is now configured on `main` requiring the `Quality Gate` check (observation #20). The follow-up at `preferences/followups/branch-protection-rule` is **CLOSED**. No further action required.
2. **Node.js 20 actions deprecation** — `actions/checkout@v4` and `astral-sh/setup-uv@v3` will be forced to Node 24 on 2026-06-16. Tracked for the `dev-tooling` change (Dependabot config for action versions). **Action**: address in `dev-tooling` change before the forced migration.

### SUGGESTIONs (deferred to the `dev-tooling` change)

These are the 7 SUGGESTIONs from the verify-report. They all live in the future `dev-tooling` change's scope (Dependabot, pre-commit, Makefile, AGENTS.md notes, etc.) and are NOT in scope for `ci-quality-gate` per the proposal's explicit out-of-scope list.

1. Orchestrator's note "workflow has 9 named steps" was inaccurate — the workflow has exactly 8 user-defined steps. Spec is correct; orchestrator rubric needs alignment. (No code/spec change needed.)
2. Add Dependabot config to auto-update `actions/checkout` and `astral-sh/setup-uv` before the Node 24 forced migration.
3. Pin Python to a patch version (e.g., `3.12.4`) once the team is comfortable.
4. Add a status badge to the README showing the Quality Gate status.
5. Add a CODEOWNERS file to formalize review ownership.
6. Add Dependabot for `pyproject.toml` dependencies (pytest, ruff, mypy minor bumps).
7. Consider splitting the workflow into multiple jobs in the future if the runtime becomes a concern (current 32s is fine; sequential is the right call for a single-developer project).

## 8. Cross-References

| Kind | URL / Path |
|---|---|
| GitHub PR | https://github.com/xmiquel/98-tstlocal/pull/4 |
| GitHub CI run (PR) | https://github.com/xmiquel/98-tstlocal/actions/runs/27024240896 |
| GitHub CI run (post-merge) | https://github.com/xmiquel/98-tstlocal/actions/runs/27024303652 |
| GitHub Issue | https://github.com/xmiquel/98-tstlocal/issues/3 |
| Canonical spec | `openspec/specs/python-toolchain/spec.md` |
| Archived delta spec | `openspec/changes/archive/ci-quality-gate/specs/python-toolchain/spec.md` |
| Apply evidence (Engram) | `#21` — `sdd/ci-quality-gate/apply-progress` |
| Verify evidence (Engram) | `#22` — `sdd/ci-quality-gate/verify-report` |
| Branch-protection resolution (Engram) | `#20` — `Branch protection configured on main` |
| Visibility decision (Engram) | `#23` — `architecture/repo-visibility` |
| Previous archive report (Engram) | `#12` — `sdd/bootstrap-toolchain/archive-report` |

---

**Report generated**: 2026-06-05
**Archiver session**: `sdd-98-tstlocal-ci-quality-gate-2026-06-05`
**Project**: 98-tstlocal
**Change**: ci-quality-gate
**SDD cycle status**: **CLOSED** — planned, applied, verified, and archived
