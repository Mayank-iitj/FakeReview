#!/bin/bash
# Quick start script for Fake Review Detection System

set -e

echo "=================================="
echo "Fake Review Detection System"
echo "Quick Start Setup"
echo "=================================="

# Check Python version
echo "[1/8] Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version"

# Create virtual environment
echo "[2/8] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "[3/8] Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo "[4/8] Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

# Download NLP models
echo "[5/8] Downloading NLP models..."
python -m spacy download en_core_web_sm --quiet
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True)" 2>/dev/null
echo "✓ NLP models downloaded"

# Setup environment
echo "[6/8] Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Environment variables configured (.env created)"
    echo "⚠ Please edit .env with your database credentials"
else
    echo "✓ .env already exists"
fi

# Create data directories
echo "[7/8] Creating data directories..."
mkdir -p data/raw data/processed data/models logs
echo "✓ Data directories created"

# Database initialization
echo "[8/8] Initializing database..."
echo "Run the following commands:"
echo ""
echo "  python scripts/init_db.py        # Initialize database tables"
echo "  python scripts/train_model.py    # Train initial models"
echo "  python scripts/generate_demo_data.py  # Generate sample data"
echo ""

echo "=================================="
echo "✓ Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Update .env with your configuration"
echo "2. Initialize database (see commands above)"
echo "3. Start the API:"
echo "   uvicorn app.main:app --reload --port 8000"
echo "4. Start the dashboard (in another terminal):"
echo "   streamlit run dashboard/app.py"
echo "5. Access the system:"
echo "   - API: http://localhost:8000"
echo "   - Docs: http://localhost:8000/docs"
echo "   - Dashboard: http://localhost:8501"
echo ""
