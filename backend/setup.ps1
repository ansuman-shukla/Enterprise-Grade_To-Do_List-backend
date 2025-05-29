# Backend Setup Script for Windows PowerShell
Write-Host "Setting up Enterprise To-Do List Backend..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    exit 1
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "Please edit .env file and add your API keys:" -ForegroundColor Red
    Write-Host "  - GEMINI_API_KEY: Get from https://makersuite.google.com/app/apikey" -ForegroundColor Yellow
    Write-Host "  - MONGODB_URI: Get from MongoDB Atlas" -ForegroundColor Yellow
} else {
    Write-Host ".env file already exists" -ForegroundColor Green
}

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "To start the backend server:" -ForegroundColor Yellow
Write-Host "  1. Make sure you've configured .env with your API keys" -ForegroundColor White
Write-Host "  2. Run: uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "`nThe API will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API documentation will be available at: http://localhost:8000/docs" -ForegroundColor Cyan
