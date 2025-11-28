# 🔧 FIXES APLICADOS - Resumen Técnico

## Cambios Realizados

### 1. **Race Search Caching - FIXED ✅**
**Archivo**: `lib/api-client.ts`
**Problema**: El navegador estaba cacheando requests GET, mostrando solo Málaga aunque el backend devolvía 30 resultados
**Solución**:
- Agregado timestamp (`_t: Date.now()`) a los params para invalidar cache del navegador
- Agregados headers explícitos: `Cache-Control: no-cache, no-store, must-revalidate`
- Headers `Pragma: no-cache` y `Expires: 0`

```typescript
async searchRaces(...) {
  const response = await this.client.get('/api/v1/events/races/search', {
    params: {
      q: query,
      // ...
      _t: Date.now(),  // NEW: Force cache invalidation
    },
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0',
    },
  });
}
```

### 2. **Paso 6 Duration Loading Bug - FIXED ✅**
**Archivo**: `frontend/app/(dashboard)/dashboard/training-plan-form-v2.tsx`
**Problema**: `useEffect` estaba siendo llamado DENTRO del return JSX (violación de React Rules of Hooks), causando que `durationOpts` no se cargara
**Solución**:
- Movido el `useEffect` al nivel superior del componente (después del primer `useEffect`)
- Removido el `autoLoadDurationOptions()` anidado
- Ahora el hook se ejecuta cuando entra al Paso 6 Y hay un `general_goal` establecido

```typescript
// NOW at component level (TOP)
useEffect(() => {
  if (step === 6 && formData.general_goal && !formData.has_target_race && !durationOpts.data) {
    console.log('📋 Loading duration options for goal:', formData.general_goal);
    durationOpts.getDurationOptions(formData.general_goal);
  }
}, [step, formData.general_goal, formData.has_target_race, durationOpts]);
```

### 3. **Form Validation - ENHANCED ✅**
**Archivo**: `frontend/app/(dashboard)/dashboard/training-plan-form-v2.tsx`
**Agregado**: Función `isStepValid()` que valida cada paso según sus requisitos

```typescript
const isStepValid = (): boolean => {
  switch (step) {
    case 1: return formData.has_target_race !== null;
    case 2: return formData.general_goal !== null && formData.priority !== null;  // BOTH required
    case 3: return formData.training_days_per_week !== null;
    case 4: return formData.preferred_long_run_day !== null;
    case 5: return (strength && cross-training validations);
    case 6: return training_method && recovery_focus && plan_duration_weeks;
    default: return false;
  }
};
```

### 4. **Buttons Disabled State - FIXED ✅**
**Archivo**: `frontend/app/(dashboard)/dashboard/training-plan-form-v2.tsx`
**Cambios**:
- 6 botones "Siguiente" ahora usan `disabled={!isStepValid()}`
- Botón "Crear Plan" usa `disabled={isLoading || !isStepValid()}`
- Todos los botones deshabilitados tienen clase `disabled:bg-gray-600` para visual feedback

```typescript
<Button 
  onClick={() => setStep(2)} 
  disabled={!isStepValid()}
  className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600"
>
  Siguiente →
</Button>
```

---

## 🧪 Cómo Verificar los Fixes

### Fix #1: Race Search
1. Ir a http://localhost:3000/dashboard/training-plans
2. Login con: `test@example.com` / `password123`
3. Paso 1: Escribir "marat" en el buscador
4. **ESPERADO**: Ver 30+ resultados (no solo Málaga)
5. **VERIFICACIÓN**: Abrir DevTools → Network → Buscar `search?q=marat`
   - Header `_t` debe tener timestamp diferente cada búsqueda (no cache)

### Fix #2: Duration Loading
1. Paso 6: Sin carrera objetivo
2. Llegar al Paso 6
3. Comprobar que aparecen opciones de duración (4, 8, 12, 16 semanas)
4. **VERIFICACIÓN**: Consola debe mostrar `📋 Loading duration options for goal: marathon`

### Fix #3: Validation
1. **Paso 1**: Botón gris hasta seleccionar opción (race o no race)
2. **Paso 2**: Botón gris hasta seleccionar AMBOS (objetivo Y prioridad)
3. **Paso 6**: Botón "Crear Plan" gris hasta tener duración seleccionada
4. **Verificación**: Intentar hacer click - no debe funcionar si botón está gris

---

## 🛠 Test Cases

### Scenario 1: Con carrera objetivo
1. Buscar "marat" → Seleccionar Maratón de Madrid 2025-04-13
2. Duración debe calcularse automáticamente
3. Pasar por Paso 2 (seleccionar objetivo + prioridad)
4. Llegada a Paso 6 → Duración YA está seleccionada
5. Botón "Crear Plan" debe estar HABILITADO
6. Click → Crear plan

### Scenario 2: Sin carrera objetivo
1. Paso 1 → "No, quiero entrenarme en general"
2. Paso 2 → Seleccionar Maratón + Velocidad
3. Paso 6 → Botón GRIS hasta seleccionar duración (4, 8, 12, 16)
4. Seleccionar 12 semanas
5. Botón se habilita → Click → Crear plan

### Scenario 3: Bug Testing
1. **Paso 2**: Seleccionar solo objetivo (no prioridad) → Botón debe estar GRIS
2. **Paso 2**: Seleccionar solo prioridad (no objetivo) → Botón debe estar GRIS
3. **Paso 2**: Seleccionar AMBOS → Botón se habilita

---

## 📊 Archivos Modificados

| Archivo | Cambios | Estado |
|---------|---------|--------|
| `lib/api-client.ts` | Cache-busting en searchRaces | ✅ LISTO |
| `frontend/app/(dashboard)/dashboard/training-plan-form-v2.tsx` | useEffect fix + validation + buttons | ✅ LISTO |
| `backend/app/main.py` | No cambios necesarios | ✅ OK |
| `backend/app/routers/events.py` | No cambios necesarios | ✅ OK |

---

## 🚀 Próximos Pasos

1. ✅ COMPLETADO: Fixes de bugs
2. ⏳ PENDIENTE: Test completo del formulario
3. ⏳ PENDIENTE: Implementación de arquitectura de 2-week rolling adaptive calendar

