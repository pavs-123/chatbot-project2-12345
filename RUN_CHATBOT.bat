@echo off
REM Easy Chatbot Launcher for Windows
REM Double-click this file to start the chatbot

echo ================================================================
echo   AI CHATBOT - Starting...
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    echo.
    pause
    exit /b 1
)

REM Run the launcher script
python run_chatbot.py

echo.
pause
