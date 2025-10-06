# ⚡ Quick Start Guide

Get up and running with CV Creator in 5 minutes!

## Prerequisites Check

Before starting, ensure you have:
- [ ] Python 3.9+ installed
- [ ] Ollama installed and running
- [ ] At least 10GB free disk space
- [ ] 8GB+ RAM

## 3-Step Quick Setup

### Step 1: Install Ollama Models (One-time)

```bash
ollama pull gemma:2b
ollama pull llama3.2-vision:11b
```

⏱️ This will take 5-10 minutes depending on your internet speed.

### Step 2: Setup Python Environment

```bash
# Navigate to project folder
cd cv-creator-llm

# Create and activate virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

⏱️ This will take 2-3 minutes.

### Step 3: Run the Application

```bash
python run.py
```

✅ Open your browser to: **http://localhost:8000**

## First Resume Generation

### 1. Upload Resume
- Click the upload area or drag-drop your resume (PDF/DOCX)
- Wait for extraction to complete (~10 seconds)

### 2. Add Job Description
- Paste a job description in the text area
- Click "Parse Job Requirements"
- Wait for analysis (~5 seconds)

### 3. Generate Tailored Resume
- Choose format (PDF or DOCX)
- Select optimization level (use "Balanced")
- Click "Generate Resume"
- Wait for generation (~30-60 seconds)

### 4. Download & Review
- Check your ATS score
- Review keyword matches
- Download optimized resume
- Read AI recommendations

## Tips for Best Results

### ✅ Do's
- Use recent resume with clear formatting
- Provide complete job descriptions
- Include specific skills and requirements
- Use "Balanced" optimization for first try
- Review and iterate based on recommendations

### ❌ Don'ts
- Don't use heavily formatted resumes (tables, graphics)
- Don't paste incomplete job descriptions
- Don't use "Aggressive" optimization without reviewing
- Don't skip the ATS analysis

## Common Issues & Quick Fixes

### "Ollama connection refused"
```bash
# Start Ollama
ollama serve
```

### "Model not found"
```bash
# Pull missing models
ollama pull gemma:2b
ollama pull llama3.2-vision:11b
```

### "Port already in use"
```bash
# Use different port
uvicorn app.main:app --port 8080
```

### Resume extraction fails
- Check file is PDF or DOCX
- Ensure file is not password-protected
- Try a different resume format

## Example Workflow

**Scenario**: You're applying for a "Senior Software Engineer" position at TechCorp.

1. **Upload** your existing software engineer resume
2. **Paste** the full job description from TechCorp's posting
3. **Select** "Balanced" optimization + "PDF" format
4. **Generate** and wait ~45 seconds
5. **Review** the 85% ATS score and keyword matches
6. **Download** your tailored resume
7. **Apply** to TechCorp with confidence!

## What Happens Behind the Scenes?

1. **Resume Upload** → PDF/DOCX text extraction → LLM parses into structured JSON
2. **Job Description** → LLM extracts skills, keywords, requirements
3. **Tailoring** → LLM rewrites experience bullets, optimizes keywords, generates summary
4. **ATS Analysis** → Keyword matching, format checking, scoring
5. **Generation** → Professional PDF/DOCX creation with optimized content

## Performance Expectations

| Task | Expected Time |
|------|--------------|
| Resume extraction | 5-15 seconds |
| Job parsing | 5-10 seconds |
| Resume tailoring | 30-60 seconds |
| Document generation | 2-5 seconds |
| **Total workflow** | **~1-2 minutes** |

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore [INSTALLATION.md](INSTALLATION.md) for troubleshooting
- Check API docs at http://localhost:8000/docs
- Experiment with different optimization levels
- Try the revision feature for specific sections

## Need Help?

1. Check console output for errors
2. Verify Ollama is running: `ollama list`
3. Test health endpoint: `curl http://localhost:8000/health`
4. Review logs in terminal
5. Restart the application

## Pro Tips

💡 **Keyword Optimization**: Review "Missing Keywords" and incorporate them naturally

💡 **Multiple Versions**: Generate 2-3 versions with different optimization levels

💡 **Iterative Refinement**: Use the revision feature to fine-tune specific sections

💡 **ATS Target**: Aim for 75%+ ATS score for best results

💡 **Save Originals**: Keep your original resume, generate new files for each job

---

**Ready to create your perfect resume? Let's go! 🚀**

```bash
python run.py
```
