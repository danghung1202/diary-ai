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

echo [1/4] Python found
python --version
echo.

REM Create virtual environment
if exist "venv\" (
    echo [2/4] Virtual environment already exists, skipping creation
) else (
    echo [2/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)
echo.

REM Activate and install dependencies
echo [3/4] Installing dependencies...
call venv\Scripts\activate.bat

pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

REM Run pywin32 post-install
echo [4/4] Configuring pywin32...
python venv\Scripts\pywin32_postinstall.py -install 2>nul
echo.

echo ============================================================
echo  Installation Complete!
echo ============================================================
echo.
echo To run the Activity Logger:
echo   1. Double-click: run.bat
echo   2. Or manually:
echo      - venv\Scripts\activate
echo      - python -m src.main
echo.
echo Configuration file: config\config.json
echo Logs will be saved to: logs\
echo.
echo See README.md for full documentation
echo See QUICKSTART.md for quick start guide
echo.
pause
