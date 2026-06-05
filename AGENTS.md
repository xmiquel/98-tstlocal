# AGENTS.md

<!-- Spec: openspec/changes/dev-tooling/specs/python-toolchain/spec.md (AGENTS.md requirement) -->

Project conventions, tooling pointers, and known gotchas for AI agents and developers
working in `98-tstlocal`. For the user-facing readme, see `README.md`.

## Project overview

`98-tstlocal` is a Python project for trading strategy creation, backtesting, and
tracking. The full architecture and roadmap live in `openspec/`. The deployment
target is **Windows** (MetaTrader 5 integration is planned; see
`openspec/changes/` for current work).

**Stack**

- Python 3.12, managed by `uv`
- Linting: `ruff` (E, F, I, B, UP, SIM, S)
- Type checking: `mypy --strict`
- Testing: `pytest` + `pytest-cov` (>= 80% coverage gate)
- CI: GitHub Actions, `windows-latest` runner
- Spec-driven development: OpenSpec, strict TDD mode

## Pointers

- `openspec/specs/` — canonical capability specs
- `openspec/changes/` — active and archived changes
- `openspec/changes/archive/` — historical change records
- `README.md` — user-facing readme
- `Makefile` — quality commands (`make ci` mirrors the CI workflow)
- `.pre-commit-config.yaml` — pre-commit hooks
- `.github/workflows/ci.yml` — CI workflow
- `.github/dependabot.yml` — Dependabot config
- `pyproject.toml` — project config + dependencies

## Conventions

- **Conventional Commits**: `chore(...)`, `feat(...)`, `fix(...)`, `docs(...)`, etc.
  See recent commits on `main` for the types in use.
- **No AI attribution**: never add `Co-Authored-By` trailers or AI mentions to commits.
- **`uv run <tool>`**: never call tools directly; always go through `uv run` so the
  right version is used.
- **Strict TDD**: tests before code; coverage >= 80%; local re-run of `make ci` after
  every commit on a feature branch.
- **Squash-merge**: feature branches are squash-merged to `main`, then deleted.
- **PR labels**: every PR has a `type:*` label and references an issue with the
  `status:approved` label.
- **Branch protection**: `main` requires the "Quality Gate" status check; PRs must
  rebase before merge (strict: true).

## Known gotchas

### PowerShell `RemoteException` noise on `uv`

When running `uv` commands in PowerShell on Windows, you may see `RemoteException`
banners in the output. These are **terminal artifacts, not real failures**. Trust
the exit code; ignore the banner. This is well-known and not actionable.

### `gh` CLI Windows path quirk

GitHub CLI installed via `winget` is not in the default PowerShell `PATH`. Use the
full path:

    & "C:\Users\xmiqu\AppData\Local\Microsoft\WinGet\Packages\GitHub.cli_Microsoft.Winget.Source_8wekyb3d8bbwe\bin\gh.exe" <command>

Or add the winget bin directory to your user `PATH` and restart the shell.

### Pre-commit setup (one-time per clone)

After cloning, run:

    uv run pre-commit install

to install the git hooks. They run automatically on `git commit`. To bypass for
emergencies: `git commit --no-verify` (CI still runs the same checks).

### Dependabot auto-merge (one-time USER setup)

For Dependabot PRs to self-merge on CI green, the repo must have auto-merge
enabled:

    gh repo edit xmiquel/98-tstlocal --enable-auto-merge

This is a one-time setup, not part of the dev-tooling PR. Dependabot will
auto-create a `dependencies` label on its first PR.
