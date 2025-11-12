@echo off
cd /d %~dp0
call venv\Scripts\activate.bat
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
pause



