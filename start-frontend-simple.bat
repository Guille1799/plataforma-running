@echo off
REM RunCoach AI - Frontend Development Server
REM Simple, direct, no fancy stuff

cd /d "%~dp0"

echo.
echo ========================================
echo    RunCoach AI - Frontend Server
echo    Next.js en http://localhost:3000
echo ========================================
echo.

npm run dev

pause
