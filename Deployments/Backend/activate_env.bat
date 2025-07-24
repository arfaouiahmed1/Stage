@echo off
REM Backend Development Environment Activation Script
echo.
echo 🚀 Setting up Backend Development Environment...
echo.

REM Set the conda environment path
set "CONDA_ENV_PATH=%~dp0.conda"
set "CONDA_EXE=C:\Users\ahmed\miniconda3\Scripts\conda.exe"

REM Check if conda environment exists
if not exist "%CONDA_ENV_PATH%" (
    echo ❌ Conda environment not found at: %CONDA_ENV_PATH%
    echo 💡 Please create the environment first using: conda create --prefix ./.conda python=3.11
    pause
    exit /b 1
)

REM Set environment variables
set "CONDA_DEFAULT_ENV=%CONDA_ENV_PATH%"
set "PYTHONPATH=%~dp0src"
set "CONDA_PREFIX=%CONDA_ENV_PATH%"

REM Add conda environment to PATH
set "PATH=%CONDA_ENV_PATH%;%CONDA_ENV_PATH%\Scripts;%CONDA_ENV_PATH%\Library\bin;%PATH%"

echo ✅ Environment Variables Set:
echo    CONDA_PREFIX: %CONDA_PREFIX%
echo    PYTHONPATH: %PYTHONPATH%
echo    Working Directory: %~dp0
echo.

REM Test Python
set "PYTHON_EXE=%CONDA_ENV_PATH%\python.exe"
if exist "%PYTHON_EXE%" (
    for /f "tokens=*" %%i in ('"%PYTHON_EXE%" --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo ✅ Python available: !PYTHON_VERSION!
    echo ✅ Python executable: %PYTHON_EXE%
) else (
    echo ❌ Python executable not found in conda environment
)

echo.
echo 🎉 Backend environment ready for development and Copilot!
echo 💡 You can now run: python src/main.py or python test_generation.py
echo.

REM Keep the command prompt open
cmd /k
