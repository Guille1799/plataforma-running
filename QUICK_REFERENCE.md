# ⚡ QUICK REFERENCE - Plataforma de Running

**Tarjeta de referencia rápida para desarrolladores**

---

## 🚀 ARRANCAR RÁPIDO

```powershell
# Terminal 1 - Backend
cd c:\Users\guill\Desktop\plataforma-running\backend
.\venv\Scripts\uvicorn.exe app.main:app --reload
# → http://127.0.0.1:8000

# Terminal 2 - Frontend
cd c:\Users\guill\Desktop\plataforma-running\frontend
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
npm run dev
# → http://localhost:3000
```

---

## 📁 ESTRUCTURA CRÍTICA

```
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── models.py            # User, Workout, ChatMessage
│   ├── schemas.py           # Pydantic validation
│   ├── database.py          # SQLAlchemy setup
│   ├── services/
│   │   ├── coach_service.py         # 🧠 HR/Power zones, Karvonen
│   │   ├── training_plan_service.py # 📅 Duration calc
│   │   ├── events_service.py        # 🏃 Races (27 Spanish)
│   │   └── garmin_service.py        # 📱 Garmin sync
│   └── routers/
│       ├── auth.py
│       ├── workouts.py
│       ├── training_plans.py        # ⭐ Duration endpoints
│       ├── coach.py
│       └── events.py                # ⭐ Race search

frontend/
├── app/
│   ├── layout.tsx           # Root + Providers
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── (dashboard)/
│   │   ├── page.tsx         # Dashboard home
│   │   ├── workouts/page.tsx
│   │   ├── coach/page.tsx
│   │   └── stats/page.tsx
│   └── providers.tsx        # AuthProvider + QueryProvider
├── lib/
│   ├── api-client.ts        # API client + types
│   ├── auth-context.tsx     # Auth hooks
│   ├── formatters.ts        # pace, HR, distance utils
│   └── types.ts             # TypeScript types
├── components/
│   ├── training-plan-form-v2.tsx  # ⭐ 6-step wizard
│   └── ui/                   # shadcn/ui components
└── public/                  # Static files
```

---

## 🔑 ARCHIVOS MÁS IMPORTANTES

| Archivo | Qué hace | Cuando editar |
|---------|---------|---------------|
| `coach_service.py` | Calcula zonas HR/Potencia | Cambiar Karvonen, agregar zonas |
| `training_plan_service.py` | Calcula duración plans | Cambiar recomendaciones |
| `events_service.py` | Busca carreras españolas | Agregar races, mejorar search |
| `training-plan-form-v2.tsx` | Wizard 6 pasos | UI/UX del formulario |
| `api-client.ts` | Cliente API | Agregar endpoints |
| `auth-context.tsx` | Session del usuario | Auth logic |

---

## ⚙️ CONFIGURACIÓN CLAVE

### Backend `.env`
```bash
GROQ_API_KEY=gsk_...              # ⭐ Obligatorio
DATABASE_URL=sqlite:///runcoach.db # Desarrollo
JWT_SECRET_KEY=super_secret_key    # ⭐ Obligatorio
DEBUG=True                         # Dev only
```

### Frontend `setup-env` (o hardcoded)
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
```

---

## 🔗 ENDPOINTS MÁS USADOS

```bash
# Auth
POST   /api/v1/auth/register
POST   /api/v1/auth/login
GET    /api/v1/auth/me

# Workouts
GET    /api/v1/workouts
POST   /api/v1/workouts
GET    /api/v1/workouts/{id}

# Training Plans
POST   /api/v1/training-plans
GET    /api/v1/training-plans/{id}
POST   /api/v1/training-plans/duration/with-target-race  # ⭐
GET    /api/v1/training-plans/duration-options/{goal_type}  # ⭐

# Coach AI
POST   /api/v1/coach/chat
POST   /api/v1/coach/analyze-workout

# Races
GET    /api/v1/events/races/search?q=madrid

# Docs
GET    /docs              # Swagger UI
```

---

## 🧪 TESTING

```bash
# Backend - pytest
cd backend && pytest
cd backend && pytest tests/test_coach_service.py -v

# Frontend - jest (si existe)
cd frontend && npm test

# E2E - playwright (si existe)
npm run test:e2e
```

---

## 🐛 DEBUGGING

### Backend
```python
# Print debug info
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Value: {value}")

# En coach_service.py ya hay logger configurado
logger.info(f"HR zones calculated: {zones}")
```

### Frontend
```typescript
// Console logs
console.log('Debug:', value)

// React DevTools
F12 → Components tab

// Network
F12 → Network tab → check API calls
```

---

## 📊 MODELOS DE DATOS

### User
```python
- id: int (PK)
- email: str (unique)
- password: str (hashed)
- full_name: str
- max_heart_rate: int
- resting_heart_rate: int = 60
- ftp_watts: int = 0
- power_zones: JSON  # Calculado automático
- hr_zones: JSON     # Calculado automático
- active_plan_id: int (FK)
```

### Workout
```python
- id: int (PK)
- user_id: int (FK)
- title: str
- distance_meters: float
- duration_seconds: int
- avg_heart_rate: int
- max_heart_rate: int
- source: str (garmin, manual, etc)
- start_time: datetime
- zone: str (Z1-Z7)
```

### TrainingPlan
```python
- id: int (PK)
- user_id: int (FK)
- goal_type: str (5K, 10K, HM, M)
- target_race_date: datetime (opcional)
- start_date: datetime
- plan_duration_weeks: int
- workouts: List[Workout]
```

---

## 🎯 FEATURES CLAVE

### ✅ Karvonen Formula (HR Zones)
```python
# Más preciso que % max HR
# Formula: (Max HR - Resting HR) * % + Resting HR
# Ejemplo: (200 - 60) * 0.5 + 60 = 130 bpm (Z2)

# Implementado en: coach_service.py → calculate_hr_zones()
```

### ✅ Power Zones (7 zonas)
```python
# Basado en FTP (Functional Threshold Power)
# Z1: <55% FTP (Recovery)
# Z2: 55-75% FTP (Endurance)
# ...
# Z7: >150% FTP (Neuromuscular)

# Implementado en: coach_service.py → _calculate_power_zones()
```

### ✅ Plan Duration Auto-calc
```python
# Con carrera: calcula automáticamente del hoy a carrera
# Sin carrera: muestra 3 opciones (quick, optimal, extended)

# Endpoints:
# POST /duration/with-target-race → (target_race_date, goal_type)
# GET /duration-options/{goal_type} → returns 3 options
```

### ✅ Race Search (27 Spanish Races)
```python
# Busca con: accent-insensitive, case-insensitive, partial match
# Ejemplo: "león" = "León", "mad" = "Madrid", "sevilla" = "Sevilla"
# Caché: @lru_cache(maxsize=128) por 1 hora

# Endpoint: GET /events/races/search?q={query}
```

---

## 🚨 ERRORES COMUNES

| Error | Solución |
|-------|----------|
| `ModuleNotFoundError: No module named 'groq'` | `pip install groq` |
| `GROQ_API_KEY not found` | Agrega a `.env` |
| `Database locked` | Reinicia backend, SQLite no soporta escritura concurrente |
| `TypeError: expected str, got None` | Validar form data antes de enviar API |
| `CORS error` | Revisar `ALLOWED_ORIGINS` en backend |
| `404 on /api/v1/events/races` | Imports en `app/__init__.py` incompletos |

---

## 💡 TIPS & TRICKS

### Backend
```python
# Usar async para operations largas
async def long_operation():
    result = await expensive_call()
    return result

# Logs útiles
logger.info(f"Plan created: id={plan.id}, user={user.email}")
logger.error(f"Failed to sync: {str(e)}")

# Caché local
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(x: int) -> int:
    return x ** 2
```

### Frontend
```typescript
// useEffect cleanup
useEffect(() => {
  const unsubscribe = subscribeToData()
  return () => unsubscribe() // Cleanup
}, [])

// Error boundaries
<ErrorBoundary>
  <YourComponent />
</ErrorBoundary>

// Loading states
{isLoading ? <Spinner /> : <Data />}

// Type-safe queries
const { data, isLoading, error } = useQuery({
  queryKey: ['workouts', userId],
  queryFn: () => api.getWorkouts(userId)
})
```

---

## 🔄 WORKFLOW TÍPICO

### Agregar nueva feature

1. **Backend**:
   ```python
   # 1. Add schema in schemas.py
   class NewFeatureSchema(BaseModel):
       field: str
   
   # 2. Add model in models.py
   class NewFeature(Base):
       __tablename__ = "new_features"
       id: int = Column(Integer, primary_key=True)
   
   # 3. Add service method in service.py
   def create_new_feature(data: NewFeatureSchema) -> NewFeature:
       pass
   
   # 4. Add router endpoint in routers/
   @router.post("/new-feature")
   async def create(data: NewFeatureSchema, db: Session):
       return await service.create_new_feature(data)
   ```

2. **Frontend**:
   ```typescript
   // 1. Add API client method in lib/api-client.ts
   export async function createNewFeature(data) {
     return apiClient.post('/new-feature', data)
   }
   
   // 2. Add TypeScript type in lib/types.ts
   export interface NewFeature {
     id: number
     field: string
   }
   
   // 3. Create React component
   export function NewFeatureComponent() {
     return <div>...</div>
   }
   
   // 4. Add page/route
   // app/(dashboard)/new-feature/page.tsx
   ```

3. **Test**:
   ```bash
   cd backend && pytest tests/test_new_feature.py
   cd frontend && npm test -- new-feature.test.tsx
   ```

---

## 📦 VERSIONES

```
Python: 3.12+
Node.js: 18+
Next.js: 16+
React: 18+
FastAPI: 0.104+
SQLAlchemy: 2.0+
TypeScript: 5+
```

---

## 🔗 RECURSOS

- FastAPI Docs: https://fastapi.tiangolo.com
- Next.js Docs: https://nextjs.org/docs
- Groq API: https://console.groq.com
- SQLAlchemy: https://docs.sqlalchemy.org
- Tailwind CSS: https://tailwindcss.com

---

## 📞 SOPORTE RÁPIDO

**Revisar logs primero**:
```bash
docker-compose logs backend
docker-compose logs frontend
```

**Verificar config**:
```bash
cat backend/.env | grep -E "GROQ|DATABASE|JWT"
```

**Test endpoints**:
```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:3000 -I
```

---

## ✅ CHECKLIST DIARIO

- [ ] Backend compilando sin errores
- [ ] Frontend compilando sin errores
- [ ] Tests pasando (al menos los principales)
- [ ] Database accesible
- [ ] GROQ_API_KEY configurado
- [ ] No hay console.errors en browser
- [ ] API responde en < 500ms

---

**Happy Coding! 🚀**

*Última actualización: Nov 2024*
*Versión: 1.0*
