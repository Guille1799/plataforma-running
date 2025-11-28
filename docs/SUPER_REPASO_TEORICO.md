# 🎓 SUPER REPASO TEÓRICO - Plataforma Running

**¿Qué es esto? ¿Por qué existe? ¿Cómo funciona?**

---

## 1️⃣ ¿QUÉ ES PLATAFORMA RUNNING?

### Definición Simple
**RunCoach AI** es una aplicación web que ayuda a corredores a:
- 📅 Crear planes de entrenamiento personalizados
- 📊 Analizar sus entrenamientos y métricas
- 🤖 Recibir coaching personalizado usando IA
- 📱 Sincronizar entrenamientos con Garmin, Strava, etc.
- 🎯 Cumplir objetivos de carrera

### El Problema que Resuelve
Un corredor típico enfrenta:
- ❌ No sabe cómo entrenar (sin plan = caos)
- ❌ No entiende sus métricas (¿a qué ritmo debo correr?)
- ❌ No tiene coach personal (¡caro!)
- ❌ Sus entrenamientos están dispersos (Garmin, Strava, Apple Watch, etc.)
- ❌ No sabe si está sobreentrenando

### La Solución
Una plataforma que:
- ✅ Genera planes automáticos basados en objetivos
- ✅ Explica qué significan tus datos
- ✅ Usa IA (Llama 3.3) para coaching inteligente
- ✅ Sincroniza entrenamientos de múltiples fuentes
- ✅ Detecta sobreentrenamiento con análisis de HRV

---

## 2️⃣ STACK TECNOLÓGICO

### Frontend (Lo que VES en el navegador)
```
Next.js 16 (React framework)
├─ TypeScript (lenguaje seguro)
├─ React 19 (componentes)
├─ Tailwind CSS (estilos)
└─ Shadcn UI (componentes bonitos)

Corre en: http://localhost:3001
```

**¿Por qué Next.js?**
- Súper rápido (Turbopack)
- Server-side rendering (SEO)
- API routes integradas
- Deployment fácil en Vercel

### Backend (Lo que PROCESA los datos)
```
FastAPI (framework Python)
├─ Python 3.13 (lenguaje)
├─ SQLAlchemy (base de datos)
├─ Pydantic (validación)
└─ JWT (seguridad)

Corre en: http://localhost:3000
```

**¿Por qué FastAPI?**
- Muy rápido
- Documentación automática (/docs)
- Validación built-in
- Async/await para operaciones lentas

### Base de Datos
```
SQLite (desarrollo) → runcoach.db
PostgreSQL (producción) → Render

Tablas principales:
├─ users (registros de usuarios)
├─ workouts (entrenamientos)
├─ athlete_profiles (info del corredor)
├─ training_plans (planes creados)
└─ goals (objetivos de carrera)
```

### IA / LLM
```
Groq API
└─ Llama 3.3 70B (modelo de IA)

Usado para:
- Analizar entrenamientos
- Dar consejos de entrenamiento
- Generar recomendaciones personalizadas
```

### Deployment (Producción)
```
Frontend → Vercel (hosting + CI/CD)
Backend → Render (hosting + CI/CD)
Database → PostgreSQL en la nube
```

---

## 3️⃣ ARQUITECTURA DEL SISTEMA

### Flujo de una Request (Ejemplo: Crear Plan)

```
1. Usuario en frontend hace click: "Crear Plan"
   ↓
2. Frontend envía POST a backend: /api/v1/training-plans/generate
   Datos: { objective: "marathon", target_date: "2025-05-15", priority: "finish" }
   ↓
3. Backend recibe la request:
   - Valida datos con Pydantic
   - Busca al usuario en base de datos
   - Calcula duraciones posibles
   ↓
4. Backend llama servicio de IA (Groq):
   - "Dame un plan de entrenamiento para maratón"
   - IA devuelve plan JSON
   ↓
5. Backend guarda plan en base de datos
   ↓
6. Backend devuelve plan a frontend: { id: 123, weeks: [...] }
   ↓
7. Frontend muestra el plan al usuario
   ✅ Plan creado exitosamente
```

### Estructura de Carpetas

```
plataforma-running/
│
├─ app/                          ← Frontend (Next.js)
│  ├─ (auth)/login/page.tsx      Login page
│  ├─ (dashboard)/dashboard/     Dashboard pages
│  ├─ workouts/                  Workout pages
│  └─ components/                React components
│
├─ backend/                       ← Backend (FastAPI)
│  ├─ app/
│  │  ├─ main.py                 Punto de entrada del API
│  │  ├─ routers/                Endpoints del API
│  │  │  ├─ auth.py              Login, registro
│  │  │  ├─ training_plans.py    Crear/ver planes
│  │  │  ├─ coach.py             AI coaching
│  │  │  ├─ workouts.py          Gestión de entrenamientos
│  │  │  ├─ garmin.py            Sincronización Garmin
│  │  │  └─ ...
│  │  ├─ services/               Lógica de negocio
│  │  │  ├─ coach_service.py     Cálculo de zonas HR
│  │  │  ├─ training_plan_service.py   Generar planes
│  │  │  ├─ events_service.py    Buscar carreras
│  │  │  └─ ...
│  │  ├─ models/                 Modelos de DB
│  │  │  └─ models.py
│  │  └─ database.py             Conexión a DB
│  ├─ requirements.txt           Dependencias Python
│  └─ tests/                     Tests
│
├─ docs/                         ← Documentación
├─ docker-compose.prod.yml       Docker configuration
└─ README.md                     Instrucciones inicio rápido
```

---

## 4️⃣ COMPONENTES PRINCIPALES

### Backend Endpoints (API)

**Autenticación**
```
POST /auth/register         → Crear cuenta
POST /auth/login            → Iniciar sesión
POST /auth/refresh          → Renovar token
```

**Entrenamientos**
```
GET  /workouts              → Listar tus entrenamientos
POST /workouts              → Crear entrenamiento
GET  /workouts/{id}         → Ver entrenamiento específico
```

**Planes de Entrenamiento**
```
POST /training-plans/generate        → Crear nuevo plan
GET  /training-plans                 → Listar planes
GET  /training-plans/{id}            → Ver plan específico
GET  /training-plans/duration-options → Ver duraciones posibles
```

**Sincronización Garmin**
```
POST /garmin/connect        → Conectar Garmin (OAuth)
POST /garmin/sync           → Sincronizar entrenamientos
GET  /garmin/status         → Ver estado conexión
```

**Strava**
```
POST /strava/connect        → Conectar Strava
POST /strava/sync           → Sincronizar
```

**Eventos/Carreras**
```
GET /events/races/search?query=marathon   → Buscar carreras
```

**AI Coach**
```
POST /coach/analyze/{workout_id}      → Analizar un entrenamiento
POST /coach/chat                       → Chatear con el coach
GET  /coach/chat/history               → Ver historial
```

---

## 5️⃣ FLUJOS PRINCIPALES DEL NEGOCIO

### Flujo 1: Un Nuevo Usuario Se Registra

```
1. Usuario accede a http://localhost:3001
   ↓
2. Ve pantalla de login, clickea "Registrarse"
   ↓
3. Completa formulario:
   - Email: usuario@email.com
   - Contraseña: password123
   - Nombre: Juan
   ↓
4. Frontend envía POST /auth/register
   ↓
5. Backend:
   - Valida email (único)
   - Hashea contraseña con bcrypt
   - Crea usuario en DB
   - Retorna JWT token
   ↓
6. Frontend guarda token en localStorage
   ↓
7. Usuario es redirigido al dashboard
   ✅ Usuario registrado
```

### Flujo 2: Crear un Plan de Entrenamiento

```
1. Usuario va a "Crear Plan"
   ↓
2. Formulario de 6 pasos:
   PASO 1: ¿Cuál es tu objetivo?
           Options: Correr una carrera / Mejorar forma física
   
   PASO 2: Tipo de plan (si es carrera)
           Options: Maratón, Half Marathon, 10K, 5K
   
   PASO 3: Prioridad
           Options: "Acabar", "Competitivo", "Ganar"
   
   PASO 4: Búsqueda de carrera
           Input: "Madrid Marathon 2025"
           Backend busca en DB de carreras
   
   PASO 5: Seleccionar carrera
   
   PASO 6: Duración del plan
           Options: 12 semanas, 16 semanas, 20 semanas
   
   ↓
3. Usuario hace click "Crear Plan"
   ↓
4. Frontend envía POST /training-plans/generate
   {
     objective_type: "race",
     race_id: 42,
     priority: "competitive",
     duration_weeks: 16
   }
   ↓
5. Backend:
   - Lee usuario del token JWT
   - Lee info de carrera
   - Calcula zonas de HR usando Karvonen
   - Llama a Groq: "Dame plan de 16 semanas para maratón"
   - Groq retorna plan JSON
   - Guarda en DB
   ↓
6. Frontend recibe plan y lo muestra
   ✅ Plan creado
```

### Flujo 3: Sincronizar Entrenamientos desde Garmin

```
1. Usuario va a Perfil → Conectar Garmin
   ↓
2. Clickea "Conectar Garmin"
   ↓
3. Frontend lo redirige a Garmin (OAuth)
   ↓
4. Usuario se loguea en Garmin
   ↓
5. Garmin devuelve "código de autorización" al backend
   ↓
6. Backend intercambia código por "refresh token"
   - Lo almacena encriptado en la DB
   ✓ Usuario autenticado con Garmin
   ↓
7. Backend llama a Garmin API
   - Obtiene últimos 50 entrenamientos
   - Procesa cada uno (distancia, ritmo, HR, etc.)
   ↓
8. Backend crea Workout en DB para cada entrenamiento
   ↓
9. Frontend muestra lista de entrenamientos
   ✅ Entrenamientos sincronizados
```

---

## 6️⃣ CONCEPTOS CLAVE

### JWT (JSON Web Token)
- Es como un "carnet de identidad digital"
- Contiene: `{ user_id: 5, exp: 2025-11-28 }`
- Se envía en cada request: `Authorization: Bearer <token>`
- Backend verifica firma del token
- Si es válido, sabe quién eres

### Karvonen Formula (Cálculo de Zonas HR)
```
Es la fórmula que usamos para calcular a qué ritmo cardíaco 
debes entrenar.

FC Máxima = 220 - edad
           (o una estimación basada en entrenamientos)

FC Reserva = FC Máxima - FC Reposo

Zone 2 (Fácil):
  HR = FC Reposo + (FC Reserva × 0.6-0.7)
  Ejemplo: Usuario de 35 años, FC Max 185, FC Reposo 60
  HR = 60 + (185-60) × 0.65 = 60 + 81 = 141 bpm

Zone 5 (Máxima):
  HR = FC Reposo + (FC Reserva × 0.9-1.0)
  HR = 60 + 125 = 185 bpm
```

### Sobreentrenamiento (Overtraining)
- El cuerpo está cansado por entrenamiento excesivo
- Síntomas: HR elevada en reposo, fatiga, lesiones
- Se detecta con HRV (Heart Rate Variability)
- Si HR en reposo sube 5+ bpm → posible overtraining

### HRV (Heart Rate Variability)
- Variación en tiempo entre latidos del corazón
- HRV alta = recuperación buena
- HRV baja = fatiga/sobreentrenamiento
- Se mide en ms (milisegundos)

---

## 7️⃣ ESTADO ACTUAL DEL PROYECTO

### ✅ Completado

**Backend (90%)**
- ✅ Autenticación JWT completa
- ✅ CRUD de entrenamientos
- ✅ Sincronización Garmin OAuth
- ✅ Sincronización Strava
- ✅ Cálculo de zonas cardíacas (Karvonen)
- ✅ Generación de planes de entrenamiento
- ✅ AI Coach (Llama 3.3 via Groq)
- ✅ HRV Analysis
- ✅ Detección de overtraining
- ✅ API documentation (/docs)
- ✅ 17+ routers (endpoints)
- ✅ Docker setup

**Frontend (85%)**
- ✅ Registro e login
- ✅ Dashboard con métricas
- ✅ Formulario de 6 pasos para crear plan
- ✅ Búsqueda de carreras
- ✅ Visualización de entrenamientos
- ✅ Perfil de usuario
- ✅ Sincronización Garmin (UI)
- ✅ Responsive design
- ✅ Dark mode

**DevOps**
- ✅ Docker (backend + frontend)
- ✅ docker-compose.prod.yml
- ✅ .env configuration templates
- ✅ GitHub Actions CI/CD ready
- ✅ Vercel deployment (live)
- ✅ Render deployment (live)

### 🔲 Por Hacer / Mejoras

**Backend**
- 🔲 Caché en búsqueda de eventos (performance)
- 🔲 Migrations con Alembic (mejor que create_all)
- 🔲 Advanced analytics (VDOT, FTP estimation)
- 🔲 Real-time notifications
- 🔲 Rate limiting
- 🔲 Logging centralizado

**Frontend**
- 🔲 Gráficos de progreso (charts.js)
- 🔲 E2E tests (Playwright)
- 🔲 Mobile app (React Native)
- 🔲 Offline mode
- 🔲 Push notifications
- 🔲 Advanced filters

**Integraciones**
- 🔲 Apple Health
- 🔲 Fitbit
- 🔲 Suunto
- 🔲 Coros
- 🔲 Polar

---

## 8️⃣ CÓMO FUNCIONA EN DESARROLLO

### Terminal 1: Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 3000
```
- Corre en http://localhost:3000
- Auto-recarga cuando cambias código (--reload)
- Documentación en http://localhost:3000/docs

### Terminal 2: Frontend
```bash
npm run dev -- -p 3001
```
- Corre en http://localhost:3001
- Auto-recarga con hot module replacement
- Conecta a backend en http://localhost:3000

### Base de Datos
- **Desarrollo**: SQLite local (runcoach.db)
- **Producción**: PostgreSQL en Render

---

## 9️⃣ CÓMO PROBAR LOCALMENTE

### Paso 1: Registrarse
```
URL: http://localhost:3001
Email: test@example.com
Password: password123
```

### Paso 2: Completar Perfil
- Edad: 35
- Peso: 75 kg
- Altura: 180 cm
- FC Máxima: 185 bpm
- Nivel: Intermedio

### Paso 3: Crear Plan
- Objetivo: Correr una carrera
- Tipo: Maratón
- Prioridad: Competitive
- Carrera: "Madrid Marathon"
- Duración: 16 semanas

### Paso 4: Ver Plan
- Dashboard muestra el plan creado
- Puedes ver zonas de frecuencia cardíaca
- Puedes ver entrenamientos propuestos

---

## 🔟 TECNOLOGÍAS CLAVE (Explicadas Simple)

| Tech | ¿Qué es? | ¿Por qué? |
|------|---------|---------|
| FastAPI | Framework web Python | Rápido, con docs auto, validación built-in |
| Next.js | Framework React | SSR, performance, deployment fácil |
| SQLAlchemy | ORM (acceso a DB) | No escribas SQL, usa Python |
| Pydantic | Validación de datos | Asegura que datos sean válidos |
| JWT | Autenticación sin sesión | Stateless, escalable |
| Groq API | Acceso a Llama 3.3 | IA poderosa sin GPU propia |
| Docker | Containerización | App funciona igual en dev y prod |
| Vercel | Hosting frontend | Deployments automáticos, muy rápido |
| Render | Hosting backend | PostgreSQL incluida, CI/CD fácil |

---

## 🎯 RESUMEN EJECUTIVO

**Plataforma Running** es una app web que:

1. **Registra usuarios** con JWT tokens
2. **Crea planes de entrenamiento** usando IA (Llama 3.3)
3. **Sincroniza entrenamientos** desde Garmin, Strava, etc.
4. **Analiza métricas** (HR zones, VDOT, overtraining)
5. **Proporciona coaching** personalizado mediante IA

**Stack:** Next.js (frontend) + FastAPI (backend) + PostgreSQL (prod)
**Deployment:** Vercel + Render (ya en producción)
**Estado:** 90% completada, lista para beta testing

---

## 📞 PRÓXIMOS PASOS

Ahora que entiendes la teoría:

1. **Tester funcionalidades** (crear cuenta, plan, etc.)
2. **Revisar el código** (backend routers, frontend components)
3. **Identificar bugs** (si los hay)
4. **Hacer mejoras** (performance, features, UX)

¿Listo para testear? 🚀
