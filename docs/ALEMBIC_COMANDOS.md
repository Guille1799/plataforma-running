# 🔧 Comandos Alembic - Guía Rápida

## Ejecutar Alembic en Docker (Recomendado)

### Cuando el contenedor está corriendo:

```powershell
# Ver estado actual de migraciones
docker exec runcoach_backend python -m alembic current

# Marcar todas las migraciones como aplicadas (sin ejecutar SQL)
docker exec runcoach_backend python -m alembic stamp head

# Aplicar migraciones pendientes
docker exec runcoach_backend python -m alembic upgrade head

# Ver historial de migraciones
docker exec runcoach_backend python -m alembic history

# Crear nueva migración
docker exec -w /app runcoach_backend python -m alembic revision --autogenerate -m "Descripción del cambio"
```

## Ejecutar Alembic Localmente (Sin Docker)

### Requisitos:
1. Tener Python 3.11 instalado
2. Instalar dependencias: `cd backend && pip install -r requirements.txt`
3. Configurar `DATABASE_URL` en variables de entorno

### Comandos:

```powershell
# Cambiar al directorio backend
cd backend

# Ver estado actual
python -m alembic current

# Marcar como aplicadas
python -m alembic stamp head

# Aplicar migraciones
python -m alembic upgrade head
```

## ⚠️ Situación Actual

Tu base de datos ya tiene los cambios aplicados manualmente:
- ✅ Columna `role` en tabla `users` (migración 003)
- ✅ Tabla `events` (migración 004)

**Acción necesaria:** Ejecutar `alembic stamp head` para sincronizar el estado.

## Pasos Recomendados

1. **Iniciar Docker:**
   ```powershell
   .\start-dev.ps1
   ```

2. **Esperar a que el backend esté listo** (verás logs en la consola)

3. **Ejecutar stamp head:**
   ```powershell
   docker exec runcoach_backend python -m alembic stamp head
   ```

4. **Verificar que funcionó:**
   ```powershell
   docker exec runcoach_backend python -m alembic current
   ```
   
   Deberías ver algo como: `004_create_events (head)`
