@echo off
REM Production Deployment Verification Script (Windows)
REM Run this before deploying to production

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║     PRODUCTION DEPLOYMENT READINESS CHECK                     ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

set checks_passed=0
set checks_failed=0

REM 1. Check Python version
echo 🔍 Checking Python environment...
python --version >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Python installed
    set /a checks_passed+=1
) else (
    echo ❌ Python not installed
    set /a checks_failed+=1
)

REM 2. Check virtual environment
if exist "venv\" (
    echo ✅ Virtual environment found
    set /a checks_passed+=1
) else (
    echo ⚠️  Virtual environment not found ^(create with: python -m venv venv^)
    set /a checks_failed+=1
)

REM 3. Check required files
echo.
echo 🔍 Checking project structure...
for %%F in (
    "app\main.py"
    "requirements.txt"
    ".env.example"
    "docker-compose.yml"
    "Dockerfile"
) do (
    if exist %%F (
        echo ✅ Found %%F
        set /a checks_passed+=1
    ) else (
        echo ❌ Missing %%F
        set /a checks_failed+=1
    )
)

REM 4. Check .env configuration
echo.
echo 🔍 Checking environment configuration...
if exist ".env" (
    echo ✅ .env file exists
    set /a checks_passed+=1
    
    for %%V in (DATABASE_URL JWT_SECRET_KEY API_PORT) do (
        findstr /M "%%V" .env >nul 2>&1
        if !errorlevel! equ 0 (
            echo ✅ %%V configured
            set /a checks_passed+=1
        ) else (
            echo ⚠️  %%V not configured in .env
            set /a checks_failed+=1
        )
    )
) else (
    echo ⚠️  .env file not found ^(copy from .env.example^)
    set /a checks_failed+=1
)

REM 5. Check dependencies
echo.
echo 🔍 Checking dependencies...
if exist "requirements.txt" (
    echo ✅ requirements.txt exists
    set /a checks_passed+=1
    
    for /f %%A in ('find /C /V "" ^< requirements.txt') do (
        echo    Found %%A dependencies
    )
) else (
    echo ❌ requirements.txt missing
    set /a checks_failed+=1
)

REM 6. Check database setup
echo.
echo 🔍 Checking database setup...
if exist "scripts\init_db.py" (
    echo ✅ Database initialization script found
    set /a checks_passed+=1
) else (
    echo ❌ Database initialization script missing
    set /a checks_failed+=1
)

REM 7. Check Docker setup
echo.
echo 🔍 Checking Docker setup...
docker --version >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Docker installed
    set /a checks_passed+=1
    
    docker-compose --version >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ Docker Compose installed
        set /a checks_passed+=1
    ) else (
        echo ⚠️  Docker Compose not installed
        set /a checks_failed+=1
    )
) else (
    echo ⚠️  Docker not installed ^(required for containerized deployment^)
    set /a checks_failed+=1
)

REM 8. Check documentation
echo.
echo 🔍 Checking documentation...
for %%D in (README.md DEPLOYMENT.md API_GUIDE.md) do (
    if exist %%D (
        echo ✅ Found %%D
        set /a checks_passed+=1
    ) else (
        echo ⚠️  Missing %%D
        set /a checks_failed+=1
    )
)

REM Summary
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    DEPLOYMENT READINESS SUMMARY                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Passed: !checks_passed!
echo Failed: !checks_failed!
echo.

if !checks_failed! equ 0 (
    echo ✅ SYSTEM IS DEPLOYMENT READY!
    echo.
    echo Next steps:
    echo 1. Review .env configuration
    echo 2. Run: python scripts/init_db.py
    echo 3. Run: python scripts/train_model.py (optional)
    echo 4. Deploy with: docker-compose up -d
    exit /b 0
) else (
    echo ⚠️  PLEASE FIX THE ABOVE ISSUES BEFORE DEPLOYING
    exit /b 1
)
