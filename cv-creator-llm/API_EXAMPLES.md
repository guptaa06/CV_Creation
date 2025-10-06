# 🔌 API Usage Examples

Complete examples for testing all API endpoints.

## Base URL
```
http://localhost:8000
```

## 1. Health Check

**Endpoint**: `GET /health`

**cURL**:
```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "models": {
    "text_model": true,
    "vision_model": true
  },
  "timestamp": "2025-10-05T10:30:00"
}
```

**Python**:
```python
import requests

response = requests.get("http://localhost:8000/health")
print(response.json())
```

---

## 2. Upload Resume

**Endpoint**: `POST /api/upload-resume`

**cURL**:
```bash
curl -X POST http://localhost:8000/api/upload-resume \
  -F "file=@path/to/resume.pdf"
```

**Python**:
```python
import requests

files = {'file': open('resume.pdf', 'rb')}
response = requests.post(
    "http://localhost:8000/api/upload-resume",
    files=files
)
print(response.json())
```

**JavaScript**:
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/api/upload-resume', {
    method: 'POST',
    body: formData
})
.then(res => res.json())
.then(data => console.log(data));
```

**Response**:
```json
{
  "success": true,
  "message": "Resume uploaded and processed successfully",
  "data": {
    "personal_info": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1234567890"
    },
    "skills": ["Python", "JavaScript", "React"],
    "experience": [...]
  },
  "extracted_text_length": 2543
}
```

---

## 3. Parse Job Description

**Endpoint**: `POST /api/parse-job`

**cURL**:
```bash
curl -X POST http://localhost:8000/api/parse-job \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "job_description=Senior Software Engineer position requiring Python, JavaScript, React. 5+ years experience..."
```

**Python**:
```python
import requests

data = {
    'job_description': """
    Senior Software Engineer

    Requirements:
    - 5+ years experience
    - Python, JavaScript, React
    - AWS, Docker, Kubernetes
    """
}

response = requests.post(
    "http://localhost:8000/api/parse-job",
    data=data
)
print(response.json())
```

**Response**:
```json
{
  "success": true,
  "message": "Job description parsed successfully",
  "data": {
    "job_title": "Senior Software Engineer",
    "required_skills": ["Python", "JavaScript", "React", "AWS"],
    "preferred_skills": ["Docker", "Kubernetes"],
    "keywords": ["Python", "React", "AWS", "Docker", "CI/CD"],
    "experience_required": "5+ years"
  }
}
```

---

## 4. Generate Tailored Resume

**Endpoint**: `POST /api/generate-resume`

**cURL**:
```bash
curl -X POST http://localhost:8000/api/generate-resume \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Senior Software Engineer...",
    "target_format": "pdf",
    "optimization_level": "balanced"
  }'
```

**Python**:
```python
import requests

payload = {
    "job_description": "Senior Software Engineer position...",
    "target_format": "pdf",  # or "docx"
    "optimization_level": "balanced",  # minimal, balanced, aggressive
    "include_summary": True
}

response = requests.post(
    "http://localhost:8000/api/generate-resume",
    json=payload
)
result = response.json()
print(f"Generated file: {result['file_path']}")
print(f"ATS Score: {result['ats_analysis']['overall_score']}")
```

**Response**:
```json
{
  "success": true,
  "message": "Resume generated successfully",
  "file_path": "outputs/resume_20251005_103045.pdf",
  "ats_analysis": {
    "overall_score": 0.85,
    "keyword_match_score": 0.82,
    "matched_keywords": ["Python", "React", "AWS", "Docker"],
    "missing_keywords": ["Kubernetes", "CI/CD"],
    "suggestions": ["Add missing keywords: Kubernetes, CI/CD"]
  },
  "metadata": {
    "customizations": [
      "Generated professional summary aligned with job role",
      "Enhanced 3 work experience entries"
    ],
    "relevance_score": 0.83,
    "evaluation": {
      "overall_quality": 0.80,
      "relevance_to_job": 0.85
    }
  }
}
```

---

## 5. Get Evaluation Metrics

**Endpoint**: `GET /api/evaluation`

**cURL**:
```bash
curl http://localhost:8000/api/evaluation
```

**Python**:
```python
import requests

response = requests.get("http://localhost:8000/api/evaluation")
metrics = response.json()

print(f"Overall Quality: {metrics['overall_quality']}")
print(f"ATS Compliance: {metrics['ats_compliance_score']}")
print(f"Recommendations: {metrics['recommendations']}")
```

**Response**:
```json
{
  "relevance_to_job": 0.85,
  "experience_coverage": 0.78,
  "achievement_coverage": 0.65,
  "ats_compliance_score": 0.82,
  "keyword_density": 0.88,
  "overall_quality": 0.80,
  "recommendations": [
    "Include more quantifiable achievements",
    "Add Docker and Kubernetes to skills",
    "Expand cloud experience details"
  ]
}
```

---

## 6. Revise Section

**Endpoint**: `POST /api/revise-section`

**cURL**:
```bash
curl -X POST http://localhost:8000/api/revise-section \
  -H "Content-Type: application/json" \
  -d '{
    "section": "summary",
    "instructions": "Make it more concise and focus on leadership",
    "preserve_ats_score": true
  }'
```

**Python**:
```python
import requests

payload = {
    "section": "summary",  # or "skills", "experience"
    "instructions": "Make it more concise and add more technical keywords",
    "preserve_ats_score": True
}

response = requests.post(
    "http://localhost:8000/api/revise-section",
    json=payload
)
print(response.json())
```

**Response**:
```json
{
  "success": true,
  "message": "Section 'summary' revised successfully",
  "revised_content": "Experienced Senior Software Engineer with 5+ years..."
}
```

---

## 7. Download Resume

**Endpoint**: `GET /api/download/{filename}`

**cURL**:
```bash
curl -O http://localhost:8000/api/download/resume_20251005_103045.pdf
```

**Python**:
```python
import requests

filename = "resume_20251005_103045.pdf"
response = requests.get(f"http://localhost:8000/api/download/{filename}")

with open(filename, 'wb') as f:
    f.write(response.content)
print(f"Downloaded: {filename}")
```

**Browser**:
```
http://localhost:8000/api/download/resume_20251005_103045.pdf
```

---

## 8. Session Status

**Endpoint**: `GET /api/session-status`

**cURL**:
```bash
curl http://localhost:8000/api/session-status
```

**Response**:
```json
{
  "resume_uploaded": true,
  "job_parsed": true,
  "resume_tailored": true
}
```

---

## 9. Reset Session

**Endpoint**: `POST /api/reset`

**cURL**:
```bash
curl -X POST http://localhost:8000/api/reset
```

**Python**:
```python
import requests

response = requests.post("http://localhost:8000/api/reset")
print(response.json())
```

**Response**:
```json
{
  "success": true,
  "message": "Session reset successfully"
}
```

---

## Complete Workflow Example

**Python Script**:
```python
import requests
import time

BASE_URL = "http://localhost:8000"

# 1. Check health
print("1. Checking health...")
health = requests.get(f"{BASE_URL}/health").json()
print(f"   Status: {health['status']}")

# 2. Upload resume
print("\n2. Uploading resume...")
with open('my_resume.pdf', 'rb') as f:
    files = {'file': f}
    upload_response = requests.post(
        f"{BASE_URL}/api/upload-resume",
        files=files
    ).json()
print(f"   Uploaded: {upload_response['success']}")

# 3. Parse job description
print("\n3. Parsing job description...")
job_desc = """
Senior Software Engineer position requiring:
- 5+ years Python experience
- React, Node.js expertise
- AWS, Docker, Kubernetes
- CI/CD pipeline experience
"""

job_response = requests.post(
    f"{BASE_URL}/api/parse-job",
    data={'job_description': job_desc}
).json()
print(f"   Parsed: {job_response['data']['job_title']}")

# 4. Generate tailored resume
print("\n4. Generating tailored resume...")
generate_response = requests.post(
    f"{BASE_URL}/api/generate-resume",
    json={
        'job_description': job_desc,
        'target_format': 'pdf',
        'optimization_level': 'balanced'
    }
).json()

print(f"   Generated: {generate_response['file_path']}")
print(f"   ATS Score: {generate_response['ats_analysis']['overall_score']}")

# 5. Get evaluation
print("\n5. Getting evaluation...")
eval_response = requests.get(f"{BASE_URL}/api/evaluation").json()
print(f"   Overall Quality: {eval_response['overall_quality']}")
print(f"   Recommendations:")
for rec in eval_response['recommendations']:
    print(f"     - {rec}")

# 6. Download resume
print("\n6. Downloading resume...")
filename = generate_response['file_path'].split('/')[-1]
download_response = requests.get(f"{BASE_URL}/api/download/{filename}")
with open(f"tailored_{filename}", 'wb') as f:
    f.write(download_response.content)
print(f"   Downloaded: tailored_{filename}")

print("\n✅ Complete workflow finished!")
```

---

## Testing with Postman

### Collection Structure
```
CV Creator LLM API
├── Health Check
├── Upload Resume
├── Parse Job
├── Generate Resume
├── Get Evaluation
├── Revise Section
├── Download Resume
├── Session Status
└── Reset Session
```

### Environment Variables
```
base_url: http://localhost:8000
```

---

## Error Handling Examples

**Upload Error**:
```json
{
  "detail": "File type .txt not allowed. Use PDF or DOCX."
}
```

**No Resume Uploaded**:
```json
{
  "detail": "No resume uploaded"
}
```

**Ollama Not Running**:
```json
{
  "detail": "Failed to call LLM: Connection refused"
}
```

---

## Rate Limiting & Performance

- No rate limiting implemented (local deployment)
- Average response times:
  - Upload: 5-15 seconds
  - Parse Job: 5-10 seconds
  - Generate Resume: 30-60 seconds
  - Download: < 1 second

---

## API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

**Ready to test! 🚀**
