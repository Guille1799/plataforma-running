# Docker Basics for RunCoach

## Purpose

This guide explains the minimum Docker workflow for local backend services.

## Prerequisites

- Docker Desktop must be installed and running.
- Run commands from PowerShell at the project root.

## Standard startup

```powershell
.\start-dev.ps1
```

What this does:
- Starts Docker services from `docker-compose.dev.yml`
- Waits for backend health endpoint readiness
- Starts frontend locally in a separate terminal

Expected containers:
- `runcoach_db`
- `runcoach_redis`
- `runcoach_backend`
- `runcoach_celery_worker`
- `runcoach_celery_beat`

## Useful Docker commands

```powershell
docker ps
docker logs runcoach_backend
docker logs -f runcoach_backend
docker exec runcoach_backend python -m alembic current
```

## Stop services

```powershell
.\stop-dev.ps1
```

Or:

```powershell
docker-compose -f docker-compose.dev.yml stop
```

## Notes

- `start-dev.ps1` checks Docker availability; it does not launch Docker Desktop for you.
- Migrations are not auto-applied by compose startup; run Alembic manually when required.
- Canonical startup/troubleshooting guide: [`START_SERVERS.md`](START_SERVERS.md).
