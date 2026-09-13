@echo off
title Unified Threat Platform - Network Host
cls
echo =====================================================================
echo    Unified Threat Detection & Response Platform - Network Host
echo =====================================================================
echo.

REM Get local IPv4 address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    goto :found_ip
)
:found_ip
set IP=%IP:~1%

echo [*] Detected Machine IP: %IP%
echo.
echo =====================================================================
echo   SHARE THESE LINKS WITH ANY LAPTOP, PHONE, OR DEVICE ON YOUR NETWORK:
echo.
echo   [FRONTEND DASHBOARD]: http://%IP%:5173
echo   [BACKEND API DOCS]:   http://%IP%:8000/docs
echo.
echo   [CREDENTIALS]:
echo   - Admin:   admin@threatplatform.dev / Admin@12345
echo   - Analyst: analyst@threatplatform.dev / Analyst@12345
echo =====================================================================
echo.
echo Starting Backend and Frontend services on 0.0.0.0 ...
echo.

start "Backend Server (Port 8000)" cmd /k "cd /d backend && .venv\Scripts\activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul
start "Frontend Server (Port 5173)" cmd /k "cd /d frontend && npm run dev -- --host 0.0.0.0 --port 5173"

echo.
echo [*] Both servers are launching in separate windows.
echo [*] Keep those windows OPEN while testing on other devices.
pause
