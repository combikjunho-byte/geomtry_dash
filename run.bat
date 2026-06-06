@echo off
REM Double-click this file to play the game.
cd /d "%~dp0"
python main.py
if errorlevel 1 (
    echo.
    echo Something went wrong. Make sure Python and pygame are installed.
    echo To install pygame, run:  python -m pip install pygame
    pause
)
