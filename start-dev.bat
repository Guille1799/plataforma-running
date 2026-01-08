@echo off
echo ===================================================
echo 🚀 INICIANDO PLATAFORMA RUNNING (MODO DOCKER)
echo ===================================================

echo.
echo [1/2] Iniciando Backend (Docker)...
echo -----------------------------------
echo Asegurate de que Docker Desktop este abierto.
docker-compose -f docker-compose.dev.yml up -d

echo.
echo Esperando a que el backend este listo...
timeout /t 10 /nobreak >nul

echo.
echo [2/2] Iniciando Frontend (Next.js)...
echo -----------------------------------
echo Se abrira una nueva ventana para el frontend.
echo No cierres esa ventana.
echo.

start "RunCoach Frontend" cmd /k "npm run dev"

echo.
echo ✅ TODO LISTO!
echo.
echo 👉 Backend API: http://localhost:8000/docs
echo 👉 Frontend:    http://localhost:3000
echo.
echo Para detener todo, cierra la ventana del frontend y ejecuta 'stop-dev.bat'
echo.
pause
