# 🤖 CV Creator using LLMs

An AI-powered resume creation and optimization system that uses Large Language Models (LLMs) to generate ATS-friendly, job-tailored CVs. Built with **FastAPI**, **Gemma 2B**, and **Llama 3.2 Vision 11B** via Ollama.

## 🎯 Project Overview

This capstone project demonstrates how modern open-source LLMs can automate and optimize the resume creation process. The system extracts information from existing resumes, analyzes job descriptions, and generates perfectly tailored CVs with ATS optimization.

### Key Features

- 📄 **Smart Resume Parsing**: Extract structured data from PDF/DOCX resumes
- 💼 **Job Description Analysis**: AI-powered extraction of requirements and keywords
- ✨ **Intelligent Tailoring**: Customize resumes to match specific job postings
- 📊 **ATS Optimization**: Ensure maximum compatibility with Applicant Tracking Systems
- 📈 **Quality Metrics**: Comprehensive evaluation with actionable recommendations
- 🎨 **Modern Web UI**: Beautiful, responsive interface built with HTML/CSS/JS
- 🔄 **Iterative Refinement**: Real-time feedback and section-wise editing
- 📥 **Multiple Formats**: Generate professional PDF and DOCX resumes

## 🏗️ Architecture

```
┌─────────────────┐
│   FastAPI UI    │
└────────┬────────┘
         │
    ┌────▼─────┐
    │  Router  │
    └────┬─────┘
         │
    ┌────▼──────────────────────────┐
    │      Service Layer            │
    ├───────────────────────────────┤
    │ • Resume Extractor            │
    │ • Job Parser                  │
    │ • Resume Tailor               │
    │ • Document Generator          │
    │ • Evaluator                   │
    └────┬──────────────────────────┘
         │
    ┌────▼─────────────────┐
    │   LLM Service        │
    ├──────────────────────┤
    │ • Gemma 2B           │
    │ • Llama3.2-Vision    │
    └──────────────────────┘
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.9+
- [Ollama](https://ollama.ai/) installed and running
- Gemma 2B and Llama 3.2 Vision models pulled in Ollama

### Step 1: Install Ollama Models

```bash
# Pull required models
ollama pull gemma:2b
ollama pull llama3.2-vision:11b

# Verify models are available
ollama list
```

### Step 2: Clone and Setup Project

```bash
# Navigate to project directory
cd cv-creator-llm

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configuration

The `.env` file is already configured with default settings:

```env
OLLAMA_BASE_URL=http://localhost:11434
TEXT_MODEL=gemma:2b
VISION_MODEL=llama3.2-vision:11b
```

### Step 4: Run the Application

```bash
# Start the server
python -m uvicorn app.main:app --reload

# Or use the main script
python app/main.py
```

The application will be available at: **http://localhost:8000**

## 📖 Usage Guide

### Web Interface

1. **Upload Resume**
   - Click to upload or drag-and-drop your resume (PDF/DOCX)
   - System automatically extracts all information

2. **Enter Job Description**
   - Paste the target job description
   - AI analyzes requirements and keywords

3. **Generate Tailored Resume**
   - Choose output format (PDF/DOCX)
   - Select optimization level:
     - **Minimal**: Light adjustments
     - **Balanced**: Recommended approach
     - **Aggressive**: Maximum keyword optimization
   - Click "Generate Resume"

4. **Review & Download**
   - View ATS compliance score
   - Check keyword matches
   - Read AI recommendations
   - Download optimized resume

### API Endpoints

```python
# Upload resume
POST /api/upload-resume
Content-Type: multipart/form-data

# Parse job description
POST /api/parse-job
Content-Type: application/x-www-form-urlencoded

# Generate tailored resume
POST /api/generate-resume
Content-Type: application/json
{
    "job_description": "...",
    "target_format": "pdf",
    "optimization_level": "balanced"
}

# Get evaluation metrics
GET /api/evaluation

# Revise specific section
POST /api/revise-section
{
    "section": "summary",
    "instructions": "Make it more concise",
    "preserve_ats_score": true
}
```

## 🧪 Project Structure

```
cv-creator-llm/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── api/                    # API routes (optional)
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   ├── services/
│   │   ├── llm_service.py      # Ollama integration
│   │   ├── resume_extractor.py # Resume parsing
│   │   ├── job_parser.py       # Job description analysis
│   │   ├── resume_tailor.py    # Resume optimization
│   │   ├── document_generator.py # PDF/DOCX generation
│   │   └── evaluator.py        # Quality metrics
│   ├── utils/
│   │   └── document_extractor.py # File parsing utilities
│   ├── templates/
│   │   └── index.html          # Web UI
│   └── static/
│       ├── css/style.css       # Styles
│       └── js/app.js           # Frontend logic
├── samples/
│   ├── resumes/                # Sample resumes
│   ├── job_descriptions/       # Sample job postings
│   └── outputs/                # Generated resumes
├── tests/                      # Unit tests
├── uploads/                    # Uploaded files
├── outputs/                    # Generated outputs
├── requirements.txt
├── .env
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🎓 Evaluation Criteria Coverage

### 1. Report Components ✅

- **Model Selection Rationale**: Uses Gemma 2B for efficiency and Llama 3.2 Vision for layout analysis
- **Data Extraction Pipeline**: Multi-stage extraction with PDF/DOCX parsing + LLM structuring
- **Prompt Engineering**: Carefully crafted prompts for each service (extraction, tailoring, generation)
- **Comprehensive Metrics**:
  - ATS Compliance Score
  - Keyword Match Percentage
  - Experience Coverage
  - Achievement Coverage
  - Overall Quality Score

### 2. Presentation Materials ✅

- Live demo capability through web interface
- Before/after CV comparison via evaluation metrics
- Visual analytics (score displays, keyword matching)
- Success metrics and recommendations

### 3. Code Submission ✅

- Well-documented codebase with docstrings
- Modular architecture (services, models, utils)
- Configuration for local deployment
- Sample data included
- Comprehensive README

## 🔬 Technical Implementation

### LLM Integration

**Gemma 2B** (Text Generation):
- Resume data extraction
- Job requirement parsing
- Content generation and tailoring
- Keyword optimization

**Llama 3.2 Vision 11B** (Visual Analysis):
- Document layout understanding
- Format quality assessment
- Visual element detection

### Prompt Engineering Examples

**Resume Extraction**:
```python
system_prompt = """You are an expert resume parser.
Extract structured information accurately."""

prompt = f"""Extract information from this resume:
{resume_text}

Return JSON with: personal_info, experience, skills, etc."""
```

**Resume Tailoring**:
```python
prompt = f"""Optimize these responsibilities for {job_title}:
- Original: {responsibilities}
- Job Keywords: {keywords}

Rewrite with strong action verbs and quantifiable achievements."""
```

### ATS Optimization

- Keyword density analysis
- Section coverage validation
- Format compliance checking
- Recommendation engine

## 📊 Evaluation Metrics

The system provides comprehensive evaluation:

1. **Relevance to Job** (0-1): Skills and experience match
2. **Experience Coverage** (0-1): How well experience covers job requirements
3. **Achievement Coverage** (0-1): Presence of quantifiable achievements
4. **ATS Compliance** (0-1): Keyword matching and format compliance
5. **Keyword Density** (0-1): Optimal keyword usage
6. **Overall Quality** (0-1): Weighted average of all metrics

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t cv-creator-llm .
docker run -p 8000:8000 cv-creator-llm
```

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# Test with sample data
python -m pytest tests/test_services.py
```

## 📝 Features Highlights

### Prompt Engineering Excellence
- Context-aware prompts for each stage
- JSON schema enforcement
- Temperature tuning for consistency
- System prompts for role definition

### LangChain Integration (Optional Enhancement)
```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Can be extended to use LangChain for complex workflows
```

### Privacy-Centric Design
- Local LLM deployment via Ollama
- No data sent to external APIs
- Complete data control

## 🎯 Use Cases

1. **Job Seekers**: Quickly tailor resumes for multiple applications
2. **Career Coaches**: Help clients optimize their resumes
3. **Recruiters**: Understand ATS requirements better
4. **Students**: Learn resume best practices with AI guidance

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] LinkedIn profile integration
- [ ] Cover letter generation
- [ ] A/B testing different versions
- [ ] Historical tracking of applications
- [ ] Interview preparation suggestions

## 📚 References

- [Ollama Documentation](https://ollama.ai/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Gemma Model](https://ai.google.dev/gemma)
- [Llama Models](https://llama.meta.com/)
- [ResumeLM Project](https://github.com/olyaiy/resume-lm)

## 🤝 Contributing

This is a capstone project. For educational purposes, feel free to:
1. Fork the repository
2. Create feature branches
3. Submit pull requests
4. Report issues

## 📄 License

MIT License - See LICENSE file for details

## 👨‍💻 Author

Capstone Project - CV Creation using LLMs
IIITK Computer Vision Course

## 🙏 Acknowledgments

- Anthropic for Claude
- Google for Gemma models
- Meta for Llama models
- Ollama team for local LLM deployment
- FastAPI framework
- Open-source community

---

**Note**: Ensure Ollama is running with both `gemma:2b` and `llama3.2-vision:11b` models before starting the application.

For questions or issues, please check the GitHub issues or create a new one.

**Happy Resume Building! 🚀**
