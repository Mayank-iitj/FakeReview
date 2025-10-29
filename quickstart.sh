#!/bin/bash
# Quick Start Script for Linux/Mac
# Run this to set up and start the Fake Review Detector

echo "============================================================"
echo "  FAKE REVIEW DETECTOR - Quick Start"
echo "============================================================"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo -e "\n✓ Virtual environment found"
else
    echo -e "\n⚠ Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "\nActivating virtual environment..."
source venv/bin/activate

# Install dependencies
echo -e "\nInstalling dependencies..."
pip install -r requirements-streamlit.txt

# Download NLTK data
echo -e "\nDownloading NLTK data..."
python download_nltk_data.py

# Run system check
echo -e "\nRunning system check..."
python test_setup.py

# Check if models exist
if [ -f "models/best_model.pkl" ]; then
    echo -e "\n✓ Models found"
    echo -e "\nStarting Streamlit app..."
    streamlit run app.py
else
    echo -e "\n⚠ Models not found. Would you like to train them now?"
    echo "(This will take 5-15 minutes)"
    read -p "Train models now? (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "\nTraining models..."
        python main.py
        
        echo -e "\n✓ Training complete!"
        echo -e "\nStarting Streamlit app..."
        streamlit run app.py
    else
        echo -e "\nYou can train models later by running: python main.py"
        echo "Then start the app with: streamlit run app.py"
    fi
fi
