@echo off
title Threat Platform Launcher - Pravallika2025
setlocal EnableDelayedExpansion

echo =====================================================================
echo    Unified Multi-Environment Cyber Threat Detection ^& Response Platform
echo    Author / Candidate: Pravallika Kalangi (Roll: 24VV1F0044)
echo =====================================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "FRONTEND_DIR=%SCRIPT_DIR%frontend"

:: Clean any hung processes on 8000/5173 first
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":5173" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>nul
)

:: Find python executable
set "PYTHON_EXE="
if exist "%BACKEND_DIR%\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%BACKEND_DIR%\.venv\Scripts\python.exe"
) else (
    where python >nul 2>nul
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=python"
    ) else (
        where py >nul 2>nul
        if !errorlevel! equ 0 (
            set "PYTHON_EXE=py"
        )
    )
)

if "%PYTHON_EXE%"=="" (
    echo [ERROR] Python not found! Please install Python 3.11+ or ensure backend\.venv exists.
    pause
    exit /b 1
)

echo [*] Using Python: %PYTHON_EXE%
echo [1/2] Launching Backend API Server on http://localhost:8000 ...
start "Threat Platform - Backend (Port 8000)" cmd /k "title Threat Platform - Backend (Port 8000) & cd /d "%BACKEND_DIR%" & "%PYTHON_EXE%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [*] Waiting 3 seconds for Backend to initialize...
timeout /t 3 /nobreak >nul

echo [2/2] Launching Frontend SOC Dashboard on http://localhost:5173 ...
start "Threat Platform - Frontend (Port 5173)" cmd /k "title Threat Platform - Frontend (Port 5173) & cd /d "%FRONTEND_DIR%" & npm run dev -- --host 0.0.0.0 --port 5173"

echo.
echo =====================================================================
echo   SERVICES ARE RUNNING SUCCESSFULLY!
echo.
echo   * Frontend Dashboard:   http://localhost:5173
echo   * Backend API Docs:     http://localhost:8000/docs
echo   * Backend Health:       http://localhost:8000/health
echo.
echo   Default Credentials:
echo   - Admin:   admin@threatplatform.dev / Admin@12345
echo   - Analyst: analyst@threatplatform.dev / Analyst@12345
echo.
echo   Opening browser windows now...
echo =====================================================================

timeout /t 2 /nobreak >nul
start http://localhost:8000/docs
start http://localhost:5173

echo.
echo Keep both service windows open while interacting with the platform.
echo To terminate all services, run stop.bat.
echo.
pause
