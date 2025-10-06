@echo off
echo ========================================
echo CV Creator using LLMs - Quick Start
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Check if requirements are installed
echo Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Check Ollama
echo Checking Ollama status...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Ollama may not be running!
    echo Please make sure Ollama is started.
    echo.
    pause
)

REM Start the application
echo.
echo Starting CV Creator LLM...
echo.
echo Access the app at: http://localhost:8000
echo Press Ctrl+C to stop
echo.
python run.py

pause
