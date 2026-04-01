# Quick Start Guide

We simplified startup to run **Docker** (backend stack) and **Next.js** (frontend) with a reliable local flow.

## 1. Start the platform (`start-dev.ps1`)

Run the PowerShell script `start-dev.ps1` from the project root:

```powershell
.\start-dev.ps1
```

This script:
1. Starts Backend, Database, and Redis with Docker.
2. Polls `http://localhost:8000/health` until backend is ready.
3. Opens a new terminal window for Frontend.

**Important URLs:**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/docs

## 2. Stop the platform (`stop-dev.ps1`)

To shut everything down correctly:
1. Close the Frontend terminal window.
2. Run the PowerShell script:

```powershell
.\stop-dev.ps1
```

This stops Docker containers and frees resources.

---

### Troubleshooting

**If backend fails:**
- Make sure Docker Desktop is running.
- Run `docker ps` to verify containers `runcoach_backend`, `runcoach_db`, `runcoach_redis`, `runcoach_celery_worker`, and `runcoach_celery_beat` are up.

**If frontend fails:**
- Ensure port 3000 is not already in use.
- Check frontend terminal logs for build/runtime errors.
