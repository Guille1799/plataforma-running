# 🚀 AGENT START HERE - NO REPO NEEDED

**Este archivo tiene TODO lo que necesitas sin depender del contexto del repo.**

---

## 🎯 TU MISIÓN EN 3 TAREAS

### ✅ TAREA 1: Backend Optimizations (1-1.5 horas)

#### 1.1 - Caché en search_races()
**Archivo**: `backend/app/services/events_service.py`

**Cambio necesario**:
```python
# ANTES (línea ~1)
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import unicodedata
import re

logger = logging.getLogger(__name__)

# DESPUÉS - agregar DESPUÉS de imports existentes:
from functools import lru_cache
import time

# Wrapper para TTL de 1 hora
class CachedSearchRaces:
    def __init__(self):
        self.cache = {}
        self.timestamps = {}
    
    def get_cached(self, query: str) -> Optional[List[Dict]]:
        now = time.time()
        if query in self.cache:
            if now - self.timestamps[query] < 3600:  # 1 hora
                return self.cache[query]
        return None
    
    def set_cache(self, query: str, result: List[Dict]):
        self.cache[query] = result
        self.timestamps[query] = time.time()

cached = CachedSearchRaces()
```

**Código a reemplazar**:
Encuentra esta función en `events_service.py`:
```python
def search_races(self, query: str) -> List[Dict[str, Any]]:
    """Search races by query"""
    normalized_query = self._normalize_query(query)
    results = []
    for race in SPANISH_RACES_DATABASE:
        normalized_name = self._normalize_query(race['name'])
        # ... más código
```

**Reemplázalo con**:
```python
def search_races(self, query: str) -> List[Dict[str, Any]]:
    """Search races by query - WITH CACHE"""
    # Verifica caché primero
    cached_result = cached.get_cached(query)
    if cached_result is not None:
        logger.debug(f"Cache hit for query: {query}")
        return cached_result
    
    normalized_query = self._normalize_query(query)
    results = []
    for race in SPANISH_RACES_DATABASE:
        normalized_name = self._normalize_query(race['name'])
        if normalized_query in normalized_name:
            results.append(race)
    
    # Guarda en caché
    cached.set_cache(query, results)
    logger.info(f"Search races query: {query} returned {len(results)} results")
    
    return results
```

---

#### 1.2 - Logging en coach_service.py
**Archivo**: `backend/app/services/coach_service.py`

Encuentra estas funciones y agrega logs:

**En calculate_hr_zones()**:
```python
def calculate_hr_zones(self, max_hr: int, resting_hr: int = 60, ftp_watts: int = 0) -> Dict[str, Any]:
    """Calculate HR zones using Karvonen formula"""
    logger.info(f"Calculating HR zones: max_hr={max_hr}, resting_hr={resting_hr}, ftp_watts={ftp_watts}")
    
    # ... código existente ...
    
    logger.info(f"HR zones calculated: {zones}")
    return zones
```

**En identify_workout_zone()**:
```python
def identify_workout_zone(self, avg_hr: int, max_hr: int, resting_hr: int = 60) -> str:
    """Identify zone from workout HR"""
    logger.debug(f"Identifying zone: avg_hr={avg_hr}, max_hr={max_hr}, resting_hr={resting_hr}")
    
    # ... código existente ...
    
    logger.info(f"Workout zone identified: {zone}")
    return zone
```

---

#### 1.3 - N+1 Query Prevention
**Archivo**: `backend/app/routers/workouts.py`

Encuentra esta función:
```python
@router.get("/api/v1/workouts")
async def get_workouts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workouts = db.query(Workout).filter(Workout.user_id == current_user.id).all()
```

Reemplázalo con:
```python
from sqlalchemy.orm import joinedload

@router.get("/api/v1/workouts")
async def get_workouts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workouts = db.query(Workout)\
        .filter(Workout.user_id == current_user.id)\
        .joinedload(Workout.user)\
        .all()
    
    logger.info(f"Fetched {len(workouts)} workouts for user {current_user.id}")
    return workouts
```

---

### ✅ TAREA 2: Dashboard Metrics (1.5-2 horas)

**Archivo**: `frontend/app/(dashboard)/page.tsx`

**Cambio**: Agregar 4 componentes nuevos en el dashboard.

Busca esta sección:
```typescript
export default async function DashboardPage() {
  // ... código existente ...
  
  return (
    <div className="space-y-6">
      {/* componentes actuales */}
    </div>
  )
}
```

Agrega estos 4 componentes ANTES del return:

```typescript
// 1. HR ZONES VISUALIZATION
const HRZonesVisualization = ({ user }) => {
  if (!user.hr_zones) return null;
  
  const zones = user.hr_zones; // Viene como JSON del backend
  const zoneColors = {
    'Z1': 'bg-blue-500',
    'Z2': 'bg-green-500',
    'Z3': 'bg-yellow-500',
    'Z4': 'bg-orange-500',
    'Z5': 'bg-red-500'
  };
  
  return (
    <div className="bg-slate-800 rounded-lg p-6">
      <h3 className="text-xl font-bold mb-4">Zonas de FC</h3>
      <div className="space-y-3">
        {zones.map((zone, idx) => (
          <div key={idx} className="flex items-center justify-between">
            <div className={`${zoneColors[zone.name]} px-3 py-1 rounded text-white font-bold`}>
              {zone.name}
            </div>
            <span className="text-gray-300">
              {zone.min_bpm} - {zone.max_bpm} bpm
            </span>
            <span className="text-gray-500 text-sm">{zone.purpose}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// 2. WORKOUTS BY ZONE CHART (usando recharts)
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const WorkoutsByZoneChart = ({ workouts }) => {
  if (!workouts || workouts.length === 0) {
    return <div className="text-gray-400">No workouts yet</div>;
  }
  
  // Agrupa workouts por semana y zona
  const last4Weeks = getLast4Weeks(workouts);
  
  return (
    <div className="bg-slate-800 rounded-lg p-6">
      <h3 className="text-xl font-bold mb-4">Entrenamientos por Zona (4 semanas)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={last4Weeks}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="week" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="Z1" stackId="a" fill="#3b82f6" />
          <Bar dataKey="Z2" stackId="a" fill="#10b981" />
          <Bar dataKey="Z3" stackId="a" fill="#eab308" />
          <Bar dataKey="Z4" stackId="a" fill="#f97316" />
          <Bar dataKey="Z5" stackId="a" fill="#ef4444" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

// 3. PROGRESSION CHART (últimas 8 semanas)
import { LineChart, Line } from 'recharts';

const ProgressionChart = ({ workouts }) => {
  const last8Weeks = getLast8Weeks(workouts);
  
  return (
    <div className="bg-slate-800 rounded-lg p-6">
      <h3 className="text-xl font-bold mb-4">Progresión de FC (8 semanas)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={last8Weeks}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="week" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="avgHR" stroke="#ef4444" dot={{ fill: '#ef4444' }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

// 4. SMART SUGGESTIONS
const SmartSuggestions = ({ workouts, user }) => {
  const suggestions = generateSuggestions(workouts, user);
  
  return (
    <div className="bg-slate-800 rounded-lg p-6">
      <h3 className="text-xl font-bold mb-4">Sugerencias</h3>
      <ul className="space-y-3">
        {suggestions.map((sug, idx) => (
          <li key={idx} className="flex items-start gap-3 text-gray-300">
            <span className="text-green-500 mt-1">✓</span>
            {sug}
          </li>
        ))}
      </ul>
    </div>
  );
};

// Helper functions
function getLast4Weeks(workouts) {
  // Agrupa workouts por semana, retorna array con counts por zona
  // ...
}

function getLast8Weeks(workouts) {
  // Retorna progresión de FC por semana
  // ...
}

function generateSuggestions(workouts, user) {
  const suggestions = [];
  
  // Z2 balance
  const z2Count = workouts.filter(w => w.zone === 'Z2').length;
  if (z2Count < 2) suggestions.push("Agrega 2 entrenamientos en Z2 (endurance)");
  
  // Recovery
  const avgHRLastWeek = calculateAvgHR(workouts, 7);
  if (avgHRLastWeek > user.max_heart_rate * 0.75) {
    suggestions.push("Descansa 1-2 días antes de próximo entrenamiento fuerte");
  }
  
  // Balance
  suggestions.push("Buen balance de intensidades esta semana!");
  
  return suggestions.slice(0, 3);
}

function calculateAvgHR(workouts, days) {
  // Calcula promedio FC últimos N días
  // ...
}
```

Luego en el return del component, agrega:
```typescript
return (
  <div className="space-y-6">
    {/* Existentes */}
    
    {/* NUEVOS */}
    <HRZonesVisualization user={activePlan?.user} />
    <WorkoutsByZoneChart workouts={workouts} />
    <ProgressionChart workouts={workouts} />
    <SmartSuggestions workouts={workouts} user={activePlan?.user} />
  </div>
)
```

---

### ✅ TAREA 3: UI Polish (1-1.5 horas)

#### 3.1 Responsive Design
Verifica en el archivo `frontend/app/layout.tsx` que tenga:
```typescript
export const metadata = {
  viewport: "width=device-width, initial-scale=1, maximum-scale=1",
}
```

#### 3.2 Dark Mode WCAG AA
En Tailwind config (`frontend/tailwind.config.ts`):
```javascript
module.exports = {
  darkMode: 'class',
  theme: {
    colors: {
      slate: {
        800: '#1e293b',  // Background dark
        700: '#334155',  // Hover
        600: '#475569',  // Text secondary
      },
      white: '#ffffff',  // 5:1 contrast on slate-800
    }
  }
}
```

#### 3.3 Loading States
En componentes que hacen fetch, agrega:
```typescript
const [isLoading, setIsLoading] = useState(false);

if (isLoading) {
  return <SkeletonLoader />;  // shadcn skeleton
}

// Cuando hagas fetch:
setIsLoading(true);
await fetchData();
setIsLoading(false);
```

#### 3.4 Animaciones Suaves
En Tailwind:
```typescript
<button className="transition-all duration-300 hover:scale-105">
  Click me
</button>
```

---

## 🎯 RESUMEN DE ARCHIVOS A EDITAR

| Archivo | Cambio | Tiempo |
|---------|--------|--------|
| `backend/app/services/events_service.py` | Agregar caché | 20 min |
| `backend/app/services/coach_service.py` | Agregar logging | 20 min |
| `backend/app/routers/workouts.py` | Prevenir N+1 | 20 min |
| `frontend/app/(dashboard)/page.tsx` | 4 componentes nuevos | 90 min |
| `frontend/tailwind.config.ts` | Dark mode WCAG | 10 min |
| `frontend/app/layout.tsx` | Viewport responsive | 5 min |

---

## ✅ VALIDACIÓN FINAL

Después de terminar:

```bash
# Backend
cd backend
pytest  # Debe pasar

# Frontend
cd frontend
npm run build  # Sin errores
tsc --noEmit  # Sin errores TypeScript

# Test API
curl http://localhost:8000/docs  # Swagger debe cargar
```

---

## 🚀 ¡LISTO!

Todo lo que necesitas está en este archivo. No dependes del contexto del repo.

**Empieza por TAREA 1, luego TAREA 2, luego TAREA 3.**

**¡ADELANTE!**
