# 🏃‍♂️ RunCoach AI - Guía Completa de Uso

## 🚀 Setup Rápido (Una Vez)

### Ejecutar Setup Automático
```powershell
cd c:\Users\guill\Desktop\plataforma-running\backend
.\setup_everything.ps1
```

Este script hace TODO automáticamente:
- ✅ Registra usuario
- ✅ Conecta Garmin
- ✅ Sincroniza workouts
- ✅ Configura perfil
- ✅ Crea objetivo
- ✅ Prueba todas las features del Coach AI

---

## 📚 API Endpoints - Guía de Uso

### 🔐 Autenticación

#### Registro
```bash
POST /api/v1/auth/register
{
  "name": "Guillermo",
  "email": "tu@email.com",
  "password": "TestPass123!"
}
```

#### Login
```bash
POST /api/v1/auth/login
{
  "email": "tu@email.com",
  "password": "TestPass123!"
}
```

**Respuesta:** Token JWT válido por 30 minutos

---

### 📡 Garmin Connect

#### Conectar Cuenta
```bash
POST /api/v1/garmin/connect
Authorization: Bearer {token}
{
  "email": "garmin@email.com",
  "password": "garmin_password"
}
```

#### Sincronizar Entrenamientos
```bash
POST /api/v1/garmin/sync
Authorization: Bearer {token}
{
  "start_date": "2025-11-01",  # Opcional
  "end_date": "2025-11-13"     # Opcional
}
```

**Respuesta:** Número de workouts sincronizados + IDs

#### Ver Estado de Conexión
```bash
GET /api/v1/garmin/status
Authorization: Bearer {token}
```

---

### 🏃 Workouts

#### Listar Entrenamientos
```bash
GET /api/v1/workouts?skip=0&limit=50
Authorization: Bearer {token}
```

#### Ver Workout Específico
```bash
GET /api/v1/workouts/{workout_id}
Authorization: Bearer {token}
```

---

### 👤 Perfil de Atleta

#### Ver Perfil
```bash
GET /api/v1/profile
Authorization: Bearer {token}
```

#### Actualizar Perfil
```bash
PATCH /api/v1/profile
Authorization: Bearer {token}
{
  "running_level": "intermediate",    # beginner/intermediate/advanced
  "max_heart_rate": 180,
  "coaching_style": "balanced",       # motivator/technical/balanced/custom
  "preferences": {
    "music": true,
    "time_of_day": "evening",
    "terrain_preference": "road"
  }
}
```

---

### 🎯 Objetivos

#### Crear Objetivo
```bash
POST /api/v1/profile/goals
Authorization: Bearer {token}
{
  "name": "Sub-40 en 10K",
  "goal_type": "race",              # race/distance/pace/frequency/health
  "target_value": "39:59",
  "deadline": "2025-12-31T00:00:00Z",
  "description": "Correr 10K en menos de 40 minutos"
}
```

#### Listar Objetivos
```bash
GET /api/v1/profile/goals
Authorization: Bearer {token}
```

#### Actualizar Objetivo
```bash
PATCH /api/v1/profile/goals/{index}
Authorization: Bearer {token}
{
  "completed": true
}
```

#### Eliminar Objetivo
```bash
DELETE /api/v1/profile/goals/{index}
Authorization: Bearer {token}
```

---

### 🤖 Coach AI - Análisis

#### Analizar Workout (Post-Entrenamiento)
```bash
POST /api/v1/coach/analyze/{workout_id}
Authorization: Bearer {token}
```

**Proporciona:**
- Resumen del esfuerzo
- Análisis técnico (pace, FC, zonas)
- Recomendación para próximo entrenamiento
- Emoji de reacción

#### Analizar Técnica de Running
```bash
POST /api/v1/coach/analyze-form/{workout_id}
Authorization: Bearer {token}
```

**Proporciona:**
- Métricas de forma
- Problemas detectados
- Recomendaciones técnicas
- Ejercicios/drills sugeridos

#### Ver Zonas Cardíacas
```bash
GET /api/v1/coach/hr-zones
Authorization: Bearer {token}
```

**Respuesta:** 5 zonas con rangos de BPM

---

### 📅 Coach AI - Planificación

#### Generar Plan Semanal
```bash
POST /api/v1/coach/plan?start_date=2025-11-18
Authorization: Bearer {token}
```

**Proporciona:**
- Plan de 7 días
- Tipos de entrenamiento variados
- Distancias y ritmos objetivo
- Volumen semanal total

---

### 💬 Coach AI - Chatbot

#### Conversar con el Coach
```bash
POST /api/v1/coach/chat
Authorization: Bearer {token}
{
  "message": "¿Qué ejercicios me recomiendas para mejorar cadencia?"
}
```

**Mantiene contexto:** El coach recuerda toda la conversación

#### Ver Historial de Chat
```bash
GET /api/v1/coach/chat/history?limit=50
Authorization: Bearer {token}
```

#### Limpiar Historial
```bash
DELETE /api/v1/coach/chat/history
Authorization: Bearer {token}
```

---

## 🎨 Estilos de Coaching

### Motivator
- Energético y entusiasta
- Enfocado en celebrar logros
- Usa emojis y lenguaje animado
- Positivo incluso en entrenamientos difíciles

### Technical
- Analítico y basado en datos
- Enfocado en eficiencia y técnica
- Explicaciones fisiológicas detalladas
- Referencias científicas

### Balanced (Default)
- Mix de motivación y técnica
- Reconoce logros y áreas de mejora
- Usa datos sin abrumar
- Tono amigable y profesional

### Custom
Usa `preferences.custom_prompt` para definir tu propio estilo:
```json
{
  "coaching_style": "custom",
  "preferences": {
    "custom_prompt": "Eres un coach directo y sin rodeos, enfocado en resultados..."
  }
}
```

---

## 📊 Zonas Cardíacas

| Zona | Nombre | % FCM | Descripción |
|------|--------|-------|-------------|
| 1 | Recovery | 50-60% | Recuperación activa, conversación fácil |
| 2 | Aerobic Base | 60-70% | Base aeróbica, ritmo cómodo |
| 3 | Tempo | 70-80% | Ritmo controlado, conversación difícil |
| 4 | Threshold | 80-90% | Umbral anaeróbico, esfuerzo alto |
| 5 | VO2 Max | 90-100% | Máxima intensidad, insostenible |

---

## 💡 Tips y Mejores Prácticas

### Para Mejor Análisis
1. Sincroniza workouts regularmente
2. Configura tu FCM correctamente
3. Define objetivos claros
4. Usa el chatbot para preguntas específicas

### Para Planes Personalizados
1. Mantén tu perfil actualizado
2. Registra lesiones activas
3. Actualiza objetivos según progreso
4. Configura preferencias de horario

### Para Chatbot Efectivo
- Pregunta específicamente
- Menciona contexto (ej: "para mi próximo 10K")
- Pide ejercicios concretos
- Consulta sobre dudas técnicas

---

## 🔧 Troubleshooting

### Token Expirado
```bash
POST /api/v1/auth/refresh
{
  "refresh_token": "tu_refresh_token"
}
```

### Garmin No Sincroniza
1. Verifica credenciales
2. Reconecta: `POST /api/v1/garmin/connect`
3. Intenta sync con fechas específicas

### Coach No Responde
- Verifica que GROQ_API_KEY esté configurado
- Revisa que tengas workouts sincronizados
- Asegúrate de tener FCM configurado

---

## 📈 Roadmap de Features

### ✅ Implementado
- [x] Autenticación JWT
- [x] Integración Garmin
- [x] Análisis post-workout
- [x] Plan semanal
- [x] Chatbot con memoria
- [x] Análisis de técnica
- [x] Zonas cardíacas
- [x] Perfil de atleta
- [x] Sistema de objetivos

### 🚧 Próximamente
- [ ] Frontend React/Next.js
- [ ] Integraciones premium (Spotify, Weather, Strava)
- [ ] Análisis avanzado de FIT (cadencia, oscilación vertical)
- [ ] Voice coach durante entrenamientos
- [ ] Race predictor
- [ ] Injury prevention system
- [ ] Social features (leaderboards, challenges)

---

## 🎯 Ejemplos de Uso Completo

### Workflow Típico

1. **Lunes - Planificar Semana**
```bash
POST /api/v1/coach/plan
# Obtén plan de 7 días
```

2. **Miércoles - Analizar Entrenamiento**
```bash
POST /api/v1/coach/analyze/5
# Feedback post-workout
```

3. **Viernes - Consultar al Coach**
```bash
POST /api/v1/coach/chat
{ "message": "¿Debo hacer el tempo run mañana o descansar?" }
```

4. **Domingo - Revisar Progreso**
```bash
GET /api/v1/workouts?skip=0&limit=10
# Ver últimos 10 entrenamientos
```

---

## 📞 Soporte

- **API Docs:** http://127.0.0.1:8000/docs
- **Repositorio:** (tu repo)
- **Issues:** (tu sistema de tickets)

---

**Versión:** 0.1.0  
**Última actualización:** 13 Nov 2025  
**Estado:** ✅ Production Ready
