# 🚀 AGENT BRIEF - START HERE

**Este archivo es tu punto de entrada. Léelo primero.**

---

## 📍 CONTEXTO DEL REPOSITORIO

**Nombre**: Plataforma de Running (RunCoach)  
**Ubicación**: `c:\Users\guill\Desktop\plataforma-running`  
**Tipo**: Full-stack web app (Backend FastAPI + Frontend Next.js)  
**Estado**: Production-ready, ready for advanced features

---

## 📂 ESTRUCTURA DEL PROYECTO

```
c:\Users\guill\Desktop\plataforma-running\
├── backend/                          # Python FastAPI
│   ├── app/
│   │   ├── main.py                  # App entry point
│   │   ├── models.py                # SQLAlchemy models
│   │   ├── schemas.py               # Pydantic validation
│   │   ├── services/
│   │   │   ├── coach_service.py     # 🔑 HR zones, Power zones, Karvonen
│   │   │   ├── training_plan_service.py  # 🔑 Duration calculation
│   │   │   ├── events_service.py    # 🔑 Race search (27 races)
│   │   │   └── garmin_service.py
│   │   └── routers/                 # API endpoints
│   ├── requirements.txt
│   ├── pytest.ini
│   └── .env                         # 🔑 Config (GROQ_API_KEY, etc)
│
├── frontend/                        # Next.js React TypeScript
│   ├── app/
│   │   ├── layout.tsx              # Root layout
│   │   ├── (auth)/                 # Auth pages
│   │   └── (dashboard)/            # Dashboard pages
│   ├── components/
│   │   ├── training-plan-form-v2.tsx  # 🔑 6-step wizard form
│   │   └── ui/                     # shadcn/ui components
│   ├── lib/
│   │   ├── api-client.ts           # API client
│   │   ├── auth-context.tsx        # Auth state
│   │   └── types.ts                # TypeScript types
│   ├── package.json
│   └── next.config.js
│
├── 🔑 DOCUMENTACIÓN CRÍTICA
│   ├── AGENT_MEGA_TASK.md          # ⭐ YOUR MAIN TASK FILE (660+ lines)
│   ├── QUICK_REFERENCE.md          # Quick tarjeta
│   ├── API_REFERENCE.md            # All endpoints
│   ├── TEST_CASES.md               # 40+ test cases
│   ├── DEPLOY_GUIDE.md             # Deployment
│   └── validate_platform.py        # Validation script
│
└── docker-compose.yml              # Docker setup
```

---

## 🎯 TU MISIÓN (TIER 1 - CRÍTICO)

### Tarea 1: Backend Optimizations (1-1.5 horas)
**Archivo**: `backend/app/services/events_service.py`
- [ ] Agregar `@lru_cache` a `search_races()`
- [ ] TTL de 1 hora para caché
- [ ] Normalizar queries (lowercase, sin acentos)
- [ ] Resultado: búsquedas < 1ms en lugar de 100ms+

**Archivo**: `backend/app/services/coach_service.py`
- [ ] Agregar logging en métodos clave
- [ ] Logger format: timestamp | LEVEL | función | mensaje
- [ ] Log en: calculate_hr_zones, identify_workout_zone, etc.

**Archivo**: `backend/app/routers/workouts.py`
- [ ] Implementar eager loading para prevenir N+1 queries
- [ ] Usar SQLAlchemy joinedload/selectinload
- [ ] Test: GET `/api/v1/workouts` < 200ms

### Tarea 2: Dashboard Metrics (1.5-2 horas)
**Archivo**: `frontend/app/(dashboard)/page.tsx`

Agregar 4 componentes nuevos:

1. **HR Zones Visualization**
   - Mostrar 5 zonas (Z1-Z5) con rangos en bpm
   - Colores: azul, verde, amarillo, naranja, rojo
   - Formato: "Z1: 100-130 bpm (Recovery)" etc.
   - Source: `user.hr_zones` (JSON)

2. **Workouts by Zone Chart**
   - Gráfico: últimas 4 semanas, por zona
   - X-axis: semanas, Y-axis: cantidad workouts
   - Barras apiladas por zona (colores)
   - Librería: recharts (ya instalada)

3. **Progression Chart**
   - Gráfico: últimas 8 semanas, avg HR por semana
   - Línea roja con puntos
   - X-axis: semanas, Y-axis: HR
   - Opcional: tendencia FTP (watts)

4. **Smart Suggestions**
   - Mínimo 3 sugerencias basadas en datos
   - Ejemplos:
     - "Tu Z2 (endurance) está bajo. Agrega 2 workouts más"
     - "Buen balance de intensidad esta semana"
     - "Descansa 1-2 días antes de carrera"

### Tarea 3: UI Polish (1-1.5 horas)

**Responsive Design**
- [ ] Test en: 375px (mobile), 768px (tablet), 1920px (desktop)
- [ ] No hay scroll horizontal en mobile
- [ ] Touch targets mínimo 48px
- [ ] Font mínimo 16px (no auto-zoom)

**Animaciones**
- [ ] Transiciones suaves: 300ms fade in/out
- [ ] Loading spinners en async calls
- [ ] Hover effects en botones/cards
- [ ] Sin motion sickness (Max 3-4 animaciones simultáneas)

**Dark Mode**
- [ ] Text contrast ≥ 4.5:1 (WCAG AA)
- [ ] Bordes visibles (no se pierden en dark)
- [ ] Hover states claramente visibles
- [ ] Verifica: Dropdowns, Cards, Buttons, Inputs

**Loading States**
- [ ] Dashboard loading: skeleton loaders
- [ ] API calls: spinners
- [ ] Form submission: disable botón + loading indicator
- [ ] Smooth transitions entre estados

---

## ✅ VERIFICACIÓN INICIAL

Antes de empezar, ejecuta ESTO (en terminal):

```powershell
# En: c:\Users\guill\Desktop\plataforma-running

# 1. Validar plataforma
python validate_platform.py

# 2. Verificar backend
cd backend
pytest -v

# 3. Verificar frontend
cd ../frontend
npm run build
tsc --noEmit

# 4. Verificar que NO hay errores
cd ..
```

**Resultado esperado**:
```
✅ Platform validation passed
✅ Backend tests: 100% passing
✅ Frontend compiles without errors
✅ TypeScript strict: 0 errors
```

---

## 🔑 ARCHIVOS CLAVE A CONOCER

| Archivo | Líneas | Qué hace |
|---------|--------|----------|
| `coach_service.py` | 1600+ | Karvonen, Power zones, HR zones |
| `training_plan_service.py` | 400+ | Duration calculation |
| `events_service.py` | 200+ | Race search (27 races) |
| `training-plan-form-v2.tsx` | 400+ | 6-step form wizard |
| `api-client.ts` | 250+ | API client con tipos |

---

## 📚 DOCUMENTACIÓN DE REFERENCIA

**PRIMERO LEE ESTOS (en orden)**:

1. **Este archivo** (ya estás aquí ✅)
2. **AGENT_MEGA_TASK.md** (660 líneas, todas las tareas detalladas)
3. **QUICK_REFERENCE.md** (tarjeta rápida de desarrollo)
4. **API_REFERENCE.md** (todos los endpoints disponibles)

**SI NECESITAS ESPECIAL**:

- Testing: **TEST_CASES.md** (40+ casos de prueba)
- Deployment: **DEPLOY_GUIDE.md** (3 opciones)
- Questions: **QUICK_REFERENCE.md** (FAQ)
- Inventario: **DOCUMENTATION_MANIFEST.md** (qué documenta cada archivo)

---

## 🎯 CHECKLIST ANTES DE CODEAR

- [ ] Lei este archivo ✅
- [ ] Lei AGENT_MEGA_TASK.md
- [ ] Ejecuté `validate_platform.py` (sin errores)
- [ ] Backend levantado en :8000 (uvicorn)
- [ ] Frontend levantado en :3000 (npm run dev)
- [ ] .env tiene GROQ_API_KEY
- [ ] Tests pasando (pytest)

---

## 🚀 COMENZAR AHORA

### Paso 1: Lee AGENT_MEGA_TASK.md
```
c:\Users\guill\Desktop\plataforma-running\AGENT_MEGA_TASK.md
```

### Paso 2: Valida la plataforma
```powershell
python validate_platform.py
```

### Paso 3: Empieza por Tarea 1
Implementa caché en `events_service.py`

---

## 💡 TIPS IMPORTANTES

1. **Usa `grep_search`** para encontrar código rápido
2. **Usa `read_file`** para ver archivos largos
3. **Usa `replace_string_in_file`** para edits precisas
4. **Usa `multi_replace_string_in_file`** para múltiples cambios
5. **Sé específico** en búsquedas: "search_races method" no solo "search"

---

## 🔗 REFERENCIAS RÁPIDAS

- **Backend API**: http://localhost:8000/docs (Swagger)
- **Frontend**: http://localhost:3000
- **Database**: SQLite en `backend/runcoach.db`
- **Logs**: Terminal donde corre uvicorn/npm

---

## ✨ ÉXITO SE MIDE POR

- ✅ Tarea 1 completa: API < 200ms, logging funciona
- ✅ Tarea 2 completa: Dashboard metrics visibles y bonitas
- ✅ Tarea 3 completa: UI responsiva, dark mode WCAG AA
- ✅ 0 errores en compilación
- ✅ Tests 100% pasando
- ✅ Sin breaking changes

---

## 🆘 SI ALGO FALLA

1. Consulta **TROUBLESHOOTING.md**
2. Revisa logs en terminal
3. Ejecuta `validate_platform.py` de nuevo
4. Si persiste, abre issue con detalles

---

**¡ADELANTE! 🚀**

*Próximo paso: Lee AGENT_MEGA_TASK.md (línea 1)*

---

*Archivo creado: Nov 16, 2025*  
*Para: Cloud Agent*  
*Estado: Ready to execute*
