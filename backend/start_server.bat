@echo off
set PYTHONPATH=%~dp0
python -m uvicorn app.main:app --reload --port 8000
