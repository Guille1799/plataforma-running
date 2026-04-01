# Start Servers

## Quick Start

### All-in-One (Recommended)

```powershell
.\start-dev.ps1
```

This script:
1. Starts backend with Docker (PostgreSQL + Redis + FastAPI)
2. Waits for backend readiness
3. Starts frontend locally with npm

**URLs**
- Backend API docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

### Start Services Separately

**Backend (Docker)**

```powershell
docker-compose -f docker-compose.dev.yml up
```

**Frontend (Local)**

```powershell
npm run dev
```

## Stop Services

```powershell
.\stop-dev.ps1
```

Or manually:

```powershell
# Stop Docker services
docker-compose -f docker-compose.dev.yml stop

# Stop Frontend
Get-Process node | Stop-Process -Force
```

## Database Migrations

Migrations are **not automatically applied** by `docker-compose.dev.yml` startup.
Apply them explicitly when needed.

**Docker mode**

```powershell
docker exec runcoach_backend python -m alembic upgrade head
```

**Local backend mode (without Docker)**

```powershell
cd backend
python -m alembic upgrade head
```

Create a new migration:

```powershell
cd backend
python -m alembic revision --autogenerate -m "Describe your change"
python -m alembic upgrade head
```

Check migration state:

```powershell
cd backend
python -m alembic current
python -m alembic history
```

## Troubleshooting

**Backend does not start**
- Ensure Docker Desktop is running
- Rebuild services: `docker-compose -f docker-compose.dev.yml up --build`

**Migration errors**
- If DB is out of sync: `docker exec runcoach_backend python -m alembic stamp head`
- Restart backend: `docker-compose -f docker-compose.dev.yml restart backend`

**Frontend lock issues**

```powershell
.\clean-frontend.ps1
```

**Port already in use**

```powershell
Get-NetTCPConnection -LocalPort 8000
Get-NetTCPConnection -LocalPort 3000
```
