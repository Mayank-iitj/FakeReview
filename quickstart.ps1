# Quick Start Script for Windows PowerShell
# Run this to set up and start the Fake Review Detector

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 58) -ForegroundColor Cyan
Write-Host "  FAKE REVIEW DETECTOR - Quick Start" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Cyan

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "`n✓ Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "`n⚠ Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Cyan
pip install -r requirements-streamlit.txt

# Download NLTK data
Write-Host "`nDownloading NLTK data..." -ForegroundColor Cyan
python download_nltk_data.py

# Run system check
Write-Host "`nRunning system check..." -ForegroundColor Cyan
python test_setup.py

# Check if models exist
if (Test-Path "models\best_model.pkl") {
    Write-Host "`n✓ Models found" -ForegroundColor Green
    Write-Host "`nStarting Streamlit app..." -ForegroundColor Cyan
    streamlit run app.py
} else {
    Write-Host "`n⚠ Models not found. Would you like to train them now?" -ForegroundColor Yellow
    Write-Host "(This will take 5-15 minutes)" -ForegroundColor Yellow
    $response = Read-Host "`nTrain models now? (y/n)"
    
    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Host "`nTraining models..." -ForegroundColor Cyan
        python main.py
        
        Write-Host "`n✓ Training complete!" -ForegroundColor Green
        Write-Host "`nStarting Streamlit app..." -ForegroundColor Cyan
        streamlit run app.py
    } else {
        Write-Host "`nYou can train models later by running: python main.py" -ForegroundColor Yellow
        Write-Host "Then start the app with: streamlit run app.py" -ForegroundColor Yellow
    }
}
