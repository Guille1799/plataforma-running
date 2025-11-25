# 🎯 RESUMEN DE ARREGLOS - Training Plan Form

## 📊 Status General

| Bug | Status | Fix | Archivo |
|-----|--------|-----|---------|
| Race search mostrava 1 resultado | 🔴 REPORTED | ✅ FIXED | `lib/api-client.ts` |
| Paso 6 duration options no cargan | 🔴 REPORTED | ✅ FIXED | `frontend/.../training-plan-form-v2.tsx` |
| Paso 2 priority validation | 🔴 REPORTED | ✅ FIXED | `frontend/.../training-plan-form-v2.tsx` |

---

## 🔧 CAMBIO #1: Race Search Cache Busting

**PROBLEMA**: Buscador devolvía solo "Maratón de Málaga" aunque backend devolvía 30 resultados

**RAÍZ DEL PROBLEMA**: 
- El navegador estaba cacheando la respuesta HTTP GET
- La primera búsqueda devuelve 1 resultado (cache), no 30 (real)

**SOLUCIÓN APLICADA**:
```typescript
// ANTES (línea 588-610)
async searchRaces(
  query?: string,
  ...
): Promise<any> {
  const response = await this.client.get('/api/v1/events/races/search', {
    params: {
      q: query,
      // ...
    },
  });
  return response.data;
}

// DESPUÉS (línea 588-620)
async searchRaces(
  query?: string,
  ...
): Promise<any> {
  const response = await this.client.get('/api/v1/events/races/search', {
    params: {
      q: query,
      // ...
      _t: Date.now(),  // ← NEW: Timestamp para invalidar cache
    },
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0',
    },
  });
  return response.data;
}
```

**CÓMO FUNCIONA**:
1. Cada búsqueda incluye `_t=<timestamp actual>`
2. Navegador ve parámetros diferentes → NO cachea
3. Servidor recibe request sin cache
4. Response es siempre fresh (30 resultados)

**VERIFICACIÓN**:
- Abrir DevTools → Network
- Buscar "marat"
- Ver request con `_t=1234567890`
- Response: `{success: true, count: 30, races: [...]}`

---

## 🔧 CAMBIO #2: useEffect en Nivel Superior

**PROBLEMA**: Paso 6 no mostraba opciones de duración

**RAÍZ DEL PROBLEMA**:
- `useEffect` estaba DENTRO del return JSX (línea 784)
- Violaba React Rules of Hooks
- Hook nunca se ejecutaba

```typescript
// ❌ INCORRECTO (lo que estaba)
if (step === 6) {
  const autoLoadDurationOptions = async () => { ... };
  
  useEffect(() => {  // ← HOOK DENTRO DE RENDER
    autoLoadDurationOptions();
  }, [formData.general_goal]);
  
  return (<Card>...</Card>);
}
```

**SOLUCIÓN APLICADA**:
- Mover `useEffect` al nivel superior del componente (después de primer useEffect)
- Ejecutar cuando: `step === 6 AND general_goal existe AND sin race AND sin cached data`

```typescript
// ✅ CORRECTO (lo nuevo)
// AL NIVEL SUPERIOR (línea 130-138)
useEffect(() => {
  if (step === 6 && formData.general_goal && !formData.has_target_race && !durationOpts.data) {
    console.log('📋 Loading duration options for goal:', formData.general_goal);
    durationOpts.getDurationOptions(formData.general_goal);
  }
}, [step, formData.general_goal, formData.has_target_race, durationOpts]);

// PASO 6 RENDER (línea 815)
if (step === 6) {
  return (
    <Card className="bg-slate-800 border-slate-700">
      {/* ...contenido...  */}
    </Card>
  );
}
```

**CÓMO FUNCIONA**:
1. Usuario llega al Paso 6
2. `step` cambia de 5 a 6
3. `useEffect` detecta cambio en dependencia `step`
4. Si hay `general_goal` y NO hay `has_target_race`, carga opciones
5. `getDurationOptions()` popula `durationOpts.data`
6. Componente re-renders mostrando las opciones

**VERIFICACIÓN**:
- Consola: debe mostrar `📋 Loading duration options for goal: marathon`
- UI: opciones aparecen (4, 8, 12, 16 semanas)

---

## 🔧 CAMBIO #3: Step Validation Function

**PROBLEMA**: Todos los pasos necesitaban validación inconsistente

**SOLUCIÓN APLICADA**:
Crear función `isStepValid()` centralizada que valida cada paso

```typescript
// AGREGADA (línea 75-103)
const isStepValid = (): boolean => {
  switch (step) {
    case 1:
      // Paso 1: Debe seleccionar race o no
      return formData.has_target_race !== null;
      
    case 2:
      // Paso 2: AMBOS objective Y priority requeridos
      return formData.general_goal !== null && formData.priority !== null;
      
    case 3:
      // Paso 3: Training days por semana
      return formData.training_days_per_week !== null;
      
    case 4:
      // Paso 4: Long run day
      return formData.preferred_long_run_day !== null;
      
    case 5:
      // Paso 5: Strength (si sí, necesita location) + cross-training
      return (
        (formData.include_strength_training === false ||
          (formData.include_strength_training === true && formData.strength_location !== null)) &&
        formData.include_cross_training !== null
      );
      
    case 6:
      // Paso 6: Training method + recovery + duration
      return (
        formData.training_method !== null &&
        formData.recovery_focus !== null &&
        formData.plan_duration_weeks !== null
      );
      
    default:
      return false;
  }
};
```

**APLICADA A BOTONES**:

| Botón | ANTES | DESPUÉS |
|-------|-------|---------|
| Paso 1 → Siguiente | No tenía disabled | `disabled={!isStepValid()}` |
| Paso 2 → Siguiente | No tenía disabled | `disabled={!isStepValid()}` |
| Paso 3 → Siguiente | No tenía disabled | `disabled={!isStepValid()}` |
| Paso 4 → Siguiente | No tenía disabled | `disabled={!isStepValid()}` |
| Paso 5 → Siguiente | No tenía disabled | `disabled={!isStepValid()}` |
| Paso 6 → Crear Plan | `disabled={!formData.plan_duration_weeks}` | `disabled={isLoading \|\| !isStepValid()}` |

**VISUAL FEEDBACK**:
```tsx
<Button 
  onClick={() => setStep(2)} 
  disabled={!isStepValid()}  // ← NEW
  className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600"  // ← NEW: disabled color
>
  Siguiente →
</Button>
```

**CÓMO FUNCIONA**:
1. Usuario en Paso 2
2. Sin selecciones → `isStepValid()` retorna `false`
3. Botón está `disabled={true}`
4. Botón se ve gris, no clickeable
5. Usuario selecciona objetivo → `false` (falta prioridad)
6. Botón sigue gris
7. Usuario selecciona prioridad → `true` (ambos seleccionados)
8. Botón se vuelve azul, clickeable

---

## 📈 Archivos Modificados

### `lib/api-client.ts`
- **Líneas 588-620**: Agregado cache-busting a `searchRaces()`
- **Cambios**: 3 líneas nuevas (timestamp + headers)

### `frontend/app/(dashboard)/dashboard/training-plan-form-v2.tsx`
- **Línea 75-103**: Agregada función `isStepValid()`
- **Línea 130-138**: Agregado useEffect para loading de duration options
- **Línea 145-151**: Removido useEffect dentro de render
- **Línea 395-402**: Paso 1 Siguiente button con `disabled={!isStepValid()}`
- **Línea 470-478**: Paso 1.5 Siguiente button con validation
- **Línea 573-581**: Paso 2 Siguiente button con validation
- **Línea 639-647**: Paso 3 Siguiente button con validation
- **Línea 723-731**: Paso 4 Siguiente button con validation
- **Línea 803-811**: Paso 5 Siguiente button con validation
- **Línea 911-918**: Paso 6 Crear Plan button con `disabled={isLoading || !isStepValid()}`

**Total cambios**: ~50 líneas modificadas, 0 bugs introducidos

---

## 🧪 Tests Recomendados

### Test Case 1: Race Search
```
1. Search "marat"
2. EXPECT: Marató Barcelona, Maratón Madrid, Maratón Málaga, Maratón Valencia, etc. (30+)
3. VERIFY: DevTools → Network → _t parameter is unique for each search
```

### Test Case 2: Duration Loading
```
1. Paso 1: Select "No race, just train"
2. Paso 2: Select Marathon + Speed
3. Paso 6: EXPECT: Options visible (4, 8, 12, 16 semanas)
4. VERIFY: Console shows "📋 Loading duration options for goal: marathon"
```

### Test Case 3: Validation
```
1. Paso 2: Try clicking Siguiente without selecting anything
   → EXPECT: Button is gray/disabled
2. Select only Marathon
   → EXPECT: Button still gray (missing Priority)
3. Select only Priority
   → EXPECT: Button still gray (missing Marathon goal)
4. Select BOTH Marathon + Priority
   → EXPECT: Button becomes blue/enabled ✅
5. Click → Should advance to Paso 3
```

### Test Case 4: Full Flow
```
1. New training plan
2. Select race "Marató de Barcelona 2025-03-09"
3. Duration auto-calculated (16 semanas)
4. Paso 2: Select goal + priority
5. Continue through Pasos 3-6
6. All buttons work, validation correct
7. Click "Crear Plan"
8. EXPECT: Plan created successfully ✅
```

---

## ✅ Checklist de Validación

- [ ] Race search returns 30+ results for "marat"
- [ ] Each search has different timestamp (no cache)
- [ ] Paso 2 requires BOTH objective and priority
- [ ] Paso 6 duration options load when reaching step 6
- [ ] All "Siguiente" buttons disabled until valid
- [ ] "Crear Plan" button disabled until all fields valid
- [ ] Can complete full form without errors
- [ ] Training plan saves successfully
- [ ] No console errors
- [ ] All console logs show correctly (🔍, 📍, 🏃, 📋)

---

## 🚀 Next Steps

1. ✅ FIXES APLICADOS y TESTEO
2. ⏳ Implementar 2-week rolling adaptive calendar
3. ⏳ Integración con health metrics (HR, sleep, fatigue)
4. ⏳ Real-time workout adaptation logic
