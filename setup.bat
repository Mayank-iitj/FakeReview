@echo off
REM Quick start script for Fake Review Detection System (Windows)

echo ==================================
echo Fake Review Detection System
echo Quick Start Setup
echo ==================================

REM Check Python version
echo [1/8] Checking Python version...
python --version
echo OK

REM Create virtual environment
echo [2/8] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo OK - Virtual environment created
) else (
    echo OK - Virtual environment already exists
)

REM Activate virtual environment
echo [3/8] Activating virtual environment...
call venv\Scripts\activate.bat
echo OK

REM Install dependencies
echo [4/8] Installing dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo OK - Dependencies installed

REM Download NLP models
echo [5/8] Downloading NLP models...
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
echo OK - NLP models downloaded

REM Setup environment
echo [6/8] Setting up environment...
if not exist ".env" (
    copy .env.example .env
    echo OK - Environment variables configured
    echo WARNING: Please edit .env with your database credentials
) else (
    echo OK - .env already exists
)

REM Create data directories
echo [7/8] Creating data directories...
if not exist "data\raw" mkdir data\raw
if not exist "data\processed" mkdir data\processed
if not exist "data\models" mkdir data\models
if not exist "logs" mkdir logs
echo OK - Data directories created

REM Database initialization
echo [8/8] Database initialization...
echo.
echo Run the following commands:
echo.
echo   python scripts\init_db.py
echo   python scripts\train_model.py
echo   python scripts\generate_demo_data.py
echo.

echo ==================================
echo OK - Setup Complete!
echo ==================================
echo.
echo Next steps:
echo 1. Update .env with your configuration
echo 2. Initialize database (see commands above)
echo 3. Start the API:
echo    uvicorn app.main:app --reload --port 8000
echo 4. Start the dashboard (in another terminal):
echo    streamlit run dashboard/app.py
echo 5. Access the system:
echo    - API: http://localhost:8000
echo    - Docs: http://localhost:8000/docs
echo    - Dashboard: http://localhost:8501
echo.
pause
