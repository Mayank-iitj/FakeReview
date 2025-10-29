"""
Setup and Installation Script
Run this after cloning the repository to set up the environment.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print('='*60)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return False


def download_nltk_data():
    """Download required NLTK data."""
    print("\n" + "="*60)
    print("  Downloading NLTK Data")
    print("="*60)
    
    try:
        import nltk
        
        datasets = ['stopwords', 'punkt', 'wordnet', 'averaged_perceptron_tagger']
        
        for dataset in datasets:
            print(f"Downloading {dataset}...")
            nltk.download(dataset, quiet=True)
        
        print("✓ All NLTK data downloaded successfully")
        return True
    except Exception as e:
        print(f"Error downloading NLTK data: {str(e)}")
        return False


def main():
    """Main setup function."""
    
    print("\n" + "="*60)
    print("  FAKE REVIEW DETECTOR - Setup Script")
    print("="*60)
    
    # Check Python version
    python_version = sys.version_info
    print(f"\nPython version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print("❌ Error: Python 3.7 or higher is required")
        sys.exit(1)
    
    print("✓ Python version is compatible")
    
    # Install requirements
    print("\n" + "="*60)
    print("  Installing Dependencies")
    print("="*60)
    
    success = run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python packages..."
    )
    
    if not success:
        print("❌ Failed to install dependencies")
        print("Try running manually: pip install -r requirements.txt")
        sys.exit(1)
    
    print("✓ All dependencies installed")
    
    # Download NLTK data
    download_nltk_data()
    
    # Create necessary directories
    print("\n" + "="*60)
    print("  Creating Directories")
    print("="*60)
    
    directories = [
        'data',
        'models',
        'visualizations',
        'notebooks'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ {directory}/ directory ready")
    
    # Success message
    print("\n" + "="*60)
    print("  Setup Complete!")
    print("="*60)
    
    print("\n✓ Fake Review Detector is ready to use!")
    print("\nNext steps:")
    print("  1. Place your dataset at data/reviews.csv (or let it create a sample)")
    print("  2. Train models: python main.py")
    print("  3. Run web app: streamlit run app.py")
    print("\nFor detailed usage, see USAGE_GUIDE.md")
    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {str(e)}")
        sys.exit(1)
