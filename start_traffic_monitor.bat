@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM Website Traffic Monitor Launcher
REM Keep this .bat file in the SAME folder as traffic_addon.py
REM ============================================================

tasklist /FI "IMAGENAME eq mitmdump.exe" 2>NUL | find /I "mitmdump.exe" >NUL

if %ERRORLEVEL%==0 (
    echo.
    echo A traffic monitor ^(mitmdump^) is already running.
    choice /c KN /m "Press K to kill it and start fresh, or N to start a second instance"
    
    if errorlevel 2 goto startnew
    if errorlevel 1 goto killandfresh
)

goto freshstart


:killandfresh

echo.
echo Closing the existing traffic monitor and Chrome...

taskkill /IM mitmdump.exe /F >nul 2>&1
taskkill /IM chrome.exe /F >nul 2>&1

timeout /t 2 /nobreak >nul

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TIMESTAMP=%%i

set TRAFFIC_CSV_PATH=usage_!TIMESTAMP!.csv
set PORT=8082

goto launch


:startnew

echo.
echo Starting a second traffic monitor on port 8083...

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TIMESTAMP=%%i

set TRAFFIC_CSV_PATH=usage_!TIMESTAMP!.csv
set PORT=8083

goto launch


:freshstart

echo.
echo Closing any running Chrome windows...

taskkill /IM chrome.exe /F >nul 2>&1

timeout /t 2 /nobreak >nul

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TIMESTAMP=%%i

set TRAFFIC_CSV_PATH=usage_!TIMESTAMP!.csv
set PORT=8082

goto launch


:launch

echo.
echo ============================================================
echo Starting Website Traffic Monitor
echo ============================================================
echo.
echo Proxy Port : !PORT!
echo CSV File   : !TRAFFIC_CSV_PATH!
echo.
echo ============================================================

start "Traffic Monitor" cmd /k "cd /d %~dp0 && mitmdump -s traffic_addon.py -p !PORT!"

echo.
echo Waiting for mitmproxy to start...

timeout /t 5 /nobreak >nul


echo.
echo Launching Chrome through the proxy...

start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
    --proxy-server="127.0.0.1:!PORT!" ^
    --disable-quic ^
    "http://mitm.it"


echo.
echo ============================================================
echo Traffic Monitor Started
echo ============================================================
echo.
echo Proxy : 127.0.0.1:!PORT!
echo CSV   : !TRAFFIC_CSV_PATH!
echo.
echo Chrome has been started through mitmproxy.
echo.
echo If this is the first run:
echo 1. Open http://mitm.it
echo 2. Install the Windows certificate
echo 3. Browse normally
echo.
echo TEST MODE:
echo A pop up dialog will appear for new day.
echo.
echo ============================================================
echo.

pause