# GitHub Workflows

This directory contains CI and monitoring workflows for RunCoach AI.

## `tests.yml` (Quality checks)

Runs on push/PR to `main` and `develop` (with path filters).

Jobs:
- **backend-tests**: Python 3.11, install test dependencies, run `pytest`.
- **frontend-quality**: Node 20, run `npm ci`, `npm run lint`, `npm run typecheck`, and `npm run build`.

## `monitor-production.yml` (Production monitoring)

Runs on:
- Push to `main`
- Manual workflow dispatch
- Hourly cron schedule

Behavior:
- Checks frontend (Vercel) and backend (Render `/health`).
- Writes `docs/PRODUCTION_STATUS.md`.
- On scheduled runs, commits updated status.
- Can open/update GitHub issues when failures are detected.

View runs:
- [GitHub Actions](https://github.com/Guille1799/plataforma-running/actions)
