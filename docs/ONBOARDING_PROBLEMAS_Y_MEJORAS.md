# 🐛 Problemas y Mejoras del Onboarding

**Fecha:** 2026-01-10  
**Propósito:** Documentar problemas encontrados en el onboarding y respuestas a preguntas del usuario.

---

## 🐛 Problemas Encontrados

### 1. "Balanced" está preseleccionado visualmente

**Problema:**  
En el paso "How should your coach be?", la opción "Balanced" aparece visualmente preseleccionada (con borde azul y fondo azul), aunque el usuario no la haya elegido aún.

**Causa:**  
En `app/onboarding/page.tsx` línea 123, el estado inicial tiene:
```typescript
coach_style_preference: 'balanced',
```

Esto hace que la condición en la línea 274 (`data.coach_style_preference === style.id`) sea `true` para "balanced" desde el inicio, mostrándolo como seleccionado.

**Solución propuesta:**
- Cambiar el valor inicial a `''` (string vacío) en lugar de `'balanced'`
- O cambiar la lógica para que solo se muestre como seleccionado si el usuario ya pasó por ese paso y lo eligió explícitamente

---

### 2. Onboarding está en inglés pero pregunta por idioma al final

**Problema:**  
Todo el texto del onboarding está hardcodeado en inglés, pero el usuario solo puede elegir el idioma en el paso 4 (después de device, use case y coach style).

**Impacto:**
- Usuarios que no hablan inglés ven todo en inglés hasta el paso 4
- Si eligen español, el onboarding sigue en inglés (no hay traducción implementada)
- La experiencia es confusa para usuarios no angloparlantes

---

## ❓ Preguntas del Usuario y Respuestas

### 1. ¿No debería estar el idioma en el primer paso?

**Respuesta:**  
**Sí, tiene mucho sentido.** El idioma debería ser el primer paso porque:
- Permite que el resto del onboarding se muestre en el idioma elegido
- Mejora la UX para usuarios no angloparlantes
- Es una práctica común en aplicaciones multiidioma

**Estado actual:**
- El idioma está en el paso 4 (después de device, use case, style)
- No hay i18n implementado (aunque `next-intl` está instalado)
- Todo el texto está hardcodeado en inglés

**Recomendación:**
- Mover el paso de idioma al inicio (paso 1)
- Implementar i18n con `next-intl` (ya está instalado)
- Traducir todo el onboarding al español e inglés

---

### 2. ¿Solo deberíamos dejar inglés y español?

**Respuesta:**  
**Sí, tiene sentido para ahora.** Actualmente hay 4 idiomas en el array:
```typescript
const LANGUAGES = [
  { id: 'es', name: 'Español' },
  { id: 'en', name: 'English' },
  { id: 'fr', name: 'Français' },
  { id: 'de', name: 'Deutsch' },
];
```

**Razones para dejar solo ES y EN:**
- **Enfoque:** Estamos enfocados en hacer Garmin perfecto, no en multiidioma completo
- **Mantenimiento:** Menos idiomas = menos trabajo de traducción y mantenimiento
- **Audiencia:** Si la audiencia principal es hispanohablante/anglófona, no necesitamos francés/alemán aún
- **Recursos:** Traducir y mantener 4 idiomas requiere mucho trabajo

**Recomendación:**
- Dejar solo `es` y `en` por ahora
- Agregar otros idiomas en el futuro si hay demanda
- Documentar esto en `docs/TODO_FUTURO_Y_MEJORAS.md`

---

### 3. ¿El inglés como idioma está operativo? ¿Merece la pena desarrollarlo?

**Respuesta:**  
**Estado actual:**
- ❌ **NO está operativo** - No hay i18n implementado
- ❌ **No hay traducciones** - Todo está hardcodeado en inglés
- ✅ **Backend soporta idioma** - Se guarda `user.language` en la BD
- ✅ **`next-intl` está instalado** - Pero no está configurado ni usado

**¿Merece la pena desarrollarlo?**

**Sí, pero con prioridad media:**
- ✅ **Pros:**
  - Amplía la audiencia potencial
  - Muchos runners hablan inglés
  - Facilita expansión internacional futura
  - `next-intl` ya está instalado (menos trabajo)

- ⚠️ **Contras:**
  - Requiere traducir TODO el frontend
  - Requiere mantener traducciones actualizadas
  - Duplica el trabajo de contenido
  - Si la audiencia principal es hispanohablante, puede no ser prioritario

**Recomendación:**
- **Corto plazo:** Enfocarse en español (audiencia principal)
- **Medio plazo:** Implementar inglés cuando tengamos más contenido estable
- **Largo plazo:** Agregar más idiomas si hay demanda

**Acción sugerida:**
- Documentar en `docs/TODO_FUTURO_Y_MEJORAS.md` como "Implementar i18n completo (ES + EN)"

---

### 4. ¿Cómo se hace el custom del entrenador? ¿Dónde y cuándo?

**Respuesta:**  
**Estado actual:**
- ✅ **Backend soporta custom prompt:**
  - Campo: `user.preferences.custom_prompt` (String, max 1000 caracteres)
  - Se usa cuando `coach_style_preference == "custom"`
  - Está en el schema `AthletePreferences` (línea 246 de `backend/app/schemas.py`)

- ❌ **NO hay UI para configurarlo:**
  - No hay campo en el onboarding para escribir el prompt custom
  - No hay campo en la página de perfil (`app/(dashboard)/profile/page.tsx`)
  - El usuario puede elegir "Custom" pero no puede configurar qué significa

**Cómo funciona técnicamente:**
1. Usuario elige "Custom" en onboarding → Se guarda `coach_style_preference = "custom"`
2. Si `user.preferences.custom_prompt` existe, se usa ese prompt
3. Si no existe, el sistema usa el prompt de "balanced" (fallback)

**Dónde debería estar:**
- **Opción 1:** En el onboarding, si elige "Custom", mostrar un textarea para escribir el prompt
- **Opción 2:** En la página de perfil, agregar una sección "Custom Coach Prompt" (solo visible si `coaching_style == "custom"`)

**Recomendación:**
- Agregar en onboarding: Si elige "Custom", mostrar un paso adicional con textarea
- O agregar en perfil: Sección para editar el custom prompt
- Validar que el prompt tenga sentido (no vacío, no demasiado largo, etc.)

---

## 📋 Checklist de Mejoras Necesarias

### Prioridad Alta (Hacer ahora)
- [ ] **Quitar preselección de "Balanced"** - Cambiar inicial a `''`
- [ ] **Mover idioma al paso 1** - Reordenar pasos del onboarding
- [ ] **Limitar idiomas a ES y EN** - Eliminar francés y alemán del array
- [ ] **Agregar UI para custom prompt** - En onboarding o perfil

### Prioridad Media (Hacer después)
- [ ] **Implementar i18n básico** - Configurar `next-intl` y traducir onboarding
- [ ] **Traducir onboarding a español** - Todos los textos hardcodeados
- [ ] **Traducir onboarding a inglés** - Si decidimos mantenerlo

### Prioridad Baja (Futuro)
- [ ] **Traducir resto de la aplicación** - Dashboard, componentes, etc.
- [ ] **Agregar más idiomas** - Si hay demanda

---

## 📝 Notas Técnicas

### Estructura actual del onboarding:
```
Paso 1: Device (garmin, xiaomi, apple, strava, manual)
Paso 2: Use Case (fitness_tracker, training_coach, race_prep, general_health)
Paso 3: Coach Style (motivator, technical, balanced, custom)
Paso 4: Language (es, en, fr, de) + Notifications toggle
Paso 5: Confirm
```

### Estructura propuesta:
```
Paso 1: Language (es, en) ← MOVER AQUÍ
Paso 2: Device
Paso 3: Use Case
Paso 4: Coach Style (+ Custom prompt si elige custom)
Paso 5: Notifications toggle
Paso 6: Confirm
```

### Campos en BD relacionados:
- `user.language` - Idioma elegido (es, en, fr, de)
- `user.coach_style_preference` - Estilo de coach (motivator, technical, balanced, custom)
- `user.preferences.custom_prompt` - Prompt personalizado (solo si custom)

---

## 🔗 Referencias

- `app/onboarding/page.tsx` - Componente del onboarding
- `backend/app/routers/onboarding.py` - Endpoint de onboarding
- `backend/app/schemas.py` - Schemas de onboarding
- `backend/app/services/coach_service.py` - Lógica de estilos de coach
- `docs/TODO_FUTURO_Y_MEJORAS.md` - Trabajo futuro
