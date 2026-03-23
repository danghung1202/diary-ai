@echo off
REM Installation script for Workday Activity Logger

echo ============================================================
echo  Workday Activity Logger - Installation Script
echo ============================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/6] Python found
python --version
echo.

REM Create virtual environment
if exist "venv\" (
    echo [2/6] Virtual environment already exists, skipping creation
) else (
    echo [2/6] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)
echo.

REM Activate and install package (all deps + entry points)
echo [3/6] Installing diary-ai package and dependencies...
call venv\Scripts\activate.bat

pip install --upgrade pip -q
pip install -e .

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

REM Run pywin32 post-install
echo [4/6] Configuring pywin32...
python venv\Scripts\pywin32_postinstall.py -install 2>nul
echo.

REM Add venv\Scripts to user PATH (PowerShell avoids setx 1024-char limit)
echo [5/6] Registering diary-ai in PATH...
powershell -Command "$s='%~dp0venv\Scripts'; $p=[Environment]::GetEnvironmentVariable('PATH','User'); if($p -notlike '*diary-ai*'){[Environment]::SetEnvironmentVariable('PATH',$p+';'+$s,'User'); Write-Host 'PATH updated.'} else {Write-Host 'Already in PATH.'}"
echo.

REM Register Windows startup task (runs 30s after login, no console window)
echo [6/6] Registering startup task...
schtasks /create /tn "diary-ai" /tr "\"%~dp0venv\Scripts\diary-ai-tray.exe\" --tray" /sc ONLOGON /ru %USERNAME% /delay 0000:30 /f
if errorlevel 1 (
    echo WARNING: Could not register startup task. You can start diary-ai manually.
) else (
    echo Startup task registered - diary-ai will launch automatically at login.
)
echo.

echo ============================================================
echo  Installation Complete!
echo ============================================================
echo.
echo Open a NEW terminal window and run:
echo   diary-ai --tray       ^<-- background tray mode
echo   diary-ai --verbose    ^<-- foreground with logs
echo   diary-ai --version    ^<-- version check
echo.
echo Configuration file: config\config.json
echo Logs will be saved to: logs\Week N of YYYY (...)\
echo.
pause
