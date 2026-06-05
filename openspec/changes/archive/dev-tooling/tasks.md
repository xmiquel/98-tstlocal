# Tasks: Dev-Tooling

## Review Workload Forecast

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: stacked-to-main
400-line budget risk: Low

~250-280 line delta. Single PR: 6 commits in `chore/dev-tooling` branch, squash to `main`. No chained PRs.

## Context

`main` @ `de49bf9`, tree clean. CI is the unchanged 8-step contract. **Strict TDD** binding signal: 6 local quality commands + `uv run pre-commit run --all-files` + per-file structural inspection.

User-confirmed: (1) `make ci` runs **6** local commands (CI-infra skipped); (2) Makefile ships **7 named quality targets** + optional `help`.

Conventions: top-of-file comment, no AI/emojis, `uv run <tool>`, conventional commits.

## 1. Toolchain pinning

> `chore(deps): pin dev dependencies to compatible-release (~=)`

- [x] 1.1 Edit `pyproject.toml` `[dependency-groups] dev`: `pytest`, `pytest-cov`, `ruff`, `mypy` `>=` -> `~=`; add `pre-commit` with `~=`.
- [x] 1.2 Run `uv lock` to regenerate `uv.lock`.
- [x] 1.3 Verify: `uv lock --check`, `uv sync --frozen`, `uv run pytest` exit 0.

## 2. Dependabot

> `chore(ci): add Dependabot config for actions and dependencies`

- [x] 2.1 Create `.github/dependabot.yml`: 2 ecosystems — `github-actions` (track `.github/workflows/ci.yml`) and `uv` for `pyproject.toml` (fallback `pip-compile`). Include `dependencies` label.
- [x] 2.2 Verify: YAML parses; both ecosystems present; no AI attribution, no emojis.

## 3. Pre-commit

> `chore(tooling): add pre-commit hooks for ruff and mypy`

- [x] 3.1 Create `.pre-commit-config.yaml` with exactly 3 hooks: `ruff format`, `ruff check --fix` (`astral-sh/ruff-pre-commit`), `mypy` (local `uv run mypy .`). Top-of-file spec ref.
- [x] 3.2 Verify: YAML parses; `uv run pre-commit --version` exit 0; `uv run pre-commit run --all-files` exit 0.

## 4. Makefile

> `chore(tooling): add Makefile with 7 quality targets`

- [x] 4.1 Create `Makefile` with 7 named quality targets: `test`, `lint`, `format`, `format-check`, `typecheck`, `lock-check`, `ci` — all `uv run`-delegated. `ci` chains 6 local commands matching `.github/workflows/ci.yml` order.
- [x] 4.2 Verify: `make help` lists all targets; `make test`, `make lint`, `make format-check`, `make typecheck`, `make lock-check`, `make ci` all exit 0.

## 5. AGENTS.md (bundles pre-commit install doc)

> `docs(agents): scaffold AGENTS.md with project conventions and known gotchas`

- [x] 5.1 Create `AGENTS.md` with 4 sections: Project overview, Pointers (`openspec/`, `README.md`, `Makefile`, `.pre-commit-config.yaml`), Conventions (Conventional Commits, no AI/emojis, `uv run <tool>`), Known gotchas (PowerShell `RemoteException` on `uv` banner, `gh` CLI Windows path quirk). Top-of-file spec ref.
- [x] 5.2 Add Setup subsection: one-time `uv run pre-commit install`.
- [x] 5.3 Verify: at root; 5-line spec ref; 4 sections; gh quirk in gotchas; install cmd in Setup.

## 6. README.md badge

> `docs(readme): add CI status badge`

- [x] 6.1 Insert GitHub Actions badge as first content line in `README.md` (after H1): `[![CI](.../badge.svg)](.../workflows/ci.yml)`.
- [x] 6.2 Verify: badge markdown in first 5 lines of `README.md`.

## 7. Final verification (NO commit — binding TDD signal)

- [x] 7.1 Run 6 local quality commands + `uv run pre-commit run --all-files`; inspect each new file; confirm `pyproject.toml` shows `~=` for 4 dev-deps + `pre-commit`; confirm `uv.lock` committed.
- [x] 7.2 Verify: all 6 commands exit 0; pre-commit run exit 0; 4 new files at correct paths; 2 modified files show expected diffs only; `uv lock --check` exit 0.

---

## Archive-time reconciliation note (2026-06-05, sdd-archive)

The sdd-apply phase completed all 6 implementation commits on `chore/dev-tooling` (squash-merged to `main` as `7ccd19f` via PR #8) but did not persist task-checkbox state to this file (the on-disk tasks.md kept the original `- [ ]` checkboxes while in-memory todos were all marked done). The apply evidence is preserved in Engram `sdd/dev-tooling/apply-progress` (#28) with 6 commits and 4/4 binding TDD categories PASS; the verify report (#29) confirms 16/16 tasks complete, 28/28 spec scenarios compliant, CI run #27032809386 SUCCESS, and 7 files / +313/-91 on `main` at `7ccd19f`.

This archive phase **mechanically marks all 16 task checkboxes as completed** as an exceptional reconciliation under SKILL.md § Task Completion Gate, with proof anchored in the apply-progress (#28) and verify-report (#29) observations and the squash-merge commit `7ccd19fbf3868630a0b7172bbfb0197190c9c12c` on `main`. The audit trail in this file now matches the work that was actually shipped. No re-apply or re-verify was performed; the reconciliation is purely checkbox state correction based on binding TDD and post-merge evidence.
