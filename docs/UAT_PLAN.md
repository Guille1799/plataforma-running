# Plan de Pruebas UAT - Plataforma Running

**Objetivo**: Validar funcionamiento end-to-end de la plataforma en local antes de producción.

**Fecha**: 20 de Noviembre 2025
**Ambiente**: Local (Backend en localhost:8000, Frontend en localhost:3000)

---

## 📋 Casos de Prueba

### 1. AUTENTICACIÓN - Registro

**Descripción**: Verificar que un usuario puede registrarse correctamente

**Pasos**:
1. Ir a http://localhost:3000/register
2. Llenar formulario con:
   - Nombre: `Test User UAT`
   - Email: `test.uat@example.com`
   - Contraseña: `TestPassword123!`
3. Click en "Registrarse"

**Resultado Esperado**:
- ✅ Sin errores CORS
- ✅ Sin errores de validación
- ✅ Redirigido a onboarding
- ✅ Backend log: `201 Created`

**Resultado Actual**: [ ] PASS [ ] FAIL
**Notas**: 

---

### 2. AUTENTICACIÓN - Login

**Descripción**: Verificar que un usuario puede hacer login

**Pasos**:
1. Ir a http://localhost:3000/login
2. Usar credenciales del test anterior
3. Click en "Login"

**Resultado Esperado**:
- ✅ Sin errores
- ✅ Token recibido y almacenado
- ✅ Redirigido a dashboard o siguiente pantalla
- ✅ Backend log: `200 OK`

**Resultado Actual**: [ ] PASS [ ] FAIL
**Notas**: 

---

### 3. ONBOARDING - Completar Perfil

**Descripción**: Completar el flujo de onboarding

**Pasos**:
1. Llenar información de atleta:
   - Nivel: "Intermediate"
   - Objetivos: "Sub-40 10K"
   - Estilo: "Balanced"
2. Click "Continuar" o "Completar"

**Resultado Esperado**:
- ✅ Onboarding marcado como completado
- ✅ Acceso a dashboard principal
- ✅ Backend log: `200 OK`

**Resultado Actual**: [ ] PASS [ ] FAIL
**Notas**: 

---

### 4. GARMIN - Conectar Cuenta

**Descripción**: Conectar Garmin Connect (con credenciales de prueba)

**Pasos**:
1. En dashboard, click "Conectar Garmin"
2. (Si abre ventana de login) Usar:
   - Email: `guillermomartindeoliva@gmail.com`
   - Contraseña: [tu contraseña real]
3. Autorizar acceso
4. Volver a la app

**Resultado Esperado**:
- ✅ Conexión exitosa
- ✅ Credenciales almacenadas
- ✅ Backend log: `200 OK`
- ✅ Sin errores de timeout

**Resultado Actual**: [ ] PASS [ ] FAIL
**Notas**: 

---

### 5. GARMIN - Sincronizar Workouts

**Descripción**: Sincronizar workouts desde Garmin

**Pasos**:
1. Click "Sincronizar Garmin" o "Sync Workouts"
2. Esperar a que se complete
3. Verificar que aparecen workouts en la lista

**Resultado Esperado**:
- ✅ Sync inicia sin errores
- ✅ Muestra progreso o notificación
- ✅ Workouts aparecen en la lista
- ✅ Backend log: `200 OK` + número de workouts sincronizados

**Resultado Actual**: [ ] PASS [ ] FAIL
**Notas**: [ ] TIMEOUT [ ] ERROR [ ] SLOW

---

### 6. WORKOUTS - Listar Entrenamientos

**Descripción**: Ver lista de entrenamientos sincronizados

**Pasos**:
1. Ir a /workouts o sección de entrenamientos
2. Verificar que aparecen workouts
3. Click en uno para ver detalles

**Resultado Esperado**:
- ✅ Lista carga sin errores
- ✅ Muestra información: fecha, distancia, tiempo, ritmo
- ✅ Backend: `GET /api/v1/workouts` → `200 OK`

**Resultado Actual**: [ ] PASS [ ] FAIL
**Notas**: 

---

### 7. DATABASE - Verificar Datos

**Descripción**: Validar que los datos se guardaron correctamente

**Pasos**:
1. Abrir terminal en `backend/`
2. Ejecutar: `sqlite3 runcoach.db`
3. Ejecutar queries:
   ```sql
   SELECT * FROM users WHERE email = 'test.uat@example.com';
   SELECT * FROM workouts WHERE user_id = <user_id_del_paso_anterior>;
   ```

**Resultado Esperado**:
- ✅ Usuario existe en DB
- ✅ Workouts están vinculados al usuario
- ✅ Todas las columnas tienen datos válidos

**Resultado Actual**: [ ] PASS [ ] FAIL
**Notas**: 

---

## 🐛 Bugs Encontrados

| # | Descripción | Severidad | Estado |
|---|-------------|-----------|--------|
| B1 | Garmin sync "colgado" en producción | HIGH | [ ] OPEN [ ] FIXED [ ] WONT_FIX |
|    |            |           |        |

---

## 📊 Resumen

**Total Pruebas**: 7
**Pasadas**: [ ]
**Fallidas**: [ ]
**Bloqueadas**: [ ]

**% Completitud**: [ ]%

---

## ✅ Próximos Pasos

- [ ] Documentar todos los hallazgos
- [ ] Crear tickets de bugs si es necesario
- [ ] Hacer fix si es simple
- [ ] Redeploy a producción cuando todo esté verde
