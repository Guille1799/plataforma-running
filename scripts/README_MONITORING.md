# 🔍 Sistema de Monitoreo - Guía Rápida

## Uso Básico

```powershell
# Monitoreo simple (una vez)
.\scripts\production-monitor.ps1

# Monitoreo continuo (cada 60 segundos)
.\scripts\production-monitor.ps1 -Continuous

# Monitoreo cada 30 segundos
.\scripts\production-monitor.ps1 -Continuous -IntervalSeconds 30
```

## Qué Hace

1. Verifica que el Frontend (Vercel) responda
2. Verifica que el Backend (Render) responda en `/health`
3. Muestra tiempos de respuesta
4. Detecta errores automáticamente
5. Genera reportes en `monitoring-report-*.txt`

## Resultados

- ✅ **healthy**: Servicio operativo
- ❌ **error/timeout/unreachable**: Problema detectado

## Ver Documentación Completa

Ver: `docs/MONITORING_GUIDE.md`
