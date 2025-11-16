# 📖 GUÍA COMPLETA DE USUARIO - Plataforma de Running

## 🎯 Introducción

Bienvenido a la **plataforma de entrenamiento de running más avanzada del mundo**. Esta guía te mostrará cómo aprovechar al máximo cada feature.

---

## 🚀 **EMPEZAR**

### Paso 1: Crear Cuenta
1. Ve a `localhost:3000` (o tu dominio)
2. Haz clic en "Registrarse"
3. Completa:
   - Email (válido)
   - Contraseña (mínimo 8 caracteres)
4. Haz clic en "Crear Cuenta"

### Paso 2: Login
1. Usa tu email y contraseña
2. Serás redirigido al Dashboard

### Paso 3: Completar Perfil
En "Perfil":
1. **Datos físicos**: altura, peso
2. **Frecuencia cardíaca máxima** (importante):
   - Opción A: Test de campo (sprint máximo hasta que no puedas más)
   - Opción B: Usa 220 - tu edad (estimado)
   - Opción C: Conecta Garmin/Strava (auto-detecta)
3. **Poder máximo (FTP)** (opcional, para Watts):
   - Test: 20 minutos a máximo esfuerzo sostenible
4. **Nivel de running**: Principiante, Intermedio, Avanzado

---

## 📅 **CREAR TU PRIMER PLAN DE ENTRENAMIENTO**

### Opción 1: CON CARRERA OBJETIVO (Recomendado)

**¿Cuándo usar?**: Tienes una carrera en mente

**Pasos:**

1. **Paso 1: ¿Tienes carrera objetivo?**
   - Haz clic en "Sí, tengo una carrera en mente"
   - Escribe nombre o ciudad: "Madrid", "10K Barcelona", etc.
   - Selecciona de los resultados
   - **Automáticamente:**
     - Se calcula duración del plan
     - Se sugiere objetivo según distancia
     - Se muestra recomendación

2. **Paso 2: Objetivo y Prioridad**
   - El objetivo ya está establecido (no editable)
   - Selecciona prioridad:
     - 🚀 **Velocidad**: quiero ser más rápido
     - 💪 **Resistencia**: quiero correr más lejos
     - 😌 **Recuperación**: quiero disfrutar y recuperarme bien
     - ⚖️ **Equilibrado**: un poco de todo

3. **Paso 3: Tu Disponibilidad**
   - ¿Cuántos días puedes entrenar? (3-7)
   - ¿Qué día prefieres para la "tirada larga"? (generalmente sábado)

4. **Paso 4: Entrenamientos Adicionales**
   - ¿Incluir fuerza? (Sí/No)
     - Si sí, ¿dónde? (Gym, Casa, Ambos)
   - ¿Incluir cross-training? (yoga, natación, etc.)
     - Si sí, ¿qué tipos?

5. **Paso 5: Método de Entrenamiento**
   - **Por Zonas de Frecuencia Cardíaca**: necesitas FC máx
   - **Por Ritmo**: necesitas saber tus ritmos objetivo
   - **Automático**: nosotros elegimos el mejor para ti

6. **Paso 6: Recuperación**
   - **Duración**: Automática (calculada desde hoy a carrera)
   - **Enfoque de recuperación**: Minimal, Moderado, Alto
   - Consideraciones por lesiones

7. **¡CREAR PLAN!**
   - Espera a que se genere (30 segundos aprox)
   - Tu plan está listo

---

### Opción 2: SIN CARRERA OBJETIVO

**¿Cuándo usar?**: Quieres entrenar sin objetivo específico

**Pasos:**

1. **Paso 1: ¿Tienes carrera objetivo?**
   - Haz clic en "No, entreno sin carrera específica"

2. **Pasos 2-5**: Igual que arriba
   - Selecciona objetivo general: Maratón, Media Maratón, 10K, 5K, Mejorar Fitness, etc.
   - Prioridad, disponibilidad, entrenamientos adicionales

3. **Paso 6: DURACIÓN (IMPORTANTE)**
   - Se muestran opciones recomendadas:
     - ⭐ **Opción Recomendada**: la que los expertos sugieren
     - Opción Rápida: menos semanas
     - Opción Extendida: más semanas
   - Cada opción tiene descripción
   - Selecciona una → crea plan

---

## 📊 **TU DASHBOARD**

### Sección 1: Resumen de Hoy
- Plan activo
- Entrenamiento de hoy (si lo hay)
- Próxima carrera (si existe)

### Sección 2: Tus Zonas de Entrenamiento

**Zonas de Frecuencia Cardíaca (si tienes FC máx establecida):**
```
Z1 - Recuperación (50-60% HRR): Muy fácil
Z2 - Base Aeróbica (60-70%): Fácil y sostenible
Z3 - Tempo (70-80%): Conversación difícil
Z4 - Umbral (80-90%): Muy difícil
Z5 - VO2 Max (90-100%): Máximo esfuerzo
```

**Zonas de Potencia (si tienes FTP establecida):**
```
Z1: <55% FTP - Recuperación
Z2: 55-75% FTP - Resistencia
Z3: 75-90% FTP - Tempo
Z4: 90-105% FTP - Umbral
Z5: 105-120% FTP - VO2 Max
Z6: 120-150% FTP - Capacidad anaeróbica
Z7: >150% FTP - Potencia neuromuscular
```

**💡 Consejo**: Entrena en Z2 el 80% del tiempo, Z3-Z4 el 15%, Z5+ el 5%

### Sección 3: Entrenamientos por Zona (Últimas 4 semanas)
- Gráfico mostrando % de tiempo en cada zona
- Hover: valores exactos
- Ayuda a validar que tu distribución es correcta

### Sección 4: Progresión de Volumen (Últimas 8 semanas)
- Gráfico de líneas con:
  - Tu volumen actual (línea azul)
  - Media histórica (línea verde punteada)
  - Máximo semanal (línea roja punteada)
- Tendencia: "↗️ Progresando bien" o "↘️ Volumen bajando"

### Sección 5: Sugerencias Inteligentes
- "Tu volumen está en zona verde (30km/semana)" ✓
- "Recomendamos descansar este fin de semana" (si HR elevado)
- "¡Próxima carrera en 12 días! Aumenta velocidad"

---

## 📱 **TUS ENTRENAMIENTOS**

### Ver Plan
1. Ve a "Planes"
2. Selecciona tu plan activo
3. Verás todas las semanas

### Una Semana
Ejemplo de semana típica con carrera objetivo (Media Maratón):

```
LUNES: Easy Run + Fuerza
- 5 km @ Z2 (fácil)
- + 20 min core y glúteos (gym)

MARTES: Speed Work
- 3 km calentamiento
- 6 x 800m @ Z4 (esfuerzo alto)
- 2 km enfriamiento
- Total: 8 km

MIÉRCOLES: Recovery Run
- 4 km @ Z1-Z2 (muy fácil)

JUEVES: Tempo Run
- 2 km calentamiento
- 6 km @ Z3 (conversación difícil)
- 2 km enfriamiento
- Total: 10 km

VIERNES: Yoga (Cross-training)
- 45 min sesión completa

SÁBADO: Long Run (TIRADA LARGA)
- 12 km @ Z2 (cómodo, conversacional)
- Objetivo: durabilidad

DOMINGO: Descanso
- 0 km, recuperación activa opcional
```

### Entrenamientos Especiales

**Easy Run / Recovery Run:**
- Debes poder hablar frases completas
- Ritmo: 1:30 - 2:00 min/km MÁS LENTO que carrera
- Objetivo: adaptación fisiológica, recuperación activa

**Tempo Run:**
- Puedes hablar palabras sueltas
- Ritmo: 45 - 90 segundos más rápido que carrera
- Objetivo: mejorar umbral aeróbico

**Speed Work / Intervalos:**
- No puedes hablar
- Intercalar: sprints con recuperación
- Objetivo: mejorar velocidad máxima, VO2 Max

**Long Run:**
- Muy fácil, conversacional (Z2)
- Largo pero cómodo
- Objetivo: resistencia aeróbica
- Aumenta 1km cada semana (máximo)

**Cross-Training:**
- Yoga, natación, ciclismo, etc.
- Recuperación activa
- Mantiene fitness sin impacto

---

## 🧠 **COACH AI**

### Chatear con tu Entrenador
1. Ve a "Coach"
2. Escribe preguntas como:
   - "¿Por qué hoy tengo un Speed Work?"
   - "No completé el entrenamiento, ¿qué hago?"
   - "¿Estoy sobreentrenando?"
   - "¿Cómo corro más rápido?"

El AI analizará tu:
- Plan personalizado
- Entrenamientos recientes
- Datos de FC/watts
- Y te dará consejos específicos

### Análisis de Workout
Después de sincronizar un entrenamiento:
1. Ve a "Workouts"
2. Haz clic en un entrenamiento
3. El Coach analiza:
   - ¿Cuál fue tu zona?
   - ¿Completaste el objetivo?
   - ¿Cómo estuvo tu rendimiento?
   - Consejos para mejorar

---

## 🔗 **SINCRONIZAR ENTRENAMIENTOS**

### Desde Garmin
1. Ve a "Perfil" → "Integraciones"
2. Haz clic "Conectar Garmin"
3. Autentica con tu cuenta Garmin Connect
4. Automáticamente sincroniza entrenamientos

### Desde Strava
1. Ve a "Perfil" → "Integraciones"
2. Haz clic "Conectar Strava"
3. Autentica con tu cuenta Strava
4. Automáticamente sincroniza entrenamientos

### Manual
1. Ve a "Workouts" → "Agregar"
2. Completa:
   - Fecha y hora
   - Tipo (Easy, Tempo, Speed, etc.)
   - Distancia y tiempo
   - FC promedio (si tienes)
   - Notas
3. Guardar

---

## 📈 **ESTADÍSTICAS & ANÁLISIS**

### Volumen Semanal
- Objetivo: aumentar 10% máximo por semana
- Muy rápido: riesgo de lesión
- Muy lento: no progresa

### Distribución por Zona
- Z1-Z2: 80% (base aeróbica)
- Z3-Z4: 15% (intensidad)
- Z5+: 5% (máxima)

### HR Trends
- HR en reposo bajando: ¡buena forma!
- HR en reposo subiendo: posible fatiga
- HR elevado en Easy Runs: cansancio, descanso

### Exportar Datos
1. Ve a "Perfil" → "Exportar"
2. Descarga:
   - Plan en PDF
   - Workouts en CSV
   - Reporte semanal

---

## 🏁 **COMPLETAR TU PLAN**

### Últimas 2 Semanas
- Reducción gradual de volumen (taper)
- Menos distancia, misma intensidad
- Objetivo: llegar fresco a la carrera

### Semana de Carrera
- 50% del volumen normal
- Entrenamientos cortos y rápidos
- Mucho descanso
- Noche anterior: hidratación y carbohidratos

### Después de la Carrera
1. Easy run 2-3 días después
2. Semana de recuperación completa
3. Luego: nuevo plan o descanso

---

## 💡 **CONSEJOS PRO**

1. **Sigue el plan al 90%** - no es perfecto, adaptaciones son normales
2. **Escucha tu cuerpo** - si duele (no es músculo), descansa
3. **Varía la superficie** - asfalto, tierra, pista para variar impacto
4. **Entrena en grupo a veces** - motivación + social
5. **Come bien y duerme bien** - 80% del rendimiento es fuera de correr
6. **Haz fuerza 2x/semana** - previene lesiones
7. **No compitas en entrenamientos** - respeta las zonas
8. **Calienta y enfría siempre** - 5 min antes y después mínimo

---

## 🆘 **PROBLEMAS COMUNES**

**P: Me duele la rodilla en Easy Run**
R: Probablemente volumen muy rápido. Reduce 20%, añade fuerza de glúteos.

**P: No puedo hacer Speed Work como dice el plan**
R: Está bien, hazlo más fácil. El plan es orientativo, escucha tu cuerpo.

**P: Mi plan desapareció**
R: Revisa "Planes" → "Archivados". Puedes reactivar planes antiguos.

**P: ¿Puedo cambiar mi FC máxima?**
R: Sí, ve a Perfil. El plan se recalculará automáticamente.

**P: Sincronización de Garmin no funciona**
R: Desconecta/reconecta en Perfil. Limpia caché del navegador.

---

## 🚀 **¿LISTO PARA EMPEZAR?**

1. **Crea tu cuenta** → Login → Perfil completo
2. **Elige tu carrera** o **objetivo general**
3. **Crea tu plan** → Automáticamente generado
4. **Sigue el plan** → Sync tus entrenamientos
5. **Celebra progreso** → Próxima carrera 🏁

¡**LA EXCELENCIA TE ESPERA!** 🏆
