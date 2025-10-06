"""
Main FastAPI application
"""
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.schemas import (
    GenerateResumeRequest,
    ResumeResponse,
    RevisionRequest,
    EvaluationMetrics,
)
from app.services import (
    llm_service,
    resume_extractor,
    job_parser,
    resume_tailor,
    document_generator,
    evaluator,
)
from app.utils import DocumentExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered CV creation and optimization using LLMs",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Create directories
Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)
Path(settings.OUTPUT_DIR).mkdir(exist_ok=True)


# Global state for current resume session
current_session = {
    "original_resume": None,
    "tailored_resume": None,
    "job_requirements": None,
    "ats_analysis": None,
}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render home page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    models_status = llm_service.verify_models()

    return {
        "status": "healthy",
        "models": models_status,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/models")
async def get_available_models():
    """Get list of available Ollama models"""
    try:
        available_models = llm_service.get_available_models()

        # Auto-select first model if none is currently selected
        if available_models:
            if not settings.PARSING_MODEL:
                settings.PARSING_MODEL = available_models[0]["name"]
                logger.info(f"Auto-selected parsing model: {settings.PARSING_MODEL}")

            if not settings.GENERATION_MODEL:
                settings.GENERATION_MODEL = available_models[0]["name"]
                logger.info(f"Auto-selected generation model: {settings.GENERATION_MODEL}")

        return {
            "success": True,
            "models": available_models,
            "current_parsing_model": settings.PARSING_MODEL,
            "current_generation_model": settings.GENERATION_MODEL,
        }
    except Exception as e:
        logger.error(f"Error fetching models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/select-model")
async def select_model(model_name: str = Form(...), model_type: str = Form(default="parsing")):
    """Select LLM model to use

    Args:
        model_name: Name of the model to use
        model_type: Type of model - 'parsing' for resume extraction or 'generation' for resume generation
    """
    try:
        # Verify model exists
        available = llm_service.get_available_models()
        if model_name not in [m["name"] for m in available]:
            raise HTTPException(status_code=400, detail=f"Model {model_name} not found")

        # Update settings based on model type
        if model_type == "parsing":
            settings.PARSING_MODEL = model_name
            logger.info(f"Parsing model updated to: {model_name}")
        elif model_type == "generation":
            settings.GENERATION_MODEL = model_name
            logger.info(f"Generation model updated to: {model_name}")
        else:
            raise HTTPException(status_code=400, detail=f"Invalid model_type: {model_type}. Use 'parsing' or 'generation'")

        return {
            "success": True,
            "message": f"{model_type.capitalize()} model set to {model_name}",
            "selected_model": model_name,
            "model_type": model_type,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error selecting model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and extract resume data

    Args:
        file: Resume file (PDF or DOCX)

    Returns:
        Extracted resume data
    """
    try:
        # Validate file type
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not allowed. Use PDF or DOCX.",
            )

        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resume_{timestamp}{file_ext}"
        filepath = Path(settings.UPLOAD_DIR) / filename

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Resume uploaded: {filepath}")

        # Extract text
        extracted_text = DocumentExtractor.extract_and_clean(str(filepath))

        # Extract structured data
        resume_data = resume_extractor.extract_resume_data(extracted_text)

        # Store in session
        current_session["original_resume"] = resume_data

        return {
            "success": True,
            "message": "Resume uploaded and processed successfully",
            "data": resume_data.dict(),
            "extracted_text_length": len(extracted_text),
        }

    except Exception as e:
        logger.error(f"Error uploading resume: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/parse-job")
async def parse_job_description(job_description: str = Form(...)):
    """
    Parse job description

    Args:
        job_description: Job description text

    Returns:
        Parsed job requirements
    """
    try:
        job_requirements = job_parser.parse_job_description(job_description)

        # Store in session
        current_session["job_requirements"] = job_requirements

        return {
            "success": True,
            "message": "Job description parsed successfully",
            "data": job_requirements.dict(),
        }

    except Exception as e:
        logger.error(f"Error parsing job description: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-resume", response_model=ResumeResponse)
async def generate_tailored_resume(request: GenerateResumeRequest):
    """
    Generate tailored resume

    Args:
        request: Generation request with job description and options

    Returns:
        Generated resume file path and analysis
    """
    try:
        if not current_session.get("original_resume"):
            raise HTTPException(status_code=400, detail="No resume uploaded")

        # Parse job description if not already done
        if not current_session.get("job_requirements"):
            job_requirements = job_parser.parse_job_description(request.job_description)
            current_session["job_requirements"] = job_requirements
        else:
            job_requirements = current_session["job_requirements"]

        # Tailor resume
        tailored_resume = resume_tailor.tailor_resume(
            resume_data=current_session["original_resume"],
            job_requirements=job_requirements,
            optimization_level=request.optimization_level,
        )

        # Store in session
        current_session["tailored_resume"] = tailored_resume
        current_session["ats_analysis"] = tailored_resume.ats_analysis

        # Generate document
        output_path = document_generator.generate(
            resume_data=tailored_resume.resume_data,
            format=request.target_format,
        )

        # Evaluate quality
        metrics = evaluator.evaluate(
            original_resume=current_session["original_resume"],
            tailored_resume=tailored_resume.resume_data,
            job_requirements=job_requirements,
            ats_analysis=tailored_resume.ats_analysis,
        )

        return ResumeResponse(
            success=True,
            message="Resume generated successfully",
            file_path=output_path,
            ats_analysis=tailored_resume.ats_analysis,
            metadata={
                "customizations": tailored_resume.customizations_made,
                "relevance_score": tailored_resume.relevance_score,
                "evaluation": metrics.dict(),
            },
        )

    except Exception as e:
        logger.error(f"Error generating resume: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download/{filename}")
async def download_resume(filename: str):
    """Download generated resume"""
    filepath = Path(settings.OUTPUT_DIR) / filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/octet-stream",
    )


@app.post("/api/revise-section")
async def revise_section(request: RevisionRequest):
    """
    Revise specific resume section

    Args:
        request: Revision request with section and instructions

    Returns:
        Revised content
    """
    try:
        if not current_session.get("tailored_resume"):
            raise HTTPException(status_code=400, detail="No tailored resume available")

        tailored_data = current_session["tailored_resume"].resume_data
        job_req = current_session.get("job_requirements")

        # Handle different sections
        if request.section == "summary":
            # Revise summary
            system_prompt = "You are an expert resume writer. Revise the professional summary based on the user's feedback."
            prompt = f"""Current summary:
{tailored_data.summary}

User instructions:
{request.instructions}

Job requirements:
{job_req.job_title if job_req else 'Not specified'}

Revise the summary following the instructions while maintaining ATS optimization.
Return ONLY the revised summary."""

            revised = llm_service.generate_text(prompt, system_prompt)
            tailored_data.summary = revised.strip()

        elif request.section == "skills":
            # Revise skills based on instructions
            current_skills = ", ".join(tailored_data.skills)

            prompt = f"""Current skills:
{current_skills}

User instructions:
{request.instructions}

Provide a revised list of skills as a comma-separated string."""

            revised = llm_service.generate_text(prompt)
            tailored_data.skills = [s.strip() for s in revised.split(",")]

        # Re-evaluate if needed
        if request.preserve_ats_score and job_req:
            new_analysis = resume_tailor._analyze_ats_compliance(tailored_data, job_req)
            current_session["ats_analysis"] = new_analysis

        return {
            "success": True,
            "message": f"Section '{request.section}' revised successfully",
            "revised_content": getattr(tailored_data, request.section, None),
        }

    except Exception as e:
        logger.error(f"Error revising section: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/evaluation")
async def get_evaluation() -> EvaluationMetrics:
    """Get current resume evaluation metrics"""
    try:
        if not all(
            [
                current_session.get("original_resume"),
                current_session.get("tailored_resume"),
                current_session.get("job_requirements"),
            ]
        ):
            raise HTTPException(status_code=400, detail="Complete workflow first")

        metrics = evaluator.evaluate(
            original_resume=current_session["original_resume"],
            tailored_resume=current_session["tailored_resume"].resume_data,
            job_requirements=current_session["job_requirements"],
            ats_analysis=current_session["ats_analysis"],
        )

        return metrics

    except Exception as e:
        logger.error(f"Error getting evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/resume-data")
async def get_resume_data():
    """Get full tailored resume data for editing"""
    try:
        if not current_session.get("tailored_resume"):
            raise HTTPException(status_code=400, detail="No tailored resume available")

        tailored_resume = current_session["tailored_resume"]
        resume_data = tailored_resume.resume_data

        return {
            "success": True,
            "data": {
                "personal_info": {
                    "name": resume_data.personal_info.name,
                    "email": resume_data.personal_info.email or "",
                    "phone": resume_data.personal_info.phone or "",
                    "location": resume_data.personal_info.location or "",
                    "linkedin": resume_data.personal_info.linkedin or "",
                    "github": resume_data.personal_info.github or "",
                },
                "summary": resume_data.summary or "",
                "skills": resume_data.skills,
                "experience": [
                    {
                        "position": exp.position,
                        "company": exp.company,
                        "start_date": exp.start_date,
                        "end_date": exp.end_date,
                        "responsibilities": exp.responsibilities,
                    }
                    for exp in resume_data.experience
                ],
                "education": [
                    {
                        "degree": edu.degree,
                        "institution": edu.institution,
                        "field_of_study": edu.field_of_study or "",
                        "start_date": edu.start_date or "",
                        "end_date": edu.end_date or "",
                        "gpa": edu.gpa or "",
                    }
                    for edu in resume_data.education
                ],
                "projects": [
                    {
                        "name": proj.name,
                        "description": proj.description,
                        "technologies": proj.technologies,
                    }
                    for proj in (resume_data.projects or [])
                ],
            },
        }
    except Exception as e:
        logger.error(f"Error getting resume data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/comparison")
async def get_comparison():
    """Get before/after comparison of resume"""
    try:
        if not all([
            current_session.get("original_resume"),
            current_session.get("tailored_resume"),
            current_session.get("job_requirements"),
        ]):
            raise HTTPException(status_code=400, detail="Complete workflow first")

        original = current_session["original_resume"]
        tailored = current_session["tailored_resume"].resume_data
        job_req = current_session["job_requirements"]

        # Compare skills
        original_skills = set(s.lower() for s in original.skills)
        tailored_skills = set(s.lower() for s in tailored.skills)
        skills_added = list(tailored_skills - original_skills)
        skills_removed = list(original_skills - tailored_skills)
        skills_kept = list(original_skills & tailored_skills)

        # Compare experience bullets
        original_bullets = sum(len(exp.responsibilities) for exp in original.experience)
        tailored_bullets = sum(len(exp.responsibilities) for exp in tailored.experience)

        # Calculate keyword coverage before/after
        job_keywords_lower = [k.lower() for k in job_req.keywords]

        # Original resume keyword match
        original_text = " ".join([
            *original.skills,
            *[exp.position for exp in original.experience],
            *[resp for exp in original.experience for resp in exp.responsibilities]
        ]).lower()

        original_matched = [kw for kw in job_keywords_lower if kw in original_text]

        # Tailored resume keyword match
        tailored_text = " ".join([
            *tailored.skills,
            *[exp.position for exp in tailored.experience],
            *[resp for exp in tailored.experience for resp in exp.responsibilities]
        ]).lower()

        tailored_matched = [kw for kw in job_keywords_lower if kw in tailored_text]

        # Calculate scores
        original_score = len(original_matched) / len(job_keywords_lower) if job_keywords_lower else 0
        tailored_score = len(tailored_matched) / len(job_keywords_lower) if job_keywords_lower else 0

        # Estimate overall scores (for "before" we don't have real ATS analysis, so we estimate)
        original_overall_score = round(original_score * 0.9, 2)  # Slightly lower estimate
        original_overall_quality = round(original_score * 0.85, 2)  # Slightly lower estimate

        # Get actual scores from tailored resume
        ats_analysis = current_session.get("ats_analysis")
        if ats_analysis and hasattr(ats_analysis, 'overall_score'):
            tailored_overall_score = ats_analysis.overall_score
        else:
            tailored_overall_score = round(tailored_score, 2)

        # Get evaluation if available - use tailored score for quality
        tailored_quality = round(tailored_score, 2)

        return {
            "before": {
                "summary": original.summary,
                "skills_count": len(original.skills),
                "experience_bullets": original_bullets,
                "keyword_matches": len(original_matched),
                "keyword_match_score": round(original_score, 2),
                "overall_score": original_overall_score,
                "overall_quality": original_overall_quality,
                "matched_keywords": original_matched[:20],
            },
            "after": {
                "summary": tailored.summary,
                "skills_count": len(tailored.skills),
                "experience_bullets": tailored_bullets,
                "keyword_matches": len(tailored_matched),
                "keyword_match_score": round(tailored_score, 2),
                "overall_score": tailored_overall_score if isinstance(tailored_overall_score, float) else round(tailored_score, 2),
                "overall_quality": tailored_quality,
                "matched_keywords": tailored_matched[:20],
            },
            "changes": {
                "summary_changed": original.summary != tailored.summary,
                "skills_added": skills_added[:10],
                "skills_removed": skills_removed[:10],
                "skills_kept_count": len(skills_kept),
                "new_keywords_matched": list(set(tailored_matched) - set(original_matched))[:10],
                "improvement": {
                    "keyword_score_increase": round(tailored_score - original_score, 2),
                    "keyword_count_increase": len(tailored_matched) - len(original_matched),
                    "percentage_improvement": round((tailored_score - original_score) * 100, 1) if original_score > 0 else 0,
                }
            },
            "customizations": current_session["tailored_resume"].customizations_made,
        }

    except Exception as e:
        logger.error(f"Error getting comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/session-status")
async def get_session_status():
    """Get current session status"""
    return {
        "resume_uploaded": current_session.get("original_resume") is not None,
        "job_parsed": current_session.get("job_requirements") is not None,
        "resume_tailored": current_session.get("tailored_resume") is not None,
    }


@app.post("/api/recompare")
async def recompare_resume(request: dict):
    """
    Recompare resume after user edits

    Args:
        request: Updated resume data with summary, skills, and experience

    Returns:
        Updated comparison and analysis
    """
    try:
        if not current_session.get("original_resume") or not current_session.get("job_requirements"):
            raise HTTPException(status_code=400, detail="No session data available")

        # Get updated data from request
        updated_summary = request.get("summary", "")
        updated_skills = request.get("skills", [])
        updated_experience = request.get("experience", [])

        # Get the current tailored resume
        if not current_session.get("tailored_resume"):
            raise HTTPException(status_code=400, detail="No tailored resume available")

        tailored_resume = current_session["tailored_resume"]

        # Update the resume data
        tailored_resume.resume_data.summary = updated_summary
        tailored_resume.resume_data.skills = updated_skills

        # Update experience if provided
        for i, exp_update in enumerate(updated_experience):
            if i < len(tailored_resume.resume_data.experience):
                tailored_resume.resume_data.experience[i].responsibilities = exp_update.get("responsibilities", [])

        # Recalculate ATS analysis
        from app.services.resume_tailor import resume_tailor
        ats_analysis = resume_tailor._analyze_ats_compliance(
            tailored_resume.resume_data,
            current_session["job_requirements"]
        )

        # Update session
        current_session["tailored_resume"] = tailored_resume
        current_session["ats_analysis"] = ats_analysis

        # Regenerate document with updated data
        output_path = document_generator.generate(
            resume_data=tailored_resume.resume_data,
            format="pdf",
        )

        return {
            "success": True,
            "message": "Resume recompared successfully",
            "ats_analysis": ats_analysis.dict(),
            "file_path": output_path,
        }

    except Exception as e:
        logger.error(f"Error recomparing resume: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reset")
async def reset_session():
    """Reset current session"""
    current_session.clear()
    current_session.update({
        "original_resume": None,
        "tailored_resume": None,
        "job_requirements": None,
        "ats_analysis": None,
    })

    return {"success": True, "message": "Session reset successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
