# 🐛 Bugs Fixed & Remaining Issues

**Status**: Sesión de Dec 15, 2025 - 13:10

---

## ✅ PROBLEMAS SOLUCIONADOS

### 1. **Formato de Ritmo Incorrecto** (FIXED)
**Problema**: Ritmo aparecía como `0'06" /km` en lugar de `0:06/km`
- **Líneas afectadas**: `lib/formatters.ts` + `app/(dashboard)/dashboard/training-plan-detail.tsx`
- **Causa**: Formato con apóstrofos y comillas (no estándar)
- **Solución**: Cambiado a formato `MM:SS/km`
- **Status**: ✅ DEPLOYED

### 2. **Error Client Proxies en Training Plans** (FIXED)
**Problema**: `Client.__init__() got an unexpected keyword argument 'proxies'` al generar plan con carrera
- **Líneas afectadas**: `backend/app/services/training_plan_service.py` (Groq client init)
- **Causa**: groq==0.5.0 (muy antigua) incompatible con httpx==0.28.1
- **Solución**: Actualizado groq a 0.9.0 en `requirements-prod.txt`
- **Status**: ✅ DEPLOYED + Backend reconstruido

---

## ⚠️ PROBLEMAS PENDIENTES (SIN GROQ_API_KEY)

### 3. **AI Coach - GROQ_API_KEY Not Configured**
**Problema**: Error `GROQ_API_KEY not configured` en chat/coach
- **Líneas**: Backend intenta usar `settings.groq_api_key` que es None/empty
- **Causa**: Variable de entorno GROQ_API_KEY no está seteada
- **Solución Requerida**: 
  ```bash
  # En .env o docker-compose.dev.yml, añade:
  GROQ_API_KEY=gsk_xxxxxxxxxxxxx  # Obtén de https://console.groq.com
  ```
- **Impact**: Endpoints `/api/v1/coach/chat`, `/api/v1/coach/analyze-deep/*` fallarán sin esta key

### 4. **Race Search - Accent/Tilde Sensitivity**
**Problema**: Buscar "maraton" no encuentra "Maratón" (sin tilde)
- **Líneas**: Backend search normalization o database collation
- **Causa**: Búsqueda case-sensitive o accent-sensitive
- **Solución Requerida**: Implementar normalize() en búsqueda
  ```python
  # En backend race search:
  import unicodedata
  def normalize(text):
      return ''.join(c for c in unicodedata.normalize('NFD', text) 
                     if unicodedata.category(c) != 'Mn').lower()
  ```

### 5. **Workout Sync Count Discrepancy**
**Problema**: Sync muestra 50 entrenamientos, pero refresh muestra 77
- **Líneas**: `lib/api-client.ts` getWorkouts() + Garmin sync response
- **Causa**: Posible: paginated response no devuelve count total, o sync incompleto
- **Debug**: Revisar response.data.total en api-client.ts
- **Solución Requerida**: Verificar total count correctamente

### 6. **Health Metrics - Empty Data**
**Problema**: Health metrics aparecen vacíos tras sync
- **Líneas**: Endpoints `/api/v1/health/*`
- **Causa**: Posible error en sync Garmin health o en GET health history
- **Debug**: Verificar logs de sync Garmin
- **Solución Requerida**: Implementar fallback si no hay datos de health

### 7. **Deep Workout Analysis - 404** (NEEDS TESTING)
**Problema**: Endpoint `/api/v1/coach/analyze-deep/{workoutId}` retorna 404
- **Líneas**: `backend/app/routers/coach.py` line 477 - endpoint EXISTS pero falla
- **Causa**: Posible problema en el servicio o path incorrecto
- **Status**: ⚠️ NEEDS VERIFICATION - El endpoint existe en código pero da 404

---

## 🔧 PASOS SIGUIENTES

### Inmediatos (Requieren acción del usuario):
1. **Configurar GROQ_API_KEY**
   - Ir a https://console.groq.com
   - Crear API key
   - Añadir a `.env` o `docker-compose.dev.yml`
   - `docker-compose restart` para recargar

2. **Verificar Deep Analysis endpoint**
   - Hacer POST a `http://localhost:8000/api/v1/coach/analyze-deep/1` (con workout ID real)
   - Checar logs del backend para ver error específico

### Segundo orden (Backend fixes):
3. **Race Search Normalization** - Implementar en `backend/app/routers/events.py` 
4. **Workout Sync Total Count** - Debug en API response
5. **Health Metrics Fallback** - Implementar safe defaults

---

## 📊 RESUMEN DE CAMBIOS HECHOS HOY

| Archivo | Cambio | Status |
|---------|--------|--------|
| `lib/formatters.ts` | Pace format M'SS" → MM:SS/km | ✅ |
| `app/(dashboard)/dashboard/training-plan-detail.tsx` | Fix pace display | ✅ |
| `backend/requirements-prod.txt` | groq 0.5.0 → 0.9.0 | ✅ |
| Backend Docker image | Rebuilt + tested | ✅ |

---

## 🚀 TESTING CHECKLIST

Once you configure GROQ_API_KEY, verify:

- [ ] Login works with `testuser@example.com` / `TestPass123`
- [ ] Chat AI coach responds (no 500 error)
- [ ] Can create training plan with "Media Maratón de Zaragoza"
- [ ] Pace displays correctly everywhere (MM:SS/km format)
- [ ] Garmin sync shows consistent count after refresh
- [ ] Health metrics show data after sync
- [ ] Deep workout analysis endpoint works

---

**Last Updated**: 2025-12-15 13:10 UTC+1  
**Agent**: GitHub Copilot Claude Haiku 4.5
