# Autonex Backend - Database Setup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Autonex Backend - Database Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

if (Test-Path .env) {
    Write-Host "✓ .env file already exists!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Current database configuration:" -ForegroundColor Cyan
    Get-Content .env | Write-Host
    Write-Host ""
    $overwrite = Read-Host "Do you want to overwrite it? (Y/N)"
    if ($overwrite -ne "Y" -and $overwrite -ne "y") {
        Write-Host "Setup cancelled." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To start the backend:" -ForegroundColor Cyan
        Write-Host "1. Activate virtual environment: .\venv\Scripts\Activate.ps1" -ForegroundColor White
        Write-Host "2. Run: uvicorn app.main:app --reload" -ForegroundColor White
        Write-Host ""
        pause
        exit
    }
    Write-Host ""
}

Write-Host "Creating .env file with SQLite configuration..." -ForegroundColor Yellow
Write-Host ""

# Create .env file with proper content
$envContent = @"
# Database Configuration
# SQLite (Default - Simple and ready to use)
DATABASE_URL=sqlite:///./autonex.db

# PostgreSQL (For production - uncomment and configure)
# DATABASE_URL=postgresql://username:password@localhost:5432/autonex_db
"@

$envContent | Out-File -FilePath .env -Encoding ASCII

Write-Host "✓ .env file created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Your database configuration:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Get-Content .env | Write-Host
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Activate virtual environment: .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "2. Install dependencies (if needed): pip install -r requirements.txt" -ForegroundColor White
Write-Host "3. Run backend: uvicorn app.main:app --reload" -ForegroundColor White
Write-Host ""

pause
