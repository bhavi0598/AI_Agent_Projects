@echo off
title AI Travel Planner - Local App

echo =========================================
echo  Starting Personalized AI Travel Planner
echo =========================================

REM Change to project directory (IMPORTANT)
cd /d %~dp0

REM Start Ollama (safe even if already running)
echo Starting Ollama...
start "" ollama serve

REM Wait a few seconds for Ollama to be ready
timeout /t 5 > nul

REM Run Streamlit app
echo Launching Streamlit app...
start "" cmd /k python app.py

REM Wait and open browser automatically
timeout /t 5 > nul
REM Browser does not open automatically with Uvicorn, so we force it
start http://localhost:8501

echo =========================================
echo  App is running locally in your browser
echo =========================================