# 🔧 TROUBLESHOOTING - Si algo va mal

## 🚨 Errores Comunes y Soluciones

### Error 1: "Module not found: @/components/ui/progress"

**Causa**: Next.js se ejecutó antes de instalar la dependencia

**Solución**:
```powershell
# En Terminal 2 (frontend)
# 1. Detén Next.js: Ctrl+C
# 2. Instala la dependencia
cd C:\Users\guill\Desktop\plataforma-running\frontend
npm install @radix-ui/react-progress --legacy-peer-deps

# 3. Reinicia
npm run dev

# 4. Espera "✓ Ready in X.Xs"
```

---

### Error 2: "Cannot find module '@/components/ui/badge'"

**Causa**: Badge component no existe

**Solución**:
```powershell
# El archivo debería existir en:
# C:\Users\guill\Desktop\plataforma-running\frontend\components\ui\badge.tsx

# Verifica:
Test-Path "C:\Users\guill\Desktop\plataforma-running\frontend\components\ui\badge.tsx"

# Si retorna False, el archivo se perdió
# Recrea:
# 1. Abre VS Code
# 2. Crea archivo en: frontend/components/ui/badge.tsx
# 3. Copia contenido de inicio de TECHNICAL_DOCS.md
# 4. Guarda
# 5. Recarga navegador
```

---

### Error 3: "Network Error" o "Failed to fetch" en login

**Causa**: Backend no responde

**Verificación**:
```powershell
# ¿Está Backend corriendo?
Get-Process | Where-Object {$_.ProcessName -eq "python"}

# ¿Puerto 8000 está en uso?
netstat -ano | findstr :8000

# Test conexión
Invoke-WebRequest -Uri http://127.0.0.1:8000/docs
```

**Solución**:
```powershell
# Terminal 1: Reinicia Backend
cd C:\Users\guill\Desktop\plataforma-running\backend
uvicorn app.main:app --reload
```

---

### Error 4: "Invalid password" pero estoy seguro de la contraseña

**Causa**: Contraseña no es `password123` (se cambió o no se guardó)

**Solución**:
```powershell
# Resetea password a conocida
cd C:\Users\guill\Desktop\plataforma-running\backend
python reset_password.py

# Cuando pregunta:
# Email: guillermomartindeoliva@gmail.com
# Nueva contraseña: password123

# Verifica
python debug_user_tokens.py
```

---

### Error 5: "User not found" en login

**Causa**: Email incorrecto o usuario no existe

**Solución**:
```powershell
# Verifica usuario en DB
cd C:\Users\guill\Desktop\plataforma-running\backend
python -c "
import sqlite3
conn = sqlite3.connect('runcoach.db')
cursor = conn.cursor()
cursor.execute('SELECT id, email, has_password FROM user')
for row in cursor.fetchall():
    print(f'ID: {row[0]}, Email: {row[1]}, Has Password: {row[2]}')
"

# Si no hay usuario, créalo (o reset DB)
```

---

### Error 6: Dashboard carga pero "ReadinessBadge es undefined"

**Causa**: ReadinessBadge component no tiene datos

**Verificación en DevTools**:
```javascript
// F12 → Console → Pega:
const token = localStorage.getItem('auth_token')
console.log('Token:', token ? 'Existe' : 'NO EXISTE')

// ¿Tiene auth?
fetch('http://127.0.0.1:8000/health/today', {
  headers: {'Authorization': `Bearer ${token}`}
})
.then(r => r.json())
.then(data => console.log('Health data:', data))
.catch(err => console.error('Error:', err))
```

---

### Error 7: "Compiling..." toma más de 10 segundos

**Causa**: Turbopack está reconstruyendo

**Solución**:
- Espera (normal después de cambios)
- Si pasa 30 segundos, reinicia Terminal 2
- Si persiste: `npm run build` para ver si hay errores

---

### Error 8: "Port 3000 already in use"

**Causa**: Proceso Node anterior no se cerró

**Solución**:
```powershell
# Mata todos los node.exe
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force

# Espera 2 segundos
Start-Sleep -Seconds 2

# Reinicia
cd C:\Users\guill\Desktop\plataforma-running\frontend
npm run dev
```

---

### Error 9: "JSON.parse error" en console

**Causa**: API devuelve HTML en lugar de JSON (probablemente error 500)

**Verificación**:
```powershell
# Endpoint específico que falla?
# Abre en navegador:
http://127.0.0.1:8000/workouts

# Si ve HTML rojo de error → problema en backend
# Si ve JSON → problema en frontend parsing
```

---

### Error 10: "CORS error" o "blocked by CORS policy"

**Causa**: Backend CORS no configurado para localhost:3000

**Verificación en DevTools**:
```javascript
// Console mostrará:
// Access to XMLHttpRequest at 'http://127.0.0.1:8000/...'
// from origin 'http://localhost:3000'
// has been blocked by CORS policy
```

**Solución**:
```python
# En backend/app/main.py, verifica:
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Reinicia backend si cambias
```

---

## 🔍 Debug Checklist

Si algo no funciona, sigue esto:

```
[ ] 1. ¿Backend corriendo? (netstat -ano | findstr :8000)
[ ] 2. ¿Frontend corriendo? (netstat -ano | findstr :3000)
[ ] 3. ¿Token en localStorage? (F12 → Application → auth_token)
[ ] 4. ¿Errores en console? (F12 → Console → busca rojo)
[ ] 5. ¿Errores en red? (F12 → Network → busca 4xx/5xx)
[ ] 6. ¿Base de datos existe? (ls backend/runcoach.db)
[ ] 7. ¿Archivos componentes existen? (ls frontend/components/ui/)
```

---

## 📱 Logs Útiles

### Ver logs del backend en tiempo real
```powershell
# Terminal 1 está corriendo uvicorn
# Los logs aparecen automáticamente
# Busca líneas como:
# GET /workouts 200
# POST /auth/login 200
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Ver logs del frontend (Turbopack)
```powershell
# Terminal 2 está corriendo Next.js
# Los logs muestran compilaciones:
# ✓ Ready in 2.4s
# ○ Compiling /health ...
# ✓ GET /health 200
```

### Ver errores en DevTools (F12)
```
Console: Errores JavaScript
Network: Peticiones HTTP (status 200, 4xx, 5xx)
Application → Storage → localStorage: Tokens guardados
```

---

## 🆘 Último Recurso: Reset Completo

**Si todo se rompió**:

```powershell
# 1. Para todo
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. Limpia localStorage en navegador
# F12 → Application → Storage → Clear site data

# 3. Reset base de datos
cd C:\Users\guill\Desktop\plataforma-running\backend
Remove-Item runcoach.db
python seed_health_data.py

# 4. Reinstala dependencias frontend
cd ..\frontend
npm install --legacy-peer-deps

# 5. Reinicia todo
# Terminal 1: cd backend && uvicorn app.main:app --reload
# Terminal 2: cd frontend && npm run dev

# 6. Espera ~10 segundos para que se inicialice todo

# 7. Intenta de nuevo
# http://localhost:3000
```

---

## 📞 Información Para Reportar

Si nada funciona, copia-pega esto en tu respuesta:

```
SISTEMA INFO:
- OS: Windows 11 (o tu versión)
- Node version: [copia de: node --version]
- npm version: [copia de: npm --version]
- Python version: [copia de: python --version]

ESTADO ACTUAL:
- Backend: [ ] Running [ ] Failed
- Frontend: [ ] Running [ ] Failed
- Database: [ ] Exists [ ] Missing

ERRORES EXACTOS:
[Copia los errores de console/network aquí]

QUÉ HICISTE ÚLTIMO:
[Describe los últimos 3 pasos que hiciste antes del error]

ARCHIVOS RELEVANTES:
- Token guardado: [SÍ/NO]
- Badge component existe: [SÍ/NO]
- Progress component existe: [SÍ/NO]
```

---

## 💡 Pro Tips

1. **Abre DevTools siempre** (F12)
   - Network tab → ver peticiones
   - Console tab → ver errores
   - Application → Storage → localStorage

2. **Recarga con Ctrl+Shift+R** (hard refresh)
   - Limpia cache del navegador
   - Fuerza recargar JavaScript nuevo

3. **Mantén los 2 terminals abiertos**
   - Terminal 1: Backend (uvicorn)
   - Terminal 2: Frontend (next dev)
   - Terminal 3: Debug/utilities

4. **Espera después de cambios**
   - Turbopack: ~3-5 segundos para compilar
   - Uvicorn: ~1-2 segundos para recargar

5. **Revisa Network tab primero**
   - Si la petición devuelve 500 → problema backend
   - Si devuelve 200 pero frontend falla → problema parsing
   - Si devuelve CORS error → problema de configuración
