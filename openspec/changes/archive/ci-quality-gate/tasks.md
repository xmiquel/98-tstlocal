# Tasks: CI Quality Gate

## Review Workload Forecast

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: stacked-to-main
400-line budget risk: Low

Work unit (single PR): add `.github/workflows/ci.yml`, open PR, CI green on `windows-latest`, squash-merge to `main`. One new file, no source mods.

## Context

`main` at `e20b982` (bootstrap-toolchain); tree clean except untracked `openspec/changes/ci-quality-gate/`. `uv`, `pytest`, `ruff`, `mypy` already in `pyproject.toml`. Issue labeled `status:approved` must exist before the PR (`Closes #N`). **Strict TDD** for this change: RED → GREEN is **post-push** — a spec scenario is RED until the GitHub Actions run on the PR is GREEN on `windows-latest`. Phase 2 is a sanity check, not a substitute. The binding check is the `quality-gate` job's run on the PR branch.

## Phase 1: Create the workflow file

- [x] 1.1 Create `D:\repos_2026\98-tstlocal\.github\workflows\` directory.
- [x] 1.2 Create `D:\repos_2026\98-tstlocal\.github\workflows\ci.yml` with the YAML from the proposal's *Approach* (8 spec-defined steps + setup-uv block).

>_<bubble/> Shell is PowerShell on `windows-latest`; `uv run` handles venv activation. PowerShell `RemoteException` banner noise on `uv` is a terminal artifact, not a real failure — exit codes are reliable. `uv sync --frozen` uses `uv.lock` as-is and pairs with `uv lock --check`. `actions/checkout@v4` and `astral-sh/setup-uv@v3` are pinned to major versions; Dependabot updates deferred to the `dev-tooling` change.

## Phase 2: Local validation (limited)

- [x] 2.1 Parse YAML: `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"`. Fallback: regex-check top-level keys.
- [x] 2.2 Re-read and confirm triggers, runner, permissions, concurrency, and the 8 spec-defined `uv run` invocations match the spec.

>_<bubble/> Confirms syntax and text only — not GitHub Actions semantics.

## Phase 3: Branch, commit, push

- [x] 3.1 Create branch `chore/ci-quality-gate` from `main` at `e20b982`.
- [x] 3.2 Stage ONLY `.github/workflows/ci.yml`; `git status` shows nothing else.
- [x] 3.3 Commit `chore(ci): add GitHub Actions quality gate workflow`; body lists runner, 3 triggers, 8 steps, `Refs: openspec/changes/ci-quality-gate`. No `Co-Authored-By:`.
- [x] 3.4 Push `chore/ci-quality-gate`; confirm.

## Phase 4: PR and CI observation

- [x] 4.1 Create the linked issue with `status:approved`; record number `N`.
- [x] 4.2 `gh pr create` — base `main`, head `chore/ci-quality-gate`, label `type:chore`, body has `Closes #N` and the 8 steps in the Test Plan.
- [x] 4.3 Observe CI run. All 8 spec-defined steps MUST exit 0 on `windows-latest`. Record run URL in `sdd/ci-quality-gate/apply-progress`.
- [x] 4.4 If the run FAILS, STOP. Do NOT merge. Report failing step + output to orchestrator.

## Phase 5: Merge

- [x] 5.1 `gh pr merge --squash --delete-branch` (same pattern as bootstrap-toolchain).
- [x] 5.2 Confirm squash commit on `main`; `chore/ci-quality-gate` deleted.
- [x] 5.3 Re-verify local tree clean and on `main`.

## Phase 6: Follow-up — branch protection (USER, out of scope)

- [x] 6.1 Document follow-up: USER configures repo-settings rule "Require status checks to pass before merging" → must include the `quality-gate` job.
- [x] 6.2 Save Engram observation under topic key `preferences/followups/branch-protection-rule`.

## Verification

V.1 squash commit on `main`. V.2 `.github/workflows/ci.yml` matches the spec. V.3 first CI run GREEN on `windows-latest`; run URL recorded. V.4 branch-protection follow-up in Engram. V.5 branch deleted; tree clean on `main`.
