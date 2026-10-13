@echo off
cd /d "%~dp0"

start "" /b py server.py

timeout /t 2 /nobreak >nul

start "" http://localhost:3000

:wait
timeout /t 1 /nobreak >nul

tasklist /FI "IMAGENAME eq chrome.exe" 2>NUL | find /I "chrome.exe" >NUL
if not errorlevel 1 goto wait

taskkill /F /IM python.exe >nul 2>&1

exit