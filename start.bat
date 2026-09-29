@echo off
title Threat Platform Launcher
setlocal EnableDelayedExpansion

echo ======================================================
echo    Unified Cyber Threat Detection ^& Response Platform
echo ======================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "FRONTEND_DIR=%SCRIPT_DIR%frontend"

echo [1/2] Launching Backend API Server on http://localhost:8000 ...
start "Threat Platform - Backend API" cmd /k "cd /d ""%BACKEND_DIR%"" && (if exist .venv\Scripts\python.exe (.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000) else (python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000))"

timeout /t 2 /nobreak >nul

echo [2/2] Launching Frontend SOC Dashboard on http://localhost:5173 ...
start "Threat Platform - Frontend UI" cmd /k "cd /d ""%FRONTEND_DIR%"" && npm run dev"

echo.
echo ======================================================
echo  All services are launching!
echo.
echo  * Frontend Dashboard: http://localhost:5173
echo  * Backend API Docs:   http://localhost:8000/docs
echo  * Backend ReDoc:      http://localhost:8000/redoc
echo.
echo  Default Operator Credentials:
echo    Email:    admin@threatplatform.dev
echo    Password: Admin@12345
echo ======================================================
echo.
pause
