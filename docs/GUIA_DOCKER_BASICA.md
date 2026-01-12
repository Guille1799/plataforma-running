# 🐳 Guía Básica de Docker para RunCoach

## ¿Qué es Docker?

**Nivel Técnico:** Docker es un sistema de contenedores que empaqueta aplicaciones con todas sus dependencias en un entorno aislado y reproducible.

**Nivel Simple:** Es como una "caja mágica" que contiene todo lo que necesita tu aplicación (Python, librerías, configuración) para funcionar, sin importar en qué computadora esté.

## Requisitos Previos

### 1. Docker Desktop debe estar ABIERTO y CORRIENDO

- **¿Cómo saber si está corriendo?**
  - Busca el ícono de Docker en la barra de tareas (esquina inferior derecha)
  - Si no lo ves, abre Docker Desktop desde el menú de inicio
  - Espera a que diga "Docker Desktop is running"

- **¿Por qué es necesario?**
  - Docker Desktop es el "motor" que ejecuta los contenedores
  - Sin él, los comandos `docker` no funcionan

## Dónde Ejecutar Comandos

### ✅ CORRECTO: PowerShell (tu terminal de Windows)

```powershell
# Ejecutas estos comandos en PowerShell
docker ps
docker exec runcoach_backend python -m alembic current
```

### ❌ INCORRECTO: Dentro de Docker

No ejecutas comandos "dentro" de Docker. Docker es una herramienta que usas DESDE PowerShell.

## Flujo Básico de Trabajo

### 1. Iniciar Todo (Backend + Frontend)

```powershell
# En PowerShell, desde la raíz del proyecto
.\start-dev.ps1
```

**¿Qué hace este script?**
- Abre Docker Desktop (si no está abierto)
- Inicia los contenedores (PostgreSQL, Redis, Backend, Celery)
- Espera a que estén listos
- Inicia el frontend en una nueva ventana

**¿Dónde ves los logs?**
- En la MISMA ventana de PowerShell donde ejecutaste el comando
- Verás líneas como: `INFO: Application startup complete`

### 2. Verificar que Todo Está Corriendo

```powershell
# Ver todos los contenedores corriendo
docker ps
```

**Deberías ver:**
- `runcoach_db` (PostgreSQL)
- `runcoach_redis` (Redis)
- `runcoach_backend` (FastAPI)
- `runcoach_celery_worker` (Celery Worker)
- `runcoach_celery_beat` (Celery Beat)

### 3. Ejecutar Comandos Dentro del Contenedor

```powershell
# Ejecutar un comando dentro del contenedor backend
docker exec runcoach_backend python -m alembic current

# Ver logs del backend
docker logs runcoach_backend

# Ver logs en tiempo real
docker logs -f runcoach_backend
```

### 4. Detener Todo

```powershell
.\stop-dev.ps1
```

O manualmente:
```powershell
docker-compose -f docker-compose.dev.yml stop
```

## Comandos Docker Útiles

### Ver contenedores corriendo
```powershell
docker ps
```

### Ver TODOS los contenedores (incluyendo detenidos)
```powershell
docker ps -a
```

### Ver logs de un contenedor
```powershell
docker logs runcoach_backend
```

### Ejecutar comando dentro de un contenedor
```powershell
docker exec runcoach_backend <comando>
```

### Reiniciar un contenedor
```powershell
docker restart runcoach_backend
```

### Ver qué está pasando en tiempo real
```powershell
docker-compose -f docker-compose.dev.yml logs -f
```

## Solución de Problemas

### Error: "container is not running"

**Causa:** El contenedor está detenido o no existe.

**Solución:**
```powershell
# Iniciar todo de nuevo
.\start-dev.ps1

# O solo el backend
docker-compose -f docker-compose.dev.yml up backend -d
```

### Error: "Cannot connect to Docker daemon"

**Causa:** Docker Desktop no está corriendo.

**Solución:**
1. Abre Docker Desktop
2. Espera a que diga "Docker Desktop is running"
3. Vuelve a intentar el comando

### No veo el contenedor `runcoach_backend`

**Causa:** El backend no se inició correctamente.

**Solución:**
```powershell
# Ver todos los contenedores (incluyendo detenidos)
docker ps -a

# Si está detenido, iniciarlo
docker start runcoach_backend

# Si no existe, reconstruir
docker-compose -f docker-compose.dev.yml up --build backend
```

## Diagrama del Flujo

```
┌─────────────────────────────────┐
│  1. Abres Docker Desktop        │
│     (ícono en barra de tareas)   │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  2. Abres PowerShell            │
│     (terminal de Windows)        │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  3. Ejecutas: .\start-dev.ps1   │
│     (en PowerShell)              │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  4. Docker crea contenedores:   │
│     - runcoach_db               │
│     - runcoach_redis            │
│     - runcoach_backend          │
│     - runcoach_celery_*         │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  5. Ejecutas comandos:          │
│     docker exec runcoach_...    │
│     (en PowerShell)             │
└─────────────────────────────────┘
```

## Resumen Rápido

1. **Docker Desktop debe estar abierto** (ícono en barra de tareas)
2. **Ejecutas comandos en PowerShell** (tu terminal normal)
3. **Los logs aparecen en PowerShell** (donde ejecutaste el comando)
4. **Para iniciar:** `.\start-dev.ps1`
5. **Para detener:** `.\stop-dev.ps1`
