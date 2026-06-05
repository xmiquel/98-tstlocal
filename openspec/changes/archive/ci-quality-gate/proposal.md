# Proposal: CI Quality Gate

## Intent

Make the bootstrap-toolchain quality contract **real** by enforcing it on every PR. Without CI, the 80% coverage gate, ruff, mypy, and `uv lock --check` are *suggestions* a maintainer can bypass. This is **SUGGESTION #1** from the bootstrap-toolchain verify-report — the first of six items split off into a dedicated `dev-tooling` change (this proposal covers only the CI piece).

## Scope

### In Scope
- New file: `.github/workflows/ci.yml` — single `quality-gate` job, sequential steps
- No modifications to existing files (pure addition)
- Workflow must call: `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy .`, `uv lock --check`

### Out of Scope
- **Branch protection rules** — GitHub repo-settings change, NOT a code change; tracked as follow-up
- Dependabot config, pre-commit hooks, version pinning, `Makefile`/taskfile, `AGENTS.md` note on PowerShell `RemoteException` (SUGGESTIONS 2-6 from verify-report) → land together in a separate `dev-tooling` change
- MT5-specific CI (deferred until MT5 lands in a future change)
- Release / deployment workflows, container images, deploy manifests

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `python-toolchain`: add a CI enforcement clause — "The 80% coverage gate SHALL be enforced on every pull request via GitHub Actions; the workflow SHALL fail if `pytest --cov=app --cov-fail-under=80` reports a coverage failure."

## Approach

Single `quality-gate` job on `windows-latest`, Python 3.12 only (no matrix). Sequential steps:

1. `actions/checkout@v4`
2. `astral-sh/setup-uv@v3` (with built-in uv cache)
3. `uv sync`
4. `uv run ruff check .`
5. `uv run ruff format --check .`
6. `uv run mypy .`
7. `uv run pytest` — gate enforced via `--cov-fail-under=80` from `pyproject.toml`
8. `uv lock --check`

**Shell**: `pwsh` (PowerShell 7) — explicit choice over `powershell` 5.1; documented in workflow comment.
**Triggers**: `push` to `main`, `pull_request` to `main`, `workflow_dispatch`.
**Permissions**: `contents: read` (minimal).
**Concurrency**: `group: ${{ github.workflow }}-${{ github.ref }}`, `cancel-in-progress: true`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `.github/workflows/ci.yml` | New | Single `quality-gate` job on `windows-latest` |
| `openspec/specs/python-toolchain/spec.md` | MODIFIED (delta) | Add CI enforcement requirement |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Windows runners ~2-3× slower + costlier than Linux | Med | Intentional tradeoff for MT5 alignment; document in workflow comment |
| PowerShell `RemoteException` banner noise on `uv` commands | High | Terminal artifact only; exit codes are reliable; document in workflow comment |
| `astral-sh/setup-uv@v3` caching requires recent action version | Low | Pin to `@v3` (or specific `@vX.Y.Z`) |
| `uv lock --check` fails on lockfile drift | Med | Intentional — catches drift the spec already requires |
| First CI run slow (no cache) | Med | Expected; subsequent runs are fast |
| No branch protection yet — fail-merge isn't enforced | Med | Residual risk; flag as follow-up repo-settings step |

## Alternatives Considered

- `ubuntu-latest` runner → **rejected** (MT5 is Windows-only)
- Multi-version Python matrix (3.11/3.12/3.13) → **rejected** as premature
- Multiple parallel jobs (lint / type-check / test / lockfile) → **rejected** as over-engineering for a single-developer project
- Custom `actions/cache` for uv → **rejected** in favor of `astral-sh/setup-uv@v3` built-in caching
- Dependabot combined with this change → **rejected**; out of scope, separate `dev-tooling` change

## Rollback Plan

Single `git revert` of the change commit. `.github/workflows/ci.yml` is the only file; bootstrap-toolchain artifacts are unaffected. If the workflow misbehaves mid-merge, disable via the GitHub UI (Actions tab → workflow → Disable) before reverting.

## Dependencies

- `astral-sh/setup-uv@v3` (third-party Action)
- `actions/checkout@v4` (GitHub official)
- All commands rely on `uv`, `pytest`, `ruff`, `mypy` already declared in `pyproject.toml` dev-deps (landed in bootstrap-toolchain)

## Success Criteria

- [ ] Workflow file exists at `.github/workflows/ci.yml`
- [ ] On PR to `main` from a clean branch: workflow runs and all 7 verification steps exit 0
- [ ] Deliberately broken PR (e.g. `assert False` in smoke test) → workflow fails on `pytest` with non-zero exit
- [ ] Push to non-`main` branch → workflow does NOT trigger
- [ ] `workflow_dispatch` from the Actions tab → workflow runs and succeeds
- [ ] Local re-run of the 7 commands reproduces the same exit codes as the CI run

## Test & Verification Plan (for the spec phase)

1. Push the workflow file to a test branch; open a PR to `main`.
2. Observe the workflow run on `windows-latest`; confirm all 7 steps exit 0.
3. Add `assert False` to `tests/test_smoke.py`; push; confirm the `pytest` step fails; revert.
4. Push a commit to a feature branch (no PR); confirm the workflow does NOT trigger.
5. From the Actions tab, run via `workflow_dispatch`; confirm it succeeds.
6. Locally, run the 7 commands in sequence; confirm exit codes match the CI run.
