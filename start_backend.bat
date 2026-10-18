@echo off
title CVD Backend
echo Starting AI Vulnerability Scanner Backend...
ml\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload