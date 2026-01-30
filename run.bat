@echo off
REM Workday Activity Logger - Quick Start Script

echo ========================================
echo  Workday Activity Logger
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo Virtual environment not found. Creating...
    python -m venv venv
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if dependencies installed
python -c "import win32gui" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Run the logger
echo Starting Activity Logger...
echo Press Ctrl+C to stop
echo.
python -m src.main --verbose

pause
