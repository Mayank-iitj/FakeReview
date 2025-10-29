"""
Test Script - Verify Installation and Imports
Run this to check if everything is set up correctly.
"""

import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

print("=" * 60)
print("  FAKE REVIEW DETECTOR - System Check")
print("=" * 60)

# Test 1: Python version
print("\n1. Checking Python version...")
import sys
print(f"   ✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

if sys.version_info < (3, 7):
    print("   ✗ ERROR: Python 3.7+ required")
    sys.exit(1)

# Test 2: Core dependencies
print("\n2. Checking core dependencies...")

try:
    import numpy as np
    print(f"   ✓ NumPy {np.__version__}")
except ImportError:
    print("   ✗ NumPy not installed")

try:
    import pandas as pd
    print(f"   ✓ Pandas {pd.__version__}")
except ImportError:
    print("   ✗ Pandas not installed")

try:
    import sklearn
    print(f"   ✓ Scikit-learn {sklearn.__version__}")
except ImportError:
    print("   ✗ Scikit-learn not installed")

try:
    import nltk
    print(f"   ✓ NLTK {nltk.__version__}")
except ImportError:
    print("   ✗ NLTK not installed")

try:
    import streamlit as st
    print(f"   ✓ Streamlit {st.__version__}")
except ImportError:
    print("   ✗ Streamlit not installed")

try:
    import plotly
    print(f"   ✓ Plotly {plotly.__version__}")
except ImportError:
    print("   ⚠ Plotly not installed (optional)")

# Test 3: NLTK data
print("\n3. Checking NLTK data...")

try:
    import nltk
    required_data = ['stopwords', 'punkt', 'wordnet']
    
    for dataset in required_data:
        try:
            nltk.data.find(f'corpora/{dataset}')
            print(f"   ✓ {dataset}")
        except LookupError:
            try:
                nltk.data.find(f'tokenizers/{dataset}')
                print(f"   ✓ {dataset}")
            except LookupError:
                print(f"   ✗ {dataset} not found")
                print(f"      Run: nltk.download('{dataset}')")
except Exception as e:
    print(f"   ✗ Error checking NLTK data: {e}")

# Test 4: Project structure
print("\n4. Checking project structure...")

required_dirs = ['src', 'data', 'models', 'visualizations']
for directory in required_dirs:
    dir_path = project_root / directory
    if dir_path.exists():
        print(f"   ✓ {directory}/")
    else:
        print(f"   ⚠ {directory}/ not found (will be created)")

# Test 5: Source modules
print("\n5. Checking source modules...")

modules_to_test = [
    'config',
    'data_preprocessing',
    'feature_extraction',
    'model_training',
    'evaluation',
    'prediction',
    'utils'
]

for module_name in modules_to_test:
    try:
        # Try importing from src
        exec(f"from src import {module_name}")
        print(f"   ✓ {module_name}.py")
    except ImportError:
        try:
            # Try direct import
            exec(f"import {module_name}")
            print(f"   ✓ {module_name}.py")
        except ImportError:
            print(f"   ✗ {module_name}.py not found")

# Test 6: Model files
print("\n6. Checking model files...")

model_files = ['best_model.pkl', 'vectorizer.pkl', 'label_encoder.pkl']
models_dir = project_root / 'models'

if models_dir.exists():
    for model_file in model_files:
        model_path = models_dir / model_file
        if model_path.exists():
            size = model_path.stat().st_size / (1024 * 1024)  # MB
            print(f"   ✓ {model_file} ({size:.2f} MB)")
        else:
            print(f"   ⚠ {model_file} not found (run main.py to train)")
else:
    print("   ⚠ models/ directory not found")

# Test 7: Test import of main components
print("\n7. Testing main components...")

try:
    from src.prediction import ReviewPredictor
    print("   ✓ ReviewPredictor can be imported")
except ImportError as e:
    print(f"   ✗ Cannot import ReviewPredictor: {e}")

try:
    from src.utils import create_sample_dataset
    print("   ✓ Utility functions can be imported")
except ImportError as e:
    print(f"   ✗ Cannot import utilities: {e}")

# Summary
print("\n" + "=" * 60)
print("  System Check Complete")
print("=" * 60)

print("\n📋 Next Steps:")
print("   1. If any ✗ errors, install missing packages:")
print("      pip install -r requirements-streamlit.txt")
print("\n   2. If NLTK data missing:")
print("      python download_nltk_data.py")
print("\n   3. If models not found:")
print("      python main.py")
print("\n   4. To run the app:")
print("      streamlit run app.py")

print("\n" + "=" * 60)
