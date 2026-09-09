@echo off
title Threat Platform Launcher
echo Starting Unified Threat Detection Platform...

echo Starting Backend Server on http://localhost:8000 ...
start "Threat Platform - Backend" cmd /k "cd /d %~dp0backend && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

echo Starting Frontend Server on http://localhost:5173 ...
start "Threat Platform - Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ======================================================
echo Both servers are launching!
echo Backend API Docs: http://localhost:8000/docs
echo Frontend Web App: http://localhost:5173
echo Login Email:     admin@threatplatform.dev
echo Login Password:  Admin@12345
echo ======================================================
pause
