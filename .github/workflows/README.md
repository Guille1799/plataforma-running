# GitHub Actions Workflows

Este directorio contiene los workflows de CI/CD para el proyecto RunCoach AI.

## 🟢 Monitor Production

**Archivo:** `monitor-production.yml`

**Cuándo se ejecuta:**
- Automáticamente después de cada push a `main`
- Manualmente desde GitHub Actions UI (botón "Run workflow")

**Qué hace:**
1. Verifica que el Frontend (Vercel) esté operativo
2. Verifica que el Backend (Render) esté operativo en `/health`
3. Reporta el estado de cada servicio
4. Falla el workflow si algún servicio no está operativo

**Costo:**
- ✅ Completamente gratis (usa 2000 minutos/mes gratuitos de GitHub Actions)

**Ver resultados:**
- Ve a: https://github.com/Guille1799/plataforma-running/actions
- Busca el workflow "🟢 Monitor Production"
- Revisa los logs de cada ejecución
