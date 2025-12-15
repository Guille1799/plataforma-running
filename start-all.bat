@echo off
REM Start ALL servers (Backend + Frontend)
REM Opens two Command Prompts

echo Starting RunCoach AI Servers...
echo.
echo [1] Starting Backend (FastAPI) - http://localhost:3000
start "RunCoach Backend" cmd /k "cd /d %~dp0\backend && C:/Users/Guille/miniconda3/Scripts/conda.exe run -p C:\Users\Guille\miniconda3 python -m uvicorn app.main:app --host 127.0.0.1 --port 3000 --reload"

timeout /t 2 /nobreak

echo [2] Starting Frontend (Next.js) - http://localhost:3000 (after backend ready)
start "RunCoach Frontend" cmd /k "cd /d %~dp0 && npm run dev"

echo.
echo ✅ Both servers should be starting...
echo    Backend: http://localhost:3000
echo    Frontend: http://localhost:3000
echo    Swagger: http://localhost:3000/docs
echo.
echo Close these windows to stop the servers.
pause
