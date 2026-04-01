# Production Monitoring Guide

## Purpose

Track production availability for:
- Frontend (Vercel)
- Backend API (Render `/health`)

## Quick usage

```powershell
.\scripts\production-monitor.ps1
```

Continuous mode:

```powershell
.\scripts\production-monitor.ps1 -Continuous
```

Custom interval:

```powershell
.\scripts\production-monitor.ps1 -Continuous -IntervalSeconds 30
```

## Workflow integration

GitHub workflow: `.github/workflows/monitor-production.yml`

- Runs on `main` pushes, manual dispatch, and hourly schedule.
- Writes snapshot to `docs/PRODUCTION_STATUS.md`.
- May open/update issues on failures.

## Interpreting states

- `healthy`: service responds as expected
- `timeout-sleeping`: common on free-tier Render warm-up
- `unreachable` / `error`: investigate service or networking

## Best practice

Treat `docs/PRODUCTION_STATUS.md` as point-in-time output.
Use the latest GitHub Actions run as canonical current status.
