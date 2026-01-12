# 🚀 Cómo Iniciar Servidores

## Inicio Rápido

### Todo en Uno (Recomendado)
```powershell
.\start-dev.ps1
```

Este script:
1. Inicia Backend con Docker (PostgreSQL + Redis + FastAPI)
2. Espera a que el backend esté listo
3. Inicia Frontend localmente con npm

**URLs:**
- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:3000

### Por Separado

**Backend (Docker):**
```powershell
docker-compose -f docker-compose.dev.yml up
```

**Frontend (Local):**
```powershell
npm run dev
```

## Detener

```powershell
.\stop-dev.ps1
```

O manualmente:
```powershell
# Detener Docker
docker-compose -f docker-compose.dev.yml stop

# Detener Frontend
Get-Process node | Stop-Process -Force
```

## Migraciones de Base de Datos

Las migraciones de base de datos se ejecutan **automáticamente** al iniciar el backend en Docker.

**En Docker (automático):**
- Las migraciones se ejecutan antes de iniciar el servidor
- No necesitas hacer nada manualmente

**Desarrollo local (sin Docker):**
```powershell
cd backend
python -m alembic upgrade head
```

**Crear nueva migración:**
```powershell
cd backend
python -m alembic revision --autogenerate -m "Descripción del cambio"
python -m alembic upgrade head
```

**Ver estado de migraciones:**
```powershell
cd backend
python -m alembic current    # Estado actual
python -m alembic history   # Historial completo
```

## Troubleshooting

**Backend no inicia:**
- Verifica Docker Desktop está corriendo
- Reconstruye: `docker-compose -f docker-compose.dev.yml up --build`

**Error de migraciones:**
- Si la base de datos está desincronizada: `docker exec runcoach_backend python -m alembic stamp head`
- Luego reinicia: `docker-compose -f docker-compose.dev.yml restart backend`

**Frontend con lock:**
```powershell
.\clean-frontend.ps1
```

**Puerto ocupado:**
```powershell
# Ver qué usa el puerto
Get-NetTCPConnection -LocalPort 8000  # Backend
Get-NetTCPConnection -LocalPort 3000  # Frontend
```
