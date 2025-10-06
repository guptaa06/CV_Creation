# 📦 Installation Guide

Complete step-by-step installation guide for CV Creator using LLMs.

## Prerequisites

### 1. System Requirements

- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: Minimum 8GB (16GB recommended for smooth LLM operation)
- **Storage**: 10GB free space (for models and application)
- **Python**: 3.9 or higher

### 2. Install Python

**Windows**:
```bash
# Download from python.org
# Or use winget:
winget install Python.Python.3.11
```

**macOS**:
```bash
brew install python@3.11
```

**Linux**:
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

### 3. Install Ollama

**Windows**:
```bash
# Download installer from https://ollama.ai/download/windows
# Or use winget:
winget install Ollama.Ollama
```

**macOS**:
```bash
brew install ollama
```

**Linux**:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verify installation:
```bash
ollama --version
```

## Step-by-Step Setup

### 1. Install and Start Ollama Models

```bash
# Start Ollama service (if not auto-started)
ollama serve

# In a new terminal, pull required models
ollama pull gemma:2b
ollama pull llama3.2-vision:11b

# Verify models are installed
ollama list
```

Expected output:
```
NAME                    ID              SIZE      MODIFIED
gemma:2b                xxx             1.7 GB    X minutes ago
llama3.2-vision:11b     xxx             7.9 GB    X minutes ago
```

### 2. Clone/Download Project

```bash
# If using git
git clone <repository-url>
cd cv-creator-llm

# Or if you have the zip file
# Extract it and navigate to the folder
cd cv-creator-llm
```

### 3. Create Virtual Environment

**Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 4. Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

This will install:
- FastAPI and Uvicorn (web framework)
- Ollama Python client
- PDF/DOCX processing libraries
- Document generation tools
- All other dependencies

### 5. Verify Installation

```bash
# Check if all packages are installed
pip list

# Test Ollama connection
python -c "import requests; print(requests.get('http://localhost:11434/api/tags').json())"
```

### 6. Create Required Directories

```bash
# These should already exist, but just in case:
mkdir -p uploads outputs samples/resumes samples/job_descriptions samples/outputs
```

## Running the Application

### Method 1: Using the Run Script (Recommended)

```bash
python run.py
```

This will:
- Check if Ollama is running
- Verify models are available
- Start the FastAPI server
- Display access URLs

### Method 2: Using Uvicorn Directly

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Method 3: Using Python Module

```bash
python -m uvicorn app.main:app --reload
```

### Method 4: Using Docker (Advanced)

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Accessing the Application

Once running, open your browser and navigate to:

- **Main Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## Troubleshooting

### Issue: "Ollama connection refused"

**Solution**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it:
ollama serve

# On Windows, Ollama should start automatically
# Check Task Manager for "ollama" process
```

### Issue: "Model not found"

**Solution**:
```bash
# Pull the missing model
ollama pull gemma:2b
ollama pull llama3.2-vision:11b
```

### Issue: "Module not found" errors

**Solution**:
```bash
# Make sure virtual environment is activated
# You should see (venv) in your prompt

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### Issue: "Port 8000 already in use"

**Solution**:
```bash
# Use a different port
uvicorn app.main:app --port 8080

# Or find and kill the process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

### Issue: PDF extraction errors

**Solution**:
```bash
# Install system dependencies (Linux)
sudo apt-get install -y build-essential

# Reinstall pdfplumber
pip uninstall pdfplumber
pip install pdfplumber
```

### Issue: Out of memory when running models

**Solution**:
- Close other applications
- Use smaller models if available
- Increase system RAM
- Use GPU acceleration if available

## Testing the Installation

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "models": {
    "text_model": true,
    "vision_model": true
  },
  "timestamp": "2024-XX-XX..."
}
```

### 2. Test with Sample Data

1. Open http://localhost:8000
2. Upload a sample resume from `samples/resumes/` (create one if needed)
3. Paste sample job description from `samples/job_descriptions/sample_job.txt`
4. Generate resume

## Environment Variables

You can customize settings by editing `.env`:

```env
# Application
APP_NAME="CV Creator using LLMs"
DEBUG=True
PORT=8000

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
TEXT_MODEL=gemma:2b
VISION_MODEL=llama3.2-vision:11b

# Model Parameters
TEMPERATURE=0.7
MAX_TOKENS=2048
```

## Next Steps

After successful installation:

1. Read the [README.md](README.md) for usage instructions
2. Explore the API documentation at http://localhost:8000/docs
3. Try generating your first tailored resume!

## Getting Help

If you encounter issues:

1. Check the console output for error messages
2. Verify all prerequisites are installed correctly
3. Ensure Ollama models are downloaded and running
4. Check the troubleshooting section above
5. Review application logs in the console

## Uninstallation

To remove the application:

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows

# Remove Ollama models (optional)
ollama rm gemma:2b
ollama rm llama3.2-vision:11b

# Uninstall Ollama (optional)
# Follow Ollama documentation for your OS
```

---

**Installation Complete! 🎉**

You're now ready to create AI-powered, ATS-optimized resumes!
