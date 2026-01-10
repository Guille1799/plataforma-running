# 🤝 Sistema de Coordinación entre Agents

## ⚠️ INSTRUCCIONES CRÍTICAS

**ANTES de editar cualquier archivo:**
1. Leer `.agent-lock.json` 
2. Verificar que el archivo NO esté en `files_being_edited` de otro agent
3. Agregar el archivo a TU `files_being_edited` 
4. Actualizar `.agent-lock.json` inmediatamente
5. Después de editar, REMOVER el archivo de `files_being_edited`

---

## 📋 División de Tareas Sugerida

### Agent 1 (Este Agent - Centralizar Auth):
**Tareas:**
- ✅ TIER 1: Todas las tareas de seguridad completadas
- 🔄 TIER 2.1: Centralizar autenticación
  - Completar routers principales: health, profile, onboarding
  - Luego continuar con routers secundarios

**Archivos que PUEDE editar:**
- `backend/app/dependencies/auth.py`
- `backend/app/routers/health.py`
- `backend/app/routers/profile.py`
- `backend/app/routers/onboarding.py`
- `backend/app/routers/garmin.py`
- `backend/app/routers/strava.py`
- `backend/app/routers/upload.py`
- `backend/app/routers/hrv.py`
- `backend/app/routers/overtraining.py`
- `backend/app/routers/predictions.py`
- `backend/app/routers/race_prediction_enhanced.py`
- `backend/app/routers/training_recommendations.py`
- `backend/app/routers/integrations.py`

### Agent 2 (Otro Agent):
**Tareas sugeridas:**
- Eliminar archivos `.bak` (tarea rápida y sin conflictos)
- Resolver TODOs críticos
- Agregar índices compuestos (solo `backend/app/models.py`)
- Limpiar logging (diferentes archivos a Agent 1)

**Archivos que PUEDE editar:**
- `app/components/*.tsx.bak` (eliminar)
- `backend/app/services/*.py` (limpiar logging)
- `backend/app/routers/*.py` (solo si NO están en lista de Agent 1)
- `backend/app/models.py` (índices)
- Cualquier archivo con TODOs críticos

---

## 🚫 ZONA DE NO INTERVENCIÓN

**NUNCA editar estos archivos simultáneamente:**
- `backend/app/dependencies/auth.py` (Agent 1 tiene prioridad)
- Cualquier router que Agent 1 esté editando

---

## ✅ Checklist Antes de Editar

- [ ] Leí `.agent-lock.json`
- [ ] Verifiqué que el archivo NO está siendo editado por otro agent
- [ ] Agregué el archivo a MI `files_being_edited`
- [ ] Actualicé `.agent-lock.json`
- [ ] Comencé a editar
