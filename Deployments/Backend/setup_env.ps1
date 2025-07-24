#!/usr/bin/env pwsh
# Backend Environment Auto-Activation Script

Write-Host "🚀 Initializing Backend Development Environment..." -ForegroundColor Blue

# Set the conda environment path
$condaEnvPath = Join-Path $PSScriptRoot ".conda"
$condaExe = "C:\Users\ahmed\miniconda3\Scripts\conda.exe"

# Verify conda environment exists
if (-not (Test-Path $condaEnvPath)) {
    Write-Host "❌ Conda environment not found at: $condaEnvPath" -ForegroundColor Red
    Write-Host "💡 Please create the environment first using: conda create --prefix ./.conda python=3.11" -ForegroundColor Yellow
    exit 1
}

# Set environment variables
$env:CONDA_DEFAULT_ENV = $condaEnvPath
$env:PYTHONPATH = "$PSScriptRoot\src"
$env:CONDA_PREFIX = $condaEnvPath

# Add conda environment to PATH
$env:PATH = "$condaEnvPath;$condaEnvPath\Scripts;$condaEnvPath\Library\bin;$env:PATH"

Write-Host "✅ Environment Variables Set:" -ForegroundColor Green
Write-Host "   CONDA_PREFIX: $env:CONDA_PREFIX" -ForegroundColor Cyan
Write-Host "   PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Cyan
Write-Host "   Working Directory: $PSScriptRoot" -ForegroundColor Cyan

# Test Python
try {
    $pythonExe = Join-Path $condaEnvPath "python.exe"
    if (Test-Path $pythonExe) {
        $pythonVersion = & $pythonExe --version 2>&1
        Write-Host "✅ Python available: $pythonVersion" -ForegroundColor Green
        Write-Host "✅ Python executable: $pythonExe" -ForegroundColor Green
    } else {
        Write-Host "❌ Python executable not found in conda environment" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error testing Python: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "🎉 Backend environment ready for development and Copilot!" -ForegroundColor Green
Write-Host "💡 You can now run: python src/main.py or python test_generation.py" -ForegroundColor Yellow
