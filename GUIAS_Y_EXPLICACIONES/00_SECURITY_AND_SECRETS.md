# 🔐 Gestión de Datos Sensibles en RunCoach AI

## 📋 Resumen Ejecutivo

**¿Cómo funcionan los secrets en GitHub?**
- Tu archivo `.env` con las API keys **NUNCA** se sube a GitHub
- GitHub solo tiene `.env.example` con valores de plantilla
- Cada desarrollador/servidor crea su propio `.env` local con valores reales
- El `.gitignore` bloquea automáticamente `.env` y `.env.*`

---

## 🔑 Datos Sensibles que Tenemos

### 1. **SECRET_KEY** (JWT)
**Qué es:** Clave para firmar tokens de autenticación (login/register)
**Dónde se usa:** Backend - firma y verifica JWT tokens
**Cómo se genera:**
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
**Valor actual:** En tu `.env` local (NO en GitHub)
**Importancia:** 🔴 CRÍTICO - Si se filtra, un atacante puede crear tokens falsos

### 2. **GROQ_API_KEY**
**Qué es:** API key de Groq para IA (Llama 3.3 70B)
**Dónde se usa:** Backend - análisis de entrenamientos, planes personalizados
**Cómo se obtiene:** https://console.groq.com/keys
**Formato:** `gsk_...` (empieza con gsk_)
**Valor actual:** En tu `.env` local (NO en GitHub)
**Importancia:** 🟡 MEDIO - Si se filtra, pueden usar tu cuota de API

### 3. **DATABASE_URL** (PostgreSQL)
**Qué es:** Credenciales de base de datos
**Formato:** `postgresql://usuario:contraseña@host:puerto/nombre_db`
**Desarrollo:** `postgresql://runcoach:runcoach_dev_password@db:5432/runcoach`
**Producción:** URL de Render (diferente, con SSL)
**Importancia:** 🔴 CRÍTICO - Acceso directo a todos los datos

### 4. **GARMIN_EMAIL + GARMIN_PASSWORD**
**Qué es:** Credenciales de cada usuario para Garmin
**Dónde se almacenan:** 
- Email: Base de datos (cifrado)
- Password: NUNCA se guarda - solo se usa para generar tokens OAuth
- Tokens OAuth: En volumen Docker persistente (`garmin_tokens/`)
**Importancia:** 🔴 CRÍTICO - Credenciales personales de usuarios

### 5. **STRAVA_CLIENT_ID + STRAVA_CLIENT_SECRET**
**Qué es:** Credenciales OAuth de Strava
**Dónde se usan:** Backend - autenticación con Strava API
**Cómo se obtienen:** https://www.strava.com/settings/api
**Importancia:** 🟡 MEDIO - Necesarios para OAuth de Strava

---

## 🛡️ Sistema de Protección en Capas

### Capa 1: `.gitignore`
```gitignore
# Bloquea automáticamente:
.env
.env.*        # .env.local, .env.production, etc.
!.env.example # EXCEPTO .env.example (plantilla)
```

**Resultado:** Git ignora completamente los archivos `.env` con secrets reales

### Capa 2: `.env.example`
```bash
# Archivo público en GitHub con valores de ejemplo
GROQ_API_KEY=gsk_your_api_key_here
SECRET_KEY=your-secret-key-here-change-in-production
```

**Propósito:** Mostrar qué variables necesitas sin revelar valores reales

### Capa 3: Docker Environment Variables
```yaml
# docker-compose.dev.yml
environment:
  SECRET_KEY: ${SECRET_KEY:-dev-secret-key-change-in-production}
  GROQ_API_KEY: ${GROQ_API_KEY}
```

**Funcionamiento:**
- `${GROQ_API_KEY}` → Lee del `.env` local
- `${SECRET_KEY:-valor_default}` → Lee del `.env` o usa default
- Docker inyecta las variables en los contenedores sin exponerlas

### Capa 4: GitHub Secret Scanning
GitHub automáticamente escanea commits y **bloquea** si detecta:
- API keys (como pasó con tu Groq key antes)
- Tokens de autenticación
- Contraseñas en texto plano

---

## 🔄 Flujo de Trabajo con Secrets

### Desarrollo Local

1. **Primera vez (setup inicial):**
```bash
# 1. Clonar repo (sin secrets)
git clone https://github.com/Guille1799/plataforma-running.git

# 2. Crear .env local
cp .env.example .env

# 3. Editar .env con valores reales
nano .env  # o notepad .env en Windows

# 4. Iniciar servicios (Docker lee .env automáticamente)
start-dev.bat
```

2. **Trabajo diario:**
- Tu `.env` está en tu máquina, ignorado por Git
- Puedes modificarlo sin riesgo de subirlo accidentalmente
- Si haces `git add .`, Git **ignora** `.env` automáticamente

### Producción (Render)

1. **Variables de entorno en Render Dashboard:**
```
SECRET_KEY = [valor generado manualmente]
GROQ_API_KEY = gsk_tu_key_real
DATABASE_URL = [auto-generado por Render PostgreSQL]
```

2. **Render inyecta estas variables en los contenedores:**
- No están en el código
- No están en GitHub
- Solo existen en el entorno de Render

---

## 🚨 Incidente de Seguridad Anterior

**Lo que pasó:**
- Archivos `SECURITY_AUDIT.md` y `SETUP_GROQ_AND_SECRETS.md` tenían tu Groq API key
- GitHub Secret Scanning lo detectó y **bloqueó el push**
- Tuvimos que usar `git filter-branch` para eliminar los commits del historial

**Lección aprendida:**
- NUNCA poner secrets en archivos `.md` de documentación
- Usar `GROQ_API_KEY` en lugar de `gsk_...` literal
- Revisar antes de commit con `git diff`

---

## 🔐 Sistema de Acceso y Autenticación

### Flujo de Autenticación Completo

```
┌─────────────────────────────────────────────────────────────┐
│                    1. REGISTRO (Sign Up)                     │
└─────────────────────────────────────────────────────────────┘
Usuario → POST /api/v1/auth/register
         {email, password, name}
            ↓
Backend:  1. Valida email único
          2. Hash password con bcrypt (salt rounds=12)
          3. Crea User en DB
          4. Genera access_token (JWT, expira 30 min)
          5. Genera refresh_token (JWT, expira 7 días)
            ↓
Frontend: Guarda tokens en localStorage
          Redirige a /dashboard

┌─────────────────────────────────────────────────────────────┐
│                     2. LOGIN (Sign In)                       │
└─────────────────────────────────────────────────────────────┘
Usuario → POST /api/v1/auth/login
         {email, password}
            ↓
Backend:  1. Busca user por email
          2. Verifica password con bcrypt.verify()
          3. Genera nuevos access + refresh tokens
            ↓
Frontend: Guarda tokens en localStorage
          Redirige a /dashboard

┌─────────────────────────────────────────────────────────────┐
│              3. PETICIONES AUTENTICADAS (Protegidas)         │
└─────────────────────────────────────────────────────────────┘
Usuario → GET /api/v1/workouts (cualquier endpoint protegido)
         Header: Authorization: Bearer <access_token>
            ↓
Backend:  1. Extrae token del header
          2. Verifica firma con SECRET_KEY
          3. Decodifica payload → user_id
          4. Busca User en DB
          5. Si válido → procesa petición
          6. Si expirado → 401 Unauthorized
            ↓
Frontend: Si 401 → intenta refresh token
          Si refresh falla → redirige a /login

┌─────────────────────────────────────────────────────────────┐
│                  4. REFRESH TOKEN (Renovación)               │
└─────────────────────────────────────────────────────────────┘
Frontend detecta access_token expirado
    ↓
POST /api/v1/auth/refresh
Header: Authorization: Bearer <refresh_token>
    ↓
Backend:  1. Verifica refresh_token (válido 7 días)
          2. Genera NUEVO access_token (30 min)
          3. Genera NUEVO refresh_token (7 días)
    ↓
Frontend: Actualiza tokens en localStorage
          Reintenta petición original

┌─────────────────────────────────────────────────────────────┐
│                     5. LOGOUT (Cerrar Sesión)                │
└─────────────────────────────────────────────────────────────┘
Usuario → Click "Logout"
    ↓
Frontend: 1. Elimina tokens de localStorage
          2. Redirige a /login
    ↓
Backend: NO necesita endpoint (stateless JWT)
```

### Estructura de JWT Tokens

**Access Token (30 minutos):**
```json
{
  "sub": "1",           // user_id
  "exp": 1736345678,    // timestamp de expiración
  "type": "access"
}
```

**Refresh Token (7 días):**
```json
{
  "sub": "1",           // user_id
  "exp": 1736950478,    // timestamp de expiración
  "type": "refresh"
}
```

### Almacenamiento de Tokens

**Frontend (localStorage):**
```javascript
// lib/auth.ts
localStorage.setItem('access_token', 'eyJhbGci...')
localStorage.setItem('refresh_token', 'eyJhbGci...')
```

**Backend (NO almacena tokens):**
- JWT es **stateless** → no hay tabla de "sesiones"
- Cada request verifica el token independientemente
- Logout = simplemente borrar token del frontend

---

## 📊 Tabla de Datos Sensibles

| Dato | Ubicación Local | Ubicación GitHub | Ubicación Producción | Nivel Crítico |
|------|----------------|-----------------|---------------------|---------------|
| `SECRET_KEY` | `.env` (ignorado) | `.env.example` (fake) | Render Env Vars | 🔴 CRÍTICO |
| `GROQ_API_KEY` | `.env` (ignorado) | `.env.example` (fake) | Render Env Vars | 🟡 MEDIO |
| `DATABASE_URL` | Docker Compose | NO | Render PostgreSQL | 🔴 CRÍTICO |
| Garmin OAuth Tokens | Docker Volume | NO | Docker Volume (Render) | 🔴 CRÍTICO |
| User Passwords | PostgreSQL (hash bcrypt) | NO | PostgreSQL (hash bcrypt) | 🔴 CRÍTICO |
| JWT Access Token | localStorage (frontend) | NO | localStorage (producción) | 🟠 ALTO |
| JWT Refresh Token | localStorage (frontend) | NO | localStorage (producción) | 🔴 CRÍTICO |

---

## ✅ Mejores Prácticas Implementadas

### ✅ 1. Variables de Entorno
- Secrets en `.env`, NO en código
- `.env` ignorado por `.gitignore`
- `.env.example` como plantilla pública

### ✅ 2. Bcrypt para Passwords
```python
# Al registrar
hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))

# Al hacer login
bcrypt.checkpw(password.encode(), user.hashed_password.encode())
```

### ✅ 3. JWT con Expiración
- Access: 30 minutos (corto plazo)
- Refresh: 7 días (largo plazo)
- Firma con HMAC-SHA256

### ✅ 4. OAuth Tokens Persistentes
- Garmin tokens en volumen Docker
- NO en base de datos
- Renovación automática con `garth`

### ✅ 5. HTTPS en Producción
- Render provee SSL automático
- Certificados Let's Encrypt
- Redirect HTTP → HTTPS

---

## 🚨 Qué Hacer si un Secret se Filtra

### Si tu GROQ_API_KEY se expone:

1. **Inmediatamente:**
```bash
# 1. Ir a https://console.groq.com/keys
# 2. Revocar la key comprometida
# 3. Generar nueva key
```

2. **Actualizar localmente:**
```bash
# .env
GROQ_API_KEY=gsk_nueva_key_generada
```

3. **Actualizar en producción:**
```bash
# Render Dashboard → Environment Variables
# GROQ_API_KEY = gsk_nueva_key_generada
```

4. **Limpiar historial de Git (si está en commits):**
```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch archivo_con_secret.md" \
  --prune-empty --tag-name-filter cat -- --all

git push -f origin main
```

### Si tu SECRET_KEY se expone:

**⚠️ MUY GRAVE** - Todos los tokens existentes quedan inválidos

1. **Generar nueva key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **Actualizar en `.env` y Render**

3. **Consecuencias:**
   - Todos los usuarios deben hacer login de nuevo
   - Tokens antiguos no funcionarán
   - Celery tasks pueden fallar temporalmente

---

## 📚 Recursos Adicionales

- **Generar SECRET_KEY:** `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- **Groq Console:** https://console.groq.com/keys
- **JWT Debugger:** https://jwt.io
- **Render Docs:** https://render.com/docs/environment-variables
- **Git Filter Branch:** https://git-scm.com/docs/git-filter-branch

---

## 🎯 Checklist de Seguridad

- [x] `.env` en `.gitignore`
- [x] Passwords hasheados con bcrypt
- [x] JWT con expiración
- [x] HTTPS en producción
- [x] GitHub Secret Scanning activo
- [x] OAuth tokens en volumen persistente
- [x] Variables de entorno en Render
- [x] `.env.example` con valores fake
- [ ] Rotación periódica de SECRET_KEY (cada 3-6 meses)
- [ ] Monitoreo de accesos sospechosos
- [ ] Rate limiting en endpoints de auth

---

**Última actualización:** 8 de enero de 2026
**Autor:** Guillermo (@Guille1799)
