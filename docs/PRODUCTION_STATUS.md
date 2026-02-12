# 🟢 Estado de Producción - RunCoach AI

**Última actualización:** 2026-02-12 11:35:07 UTC
**Commit:** `b7123ba`
**Workflow:** [Ver en GitHub Actions](https://github.com/Guille1799/plataforma-running/actions/runs/21944946617)

---

## 📊 Resumen

⚠️ **Algunos servicios tienen problemas** (1/2 operativos)

### Servicios Monitoreados

#### ✅ Frontend (Vercel)

- **URL:** https://plataforma-running.vercel.app
- **Health Check:** https://plataforma-running.vercel.app
- **Estado:** `healthy`
- **Status Code:** `200`
- **Response Time:** `306.81ms`
- **Timestamp:** 2026-02-12T11:34:51.795559

#### ❌ Backend API (Render)

- **URL:** https://plataforma-running.onrender.com
- **Health Check:** https://plataforma-running.onrender.com/health
- **Estado:** `timeout`
- **Error:** `Timeout después de 15 segundos`
- **Timestamp:** 2026-02-12T11:34:52.544695

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
    "response_time_ms": 306.81,
    "error": null,
    "timestamp": "2026-02-12T11:34:51.795559",
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
    "timestamp": "2026-02-12T11:34:52.544695",
    "healthy": false
  }
]
```

---

*Este archivo se actualiza automáticamente después de cada push a `main`*
*Para verificar manualmente: `.\scripts\production-monitor.ps1`*
