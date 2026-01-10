# 🔍 Guía de Monitoreo de Producción - RunCoach AI

**Última actualización:** 2026-01-10  
**Estado:** ✅ Sistema activo

---

## 📋 Resumen

Sistema de monitoreo robusto para verificar el estado de los servicios en producción (Vercel y Render) y detectar errores automáticamente.

---

## 🚀 Uso Rápido

### Monitoreo Simple (Una vez)
```powershell
.\scripts\production-monitor.ps1
```

### Monitoreo Continuo (Cada 60 segundos)
```powershell
.\scripts\production-monitor.ps1 -Continuous
```

### Monitoreo Continuo con Intervalo Personalizado
```powershell
.\scripts\production-monitor.ps1 -Continuous -IntervalSeconds 30
```

---

## 📊 Qué Monitorea

### Servicios Verificados

1. **Frontend (Vercel)**
   - URL: `https://plataforma-running.vercel.app`
   - Health Check: Verifica que la página responda correctamente
   - Métricas: Status Code, Response Time

2. **Backend API (Render)**
   - URL: `https://plataforma-running.onrender.com`
   - Health Check: `https://plataforma-running.onrender.com/health`
   - Métricas: Status Code, Response Time, JSON Response

---

## 📈 Estados del Servicio

| Estado | Significado | Acción |
|--------|-------------|--------|
| ✅ **healthy** | Servicio operativo | Ninguna |
| ⚠️ **redirecting** | Redirección (301/302) | Verificar configuración |
| ⚠️ **warning** | Respuesta inesperada (4xx) | Revisar logs |
| ❌ **unavailable** | Servicio no disponible (503) | Verificar deployment |
| ❌ **error** | Error del servidor (5xx) | Revisar logs de Render/Vercel |
| ❌ **timeout** | Timeout después de 15s | Verificar rendimiento |
| ❌ **unreachable** | No se puede conectar | Verificar URL y DNS |

---

## 📄 Reportes

Cada ejecución genera un reporte en:
```
monitoring-report-YYYYMMDD-HHMMSS.txt
```

**Contenido del reporte:**
- Estado de cada servicio
- Códigos de respuesta HTTP
- Tiempos de respuesta
- Errores detectados
- Timestamp de cada verificación

---

## 🔧 Configuración

### URLs de Producción

Las URLs están configuradas en `scripts/production-monitor.ps1`:

```powershell
$FRONTEND_URL = "https://plataforma-running.vercel.app"
$BACKEND_URL = "https://plataforma-running.onrender.com"
```

Para cambiar las URLs, edita estas variables en el script.

---

## 🎯 Casos de Uso

### 1. Verificación Rápida Después de un Deploy
```powershell
.\scripts\production-monitor.ps1
```

### 2. Monitoreo Durante Desarrollo
```powershell
# Monitoreo cada 30 segundos mientras trabajas
.\scripts\production-monitor.ps1 -Continuous -IntervalSeconds 30
```

### 3. Verificación Antes de Ir a Producción
```powershell
# Verificar que todo esté operativo
.\scripts\production-monitor.ps1
# Si todo está OK (exit code 0), proceder con deploy
```

### 4. Debugging de Problemas
```powershell
# Ejecutar monitoreo y revisar el reporte generado
.\scripts\production-monitor.ps1
# Revisar: monitoring-report-*.txt
```

---

## 🔍 Interpretación de Resultados

### ✅ Todo Operativo
```
✅ Todos los servicios están operativos (2/2)
```
**Significado:** Frontend y Backend responden correctamente.

### ⚠️ Problemas Detectados
```
⚠️  Algunos servicios tienen problemas (1/2 operativos)
  - Backend API Render: error
    Error: HTTP 500 - Internal Server Error
```
**Significado:** El backend tiene un error. Revisar logs en Render.

### ❌ Servicio Inaccesible
```
⚠️  Algunos servicios tienen problemas (1/2 operativos)
  - Backend API Render: unreachable
    Error: No se pudo conectar al servidor
```
**Significado:** El servicio no está disponible o la URL es incorrecta.

---

## 🚨 Troubleshooting

### Error: "No se pudo conectar al servidor"

**Posibles causas:**
1. El servicio está caído en Render/Vercel
2. La URL está incorrecta
3. Problemas de red/DNS

**Solución:**
1. Verificar en dashboard de Render/Vercel que el servicio esté activo
2. Verificar que la URL en el script sea correcta
3. Intentar acceder manualmente a la URL en el navegador

### Error: "Timeout después de 15 segundos"

**Posibles causas:**
1. El servicio está muy lento (cold start en Render)
2. Problemas de rendimiento

**Solución:**
1. Esperar unos segundos y volver a intentar
2. Verificar logs en Render para ver si hay errores
3. Considerar aumentar el timeout en el script (línea con `-TimeoutSec 15`)

### Error: "HTTP 500 - Internal Server Error"

**Posibles causas:**
1. Error en el código del backend
2. Problema con la base de datos
3. Variable de entorno faltante

**Solución:**
1. Revisar logs en Render dashboard
2. Verificar variables de entorno en Render
3. Verificar conexión a la base de datos

---

## 📝 Integración con CI/CD

### Ejemplo: Verificar antes de deploy
```powershell
# En tu pipeline de CI/CD
.\scripts\production-monitor.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Servicios no operativos. Abortando deploy."
    exit 1
}
Write-Host "✅ Servicios operativos. Continuando con deploy."
```

---

## 🔐 Seguridad

- ✅ No expone secrets ni credenciales
- ✅ Solo hace health checks públicos
- ✅ No requiere autenticación
- ✅ Los reportes se guardan localmente (no se suben a Git)

---

## 📚 Scripts Relacionados

- `scripts/monitor-deployments.ps1` - Script básico de monitoreo
- `scripts/monitor-deployments.py` - Versión Python (alternativa)

---

## 🆘 Soporte

Si encuentras problemas con el monitoreo:

1. Verificar que PowerShell esté actualizado
2. Verificar que tengas acceso a internet
3. Revisar los reportes generados para más detalles
4. Verificar manualmente las URLs en el navegador

---

**Última actualización:** 2026-01-10  
**Mantenido por:** Sistema de Monitoreo RunCoach AI
