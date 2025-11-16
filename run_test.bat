@echo off
cd c:\Users\guill\Desktop\plataforma-running\backend
start "Test Terminal" cmd /k ".\venv\Scripts\python.exe ..\e2e_test_package_2.py & pause"
