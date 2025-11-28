# Fase 3B: Quick Start Guide & Verification

## 🚀 Arrancar la Aplicación

### Terminal 1: Backend
```powershell
cd C:\Users\guill\Desktop\plataforma-running\backend
.\venv\Scripts\uvicorn.exe app.main:app --reload
```
**URL**: http://127.0.0.1:8000

### Terminal 2: Frontend
```powershell
cd C:\Users\guill\Desktop\plataforma-running\frontend
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
npm run dev
```
**URL**: http://localhost:3000

---

## ✅ Verificación: Device Management

### 1. Acceder a la Página
1. Abre: http://localhost:3000/dashboard/devices
2. Verás:
   - Header: "Mis Dispositivos"
   - Master Sync Control card (azul/indigo)
   - "Agregar Dispositivo" button
   - Lista vacía de dispositivos (o existentes)

### 2. Agregar un Dispositivo
1. Haz click en "Agregar Dispositivo"
2. Modal abrirá con:
   - Selector de tipo (5 opciones)
   - Campo de nombre
   - Slider de intervalo (1-24 horas)
   - Toggle de auto-sync
3. Completa:
   - Tipo: Selecciona "Garmin"
   - Nombre: "Mi Garmin Watch"
   - Intervalo: 6 horas
   - Auto-sync: ON
4. Haz click "Agregar"
5. Toast verde confirmará: "Dispositivo agregado exitosamente"

### 3. Ver Dispositivo en Lista
1. El dispositivo aparecerá con:
   - Badge: "Connected" (verde)
   - Icono: ⌚ (Garmin)
   - Nombre: "Mi Garmin Watch"
   - Intervalo: "Cada 6 horas"
   - Última sincronización: timestamp
   - Próxima sincronización: timestamp

### 4. Acciones de Dispositivo
1. Hover sobre la tarjeta
2. Verás tres botones: ⋮ (más opciones)
3. Click en ⋮:
   - **Establecer como primario**: Marca este dispositivo
   - **Editar**: Abre modal para editar (implementar en 3C)
   - **Eliminar**: Abre confirmación

### 5. Eliminar Dispositivo
1. Click en ⋮ > Eliminar
2. Confirmación: "¿Eliminar dispositivo?"
3. Click "Confirmar"
4. Toast rojo: "Dispositivo eliminado"
5. Dispositivo desaparece de la lista

### 6. Sincronización Manual
1. Click "Sincronizar Ahora" (arriba)
2. Button cambia a "Sincronizando..."
3. Espera 2-3 segundos
4. Toast: "Sincronización iniciada"
5. Button regresa a "Sincronizar Ahora"

### 7. Múltiples Dispositivos
Repite paso 2-3 pero con diferentes tipos:
- Xiaomi (📱)
- Strava (🏃)
- Apple Health (🍎)
- Manual (✍️)

Verás colores diferentes para cada tipo.

---

## 🔧 Debugging

### Si no ves componentes...
**Check 1**: ¿Frontend compiló?
```
Verifica terminal 2: "✓ Ready in 3.1s"
```

**Check 2**: ¿Backend corre?
```
Verifica terminal 1: "Application startup complete"
```

**Check 3**: Refresh página
```
Ctrl+F5 (force refresh)
```

### Si el modal no abre...
1. Abre DevTools (F12)
2. Console tab
3. ¿Hay errores rojo?
4. Si sí, reporta el error

### Si API falla...
1. DevTools > Network tab
2. Busca request POST /api/v1/profile/integrations
3. Status debe ser 200 o 201
4. Si es 400/500, revisa body error

---

## 📊 API Endpoints Usados

```
GET  /api/v1/profile/integrations
     ↓ Obtiene lista de dispositivos

POST /api/v1/profile/integrations
     ↓ Agrega nuevo dispositivo
     Body: {device_type, device_name, sync_interval_hours, auto_sync_enabled}

DELETE /api/v1/profile/integrations/{device_id}
       ↓ Elimina dispositivo

POST /api/v1/profile/integrations/{device_id}/set-primary
     ↓ Marca como dispositivo primario

POST /api/v1/profile/integrations/sync-all
     ↓ Sincroniza todos los dispositivos
```

---

## 📝 Prueba Completa

### Test 1: Add Device (Garmin)
```
- Click "Agregar Dispositivo"
- Select: Garmin
- Name: "Forerunner 945"
- Interval: 8
- Auto-sync: ✓
- Click "Agregar"
✓ Device aparece en lista
✓ Toast success
```

### Test 2: Add Device (Xiaomi)
```
- Click "Agregar Dispositivo"
- Select: Xiaomi
- Name: "Mi Band 7"
- Interval: 3
- Auto-sync: ✓
- Click "Agregar"
✓ Dos dispositivos en lista
✓ Colores diferentes
```

### Test 3: Set Primary
```
- Hover Xiaomi card
- Click ⋮ > "Establecer como primario"
- Xiaomi ahora tiene ⭐
✓ Toast: "Dispositivo primario actualizado"
```

### Test 4: Manual Sync
```
- Click "Sincronizar Ahora"
- Button: "Sincronizando..."
- Esperar 2s
✓ Toast: "Sincronización iniciada"
✓ Button normal otra vez
```

### Test 5: Delete Device
```
- Hover Garmin card
- Click ⋮ > "Eliminar"
- Confirmation alert
- Click "Confirmar"
✓ Garmin desaparece
✓ Toast: "Dispositivo eliminado"
✓ Solo Xiaomi en lista
```

---

## 🎯 Casos de Uso

### Caso 1: Usuario nuevo conecta Garmin
1. Accede /dashboard/devices
2. Ve lista vacía
3. Click "Agregar Dispositivo"
4. Selecciona Garmin
5. Completa datos
6. Verifica sincronización
✓ Listo para entrenamientos

### Caso 2: Usuario tiene múltiples dispositivos
1. Ve lista con 3 dispositivos
2. Marca uno como primario ⭐
3. Activa sincronización manual
4. Ve próxima sincronización
✓ Control total

### Caso 3: Usuario quita dispositivo
1. Abre página
2. Selecciona dispositivo a eliminar
3. Confirma acción
4. Dispositivo se elimina
✓ Datos históricos preservados

---

## 🚨 Notas Importantes

### Sincronización
- Auto-sync: Se ejecuta cada X horas (según intervalo)
- Manual sync: Se ejecuta inmediatamente
- Status: Muestra "Connected" o "Syncing"

### Dispositivo Primario
- Solo uno puede ser primario
- Usado para dashboards adaptativos (Fase 2)
- Cambio inmediato

### Colores
| Dispositivo | Color | Código |
|------------|-------|--------|
| Garmin | 🔵 Azul | #2563eb |
| Xiaomi | 🟠 Naranja | #f97316 |
| Strava | 🟠 Naranja-600 | #ea580c |
| Apple | ⚫ Gris | #1f2937 |
| Manual | 🟢 Verde | #16a34a |

---

## 📞 Support

Si algo no funciona:

1. **Verifica logs del backend**
   - ¿Request llegó?
   - ¿Qué error?

2. **Revisa DevTools**
   - Console: ¿hay errores JS?
   - Network: ¿respuesta API?

3. **Reinicia todo**
   - Ctrl+C en ambas terminales
   - Borra cache (npm run clean)
   - npm run dev nuevamente

---

## 🎓 Resumen de Componentes

| Componente | Ubicación | Propósito |
|-----------|-----------|----------|
| DevicesList | components/ | Gestor principal |
| DeviceCard | components/ | Item dispositivo |
| AddDeviceModal | components/ | Form agregar |
| Dialog | components/ui/ | Modal container |
| DropdownMenu | components/ui/ | Menu acciones |
| Select | components/ui/ | Selector tipo |
| Toast | components/ui/ | Notificaciones |
| ToastProvider | lib/ | Context estado |

---

## ✨ Próximo: Fase 3C

- Implementar Device Edit Modal
- Device Details Page
- Sync History Timeline
- Device Pairing Flows
- Advanced Settings

---

**Fase 3B Status**: ✅ COMPLETA Y FUNCIONAL

Accede a: http://localhost:3000/dashboard/devices

¡Disfruta! 🚀
