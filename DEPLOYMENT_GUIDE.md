# Streamlit Deployment Guide

## 🚀 Deploying to Streamlit Cloud

### Prerequisites
1. GitHub account
2. Streamlit Cloud account (sign up at [share.streamlit.io](https://share.streamlit.io))
3. Project pushed to GitHub

### Step 1: Prepare Your Repository

Ensure these files are in your repository:

```
fake-review-detector/
├── app.py                          # Main Streamlit app
├── requirements-streamlit.txt      # Streamlit-compatible dependencies
├── packages.txt                    # System packages (if needed)
├── .streamlit/config.toml         # Streamlit configuration
├── src/                           # Source code modules
│   ├── config.py
│   ├── data_preprocessing.py
│   ├── feature_extraction.py
│   ├── prediction.py
│   └── utils.py
├── models/                        # Pre-trained models
│   ├── best_model.pkl
│   ├── vectorizer.pkl
│   └── label_encoder.pkl
└── data/                          # Optional sample data
```

### Step 2: Train Models Locally First

Before deploying, train your models locally:

```bash
# Navigate to project directory
cd d:/fake-review-detector

# Install dependencies
pip install -r requirements-streamlit.txt

# Download NLTK data
python download_nltk_data.py

# Train models
python main.py
```

This creates the model files needed for deployment.

### Step 3: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit - Fake Review Detector"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/fake-review-detector.git
git push -u origin main
```

### Step 4: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your repository: `YOUR_USERNAME/fake-review-detector`
4. Set main file path: `app.py`
5. Click "Deploy!"

### Step 5: Configure Advanced Settings (Optional)

In Streamlit Cloud dashboard:

1. Click on your app's menu (⋮)
2. Select "Settings"
3. Under "Advanced settings":
   - Python version: 3.9 or 3.10
   - Requirements file: `requirements-streamlit.txt`

## 🔧 Troubleshooting Deployment

### Issue: Import errors

**Solution:** Ensure all imports use try-except blocks:

```python
try:
    from src.prediction import ReviewPredictor
except ImportError:
    from prediction import ReviewPredictor
```

### Issue: NLTK data not found

**Solution:** App automatically downloads NLTK data on first run. If issues persist, add to app.py:

```python
import nltk
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
```

### Issue: Model files not found

**Solution:** Two options:

1. **Include models in repo** (if < 100MB):
   ```bash
   git lfs track "*.pkl"
   git add .gitattributes
   git add models/*.pkl
   git commit -m "Add model files"
   git push
   ```

2. **Train on first run** (slower but no file size limits):
   ```python
   if not os.path.exists('models/best_model.pkl'):
       st.warning("Training models on first run...")
       # Call training function
   ```

### Issue: Memory limit exceeded

**Solution:** Reduce model complexity:
- Use fewer models
- Reduce MAX_FEATURES in config.py
- Use simpler algorithms (Naive Bayes, Logistic Regression)

### Issue: Module not found

**Solution:** Check Python path configuration:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))
```

## 📦 Local Testing

Test the app locally before deploying:

```bash
# Run locally
streamlit run app.py

# Check that it works at:
# http://localhost:8501
```

## 🌐 Alternative Deployment Options

### Option 1: Heroku

1. Create `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. Create `setup.sh`:
   ```bash
   mkdir -p ~/.streamlit/
   echo "[server]\nheadless = true\nport = $PORT\nenableCORS = false\n" > ~/.streamlit/config.toml
   ```

3. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### Option 2: Docker

1. Create `Dockerfile`:
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements-streamlit.txt .
   RUN pip install -r requirements-streamlit.txt
   COPY . .
   EXPOSE 8501
   CMD ["streamlit", "run", "app.py"]
   ```

2. Build and run:
   ```bash
   docker build -t fake-review-detector .
   docker run -p 8501:8501 fake-review-detector
   ```

### Option 3: AWS EC2

1. Launch EC2 instance
2. SSH into instance
3. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-pip
   pip3 install -r requirements-streamlit.txt
   ```
4. Run app:
   ```bash
   streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   ```

## ✅ Pre-Deployment Checklist

- [ ] All models trained and saved
- [ ] requirements-streamlit.txt up to date
- [ ] All imports have fallback error handling
- [ ] NLTK data downloads automatically
- [ ] App runs successfully locally
- [ ] Code pushed to GitHub
- [ ] .gitignore configured correctly
- [ ] README.md includes usage instructions
- [ ] Sample data included (optional)

## 🔒 Security Considerations

For production deployment:

1. **Environment Variables**: Store sensitive data in secrets
   ```python
   import streamlit as st
   api_key = st.secrets["api_key"]
   ```

2. **Rate Limiting**: Implement request limits

3. **Input Validation**: Sanitize all user inputs

4. **Model Security**: Don't expose model internals

## 📊 Monitoring

After deployment:

1. Check Streamlit Cloud logs
2. Monitor resource usage
3. Set up error alerts
4. Track user analytics (optional)

## 🎉 Success!

Your app should now be live at:
`https://share.streamlit.io/YOUR_USERNAME/fake-review-detector/main/app.py`

Or your custom domain if configured.

---

**Need Help?**
- Streamlit Docs: https://docs.streamlit.io
- Community Forum: https://discuss.streamlit.io
- GitHub Issues: Create an issue in your repo
