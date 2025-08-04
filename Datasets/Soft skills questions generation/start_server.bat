@echo off
echo ===================================================
echo Soft Skills Assessment Quiz - Server Starter
echo ===================================================
echo.

echo This script will start the FastAPI server for the Soft Skills Assessment Quiz.
echo.

echo [1/3] Checking Python installation...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://www.python.org/downloads/
    goto :error
) else (
    echo Python is installed.
)

echo [2/3] Checking required packages...
echo Installing/upgrading required packages...
python -m pip install fastapi uvicorn pandas --upgrade > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Failed to install required packages
    goto :error
) else (
    echo Required packages are installed.
)

echo [3/3] Starting the server...
echo.
echo =============================================================================
echo Server is starting at http://localhost:8000
echo.
echo Open quiz_client.html in your browser to access the quiz.
echo Press Ctrl+C to stop the server when finished.
echo =============================================================================
echo.

python -m uvicorn soft_skills_api:app --reload

goto :end

:error
echo.
echo Server startup failed. Please check the error messages above.
echo If you need help, refer to the QUIZ_SETUP_GUIDE.md file.
echo.
pause
exit /b 1

:end
pause
