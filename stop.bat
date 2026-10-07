@echo off
title Threat Platform Terminator
echo =====================================================================
echo    Terminating Threat Platform Local Services (Ports 8000 and 5173)
echo =====================================================================
echo.

echo [*] Checking port 8000 (Backend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo [*] Terminating backend PID %%a ...
    taskkill /F /PID %%a >nul 2>nul
)

echo [*] Checking port 5173 (Frontend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173" ^| findstr "LISTENING"') do (
    echo [*] Terminating frontend PID %%a ...
    taskkill /F /PID %%a >nul 2>nul
)

echo.
echo [*] Ports 8000 and 5173 are now free!
echo =====================================================================
pause
