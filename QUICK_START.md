# 🚀 Quick Start Guide - Health Metrics System

## ✅ Sistema Completamente Implementado

### 📊 Base de Datos (SQLite → PostgreSQL Ready)

**Estado Actual:**
```
✅ 1 usuario
✅ 60 workouts
✅ 30 health metrics (30 días de datos)
✅ 12 mensajes de chat
```

**Ubicación:** `backend/runcoach.db` (~150KB)

---

## 🎯 Arrancar el Proyecto

### Terminal 1: Backend
```powershell
cd C:\Users\guill\Desktop\plataforma-running\backend
.\venv\Scripts\uvicorn.exe app.main:app --reload
```
**URL:** http://127.0.0.1:8000

### Terminal 2: Frontend
```powershell
cd C:\Users\guill\Desktop\plataforma-running\frontend
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
npm run dev
```
**URL:** http://localhost:3000

---

## 🎨 Páginas Implementadas

### 1. **Dashboard Principal** (`/dashboard`)
- ✅ Readiness Badge con score circular
- ✅ Stats de workouts (esta semana, este mes)
- ✅ Pace promedio calculado
- ✅ Total de entrenamientos

### 2. **Health Dashboard** (`/health`)
- ✅ Readiness Score con breakdown de factores
- ✅ Daily Check-In widget (sliders + inputs)
- ✅ Métricas principales: HRV, Resting HR, Sleep, Body Battery
- ✅ AI Workout Recommendation
- ✅ Activity metrics (pasos, calorías, intensidad)
- ✅ Data source badges

### 3. **Health History** (`/health/history`) 🆕
- ✅ 7 gráficos interactivos (Recharts):
  - HRV con baseline
  - Sleep Duration & Score
  - Readiness Score (bar chart)
  - Resting Heart Rate
  - Body Battery
  - Stress Level
- ✅ Trend cards con % de cambio vs semana anterior
- ✅ AI Insights card

### 4. **Device Connections** (`/health/devices`)
- ✅ 3 cards: Garmin, Google Fit, Apple Health
- ✅ Status badges (conectado/desconectado)
- ✅ Botones "Conectar" + "Sincronizar"
- ✅ Upload de archivo Apple Health
- ✅ Guías de setup paso a paso

### 5. **Google Fit Callback** (`/health/callback`) 🆕
- ✅ Manejo de OAuth callback
- ✅ Loading states
- ✅ Success/error messages
- ✅ Auto-redirect después de conectar

---

## 🔧 Comandos Útiles

### Verificar Base de Datos
```powershell
cd backend
.\venv\Scripts\python.exe check_db_status.py
```

### Resetear Base de Datos (⚠️ Cuidado!)
```powershell
cd backend
Remove-Item runcoach.db
# Luego arrancar servidor para recrear
.\venv\Scripts\uvicorn.exe app.main:app --reload
```

### Poblar Health Metrics de Ejemplo
```powershell
cd backend
.\venv\Scripts\python.exe seed_health_data.py <user_id> <days>
# Ejemplo: .\venv\Scripts\python.exe seed_health_data.py 1 30
```

### Instalar Dependencias Frontend
```powershell
cd frontend
npm install
```

---

## 📱 Flujos de Usuario

### ✅ Flujo 1: Ver Health Dashboard
1. Login en http://localhost:3000
2. Click en badge de Readiness en dashboard
3. Ve score actual + métricas del día
4. Scroll para ver breakdown de factores
5. Lee recomendación del Coach AI

### ✅ Flujo 2: Daily Check-In Manual
1. Va a `/health`
2. Completa sliders (energía, molestias, ánimo, motivación)
3. Ingresa horas de sueño
4. Opcionalmente: FC en reposo + notas
5. Click "Guardar Check-In"
6. Toast "✅ Check-in guardado exitosamente"
7. Readiness score se actualiza automáticamente

### ✅ Flujo 3: Ver Tendencias Históricas
1. Va a `/health/history`
2. Ve 7 gráficos con últimos 30 días
3. Revisa trend cards (↑↓ vs semana anterior)
4. Identifica patrones en HRV, sueño, readiness
5. Lee insights del AI

### ⏳ Flujo 4: Conectar Garmin (pendiente OAuth)
1. Va a `/health/devices`
2. Click "Conectar Garmin"
3. OAuth redirect → Login en Garmin Connect
4. Acepta permisos
5. Redirect de vuelta → Token guardado
6. Click "Sincronizar Ahora"
7. Backend fetches últimos 7 días
8. Toast "✅ Datos de Garmin sincronizados"

### ⏳ Flujo 5: Conectar Google Fit (Xiaomi/Amazfit)
1. Configura Zepp Life → Google Fit sync
2. En app: Click "Conectar Google Fit"
3. Redirect a `/health/callback?code=...`
4. Callback page muestra loading → success
5. Auto-redirect a `/health/devices`
6. Click "Sincronizar Ahora"
7. Datos aparecen en dashboard

### ⏳ Flujo 6: Importar Apple Health
1. iPhone: App Salud → Perfil → Exportar datos
2. Espera a que genere `export.xml`
3. En app web: `/health/devices`
4. Upload archivo
5. Backend parsea XML
6. Toast "✅ Importados X días de datos"
7. Datos aparecen en dashboard

---

## 🏗️ Arquitectura Backend

### Capa 1: Endpoints (`routers/health.py`)
- 11 endpoints REST para health metrics
- Autenticación con JWT Bearer tokens
- Validación con Pydantic schemas

### Capa 2: Services (lógica de negocio)
- `garmin_health_service.py` (420 líneas) - Sync desde Garmin Connect API
- `google_fit_service.py` (350 líneas) - OAuth + sync desde Google Fit
- `apple_health_service.py` (200 líneas) - Parser de export.xml
- `coach_service.py` - Readiness algorithm + AI recommendations

### Capa 3: Database (`models.py`)
- `HealthMetric` (31 columnas): HRV, sleep, Body Battery, subjective metrics
- `User` (25 columnas): Incluye tokens de Garmin/Strava/Google Fit/Apple Health
- SQLite en desarrollo, auto-switch a PostgreSQL en producción

### Readiness Algorithm
```python
Score = (40% × Body Battery) + 
        (30% × Sleep Quality) + 
        (20% × HRV vs 7-day baseline) + 
        (10% × Resting HR vs baseline) + 
        (10% × Stress inverted)

Confidence:
- High: ≥60% factores disponibles
- Medium: 30-59%
- Low: <30%
```

---

## 🎨 Stack Tecnológico

### Backend
- **Framework:** FastAPI 0.104+
- **Database:** SQLAlchemy + SQLite (dev) / PostgreSQL (prod)
- **Auth:** JWT tokens con bcrypt
- **AI:** Groq API (Llama 3.3 70B Versatile)
- **Integrations:** garminconnect, google-api-python-client

### Frontend
- **Framework:** Next.js 14+ (App Router)
- **UI:** shadcn/ui + Tailwind CSS
- **State:** TanStack Query (React Query v5)
- **Charts:** Recharts
- **Notifications:** Sonner (toast)
- **Icons:** Lucide React

---

## 📊 Cobertura de Métricas

| Métrica | Garmin | Google Fit | Apple Health | Manual |
|---------|--------|------------|--------------|--------|
| HRV | ✅ | ❌ | ✅ | ❌ |
| Resting HR | ✅ | ✅ | ✅ | ✅ |
| Body Battery | ✅ | ❌ | ❌ | ❌ |
| Sleep Duration | ✅ | ✅ | ✅ | ✅ |
| Sleep Stages | ✅ | ✅ | ❌ | ❌ |
| Sleep Score | ✅ | ❌ | ❌ | ❌ |
| Stress | ✅ | ❌ | ❌ | ❌ |
| Steps | ✅ | ✅ | ✅ | ❌ |
| Calories | ✅ | ✅ | ✅ | ❌ |
| Energía | ❌ | ❌ | ❌ | ✅ |
| Molestias | ❌ | ❌ | ❌ | ✅ |
| Ánimo | ❌ | ❌ | ❌ | ✅ |
| Motivación | ❌ | ❌ | ❌ | ✅ |

**Recomendación:** Garmin (más completo) o Google Fit + Manual (budget-friendly)

---

## 🚀 Próximos Pasos

### Fase 3: Automatización
- [ ] Cron job para sync automático diario (6 AM)
- [ ] Background tasks con Celery o APScheduler
- [ ] Retry logic para failed syncs

### Fase 4: Notificaciones
- [ ] Alertas si readiness < 40 (sugerir descanso)
- [ ] Recordatorio diario de check-in
- [ ] Email digest semanal con tendencias

### Fase 5: AI Avanzado
- [ ] Predicción de rendimiento basado en readiness
- [ ] Detección de overtraining
- [ ] Sugerencias de periodización

### Fase 6: Testing
- [ ] Unit tests para services (pytest)
- [ ] Integration tests para endpoints
- [ ] E2E tests para flujos críticos (Playwright)

### Fase 7: Deploy
- [ ] Dockerizar backend + frontend
- [ ] CI/CD con GitHub Actions
- [ ] Deploy a Vercel (frontend) + Railway (backend)
- [ ] Migración a PostgreSQL
- [ ] Setup de backups automáticos

---

## 🐛 Troubleshooting

### Backend no arranca
```powershell
# Verifica que el venv esté activado
cd backend
.\venv\Scripts\activate

# Reinstala dependencias
pip install -r requirements.txt

# Verifica la base de datos
.\venv\Scripts\python.exe check_db_status.py
```

### Frontend no compila
```powershell
# Limpia cache y reinstala
cd frontend
Remove-Item -Recurse -Force .next, node_modules
npm install
npm run dev
```

### Error CORS
```python
# En backend/app/main.py, verifica:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### No hay datos de health metrics
```powershell
# Ejecuta el seeder
cd backend
.\venv\Scripts\python.exe seed_health_data.py 1 30
```

---

## 📚 Documentación de APIs

### Swagger UI (OpenAPI)
- **URL:** http://127.0.0.1:8000/docs
- Documentación interactiva automática
- Prueba endpoints directamente en el navegador
- Incluye schemas de request/response

### ReDoc
- **URL:** http://127.0.0.1:8000/redoc
- Documentación más limpia y legible

---

## 🎯 Credenciales de Prueba

**Usuario de prueba:**
- Email: `guillermomartindeoliva@gmail.com`
- Password: (el que configuraste en registro)

**Datos de prueba:**
- 60 workouts (sincronizados)
- 30 días de health metrics
- 12 mensajes de chat con Coach AI

---

## 💡 Tips

1. **Desarrollo rápido:** Usa los datos seeded en lugar de conectar dispositivos reales
2. **Debug:** Activa SQL logging en `database.py` (`echo=True`)
3. **Performance:** Las queries están optimizadas con índices en `user_id` y `date`
4. **Baselines:** Se calculan automáticamente con rolling window de 7 días
5. **AI Context:** El Coach AI recibe TODO el contexto de health metrics en cada llamada

---

**🎉 ¡El sistema está completo y funcionando!**

Visita http://localhost:3000 para empezar a usar la plataforma.
