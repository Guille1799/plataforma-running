# Plan de Pruebas: Sincronización de Garmin

## Objetivo
Verificar que la sincronización de Garmin funciona correctamente y que los datos se importan y procesan adecuadamente.

## Contexto
- **Importancia**: La sincronización de Garmin es crítica para:
  - Importar entrenamientos históricos
  - Obtener métricas de salud (HRV, Body Battery, Stress)
  - Generar planes de entrenamiento personalizados basados en datos reales
  - Análisis de rendimiento

- **Estado actual**: No hay tests automáticos para la sincronización de Garmin
- **Riesgo**: Si falla, el usuario no puede usar features clave de la plataforma

---

## Pruebas Manuales Propuestas

### Prueba 1: Conexión Inicial de Garmin

**Objetivo**: Verificar que un usuario puede conectar su cuenta de Garmin

**Pasos**:
1. Navegar a `/garmin` (o "Integraciones" en el sidebar)
2. Ingresar credenciales de Garmin Connect:
   - Email: [credenciales reales de prueba]
   - Password: [credenciales reales de prueba]
3. Hacer clic en "Conectar Garmin"
4. Verificar:
   - ✅ Mensaje de éxito: "¡Conectado exitosamente!"
   - ✅ No hay errores en consola
   - ✅ El estado cambia a "Conectado"
   - ✅ Las credenciales se guardan encriptadas en la BD

**Qué verificar en backend**:
- `user.garmin_email` se guarda
- `user.garmin_token` se guarda encriptado
- `user.garmin_connected_at` tiene timestamp

**Errores esperados a manejar**:
- Credenciales incorrectas → Error claro
- Cuenta de Garmin bloqueada → Error claro
- Problemas de red → Timeout manejado

---

### Prueba 2: Primera Sincronización (Full Sync)

**Objetivo**: Verificar que la primera sincronización importa datos históricos

**Pasos**:
1. Conectar cuenta de Garmin (Prueba 1)
2. Hacer clic en "Sincronizar Ahora"
3. Esperar a que termine (puede tardar 1-2 minutos si hay muchos datos)
4. Verificar:
   - ✅ Mensaje de éxito con número de workouts sincronizados
   - ✅ Redirección a `/workouts` (si hay nuevos workouts)
   - ✅ Los workouts aparecen en la lista
   - ✅ Las métricas de salud se importan (HRV, Body Battery, etc.)

**Qué verificar en backend**:
- `user.last_garmin_sync` se actualiza
- Se crean registros en `workouts` table
- Se crean registros en `health_metrics` table (si aplica)
- La sincronización importa hasta 2 años de datos históricos

**Datos a verificar**:
- Distancia, duración, ritmo, FC promedio/máxima
- Cadencia, oscilación vertical (si están disponibles)
- Fechas correctas
- No hay duplicados

---

### Prueba 3: Sincronización Incremental

**Objetivo**: Verificar que sincronizaciones posteriores solo importan datos nuevos

**Pasos**:
1. Tener una cuenta ya sincronizada (Prueba 2)
2. Esperar o simular que hay nuevos entrenamientos en Garmin
3. Hacer clic en "Sincronizar Ahora" de nuevo
4. Verificar:
   - ✅ Solo se importan workouts nuevos (desde `last_garmin_sync`)
   - ✅ No se duplican workouts existentes
   - ✅ `last_garmin_sync` se actualiza
   - ✅ Mensaje indica cuántos workouts nuevos se importaron

**Qué verificar**:
- La lógica de "incremental sync" funciona correctamente
- No hay duplicados por `start_time`
- El rendimiento es rápido (solo nuevos datos)

---

### Prueba 4: Sincronización Automática

**Objetivo**: Verificar que la sincronización automática funciona

**Pasos**:
1. Conectar cuenta de Garmin
2. Cerrar y abrir la aplicación después de 6 horas
3. Verificar:
   - ✅ La sincronización se ejecuta automáticamente
   - ✅ No hay errores en consola
   - ✅ Los nuevos datos aparecen sin intervención manual

**Qué verificar**:
- El hook `useAutoSync` funciona correctamente
- El intervalo de 6 horas se respeta
- No intenta sincronizar si no hay Garmin conectado

---

### Prueba 5: Manejo de Errores

**Objetivo**: Verificar que los errores se manejan correctamente

**Escenarios a probar**:

#### 5.1 Credenciales Incorrectas
- Intentar conectar con email/password incorrectos
- Verificar: Error claro, no se guardan credenciales

#### 5.2 Cuenta No Conectada
- Intentar sincronizar sin haber conectado Garmin
- Verificar: Error claro "Garmin not connected"

#### 5.3 Token Expirado
- Simular token expirado (cambiar password en Garmin)
- Intentar sincronizar
- Verificar: Error claro, opción de reconectar

#### 5.4 Sin Datos Nuevos
- Sincronizar cuando no hay nuevos workouts
- Verificar: Mensaje "No new workouts to sync" (no es error)

---

### Prueba 6: Sincronización de Métricas de Salud

**Objetivo**: Verificar que las métricas de salud se sincronizan correctamente

**Pasos**:
1. Conectar cuenta de Garmin
2. Sincronizar entrenamientos
3. Verificar en `/health`:
   - ✅ Body Battery aparece
   - ✅ HRV aparece
   - ✅ Stress Level aparece
   - ✅ Readiness Score se calcula

**Qué verificar**:
- Los datos se importan desde Garmin Connect
- Se muestran en el dashboard de Garmin
- El ReadinessBadge se actualiza

---

## Mejora Propuesta: Sincronización Obligatoria para Generación de Planes

### Problema Actual
Cuando un usuario con `primary_device = 'garmin'` intenta generar un plan de entrenamiento, el sistema no verifica si tiene datos sincronizados. Esto puede resultar en planes menos personalizados.

### Solución Propuesta

**Opción 1: Verificación y Advertencia**
- Antes de generar el plan, verificar si hay workouts sincronizados
- Si no hay workouts, mostrar advertencia pero permitir continuar
- Mensaje: "Para un plan más personalizado, sincroniza primero tus entrenamientos de Garmin"

**Opción 2: Sincronización Obligatoria (Recomendada)**
- Si `primary_device = 'garmin'` y no hay workouts sincronizados:
  - Bloquear el wizard de generación de planes
  - Mostrar modal: "Sincroniza primero tus entrenamientos de Garmin para generar un plan personalizado"
  - Botón: "Ir a Sincronizar" → redirige a `/garmin`
- Después de sincronizar, permitir generar el plan

**Implementación sugerida**:
```typescript
// En training-plan-form-v2.tsx o similar
const { userProfile } = useAuth();
const { data: workouts } = useQuery(['workouts'], () => apiClient.getWorkouts());

const canGeneratePlan = userProfile?.primary_device === 'garmin' 
  ? (workouts?.length > 0) 
  : true;

if (!canGeneratePlan) {
  return <SyncRequiredModal />;
}
```

---

## Checklist de Pruebas

- [ ] Prueba 1: Conexión inicial de Garmin
- [ ] Prueba 2: Primera sincronización (full sync)
- [ ] Prueba 3: Sincronización incremental
- [ ] Prueba 4: Sincronización automática
- [ ] Prueba 5.1: Credenciales incorrectas
- [ ] Prueba 5.2: Cuenta no conectada
- [ ] Prueba 5.3: Token expirado
- [ ] Prueba 5.4: Sin datos nuevos
- [ ] Prueba 6: Sincronización de métricas de salud

---

## Notas Técnicas

### Endpoints Relevantes
- `POST /api/v1/garmin/connect` - Conectar cuenta
- `POST /api/v1/garmin/sync` - Sincronizar entrenamientos
- `GET /api/v1/garmin/status` - Estado de conexión

### Archivos Clave
- `backend/app/routers/garmin.py` - Endpoints
- `backend/app/services/garmin_service.py` - Lógica de sincronización
- `app/(dashboard)/garmin/page.tsx` - UI de conexión
- `hooks/useAutoSync.ts` - Sincronización automática

### Consideraciones
- La primera sincronización puede tardar 1-2 minutos (2 años de datos)
- Las sincronizaciones incrementales son rápidas (< 10 segundos)
- Los tokens de Garmin pueden expirar (manejar reconexión)
- La sincronización usa `garth` para OAuth (más confiable que credenciales directas)

---

## Próximos Pasos

1. **Ejecutar pruebas manuales** según este plan
2. **Implementar mejora** de sincronización obligatoria (si se aprueba)
3. **Crear tests automáticos** para sincronización (futuro)
4. **Documentar resultados** de las pruebas
