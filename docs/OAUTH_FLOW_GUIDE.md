# 🔐 OAuth Flow para Dispositivos - Guía Completa

## Respuesta a tu Pregunta

**¿El usuario tiene que meter sus credenciales cada vez que entra?**

**NO**. Una vez que el usuario conecta su dispositivo (Garmin, Strava, etc.), **las credenciales se guardan de forma segura** y no necesita volver a autenticarse cada vez que accede al dashboard.

### Cómo Funciona

#### 1️⃣ **Primera Vez (Conexión Inicial)**
```
Usuario → Click "Agregar Dispositivo" (Garmin)
       → Selecciona tipo: Garmin
       → Click "Conectar con Garmin"
       → Redirige a: garmin.com/oauth/authorize
       → Usuario ingresa credenciales EN GARMIN (no en nuestro sitio)
       → Garmin pregunta: "¿Permitir acceso a RunCoach?"
       → Usuario acepta
       → Garmin redirige de vuelta con TOKEN
       → Backend guarda token en database (ENCRIPTADO)
       → ✅ Dispositivo conectado
```

#### 2️⃣ **Siguientes Visitas**
```
Usuario → Entra a dashboard
       → Click "Sincronizar"
       → Backend usa TOKEN GUARDADO
       → Fetch data de Garmin API
       → ✅ Datos actualizados (sin pedir credenciales)
```

---

## 📊 Arquitectura OAuth

### Flujo Completo

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │         │   Backend    │         │  Garmin API │
│  (React)    │         │  (FastAPI)   │         │  (OAuth)    │
└──────┬──────┘         └──────┬───────┘         └──────┬──────┘
       │                       │                        │
       │ 1. "Conectar Garmin"  │                        │
       ├──────────────────────>│                        │
       │                       │ 2. Genera auth URL     │
       │                       ├───────────────────────>│
       │                       │                        │
       │ 3. Redirect a Garmin  │                        │
       ├───────────────────────┼───────────────────────>│
       │                       │                        │
       │                 4. Usuario autentica           │
       │                       │                   [Login Form]
       │                       │                        │
       │ 5. Callback con code  │                        │
       │<──────────────────────┼────────────────────────┤
       │                       │                        │
       │ 6. Exchange code      │                        │
       ├──────────────────────>│ 7. POST /token        │
       │                       ├───────────────────────>│
       │                       │ 8. Returns token       │
       │                       │<───────────────────────┤
       │                       │ 9. Save to DB          │
       │                       │ [users.garmin_tokens]  │
       │ 10. Success!          │                        │
       │<──────────────────────┤                        │
       │                       │                        │
```

---

## 🔑 Tokens Guardados

### Database Schema (Ya implementado en Fase 3)

```sql
users (
  ...
  connected_devices JSON,  -- Lista de devices conectados
  device_tokens JSON,      -- Tokens OAuth por device
  sync_preferences JSON    -- Config de sincronización
)
```

### Ejemplo de `device_tokens`

```json
{
  "garmin": {
    "access_token": "abc123...",
    "refresh_token": "xyz789...",
    "expires_at": "2025-12-14T10:00:00Z",
    "scope": "activities:read"
  },
  "strava": {
    "access_token": "def456...",
    "refresh_token": "uvw012...",
    "expires_at": "2025-12-14T10:00:00Z",
    "scope": "activity:read_all"
  }
}
```

---

## 🔄 Refresh Token Flow

Los tokens OAuth **expiran** (normalmente en 1-2 horas). Pero usamos **refresh tokens** para renovarlos automáticamente:

```
Backend detecta token expirado
  → Usa refresh_token
  → Llama a /oauth/refresh en Garmin
  → Recibe nuevo access_token
  → Guarda en DB
  → Continúa sincronización
  → ✅ Usuario NO tiene que volver a autenticar
```

---

## 🛡️ Seguridad

### Datos Encriptados

```python
# backend/app/security.py
from cryptography.fernet import Fernet

def encrypt_token(token: str) -> str:
    """Encripta token antes de guardar en DB"""
    cipher = Fernet(settings.SECRET_KEY)
    return cipher.encrypt(token.encode()).decode()

def decrypt_token(encrypted: str) -> str:
    """Desencripta token para usar en API"""
    cipher = Fernet(settings.SECRET_KEY)
    return cipher.decrypt(encrypted.encode()).decode()
```

### Nunca Se Almacena

❌ **NO guardamos**: Contraseña del usuario de Garmin/Strava
✅ **SÍ guardamos**: Token OAuth (encriptado)

---

## 📝 Implementación por Dispositivo

### Garmin Connect

**OAuth 2.0 Flow**

```python
# backend/app/services/garmin_service.py

async def initiate_garmin_oauth(user_id: int):
    """Inicia OAuth flow con Garmin"""
    auth_url = f"https://connect.garmin.com/oauthConfirm"
    params = {
        "oauth_consumer_key": settings.GARMIN_CLIENT_ID,
        "oauth_callback": f"{settings.FRONTEND_URL}/callback/garmin",
        "oauth_signature_method": "HMAC-SHA1"
    }
    return auth_url + "?" + urlencode(params)

async def handle_garmin_callback(code: str, user_id: int):
    """Procesa callback de Garmin"""
    # Exchange code for token
    token_response = await garmin_client.get_token(code)
    
    # Save to DB (encrypted)
    encrypted_token = encrypt_token(token_response.access_token)
    
    await db.execute(
        "UPDATE users SET device_tokens = JSON_SET(device_tokens, '$.garmin', ?) WHERE id = ?",
        (encrypted_token, user_id)
    )
```

### Strava

**OAuth 2.0 Flow**

```python
# backend/app/services/strava_service.py

async def initiate_strava_oauth(user_id: int):
    """Inicia OAuth flow con Strava"""
    auth_url = "https://www.strava.com/oauth/authorize"
    params = {
        "client_id": settings.STRAVA_CLIENT_ID,
        "redirect_uri": f"{settings.FRONTEND_URL}/callback/strava",
        "response_type": "code",
        "scope": "activity:read_all,profile:read_all"
    }
    return auth_url + "?" + urlencode(params)
```

### Apple Health

**HealthKit Authorization**

```swift
// iOS app integration (futuro)
HKHealthStore().requestAuthorization(
    toShare: nil,
    read: [HKObjectType.workoutType()],
    completion: { success, error in
        // Envía token a backend
    }
)
```

---

## 🔄 Sincronización Automática

### Cron Job (Backend)

```python
# backend/app/tasks/sync_devices.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', hours=1)
async def auto_sync_all_devices():
    """Sincroniza todos los dispositivos con auto_sync_enabled"""
    users = await db.fetch_all("SELECT * FROM users WHERE device_tokens IS NOT NULL")
    
    for user in users:
        for device_type, config in user.connected_devices.items():
            if config.get('auto_sync_enabled'):
                await sync_device(user.id, device_type)

async def sync_device(user_id: int, device_type: str):
    """Sincroniza un dispositivo específico"""
    # Obtiene token (desencripta)
    token = decrypt_token(user.device_tokens[device_type]['access_token'])
    
    # Verifica si expiró
    if is_token_expired(user.device_tokens[device_type]['expires_at']):
        token = await refresh_oauth_token(user_id, device_type)
    
    # Fetch workouts
    workouts = await fetch_workouts_from_api(device_type, token)
    
    # Guarda en DB
    await save_workouts(user_id, workouts, source=device_type)
```

---

## 🎯 User Experience

### Primera Conexión (Una sola vez)

```
┌─────────────────────────────────────────┐
│  Agregar Dispositivo                   │
├─────────────────────────────────────────┤
│  [🔵] Garmin                           │
│  [🟠] Xiaomi                           │
│  [🟠] Strava                           │
│  [⚫] Apple Health                     │
│  [🟢] Manual                           │
└─────────────────────────────────────────┘
         ↓ Click "Garmin"
┌─────────────────────────────────────────┐
│  Conectar con Garmin                   │
├─────────────────────────────────────────┤
│  Te redirigiremos a Garmin Connect     │
│  para autorizar el acceso.             │
│                                         │
│  [Conectar con Garmin Connect] ────────┤
└─────────────────────────────────────────┘
         ↓ Redirige a garmin.com
┌─────────────────────────────────────────┐
│  🔵 Garmin Connect                     │
├─────────────────────────────────────────┤
│  Email: user@example.com               │
│  Password: ********                    │
│                                         │
│  [Login]                                │
└─────────────────────────────────────────┘
         ↓ Login exitoso
┌─────────────────────────────────────────┐
│  Autorizar RunCoach                    │
├─────────────────────────────────────────┤
│  RunCoach solicita acceso a:           │
│  ✓ Leer actividades                    │
│  ✓ Leer perfil                         │
│                                         │
│  [Denegar]  [Autorizar]  ──────────────┤
└─────────────────────────────────────────┘
         ↓ Click "Autorizar"
┌─────────────────────────────────────────┐
│  ✅ Garmin Conectado                   │
├─────────────────────────────────────────┤
│  Sincronizando actividades...          │
│  ████████████████████ 100%             │
│                                         │
│  15 entrenamientos importados          │
└─────────────────────────────────────────┘
```

### Siguientes Usos (Automático)

```
Usuario entra a dashboard
  → Ve datos actualizados (automático)
  → O click "Sincronizar Ahora"
  → ✅ Datos refresh (sin pedir credenciales)
```

---

## ⚙️ Configuración por Usuario

### Opciones de Sincronización

```typescript
// Frontend: DevicesList.tsx
interface SyncConfig {
  sync_interval_hours: number;  // 1-24 horas
  auto_sync_enabled: boolean;   // true/false
  last_sync: Date | null;       // Timestamp
  next_sync: Date | null;       // Calculado
}
```

### Panel de Control

```
┌─────────────────────────────────────────┐
│  Garmin Forerunner 945                 │
├─────────────────────────────────────────┤
│  🟢 Conectado                          │
│  Última sincronización: hace 2 horas   │
│  Próxima: en 4 horas                   │
│                                         │
│  Sincronización automática: ✓ ON       │
│  Intervalo: ──●────── 6 horas         │
│                                         │
│  [Sincronizar Ahora]  [Desconectar]    │
└─────────────────────────────────────────┘
```

---

## 🔒 Desconexión

### Revoke Token

```python
async def disconnect_device(user_id: int, device_type: str):
    """Desconecta dispositivo y revoca token"""
    # Revoke en servicio externo
    if device_type == "garmin":
        await garmin_client.revoke_token(user.device_tokens['garmin'])
    
    # Elimina de DB
    await db.execute(
        "UPDATE users SET device_tokens = JSON_REMOVE(device_tokens, '$.garmin') WHERE id = ?",
        (user_id,)
    )
```

---

## 📋 Resumen

| Acción | Requiere Credenciales | Frecuencia |
|--------|----------------------|------------|
| **Primera conexión** | ✅ Sí (en Garmin/Strava) | 1 vez |
| **Sincronización manual** | ❌ No | A demanda |
| **Sincronización automática** | ❌ No | Cada X horas |
| **Refresh token** | ❌ No | Automático |
| **Ver dashboard** | ❌ No | Siempre |

### Ventajas

✅ **UX excelente**: Usuario conecta una vez, olvida
✅ **Seguro**: Tokens encriptados, nunca contraseñas
✅ **Automático**: Sincronización en background
✅ **Standard**: OAuth 2.0 (usado por Google, Facebook, etc.)
✅ **Escalable**: Fácil agregar más devices

---

## 🚀 Próximos Pasos (Fase 3C)

### OAuth Implementation

- [ ] Endpoint `/auth/garmin/init` - Inicia OAuth
- [ ] Endpoint `/auth/garmin/callback` - Procesa callback
- [ ] Endpoint `/auth/strava/init` - Inicia OAuth
- [ ] Endpoint `/auth/strava/callback` - Procesa callback
- [ ] Frontend: OAuthCallback component
- [ ] Frontend: DeviceConnect buttons
- [ ] Token encryption/decryption
- [ ] Refresh token logic
- [ ] Auto-sync cron job

---

## 🎓 Ejemplo de Implementación Completa

### Frontend: Connect Button

```typescript
// components/ConnectDeviceButton.tsx
export function ConnectDeviceButton({ deviceType }: { deviceType: string }) {
  const handleConnect = async () => {
    // 1. Request auth URL from backend
    const response = await apiClient.initiateOAuth(deviceType);
    
    // 2. Redirect to OAuth provider
    window.location.href = response.auth_url;
  };

  return (
    <button onClick={handleConnect}>
      Conectar con {deviceType}
    </button>
  );
}

// pages/callback/[provider].tsx
export default function OAuthCallback() {
  const router = useRouter();
  const { code, state } = router.query;

  useEffect(() => {
    async function handleCallback() {
      // 3. Send code to backend
      await apiClient.handleOAuthCallback(code, state);
      
      // 4. Redirect to devices page
      router.push('/dashboard/devices?success=true');
    }
    handleCallback();
  }, [code]);

  return <div>Conectando dispositivo...</div>;
}
```

### Backend: OAuth Endpoints

```python
# routers/auth.py
@router.get("/auth/{provider}/init")
async def init_oauth(
    provider: str,
    current_user: User = Depends(get_current_user)
):
    """Inicia OAuth flow"""
    if provider == "garmin":
        auth_url = await garmin_service.get_auth_url(current_user.id)
    elif provider == "strava":
        auth_url = await strava_service.get_auth_url(current_user.id)
    
    return {"auth_url": auth_url, "state": generate_state_token()}

@router.post("/auth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str,
    state: str,
    current_user: User = Depends(get_current_user)
):
    """Procesa callback OAuth"""
    # Validate state token
    validate_state_token(state)
    
    # Exchange code for token
    if provider == "garmin":
        token = await garmin_service.exchange_code(code)
    
    # Save encrypted token
    await save_device_token(current_user.id, provider, token)
    
    return {"success": True, "device": provider}
```

---

**Conclusión**: El usuario **solo autentica una vez**, y después todo funciona automáticamente. Las credenciales se guardan de forma segura (encriptadas) y los tokens se renuevan automáticamente cuando expiran.
