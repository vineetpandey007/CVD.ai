@echo off
echo Booting CVD Platform...
start cmd /k "title CVD Backend && ml\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload"
start cmd /k "title CVD Frontend && cd frontend && npm run dev"