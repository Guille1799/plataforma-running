# 🚀 Development Guide - Iniciar Servidores Locales

## Quick Start (Lo más simple)

### Opción 1: Windows - Double-Click (⭐ Recomendado)

1. **Abre 2 Command Prompts/PowerShell**

2. **Terminal 1 - Backend:**
   ```
   cd backend
   python -m uvicorn app.main:app --reload
   ```
   ✅ Verás: `Uvicorn running on http://127.0.0.1:3000`

3. **Terminal 2 - Frontend:**
   ```
   npm run dev
   ```
   ✅ Verás: `http://localhost:3000`

### Opción 2: PowerShell con Conda (Lo que estaba costando)

```powershell
# Terminal 1 - Backend
cd .\backend
C:/Users/Guille/miniconda3/Scripts/conda.exe run -p C:\Users\Guille\miniconda3 python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
npm run dev
```

---

## ¿Por qué "cuesta tanto" iniciar?

### La Realidad: No debería costar tanto

```
PROBLEMA: Python no está en el PATH
├─ Windows instala Python pero lo oculta en Users\AppData
├─ PowerShell no lo encuentra sin conda
└─ Solución: Usar conda.exe explícitamente (lo que hicimos)

RESULTADO:
├─ Sin solución: Necesitas comando LARGO cada vez
├─ Con solución: Clic en archivo .bat O comando simple
└─ Tiempo ahorrado: 30 segundos cada vez que inicias
```

### Las 3 Formas (De Simplemente Más Fácil)

| Método | Facilidad | Velocidad | Windows | Mac/Linux |
|--------|-----------|-----------|---------|-----------|
| **Double-click `start-all.bat`** | ⭐⭐⭐⭐⭐ | 2 clics | ✅ | ❌ |
| **Script `start-backend.bat`** | ⭐⭐⭐⭐⭐ | 1 clic + NPM | ✅ | ❌ |
| **Terminal simple** | ⭐⭐ | Largo | Si usas Bash | ✅ |

---

## Status de Servidores

### ✅ Verificar que están corriendo

```powershell
# Opción 1: Check ports
netstat -ano | findstr :3000

# Opción 2: Check processes
Get-Process | Where-Object {$_.Name -like "*python*" -or $_.Name -like "*node*"}
```

### ✅ Verificar endpoints

```powershell
# Backend
Invoke-WebRequest -Uri "http://127.0.0.1:3000/docs" -UseBasicParsing

# Frontend
Invoke-WebRequest -Uri "http://127.0.0.1:3000" -UseBasicParsing
```

---

## Estructura actual

```
plataforma-running/
├─ backend/               ← FastAPI (Python)
│  ├─ app/
│  ├─ requirements.txt
│  └─ main.py
│
├─ app/                   ← Next.js (JavaScript/TypeScript)
│  ├─ components/
│  ├─ (dashboard)/
│  └─ page.tsx
│
├─ package.json          ← Dependencies
├─ tsconfig.json         ← TypeScript config
├─ next.config.ts        ← Next.js config
│
├─ start-backend.bat     ← 🆕 Script para backend
├─ start-frontend.bat    ← 🆕 Script para frontend
└─ start-all.bat         ← 🆕 Script para los dos
```

---

## Troubleshooting

### Backend no inicia

```
Error: "Python was not found"
Solución: Usa el path completo de conda
  C:/Users/Guille/miniconda3/Scripts/conda.exe run ...

Error: "ModuleNotFoundError"
Solución: Instala dependencias
  pip install -r requirements.txt
```

### Frontend no inicia

```
Error: "npm not found"
Solución: Node.js no instalado
  Descarga de https://nodejs.org/ (LTS)

Error: "Port 3000 already in use"
Solución: Mata el proceso
  Get-Process -Name node -Force | Stop-Process
  Get-Process -Name python -Force | Stop-Process
```

### Los dos puertos están en conflicto

```
Cambiar puerto del frontend en package.json:
"dev": "next dev -p 3001"

O en .env.local:
PORT=3001
```

---

## Durante el Desarrollo

### Debugging

**Backend (FastAPI):**
- Logs automáticos en terminal con `--reload`
- Swagger UI: http://127.0.0.1:3000/docs
- Cambios en código se recargan automáticamente

**Frontend (Next.js):**
- DevTools: F12 en navegador
- Cambios en código se recargan en vivo
- Network tab para ver requests al backend

### Hot Reload

Ambos servidores tienen **hot reload**:
- Guarda un archivo en `backend/` → Backend se reinicia
- Guarda un archivo en `app/` → Frontend se reinicia
- Sin necesidad de parar/reiniciar

---

## Próximos Pasos

1. ✅ **Servidores arriba**: Check
2. 🔄 **Testing en browser**: Abre http://localhost:3000
3. 📝 **Verifica componentes**: Mira Dashboard, Charts, HR Zones
4. 🚀 **Haz cambios**: Guarda archivo → Ve cambios en vivo

---

**Created:** 2025-12-15  
**Author:** RunCoach AI Development Team

