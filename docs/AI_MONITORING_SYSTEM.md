# 🤖 Sistema de Monitoreo para AI - RunCoach AI

**Última actualización:** 2026-01-10  
**Estado:** ✅ Sistema activo

---

## 🎯 Objetivo

Permitir que el AI asista (Auto) pueda ver automáticamente el estado de producción y detectar errores sin necesidad de que el usuario tenga que compartir logs manualmente.

---

## 🔄 Cómo Funciona

### 1. **Monitoreo Automático**

GitHub Actions ejecuta el workflow `monitor-production.yml`:
- **Automáticamente:** Después de cada push a `main`
- **Programado:** Cada hora (cron: `0 * * * *`)
- **Manual:** Desde GitHub Actions UI

### 2. **Verificación de Servicios**

El workflow verifica:
- ✅ **Frontend (Vercel):** `https://plataforma-running.vercel.app`
- ✅ **Backend (Render):** `https://plataforma-running.onrender.com/health`

### 3. **Generación de Estado**

Después de verificar, genera:
- 📄 **Archivo:** `docs/PRODUCTION_STATUS.md`
- 🐛 **Issue en GitHub** (si hay errores)
- 📊 **Logs en GitHub Actions**

### 4. **Lectura por AI**

Cuando el usuario pregunta sobre producción, el AI:
1. Lee automáticamente `docs/PRODUCTION_STATUS.md`
2. Analiza el estado de cada servicio
3. Detecta errores automáticamente
4. Proporciona un resumen completo del estado

---

## 📋 Formato del Archivo de Estado

El archivo `docs/PRODUCTION_STATUS.md` contiene:

```markdown
# 🟢 Estado de Producción - RunCoach AI

**Última actualización:** 2026-01-10 21:00:00 UTC
**Commit:** `abc1234`
**Workflow:** [Enlace al workflow]

## 📊 Resumen
✅ Todos los servicios están operativos (2/2)

### Servicios Monitoreados

#### ✅ Frontend (Vercel)
- URL: https://plataforma-running.vercel.app
- Estado: healthy
- Status Code: 200
- Response Time: 234ms

#### ✅ Backend API (Render)
- URL: https://plataforma-running.onrender.com
- Health Check: https://plataforma-running.onrender.com/health
- Estado: healthy
- Status Code: 200
- Response Time: 567ms
```

---

## 🔍 Cómo Usar (Para el Usuario)

### Ver Estado Actual

Simplemente pregunta:
```
"¿Cómo va producción?"
"¿Hay errores en producción?"
"Revisa el estado de producción"
```

El AI leerá automáticamente `docs/PRODUCTION_STATUS.md` y te dará un resumen completo.

### Ver Estado Manualmente

Puedes ver el archivo directamente:
- Archivo: `docs/PRODUCTION_STATUS.md`
- Se actualiza automáticamente después de cada push

### Ver en GitHub Actions

- Ve a: https://github.com/Guille1799/plataforma-running/actions
- Busca el workflow "🟢 Monitor Production"
- Revisa los logs de cada ejecución

---

## 🐛 Issues Automáticos

Cuando hay errores, el workflow:

1. **Crea un Issue en GitHub** automáticamente
2. **Incluye detalles completos** del error
3. **Etiqueta como:** `production-issue`, `monitoring`, `bug`
4. **Actualiza el issue** si se detecta el mismo error en ejecuciones posteriores

**Ver Issues de Producción:**
- Ve a: https://github.com/Guille1799/plataforma-running/issues
- Filtra por label: `production-issue`

---

## ⚙️ Configuración

### URLs Monitoreadas

Configuradas en `.github/workflows/monitor-production.yml`:

```yaml
services = [
    {
        "name": "Frontend (Vercel)",
        "url": "https://plataforma-running.vercel.app",
        "health_endpoint": "https://plataforma-running.vercel.app"
    },
    {
        "name": "Backend API (Render)",
        "url": "https://plataforma-running.onrender.com",
        "health_endpoint": "https://plataforma-running.onrender.com/health"
    }
]
```

Para cambiar las URLs, edita estas variables en el workflow.

### Frecuencia de Monitoreo

- **Después de push:** Automático (cada vez que haces push)
- **Programado:** Cada hora (`cron: '0 * * * *'`)
- **Manual:** Desde GitHub Actions UI

Para cambiar la frecuencia, edita el `schedule` en el workflow:

```yaml
schedule:
  # Cada 30 minutos
  - cron: '*/30 * * * *'
  
  # Cada 6 horas
  - cron: '0 */6 * * *'
  
  # Cada día a medianoche
  - cron: '0 0 * * *'
```

---

## 💰 Costo

- ✅ **Completamente gratis**
- Usa los 2000 minutos/mes gratuitos de GitHub Actions
- Cada ejecución usa aproximadamente 1-2 minutos
- Puedes ejecutarlo ~1000-2000 veces/mes sin costo

---

## 🔐 Permisos

El workflow necesita:

- ✅ `contents: write` - Para actualizar `docs/PRODUCTION_STATUS.md`
- ✅ `issues: write` - Para crear issues cuando hay errores
- ✅ `actions: read` - Para ver logs (por defecto)

Estos permisos están configurados en el workflow.

---

## 📊 Ejemplo de Uso

### Pregunta del Usuario:
```
"¿Cómo va producción?"
```

### Respuesta del AI:
1. Lee automáticamente `docs/PRODUCTION_STATUS.md`
2. Analiza el estado
3. Responde:
   ```
   Estado de Producción (última actualización: 2026-01-10 21:00:00):
   
   ✅ Frontend (Vercel): Operativo
      - Status: 200 OK
      - Response Time: 234ms
      - URL: https://plataforma-running.vercel.app
   
   ✅ Backend API (Render): Operativo
      - Status: 200 OK
      - Response Time: 567ms
      - URL: https://plataforma-running.onrender.com
   
   Resumen: Todos los servicios están operativos (2/2) ✅
   ```

### Si hay errores:
```
Estado de Producción (última actualización: 2026-01-10 21:00:00):
   
   ✅ Frontend (Vercel): Operativo
      - Status: 200 OK
      - Response Time: 234ms
   
   ❌ Backend API (Render): Error
      - Status: HTTP 500 - Server Error
      - Error: Connection timeout
      - Última verificación: 2026-01-10 21:00:00
   
   ⚠️ Problema detectado: El backend no está respondiendo correctamente.
   Ver detalles en: docs/PRODUCTION_STATUS.md
   ```

---

## 🚀 Próximos Pasos

1. **Hacer push** del workflow para activarlo
2. **Verificar** que se ejecuta correctamente en GitHub Actions
3. **Preguntar al AI:** "¿Cómo va producción?" para probar

---

**Última actualización:** 2026-01-10  
**Mantenido por:** Sistema de Monitoreo RunCoach AI
