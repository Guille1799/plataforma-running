# Development Quick Start

This file is a short local development reference.  
The main onboarding source is [`README_STARTUP.md`](README_STARTUP.md).

## Recommended flow (Windows + PowerShell)

```powershell
# From project root
.\start-dev.ps1
```

Expected services:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

To stop:

```powershell
.\stop-dev.ps1
```

## Manual flow (for targeted debugging)

Backend (Docker):

```powershell
docker-compose -f docker-compose.dev.yml up
```

Frontend (local):

```powershell
npm run dev
```

## Frontend quality commands

```powershell
npm run lint
npm run typecheck
npm run build
```

## Notes

- This file replaces old instructions that referenced `.bat` scripts, incorrect ports, and machine-specific local paths.
- For detailed troubleshooting, use [`docs/COMO_INICIAR_SERVIDORES.md`](docs/COMO_INICIAR_SERVIDORES.md).
