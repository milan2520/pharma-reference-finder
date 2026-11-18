@echo off
title Pharma Reference Finder

cd /d "%~dp0"

call venv\Scripts\activate.bat

start "" "%~dp0frontend\index.html"

python -m uvicorn main:app --reload --app-dir backend

pause