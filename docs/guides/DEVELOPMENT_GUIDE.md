# Development Guide

## Local Setup

Primary startup path:

```powershell
.\start-dev.ps1
```

Alternative manual startup:

```powershell
docker-compose -f docker-compose.dev.yml up
npm run dev
```

## Quality Gates

Frontend:

```powershell
npm run check
```

Backend:

```powershell
cd backend
pytest tests/ -v --tb=short
```

## Recommended Workflow

1. Create focused branch (`feature/...`, `fix/...`, `docs/...`, `chore/...`)
2. Implement one coherent change per PR
3. Run checks locally
4. Open PR with validation notes

## Common Tasks

- API development: add/extend router + service + schema
- Frontend integration: update API client + page/component
- Data changes: prefer Alembic migrations and validate startup path
