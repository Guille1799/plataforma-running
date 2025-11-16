# 🧪 RUNCOACH E2E TESTING - INSTRUCCIONES UAT

## PAQUETE 1: AUTHENTICATION & BASIC FLOW

### 📋 ANTES DE EMPEZAR

**Verifica que tengas:**
1. ✅ Backend corriendo en `http://127.0.0.1:8000`
2. ✅ Frontend corriendo en `http://localhost:3000`
3. ✅ Python 3.9+ instalado
4. ✅ requests library (`pip install requests`)

---

## 🎯 OBJETIVO DEL PAQUETE 1

Validar que los flujos críticos de autenticación y operaciones básicas funcionan:

- ✅ Servidores están accesibles
- ✅ Registro de usuario
- ✅ Login y obtener token JWT
- ✅ Acceder a perfil protegido
- ✅ Crear objetivos
- ✅ Generar planes de entrenamiento
- ✅ Calcular VDOT

---

## 🚀 CÓMO EJECUTAR

### OPCIÓN A: Desde PowerShell
```powershell
cd c:\Users\guill\Desktop\plataforma-running
python e2e_test_package_1.py
```

### OPCIÓN B: Desde Git Bash / Terminal
```bash
cd /c/Users/guill/Desktop/plataforma-running
python e2e_test_package_1.py
```

---

## ✅ RESULTADO ESPERADO

Si TODO funciona correctamente, verás:

```
============================================================
RUNCOACH E2E TEST SUITE - PAQUETE 1
AUTHENTICATION & BASIC FLOW
============================================================

📡 FASE 1: VERIFICAR SERVIDORES
------------------------------------------------------------
  ✅ PASS: Backend respondiendo correctamente
  ✅ PASS: Frontend respondiendo correctamente

🔐 FASE 2: AUTENTICACIÓN
------------------------------------------------------------
  ✅ PASS: Usuario registrado: e2e_test_XXXXXXXXXX@runcoach.test
  ✅ PASS: Login exitoso, token obtenido

⚙️  FASE 3: OPERACIONES BÁSICAS
------------------------------------------------------------
  ✅ PASS: Perfil recuperado correctamente
  ✅ PASS: Objetivo creado exitosamente (ID: X)

🚀 FASE 4: FEATURES PRINCIPALES
------------------------------------------------------------
  ✅ PASS: Plan generado: Marathon Training Plan - 12 Weeks (12 semanas)
  ✅ PASS: VDOT calculado: 45.3 (advanced)

============================================================
RESUMEN DE TESTS - PAQUETE 1
============================================================
Total:    9
Pasados:  9 ✅
Fallidos: 0 ❌
Tasa:     100.0%
============================================================
```

---

## ❌ SI ALGO FALLA

Si ves algo como:

```
❌ FAIL: Backend Health
   Razón: No se puede conectar: [Errno 111] Connection refused
```

**Significa:** Backend no está corriendo. 
**Solución:** Asegurate que `uvicorn` está ejecutándose en terminal separada.

---

## 📝 NOTAS IMPORTANTES

### 1. Cada test usa un email único
- Genera un email temporal: `e2e_test_TIMESTAMP@runcoach.test`
- Esto permite ejecutar los tests múltiples veces sin conflictos

### 2. Timeouts
- Training Plans puede tardar ~15-20 segundos (está llamando a AI)
- Es normal si ves una pausa ahí

### 3. Si Test 5 (Create Goal) falla
- No es crítico, el endpoint podría no estar en ruta exacta
- Los otros tests continuarán

### 4. Test Coverage
- ✅ Autenticación completa
- ✅ Acceso a recursos protegidos
- ✅ Features principales del app
- ✅ Integración Backend-Frontend

---

## 📊 QUÉ PROBAMOS

| # | Test | Crítico | Descripción |
|---|------|---------|-------------|
| 1 | Backend Health | 🔴 CRÍTICO | Backend debe estar en línea |
| 2 | Frontend Health | 🔴 CRÍTICO | Frontend debe estar en línea |
| 3 | User Registration | 🔴 CRÍTICO | Crear nueva cuenta |
| 4 | User Login | 🔴 CRÍTICO | Obtener JWT token |
| 5 | Get Profile | 🟡 IMPORTANTE | Acceso a recurso protegido |
| 6 | Create Goal | 🟢 BÁSICO | CRUD de objetivos |
| 7 | Generate Plan | 🔴 CRÍTICO | Feature principal con AI |
| 8 | Calculate VDOT | 🟡 IMPORTANTE | Predicciones |

---

## ✨ CUANDO TERMINES

1. 📸 Toma screenshot del output completo
2. 💬 Dime "OK" si TODO pasó
3. Si algo falló, reporta:
   - Cual test falló
   - El mensaje de error exacto
   - Qué pasos tomaste antes

Entonces procederemos al **PAQUETE 2**

---

## 🎯 PRÓXIMOS PAQUETES (después de este)

- **Paquete 2:** Workouts & Health Tracking
- **Paquete 3:** Coach AI & Chat
- **Paquete 4:** Integration Tests
- **Paquete 5:** Edge Cases & Error Handling

---

**¡Adelante! Ejecuta el test y envíame el resultado 🚀**
