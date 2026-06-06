@echo off
REM Double-click this file to play the game.
cd /d "%~dp0"
uv run python main.py
if errorlevel 1 (
    echo.
    echo Something went wrong. Make sure uv is installed.
    echo Install it from: https://docs.astral.sh/uv/  ^(or: pip install uv^)
    echo Then run:  uv sync
    pause
)
