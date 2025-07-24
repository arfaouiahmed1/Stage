# Auto-activate conda environment for Backend project
$condaEnvPath = Join-Path $PSScriptRoot ".conda"
if (Test-Path $condaEnvPath) {
    Write-Host "🐍 Auto-activating conda environment: $condaEnvPath" -ForegroundColor Green
    & "C:\Users\ahmed\miniconda3\Scripts\conda.exe" activate $condaEnvPath
} else {
    Write-Host "⚠️  Conda environment not found at: $condaEnvPath" -ForegroundColor Yellow
}

# Set environment variables for better Python path resolution
$env:PYTHONPATH = "$PSScriptRoot\src;$condaEnvPath\lib\python3.11\site-packages"

Write-Host "✅ Backend development environment ready!" -ForegroundColor Green
Write-Host "📁 Working directory: $PSScriptRoot" -ForegroundColor Cyan
Write-Host "🐍 Python path: $env:PYTHONPATH" -ForegroundColor Cyan
