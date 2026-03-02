@echo off
echo ===================================================
echo Starting App-MarkItDown Setup and Execution
echo ===================================================

cd /d "%~dp0"

IF NOT EXIST .venv (
    echo [1/3] Creating Python virtual environment...
    python -m venv .venv
) ELSE (
    echo [1/3] Virtual environment already exists.
)

echo [2/3] Activating virtual environment and installing dependencies...
call .venv\Scripts\activate.bat
pip install -r requirements.txt

IF NOT EXIST .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
)

echo [3/3] Starting the application...
python app.py

pause
