# Data Quality Platform - Backend startup script
$backendDir = $PSScriptRoot
Set-Location $backendDir

Write-Host "=== Data Quality Platform - Backend ===" -ForegroundColor Cyan
Write-Host ""

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Error: python not found. Please install Python and add to PATH." -ForegroundColor Red
    exit 1
}

Write-Host "1. Initializing database..."
python -m app.db.init_db 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "   (skip or exists)" -ForegroundColor Yellow }

Write-Host "2. Loading seed data..."
python seed_data.py 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "   (skip or exists)" -ForegroundColor Yellow }

Write-Host ""
Write-Host "3. Starting server: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "   Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
