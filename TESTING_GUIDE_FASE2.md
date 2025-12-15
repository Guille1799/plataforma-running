# 🚀 RunCoach AI - LOCAL TESTING SETUP COMPLETE ✅

## Estado Actual (15 Dec 2025)

### ✅ **Todos los Servidores Corriendo:**

```
🎯 ACCESOS DIRECTOS:
├─ Frontend:        http://localhost:3000 (Next.js)
├─ Backend API:     http://localhost:8000 (FastAPI)
├─ Swagger Docs:    http://localhost:8000/docs
├─ Database:        localhost:5432 (PostgreSQL)
└─ Cache:           localhost:6379 (Redis)
```

---

## 📋 Componentes FASE 2 Implementados y Testeando

### 1. **WorkoutStatsChart** ✅
**Ubicación:** `app/components/workout-stats-chart.tsx`

Muestra 4 gráficos interactivos:
- 📊 Weekly Distance (últimas 5 semanas)
- 💓 Heart Rate Zones (Z1-Z5 con Karvonen)
- ⚡ Intensity Distribution (% tiempo en cada zona)
- 🏃 Pace Progression (evolución del ritmo)

**Características:**
- Cálculo dinámico con `useMemo` para optimización
- Datos REALES de API backend
- Formula Karvonen personalizada por usuario
- Responsive design con Recharts

### 2. **HRZonesVisualizerV2** ✅
**Ubicación:** `app/components/hr-zones-visualizer-v2.tsx`

Visualiza 5 zonas de entrenamiento:
- Z1: Recovery (50-60% HRmax)
- Z2: Aerobic Base (60-70%)
- Z3: Sweet Spot/Tempo (70-80%)
- Z4: Threshold (80-90%)
- Z5: VO2 Max (90-100%)

**Características:**
- BPM dinámico basado en Max HR + Resting HR del usuario
- Indicador de zona actual ("En uso ahora")
- Descriptions en español de sensaciones y usos

### 3. **DateRangeFilter** ✅
**Ubicación:** `app/components/date-range-filter.tsx`

Permite filtrar datos por período:
- Last Week, Last 2 Weeks, Last Month, This Month, Last 3 Months
- Navegación Previous/Next
- "Today" reset button
- Todos los gráficos responden a cambios

### 4. **Dashboard Integration** ✅
**Ubicación:** `app/(dashboard)/dashboard/page.tsx`

Integración completa:
- Loading spinner (Loader2) mientras carga
- Empty state si no hay entrenamientos
- Métricas calculadas en tiempo real
- Filtrado client-side por fecha (sin API calls extra)

---

## 🔧 Cómo Usar Localmente

### **Opción 1: Docker Compose (Recomendado) ⭐**

```bash
cd c:\Users\Guille\proyectos\plataforma-running

# Iniciar todo (backend + db + redis + frontend)
docker-compose -f docker-compose.dev.yml up -d

# Ver status
docker-compose -f docker-compose.dev.yml ps

# Ver logs del backend
docker logs runcoach_backend -f

# Detener todo
docker-compose -f docker-compose.dev.yml down
```

### **Opción 2: PowerShell Scripts**

```powershell
# Terminal 1 - Backend
cd c:\Users\Guille\proyectos\plataforma-running
.\run-servers.ps1 -Backend

# Terminal 2 - Frontend (después de que backend esté listo)
.\run-servers.ps1 -Frontend

# Para detener todo
.\run-servers.ps1 -Kill
```

---

## 📝 Testing Checklist

### Próximas Verificaciones:

```
□ Abrir http://localhost:3000 en navegador
□ Ver página de login
□ Registrarse o login con cuenta existente
□ Navegar a /dashboard
□ Verificar que cargan los 3 componentes nuevos:
  ├─ DateRangeFilter (arriba de los gráficos)
  ├─ WorkoutStatsChart (4 gráficos)
  └─ HRZonesVisualizerV2 (5 zonas HR)
□ Cambiar el rango de fechas y ver si actualizan los gráficos
□ Abrir DevTools (F12) y verificar que NO hay errores de consola
□ Verificar Network tab para ver requests al backend (/api/v1/workouts)
□ Revisar que los datos se cargan desde http://localhost:8000
```

---

## 🐛 Troubleshooting

### "No se ve nada en http://localhost:3000"

1. **Verificar que Next.js está corriendo:**
   ```bash
   Get-Process -Name node
   ```

2. **Revisar logs del frontend:**
   ```bash
   # En la terminal donde está corriendo npm run dev
   # Deberías ver "Ready in XXXms"
   ```

3. **Limpiar cache de Next.js:**
   ```bash
   Remove-Item -Path ".next" -Recurse -Force
   npm run dev
   ```

### "Backend responde pero frontend no carga datos"

1. **Verificar que NEXT_PUBLIC_API_URL está bien:**
   ```powershell
   Get-Content .env.local
   # Debería tener: NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

2. **Revisar que backend está healthy:**
   ```bash
   curl http://localhost:8000/docs
   ```

3. **Ver errores en Network tab:**
   - Abre F12 → Network tab
   - Intenta cargar dashboard
   - Busca requests a `/api/v1/workouts`
   - Si hay errores, revisa la respuesta

### "Docker no inicia"

```bash
# Actualizar WSL
wsl --update

# Reiniciar Docker Desktop
Stop-Process -Name "Docker Desktop" -Force
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Esperar 30 segundos y verificar
docker ps
```

---

## 📊 Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        NAVEGADOR                            │
│              http://localhost:3000                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ GET /dashboard
                       │ API calls to /api/v1/workouts
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              FRONTEND (Next.js 16)                          │
│  ├─ app/(dashboard)/dashboard/page.tsx                     │
│  ├─ components/workout-stats-chart.tsx                     │
│  ├─ components/hr-zones-visualizer-v2.tsx                 │
│  ├─ components/date-range-filter.tsx                      │
│  └─ lib/api-client.ts (llamadas al backend)               │
└──────────────────────┬──────────────────────────────────────┘
                       │ Port 3000
                       │
                       │ API Requests (JSON)
                       │ Backend: http://localhost:8000
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND (FastAPI)                              │
│  ├─ routers/workouts.py (/api/v1/workouts)                │
│  ├─ routers/coach.py (/api/v1/coach/*)                    │
│  ├─ services/coach_service.py (IA generation)             │
│  └─ database/models.py (SQLAlchemy models)                │
└──────────────────────┬──────────────────────────────────────┘
                       │ Port 8000
                       │
     ┌─────────────────┼─────────────────┐
     │                 │                 │
     ▼                 ▼                 ▼
┌──────────┐    ┌──────────┐      ┌──────────┐
│PostgreSQL│    │  Redis   │      │ Groq API │
│   5432   │    │   6379   │      │  (Cloud) │
└──────────┘    └──────────┘      └──────────┘
```

---

## 📝 FASE 2 Status

### ✅ **COMPLETADO:**
- [x] WorkoutStatsChart con 4 gráficos
- [x] HRZonesVisualizerV2 dinámico
- [x] DateRangeFilter funcional
- [x] Integración en dashboard
- [x] Cálculo Karvonen para HR zones
- [x] useMemo optimizations
- [x] Loading/empty states
- [x] Docker setup

### 🔄 **TESTING (Ahora):**
- [ ] Verificar componentes en navegador
- [ ] Testear interactividad de gráficos
- [ ] Validar filtrado por fechas
- [ ] Revisar performance
- [ ] Bug fixes si encuentra

### ⏭️ **PRÓXIMO (FASE 3a):**
- [ ] Email notifications
- [ ] Push notifications
- [ ] WebSocket streaming mejorado

---

## 🎯 Comandos Útiles

```bash
# Ver estado de servicios
docker-compose -f docker-compose.dev.yml ps

# Ver logs en tiempo real
docker logs runcoach_backend -f
docker logs runcoach_db -f

# Entrar a PostgreSQL
docker exec -it runcoach_db psql -U runcoach -d runcoach

# Conectar a Redis
docker exec -it runcoach_redis redis-cli

# Rebuild backend image
docker-compose -f docker-compose.dev.yml build --no-cache backend

# Limpiar todo (ojo, borra DB!)
docker-compose -f docker-compose.dev.yml down -v

# Ver estadísticas de contenedores
docker stats
```

---

## 📍 Próximos Pasos

1. **Abrir navegador** → http://localhost:3000/login
2. **Hacer login/registro**
3. **Navegar a /dashboard**
4. **Revisar que aparecen los 3 componentes nuevos**
5. **Testear interactividad** (filtros, gráficos)
6. **Reportar bugs** o dar feedback
7. **Entonces:** Pasar a FASE 3a (notificaciones)

---

**Fecha:** 15 de Diciembre 2025  
**Status:** ✅ READY FOR TESTING  
**Backend:** ✅ Corriendo  
**Frontend:** ✅ Corriendo  
**Database:** ✅ Corriendo  
**Cache:** ✅ Corriendo
