@echo off
echo =======================================================
echo    Selenium to Playwright Convertor (Local Offline)
echo =======================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.10+.
    pause
    exit /b
)

:: Check if requirements are installed (silently)
echo [1/3] Checking dependencies...
python -m pip install -r requirements.txt -q

:: Check if Ollama is running
echo [2/3] Checking Ollama service...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Ollama is not running on localhost:11434!
    echo Please start Ollama before converting code.
    echo.
) else (
    echo [OK] Ollama is running.
)

:: Run Streamlit
echo [3/3] Starting UI Dashboard...
echo.
echo Press Ctrl+C to stop the server at any time.
python -m streamlit run app.py

pause
