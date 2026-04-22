# 🟢 Estado de Producción - RunCoach AI

**Última actualización:** 2026-04-22 12:19:27 UTC
**Commit:** `35f2ca6`
**Workflow:** [Ver en GitHub Actions](https://github.com/Guille1799/plataforma-running/actions/runs/24777837753)

---

## 📊 Resumen

⚠️ **Algunos servicios tienen problemas** (1/2 operativos)

### Servicios Monitoreados

#### ✅ Frontend (Vercel)

- **URL:** https://plataforma-running.vercel.app
- **Health Check:** https://plataforma-running.vercel.app
- **Estado:** `healthy`
- **Status Code:** `200`
- **Response Time:** `351.17ms`
- **Timestamp:** 2026-04-22T12:19:11.269737

#### ❌ Backend API (Render)

- **URL:** https://plataforma-running.onrender.com
- **Health Check:** https://plataforma-running.onrender.com/health
- **Estado:** `timeout`
- **Error:** `Timeout después de 15 segundos`
- **Timestamp:** 2026-04-22T12:19:12.368222

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
    "response_time_ms": 351.17,
    "error": null,
    "timestamp": "2026-04-22T12:19:11.269737",
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
    "timestamp": "2026-04-22T12:19:12.368222",
    "healthy": false
  }
]
```

---

*Este archivo se actualiza automáticamente después de cada push a `main`*
*Para verificar manualmente: `.\scripts\production-monitor.ps1`*
