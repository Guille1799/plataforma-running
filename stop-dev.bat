@echo off
echo ===================================================
echo 🛑 DETENIENDO PLATAFORMA RUNNING
echo ===================================================

echo.
echo Deteniendo contenedores de Docker...
docker-compose -f docker-compose.dev.yml stop

echo.
echo ✅ Servidores detenidos correctamente.
echo Puedes cerrar esta ventana.
pause
