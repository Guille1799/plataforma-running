# 🟢 Estado de Producción - RunCoach AI

**Última actualización:** 2026-05-08 09:31:55 UTC
**Commit:** `16f26aa`
**Workflow:** [Ver en GitHub Actions](https://github.com/Guille1799/plataforma-running/actions/runs/25548191772)

---

## 📊 Resumen

⚠️ **Algunos servicios tienen problemas** (1/2 operativos)

### Servicios Monitoreados

#### ✅ Frontend (Vercel)

- **URL:** https://plataforma-running.vercel.app
- **Health Check:** https://plataforma-running.vercel.app
- **Estado:** `healthy`
- **Status Code:** `200`
- **Response Time:** `225.53ms`
- **Timestamp:** 2026-05-08T09:31:39.600251

#### ❌ Backend API (Render)

- **URL:** https://plataforma-running.onrender.com
- **Health Check:** https://plataforma-running.onrender.com/health
- **Estado:** `timeout`
- **Error:** `Timeout después de 15 segundos`
- **Timestamp:** 2026-05-08T09:31:40.057721

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
    "response_time_ms": 225.53,
    "error": null,
    "timestamp": "2026-05-08T09:31:39.600251",
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
    "timestamp": "2026-05-08T09:31:40.057721",
    "healthy": false
  }
]
```

---

*Este archivo se actualiza automáticamente después de cada push a `main`*
*Para verificar manualmente: `.\scripts\production-monitor.ps1`*
