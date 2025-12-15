@echo off
REM Start RunCoach AI Backend Server
REM Usage: Double-click or run: start-backend.bat

cd /d %~dp0\backend
C:/Users/Guille/miniconda3/Scripts/conda.exe run -p C:\Users\Guille\miniconda3 python -m uvicorn app.main:app --host 127.0.0.1 --port 3000 --reload

pause
