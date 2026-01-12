# 📊 Impacto de "Use Case" en el Sistema

**Fecha:** 2026-01-10  
**Propósito:** Documentar qué hace el sistema según la opción de "main goal" que el usuario elige en el onboarding.

---

## 🎯 Opciones de "Main Goal" (Use Case)

Cuando el usuario completa el onboarding, selecciona uno de estos 4 objetivos principales:

1. **Fitness Tracker** (`fitness_tracker`)
2. **Training Coach** (`training_coach`)
3. **Race Prep** (`race_prep`)
4. **General Health** (`general_health`)

---

## 🔄 Qué Hace el Sistema con Cada Opción

### 1. Fitness Tracker (`fitness_tracker`)

**Guía personalizada del Coach:**
```
"Focus on consistency and daily movement. No pressure for intensity."
```

**Qué significa:**
- El coach enfatiza la **consistencia** sobre la intensidad
- Recomendaciones más suaves, sin presión por entrenar duro
- Enfoque en movimiento diario y actividad general
- Menos énfasis en métricas avanzadas de rendimiento

**Ideal para:**
- Usuarios que quieren mantenerse activos
- Personas que buscan mejorar su salud general
- No necesariamente enfocados en competir o mejorar tiempos

---

### 2. Training Coach (`training_coach`)

**Guía personalizada del Coach:**
```
"Follow structured training plans. Balance easy and hard efforts."
```

**Qué significa:**
- El coach enfatiza seguir **planes de entrenamiento estructurados**
- Balance entre entrenamientos fáciles y duros
- Recomendaciones más técnicas y estructuradas
- Mayor énfasis en progresión y periodización

**Ideal para:**
- Usuarios que quieren mejorar su rendimiento de forma estructurada
- Personas que buscan coaching personalizado
- Atletas que quieren seguir planes de entrenamiento

---

### 3. Race Prep (`race_prep`)

**Guía personalizada del Coach:**
```
"Follow your training plan religiously. Every workout matters for peak race fitness."
```

**Qué significa:**
- El coach enfatiza **seguir el plan al pie de la letra**
- Cada entrenamiento es importante para alcanzar el pico de forma
- Recomendaciones más estrictas y enfocadas en objetivos
- Mayor énfasis en adherencia al plan y disciplina

**Ideal para:**
- Usuarios entrenando para una carrera específica
- Atletas con fecha objetivo clara
- Personas que necesitan estructura estricta

---

### 4. General Health (`general_health`)

**Guía personalizada del Coach:**
```
"Exercise for overall wellness. Enjoy the process, don't obsess over metrics."
```

**Qué significa:**
- El coach enfatiza el **bienestar general**
- Disfrutar del proceso, no obsesionarse con métricas
- Recomendaciones más relajadas y orientadas a salud
- Menos presión por rendimiento y más por disfrute

**Ideal para:**
- Usuarios que buscan mejorar su salud general
- Personas que no quieren presión por rendimiento
- Enfoque en bienestar más que en competencia

---

## 📍 Dónde se Usa

### 1. Recomendaciones Personalizadas del Coach

**Endpoint:** `GET /api/v1/coach/personalized-recommendation`

El `use_case` se combina con:
- `primary_device` (Garmin, Xiaomi, etc.)
- `coach_style_preference` (motivator, technical, balanced, custom)

Para generar recomendaciones completamente personalizadas.

**Código relevante:**
```python
# backend/app/routers/coach.py líneas 574-586
use_case_guidance = {
    'fitness_tracker': 'Focus on consistency and daily movement. No pressure for intensity.',
    'training_coach': 'Follow structured training plans. Balance easy and hard efforts.',
    'race_prep': 'Follow your training plan religiously. Every workout matters for peak race fitness.',
    'general_health': 'Exercise for overall wellness. Enjoy the process, don\'t obsess over metrics.'
}

personalized['use_case_guidance'] = use_case_guidance.get(use_case, use_case_guidance['general_health'])
```

### 2. Almacenamiento en Base de Datos

**Campo:** `user.use_case` (String)

Se guarda cuando el usuario completa el onboarding y se puede consultar después para personalizar la experiencia.

---

## 🔮 Impacto Futuro (Pendiente de Implementar)

Actualmente, el `use_case` solo afecta las **recomendaciones del coach**. Pero podría usarse para:

- [ ] **Filtrado de contenido:** Mostrar diferentes widgets en el dashboard según el use case
- [ ] **Notificaciones personalizadas:** Diferentes tipos de recordatorios según el objetivo
- [ ] **Sugerencias de features:** Promocionar diferentes funcionalidades según el use case
- [ ] **Planes de entrenamiento:** Pre-filtrar o sugerir planes según el objetivo
- [ ] **Métricas destacadas:** Mostrar diferentes métricas en el dashboard según el use case

---

## 📝 Notas

- El `use_case` se puede cambiar después del onboarding (aunque no hay UI para esto aún)
- Si el usuario no completa el onboarding, se usa `'general_health'` como default
- El `use_case` se combina con otros factores (device, coach style) para personalización completa
