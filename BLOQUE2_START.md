# 🎬 COMENZAR AHORA - BLOQUE 2

## ✅ Estado del Sistema

```
┌──────────────────────────────────────────────────┐
│                                                  │
│  ✅ Backend        http://127.0.0.1:8000        │
│  ✅ Frontend       http://localhost:3000        │
│  ✅ Database       runcoach.db (30 metrics)     │
│  ✅ Components     Badge + Progress instalados  │
│                                                  │
│         LISTO PARA TESTING BLOQUE 2             │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 🎯 QUÉ HACER AHORA MISMO

### Paso 1️⃣: Abre tu navegador
```
Dirección: http://localhost:3000
```

**Deberías ver:**
- Página de login (no página roja de error)
- Formulario con 2 campos: Email y Password
- Botón "Ingresar"

---

### Paso 2️⃣: Ingresa las credenciales

```
Email:    guillermomartindeoliva@gmail.com
Password: password123
```

**Click en "Ingresar"**

---

### Paso 3️⃣: Espera y verifica dashboard

**Deberías ser redirigido a:**
```
http://localhost:3000/dashboard
```

**En el dashboard verás:**

1. **ReadinessBadge** (arriba, lado izquierdo)
   ```
   Circular badge con número
   Ej: 72 (varía 0-100)
   Color: Verde/Amarillo/Rojo según score
   ```

2. **Workout Stats** (centro)
   ```
   Entrenamientos: 60
   Distancia: 450.5 km
   Tiempo: 3,240 min
   ```

3. **Daily Check-In** (abajo)
   ```
   Sliders para energía, molestias, ánimo, motivación
   Campo para horas de sueño
   Botón "Submit"
   ```

---

### Paso 4️⃣: Haz click en el ReadinessBadge

**Debería navegar a:**
```
http://localhost:3000/health
```

**Verás:**
- Badge más grande
- Gráfico con breakdown (40% Body Battery, 30% Sleep, etc.)
- Tarjetas de métricas (HRV, Resting HR, Sleep, etc.)

---

### Paso 5️⃣: Reporta en este formato

**Copia y completa en tu respuesta:**

```
✅ BLOQUE 2 - RESULTADOS

1. ¿Llegaste a http://localhost:3000? 
   [ ] SÍ [ ] NO

2. ¿El login fue exitoso?
   [ ] SÍ [ ] NO
   Si NO, ¿qué error? ________________

3. ¿Ves el dashboard?
   [ ] SÍ [ ] NO

4. ReadinessBadge:
   [ ] Visible
   Score que ves: _____ (número)
   Color: [ ] Verde [ ] Amarillo [ ] Rojo

5. Workout stats:
   [ ] Visible
   Entrenamientos: _____
   Distancia: _____ km

6. Daily Check-In:
   [ ] Visible

7. ¿Click en badge → /health funciona?
   [ ] SÍ [ ] NO

8. Errores en console (F12):
   [ ] NINGUNO [ ] SÍ (listar abajo)
   ________________________
   ________________________

9. Observaciones:
   ________________________
```

---

## 🆘 Si hay errores

### Error: "Module not found: @/components/ui/progress"
```
→ Abre DevTools (F12)
→ Console tab
→ Si ves este error, recarga la página (Ctrl+Shift+R)
```

### Error: "Network Error" o "Cannot reach server"
```
→ Verifica Terminal 1 (Backend)
→ Debe decir: "Uvicorn running on http://127.0.0.1:8000"
→ Si no, copia en Terminal 1:
   cd C:\Users\guill\Desktop\plataforma-running\backend
   uvicorn app.main:app --reload
```

### Error: "User not found" o "Invalid password"
```
→ Usa exactamente estas credenciales:
   Email: guillermomartindeoliva@gmail.com
   Password: password123
→ Copia-pega (evita typos)
```

### Dashboard carga pero no ves el badge
```
→ Abre DevTools (F12)
→ Console tab
→ Busca errores rojo
→ Reporta qué dice exactamente
```

---

## 📝 Archivos de Referencia

| Archivo | Para qué |
|---------|----------|
| `BLOQUE2_CHECKLIST.md` | Instrucciones detalladas con screenshots |
| `TROUBLESHOOTING.md` | Errores comunes y soluciones |
| `VERIFICACION_PRE_TESTING.md` | Estado actual del sistema |

---

## ⏱️ Duración Estimada

- **Bloque 2**: 5-10 minutos
- Incluye: Login + verificación dashboard + navegación a /health

---

## 🎓 ¿Qué Prueban estos Pasos?

```
✅ Autenticación JWT funciona
✅ Database conección OK
✅ Components renderizan correctamente
✅ API endpoints retornan datos
✅ Navigation entre páginas funciona
✅ UI components (Badge, Progress) importan correctamente
```

---

## 🚀 Ready?

**→ Abre http://localhost:3000 AHORA**

**→ Ingresa credenciales**

**→ Reporta resultados abajo con el template**

¡Vamos! 🎉
