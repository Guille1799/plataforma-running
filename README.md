# 🏃‍♂️ RunCoach AI

> **Tu entrenador personal de running potenciado por Inteligencia Artificial**

RunCoach AI es una plataforma completa de entrenamiento de running que combina análisis avanzado de datos, integración con Garmin Connect, y coaching personalizado mediante IA (Llama 3.3 70B).

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/tests-18%2F18%20passing-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## ✨ Features Principales

### 🤖 **Coach AI Personalizado**
- **Análisis Post-Entrenamiento**: Feedback inteligente después de cada workout
- **Planes Semanales**: Genera entrenamientos de 7 días adaptados a tus objetivos
- **Chatbot Conversacional**: Pregunta cualquier cosa sobre running, el coach tiene tu historial completo
- **Análisis de Técnica**: Evaluación de tu forma de correr con recomendaciones específicas
- **3 Estilos de Coaching**: Motivador, Técnico, o Equilibrado (o personalizado)

### 📡 **Integración con Dispositivos**
- **Garmin Connect**: Sincronización automática OAuth
- **Strava**: Sincronización automática OAuth (universal hub)
  - ✨ **IDEAL para Xiaomi/Amazfit**: Conecta Zepp → Strava → RunCoach
  - Soporta: Polar, Suunto, Wahoo, Coros, y 50+ dispositivos
- **Upload Manual**: FIT, GPX, TCX (todos los dispositivos)
- Parsing completo de archivos (18+ métricas)
- Enhanced GPX parser con HR, cadence, elevation
- Almacenamiento seguro de credenciales (encriptadas)

### 📊 **Análisis Avanzado**
- **5 Zonas Cardíacas** personalizadas
- Seguimiento de progreso vs objetivos
- Métricas detalladas: pace, FC, elevación, calorías
- Identificación automática de zona de entrenamiento

### 🎯 **Sistema de Objetivos**
- Define metas (carreras, distancia, pace, frecuencia)
- Fechas límite y seguimiento
- Planes de entrenamiento orientados a objetivos
- Múltiples objetivos simultáneos

### 👤 **Perfil de Atleta**
- Nivel de running (principiante/intermedio/avanzado)
- Historial de lesiones
- Preferencias de entrenamiento
- Estilo de coaching configurable

---

## 🚀 Quick Start

### 1. Setup Automático (Recomendado)

```powershell
# Clonar repositorio
git clone <repo-url>
cd plataforma-running/backend

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
# Edita .env con tu GROQ_API_KEY

# Ejecutar setup completo (hace TODO automáticamente)
.\setup_everything.ps1
```

Este script:
- ✅ Registra tu usuario
- ✅ Conecta tu cuenta de Garmin
- ✅ Sincroniza tus entrenamientos
- ✅ Configura tu perfil de atleta
- ✅ Crea un objetivo de ejemplo
- ✅ Prueba todas las funcionalidades del Coach AI

### 2. Setup Manual

```bash
# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
uvicorn app.main:app --reload

# Acceder a la documentación interactiva
# http://127.0.0.1:8000/docs
```

---

## 📚 Documentación

- **[Guía de Usuario Completa](GUIA_COMPLETA.md)** - Cómo usar todos los endpoints
- **[Documentación Técnica](TECHNICAL_DOCS.md)** - Arquitectura, database schema, deployment
- **[CHANGELOG](CHANGELOG.md)** - Historial de versiones y features
- **[API Docs (Swagger)](http://127.0.0.1:8000/docs)** - Documentación interactiva

---

## 🏗️ Arquitectura

```
Backend (FastAPI)
├── Authentication (JWT)
├── Garmin Integration
│   ├── OAuth + Session Management
│   ├── FIT File Parsing
│   └── Activity Sync
├── Workout Management
│   ├── CRUD Operations
│   └── Metrics Storage
├── Athlete Profile
│   ├── Goals System
│   ├── Preferences
│   └── Injury Tracking
└── AI Coach (Groq/Llama 3.3)
    ├── Post-Workout Analysis
    ├── Weekly Planning
    ├── Chatbot with Memory
    └── Form/Technique Analysis

Database (SQLite/PostgreSQL)
├── Users (with athlete profile)
├── Workouts (from Garmin)
└── Chat Messages (conversation history)
```

---

## 🛠️ Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [PyJWT](https://pyjwt.readthedocs.io/) - JWT tokens

**AI & Integrations**
- [Groq](https://groq.com/) - AI inference (Llama 3.3 70B)
- [garminconnect](https://github.com/cyberjunky/python-garminconnect) - Garmin API wrapper
- [fitparse](https://github.com/dtcooper/python-fitparse) - FIT file parser

**Security**
- bcrypt - Password hashing
- Fernet - Credential encryption
- JWT - Stateless authentication

---

## 📊 API Endpoints

### 🔐 Auth (3)
- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/login` - Iniciar sesión
- `POST /api/v1/auth/refresh` - Refrescar token

### 🏃 Workouts (2)
- `GET /api/v1/workouts` - Listar entrenamientos
- `GET /api/v1/workouts/{id}` - Ver entrenamiento específico

### 📡 Garmin (4)
- `POST /api/v1/garmin/connect` - Conectar Garmin
- `POST /api/v1/garmin/sync` - Sincronizar actividades
- `GET /api/v1/garmin/status` - Estado de conexión
- `DELETE /api/v1/garmin/disconnect` - Desconectar

### 👤 Profile (6)
- `GET /api/v1/profile` - Ver perfil
- `PATCH /api/v1/profile` - Actualizar perfil
- `GET /api/v1/profile/goals` - Listar objetivos
- `POST /api/v1/profile/goals` - Crear objetivo
- `PATCH /api/v1/profile/goals/{index}` - Actualizar objetivo
- `DELETE /api/v1/profile/goals/{index}` - Eliminar objetivo

### 🤖 Coach AI (10)
- `POST /api/v1/coach/analyze/{workout_id}` - Analizar entrenamiento
- `POST /api/v1/coach/analyze-form/{workout_id}` - Analizar técnica
- `POST /api/v1/coach/plan` - Generar plan semanal
- `GET /api/v1/coach/hr-zones` - Ver zonas cardíacas
- `POST /api/v1/coach/chat` - Chatear con el coach
- `GET /api/v1/coach/chat/history` - Historial de chat
- `DELETE /api/v1/coach/chat/history` - Limpiar historial

**Total: 25 endpoints** disponibles

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=app tests/

# Tests específicos
pytest tests/test_auth.py -v
```

**Status:** ✅ 18/18 tests passing

---

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con bcrypt
- ✅ Tokens JWT con expiración
- ✅ Credenciales de Garmin encriptadas (Fernet)
- ✅ Validación de inputs con Pydantic
- ✅ Prevención de SQL injection (ORM)
- ✅ CORS configurado
- ✅ HTTPS ready

---

## 🚀 Deployment

### Development
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Production
Ver [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md) para instrucciones completas de deployment con Docker, PostgreSQL, y configuración de producción.

---

## 📈 Roadmap

### ✅ v0.1.0 (Actual)
- [x] Auth system
- [x] Garmin integration
- [x] AI Coach completo
- [x] Goals & profile system
- [x] 25 API endpoints

### 🚧 v0.2.0 (Próximo)
- [ ] Frontend (Next.js)
- [ ] Alembic migrations
- [ ] Advanced FIT parsing (cadence, vertical oscillation)
- [ ] PostgreSQL setup
- [ ] Redis caching

### 🔮 v0.3.0 (Futuro)
- [ ] Strava integration
- [ ] Weather API
- [ ] Voice coaching
- [ ] Race predictor
- [ ] Social features

---

## 🤝 Contributing

Contributions are welcome! Por favor:

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 License

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 👨‍💻 Autor

**Guillermo Martín de Oliva**
- Email: guillermomartindeoliva@gmail.com
- GitHub: [@guillermomartindeoliva](https://github.com/guillermomartindeoliva)

---

## 🙏 Agradecimientos

- [Groq](https://groq.com/) por la API gratuita de Llama 3.3
- [garminconnect](https://github.com/cyberjunky/python-garminconnect) por el wrapper de Garmin
- [FastAPI](https://fastapi.tiangolo.com/) por el increíble framework
- Comunidad de running por la inspiración

---

## 📞 Soporte

- **Issues:** [GitHub Issues](https://github.com/tu-usuario/plataforma-running/issues)
- **Docs:** [Documentación Completa](GUIA_COMPLETA.md)
- **API:** [Swagger UI](http://127.0.0.1:8000/docs)

---

<p align="center">
  Hecho con ❤️ y 🏃 por corredores, para corredores
</p>

<p align="center">
  <strong>¡Corre más inteligente, no más difícil! 🚀</strong>
</p>