# 🟢 Estado de Producción - RunCoach AI

**Última actualización:** 2026-06-26 23:25:05 UTC
**Commit:** `3d4aa20`
**Workflow:** [Ver en GitHub Actions](https://github.com/Guille1799/plataforma-running/actions/runs/28270829889)

---

## 📊 Resumen

⚠️ **Algunos servicios tienen problemas** (1/2 operativos)

### Servicios Monitoreados

#### ✅ Frontend (Vercel)

- **URL:** https://plataforma-running.vercel.app
- **Health Check:** https://plataforma-running.vercel.app
- **Estado:** `healthy`
- **Status Code:** `200`
- **Response Time:** `369.41ms`
- **Timestamp:** 2026-06-26T23:24:48.884930

#### ❌ Backend API (Render)

- **URL:** https://plataforma-running.onrender.com
- **Health Check:** https://plataforma-running.onrender.com/health
- **Estado:** `timeout`
- **Error:** `Timeout después de 15 segundos`
- **Timestamp:** 2026-06-26T23:24:49.997357

---

## 📋 Detalles Técnicos

```json
[
  {
    "name": "Frontend (Vercel)",
    "url": "https://plataforma-running.vercel.app",
    "health_endpoint": "https://plataforma-running.vercel.app",
    "status": "healthy",
    "status_code": 200,
    "response_time_ms": 369.41,
    "error": null,
    "timestamp": "2026-06-26T23:24:48.884930",
    "healthy": true
  },
  {
    "name": "Backend API (Render)",
    "url": "https://plataforma-running.onrender.com",
    "health_endpoint": "https://plataforma-running.onrender.com/health",
    "status": "timeout",
    "status_code": null,
    "response_time_ms": null,
    "error": "Timeout después de 15 segundos",
    "timestamp": "2026-06-26T23:24:49.997357",
    "healthy": false
  }
]
```

---

*Este archivo se actualiza automáticamente después de cada push a `main`*
*Para verificar manualmente: `.\scripts\production-monitor.ps1`*
