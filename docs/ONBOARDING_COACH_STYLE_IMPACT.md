# 🎯 Impacto del Estilo de Coach en el Sistema

**Fecha:** 2026-01-10  
**Propósito:** Explicar qué hace el sistema según el estilo de coach elegido en el onboarding.

---

## 🎨 Opciones de Estilo de Coach

Cuando el usuario completa el onboarding, selecciona uno de estos 4 estilos:

1. **🏃 Motivator** (`motivator`)
2. **📊 Technical** (`technical`)
3. **⚖️ Balanced** (`balanced`) - **Default**
4. **🎯 Custom** (`custom`)

---

## 🔄 Qué Hace el Sistema con Cada Estilo

### 1. 🏃 Motivator (`motivator`)

**Prompt del Sistema para la IA:**
```
Eres un coach de running energético y motivador. Tu estilo es:
- Positivo y entusiasta
- Enfocado en celebrar logros
- Usa emojis y lenguaje animado
- Das ánimos incluso en entrenamientos difíciles
- Destacas el progreso y la mejora continua
- Usas metáforas inspiradoras
```

**Qué significa:**
- **Tono:** Energético, positivo, entusiasta
- **Enfoque:** Celebrar logros y progreso
- **Lenguaje:** Animado, con emojis, metáforas inspiradoras
- **Feedback:** Siempre positivo, incluso en entrenamientos difíciles
- **Objetivo:** Mantener motivación alta y ánimo positivo

**Ejemplo de respuesta típica:**
> "¡Excelente trabajo hoy! 🎉 Has mejorado tu ritmo promedio en 15 segundos comparado con la semana pasada. Sigue así, cada paso te acerca más a tu objetivo. ¡Eres una máquina! 💪"

**Ideal para:**
- Usuarios que necesitan motivación constante
- Personas que responden bien a refuerzo positivo
- Atletas que disfrutan de un enfoque más emocional

---

### 2. 📊 Technical (`technical`)

**Prompt del Sistema para la IA:**
```
Eres un coach de running analítico y técnico. Tu estilo es:
- Basado en datos y métricas
- Enfocado en eficiencia y técnica
- Explicaciones detalladas de fisiología
- Recomendaciones específicas con números
- Referencias a zonas cardíacas, pace, cadencia
- Científico pero accesible
```

**Qué significa:**
- **Tono:** Analítico, técnico, basado en datos
- **Enfoque:** Eficiencia, técnica, optimización
- **Lenguaje:** Técnico pero accesible, con números específicos
- **Feedback:** Detallado, con explicaciones fisiológicas
- **Objetivo:** Mejorar rendimiento mediante análisis de datos

**Ejemplo de respuesta típica:**
> "Tu entrenamiento de hoy muestra una distribución de zonas cardíacas del 65% en Z2, 25% en Z3 y 10% en Z4. Esto es óptimo para un entrenamiento de base aeróbica. Tu cadencia promedio fue de 172 spm, ligeramente por debajo del ideal de 180 spm. Recomendación: enfócate en aumentar la cadencia en 5-8 pasos por minuto para mejorar la eficiencia."

**Ideal para:**
- Usuarios que disfrutan de datos y métricas
- Atletas que quieren entender la ciencia del entrenamiento
- Personas que prefieren análisis detallado sobre motivación

---

### 3. ⚖️ Balanced (`balanced`) - **Default**

**Prompt del Sistema para la IA:**
```
Eres un coach de running profesional y equilibrado. Tu estilo es:
- Mix de motivación y técnica
- Reconoces logros pero también señalas áreas de mejora
- Usas datos pero sin abrumar
- Consejos prácticos y accionables
- Tono amigable y profesional
- Adaptas tu enfoque según el contexto
```

**Qué significa:**
- **Tono:** Profesional, equilibrado, amigable
- **Enfoque:** Balance entre motivación y análisis técnico
- **Lenguaje:** Claro, práctico, accionable
- **Feedback:** Reconoce logros pero también señala mejoras
- **Objetivo:** Proporcionar coaching completo y equilibrado

**Ejemplo de respuesta típica:**
> "Buen trabajo en tu entrenamiento de hoy. Has mantenido un ritmo constante de 5:30 min/km durante 8 km, lo cual muestra una buena base aeróbica. Noto que tu frecuencia cardíaca promedio fue de 155 bpm, dentro de tu zona 2. Para el próximo entrenamiento, intenta aumentar la distancia a 10 km manteniendo el mismo ritmo. ¡Sigue así!"

**Ideal para:**
- La mayoría de usuarios (por eso es el default)
- Personas que quieren un enfoque completo
- Atletas que buscan equilibrio entre motivación y técnica

---

### 4. 🎯 Custom (`custom`)

**Prompt del Sistema para la IA:**
- El usuario define su propio prompt personalizado
- Se almacena en `user.preferences.custom_prompt`
- La IA usa exactamente el prompt que el usuario escribió

**Qué significa:**
- **Tono:** Definido por el usuario
- **Enfoque:** Completamente personalizable
- **Lenguaje:** Lo que el usuario especifique
- **Feedback:** Según las instrucciones del usuario
- **Objetivo:** Máxima personalización

**Ejemplo de uso:**
El usuario podría escribir:
> "Eres un coach de running que habla como un amigo cercano. Usa lenguaje casual, da consejos prácticos sin ser demasiado técnico, y siempre pregunta cómo me siento."

**Ideal para:**
- Usuarios que quieren control total sobre el estilo
- Personas con preferencias muy específicas
- Atletas que han usado otros coaches y saben qué quieren

---

## 📍 Dónde se Usa el Estilo de Coach

### 1. Análisis de Workouts

**Endpoint:** `POST /api/v1/coach/analyze/{workout_id}`

El estilo de coach determina **cómo** la IA analiza y presenta el feedback de cada entrenamiento.

**Código relevante:**
```python
# backend/app/services/coach_service.py líneas 407-412
coaching_style = user.coaching_style or "balanced"
custom_prompt = (
    user.preferences.get("custom_prompt") if user.preferences else None
)
system_prompt = self.get_coaching_style_prompt(coaching_style, custom_prompt)
```

### 2. Análisis Profundo de Workouts

**Endpoint:** `POST /api/v1/coach/analyze-deep/{workout_id}`

Similar al análisis normal, pero con más detalle. El estilo afecta cómo se presenta la información.

### 3. Recomendaciones Personalizadas

**Endpoint:** `GET /api/v1/coach/personalized-recommendation`

El estilo se combina con:
- `primary_device` (Garmin, Xiaomi, etc.)
- `use_case` (fitness_tracker, training_coach, etc.)

Para generar recomendaciones completamente personalizadas.

**Código relevante:**
```python
# backend/app/routers/coach.py líneas 520-586
coach_style = current_user.coach_style_preference or 'balanced'
# ... se combina con device y use_case ...
personalized['coaching_style'] = coach_style
```

### 4. Planes de Entrenamiento

**Endpoint:** `POST /api/v1/training-plans/generate`

El estilo de coach influye en cómo se generan y presentan los planes de entrenamiento.

**Código relevante:**
```python
# backend/app/services/training_plan_service.py línea 264
- Estilo de coaching: {user.coaching_style or 'balanceado'}
```

### 5. Chat con el Coach

**Endpoint:** `POST /api/v1/coach/chat`

En conversaciones con el coach, el estilo determina el tono y enfoque de todas las respuestas.

---

## 🔧 Cómo Funciona Técnicamente

### Almacenamiento

**Campo en BD:** `user.coach_style_preference` (String)
- Valores posibles: `"motivator"`, `"technical"`, `"balanced"`, `"custom"`
- Default: `"balanced"`

**Campo adicional para Custom:** `user.preferences.custom_prompt` (String)
- Solo se usa si `coach_style_preference == "custom"`

### Proceso

1. **Usuario elige estilo** en onboarding → Se guarda en `user.coach_style_preference`
2. **Cuando se necesita feedback del coach:**
   - Se obtiene el estilo del usuario
   - Se genera el prompt del sistema según el estilo
   - Se envía el prompt a la IA (Groq/Llama)
   - La IA genera respuesta con ese estilo
3. **La respuesta se personaliza** según el estilo elegido

### Prompts del Sistema

Los prompts se definen en `backend/app/services/coach_service.py` en el método `get_coaching_style_prompt()`.

---

## 🔮 Impacto Futuro (Pendiente de Implementar)

Actualmente, el estilo de coach afecta principalmente las **respuestas de texto de la IA**. Pero podría usarse para:

- [ ] **Visualización:** Diferentes colores/estilos en el dashboard según el estilo
- [ ] **Notificaciones:** Tono diferente en notificaciones push
- [ ] **Widgets:** Mostrar diferentes métricas según el estilo (técnico = más datos, motivator = más logros)
- [ ] **Tutoriales:** Guías adaptadas al estilo preferido
- [ ] **Análisis de tendencias:** Presentar datos de forma más técnica o más visual según el estilo

---

## 📝 Notas

- El estilo se puede cambiar después del onboarding (aunque no hay UI para esto aún)
- Si el usuario no completa el onboarding, se usa `"balanced"` como default
- El estilo se combina con otros factores (device, use_case) para personalización completa
- Para `custom`, el usuario debe proporcionar su propio prompt (no hay UI para esto aún)

---

## 🎯 Resumen Comparativo

| Estilo | Tono | Enfoque | Datos | Emojis | Ideal Para |
|--------|------|---------|-------|--------|------------|
| **Motivator** | Energético | Logros | Mínimos | ✅ Muchos | Necesitan motivación |
| **Technical** | Analítico | Métricas | ✅ Muchos | ❌ Ninguno | Amantes de datos |
| **Balanced** | Profesional | Equilibrado | Moderados | ⚠️ Ocasionales | Mayoría de usuarios |
| **Custom** | Personalizado | Definido por usuario | Variable | Variable | Control total |
