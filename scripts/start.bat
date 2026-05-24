@echo off
chcp 65001 >nul
cd /d "%~dp0..\backend"
if not exist ".venv\Scripts\activate.bat" (
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)
echo http://127.0.0.1:8000/
python -m app.main
pause
