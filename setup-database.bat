@echo off
echo ========================================
echo  Autonex Backend - Database Setup
echo ========================================
echo.

cd /d "%~dp0"

if exist .env (
    echo ✓ .env file already exists!
    echo.
    echo Current database configuration:
    type .env
    echo.
    choice /C YN /M "Do you want to overwrite it"
    if errorlevel 2 goto :end
    echo.
)

echo Creating .env file with SQLite configuration...
echo.

echo # Database Configuration > .env
echo # SQLite (Default - Simple and ready to use) >> .env
echo DATABASE_URL=sqlite:///./autonex.db >> .env
echo. >> .env
echo # PostgreSQL (For production - uncomment and configure) >> .env
echo # DATABASE_URL=postgresql://username:password@localhost:5432/autonex_db >> .env

echo ✓ .env file created successfully!
echo.
echo ========================================
echo Your database configuration:
echo ========================================
type .env
echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Activate virtual environment:  venv\Scripts\activate
echo 2. Install dependencies (if needed):  pip install -r requirements.txt
echo 3. Run backend:  uvicorn app.main:app --reload
echo.

:end
pause
