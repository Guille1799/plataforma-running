# Verificación de create_all() en Render

**Fecha:** 2026-01-10  
**Objetivo:** Verificar que Render NO ejecute `create_all()` y use Alembic en producción

---

## Estado Actual

### Código (backend/app/main.py)

El código está correctamente configurado:

```python
if settings.environment == "development":
    # Solo se ejecuta en desarrollo
    models.Base.metadata.create_all(bind=engine)
else:
    # En producción solo usa Alembic
    logger.info("Production mode: Using Alembic migrations for database schema management")
```

**Lógica:** Si `ENVIRONMENT=production`, NO se ejecuta `create_all()`.

---

## Verificación Requerida en Render

### Paso 1: Verificar Variable ENVIRONMENT

1. Ve a: https://dashboard.render.com
2. Selecciona tu servicio backend
3. Ve a: **Environment** (menú lateral)
4. Busca la variable: `ENVIRONMENT`
5. **Debe estar configurada como:** `production`

**Si NO existe o está en otro valor:**
- Agregar/Editar: `ENVIRONMENT` = `production`
- Guardar cambios
- Render reiniciará automáticamente

### Paso 2: Verificar Logs de Render

Después de asegurar que `ENVIRONMENT=production`:

1. Ve a: Render Dashboard → Tu servicio → **Logs**
2. Busca el mensaje al iniciar:
   - ✅ **CORRECTO:** `"Production mode: Using Alembic migrations for database schema management"`
   - ❌ **INCORRECTO:** `"Development mode: Auto-creating database tables if they don't exist"`

**Si ves el mensaje de "Development mode":**
- La variable `ENVIRONMENT` NO está configurada como `production`
- Agregar/Editar la variable según Paso 1

### Paso 3: Verificar Alembic en Render

Verificar que Alembic esté configurado:

**Opción A: Si usas Dockerfile (backend/Dockerfile)**

El Dockerfile actual NO incluye migraciones. Necesitas una de estas opciones:

1. **Actualizar Start Command en Render:**
   - Ve a: Render Dashboard → Tu servicio → **Settings** → **Build & Deploy**
   - Busca: **Start Command**
   - Cambiar a: `alembic upgrade head && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **O actualizar Dockerfile** (alternativa):
   - Modificar `CMD` en `backend/Dockerfile` para incluir migraciones

**Opción B: Si NO usas Dockerfile (Render Build)**

1. Ve a: Render Dashboard → Tu servicio → **Settings** → **Build & Deploy**
2. Busca: **Start Command**
3. **Debe incluir migraciones antes de iniciar:**
   ```bash
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
   
   O si usas gunicorn:
   ```bash
   alembic upgrade head && gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
   ```

**Si NO incluye `alembic upgrade head`:**
- Actualizar el Start Command para incluir las migraciones
- Guardar cambios
- Render reiniciará automáticamente

**NOTA:** Si Render usa Dockerfile, el Start Command en Render puede sobreescribir el CMD del Dockerfile.

---

## Resultado Esperado

Si todo está configurado correctamente:

1. ✅ Variable `ENVIRONMENT=production` configurada en Render
2. ✅ Logs muestran "Production mode: Using Alembic migrations"
3. ✅ Start Command incluye `alembic upgrade head`
4. ✅ NO se ejecuta `create_all()` (verificado en logs)
5. ✅ Base de datos se crea/actualiza usando Alembic migrations

---

## Conclusión

**Código:** ✅ Correcto - Solo ejecuta `create_all()` en desarrollo

**Configuración Render:** ⚠️ Necesita verificación manual:
- Verificar variable `ENVIRONMENT=production`
- Verificar Start Command incluye `alembic upgrade head`
- Verificar logs muestran modo producción

**Acción Requerida:**
- Usuario debe verificar manualmente en Render Dashboard
- Si falta `ENVIRONMENT=production`, agregarla
- Si Start Command no incluye Alembic, actualizarlo

---

**Última actualización:** 2026-01-10
