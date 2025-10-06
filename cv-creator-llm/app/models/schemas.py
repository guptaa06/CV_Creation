"""
Pydantic models for data validation and serialization
"""
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime


class PersonalInfo(BaseModel):
    """Personal information schema"""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None


class Education(BaseModel):
    """Education entry schema"""
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    achievements: Optional[List[str]] = []


class Experience(BaseModel):
    """Work experience entry schema"""
    company: str
    position: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    current: bool = False
    responsibilities: List[str] = []
    achievements: Optional[List[str]] = []


class Project(BaseModel):
    """Project entry schema"""
    name: str
    description: str
    technologies: List[str] = []
    link: Optional[str] = None
    achievements: Optional[List[str]] = []


class Certification(BaseModel):
    """Certification entry schema"""
    name: str
    issuer: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None


class ResumeData(BaseModel):
    """Complete resume data structure"""
    personal_info: PersonalInfo
    summary: Optional[str] = None
    education: List[Education] = []
    experience: List[Experience] = []
    skills: List[str] = []
    projects: Optional[List[Project]] = []
    certifications: Optional[List[Certification]] = []
    languages: Optional[List[str]] = []
    achievements: Optional[List[str]] = []


class JobRequirements(BaseModel):
    """Job description requirements schema"""
    job_title: str
    company: Optional[str] = None
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    responsibilities: List[str] = []
    qualifications: List[str] = []
    keywords: List[str] = []
    experience_required: Optional[str] = None


class ATSAnalysis(BaseModel):
    """ATS compatibility analysis"""
    overall_score: float = Field(..., ge=0, le=1)
    keyword_match_score: float = Field(..., ge=0, le=1)
    matched_keywords: List[str] = []
    missing_keywords: List[str] = []
    suggestions: List[str] = []
    format_compliance: bool = True
    section_coverage: Dict[str, bool] = {}


class TailoredResume(BaseModel):
    """Tailored resume response"""
    resume_data: ResumeData
    ats_analysis: ATSAnalysis
    customizations_made: List[str] = []
    relevance_score: float = Field(..., ge=0, le=1)


class GenerateResumeRequest(BaseModel):
    """Request to generate tailored resume"""
    job_description: str
    target_format: str = Field(default="pdf", pattern="^(pdf|docx)$")
    include_summary: bool = True
    optimization_level: str = Field(default="balanced", pattern="^(minimal|balanced|aggressive)$")


class ResumeResponse(BaseModel):
    """Response after resume generation"""
    success: bool
    message: str
    file_path: Optional[str] = None
    ats_analysis: Optional[ATSAnalysis] = None
    metadata: Optional[Dict[str, Any]] = None


class RevisionRequest(BaseModel):
    """Request for resume revision"""
    section: str  # e.g., "summary", "experience", "skills"
    instructions: str
    preserve_ats_score: bool = True


class EvaluationMetrics(BaseModel):
    """Evaluation metrics for resume quality"""
    relevance_to_job: float = Field(..., ge=0, le=1)
    experience_coverage: float = Field(..., ge=0, le=1)
    achievement_coverage: float = Field(..., ge=0, le=1)
    ats_compliance_score: float = Field(..., ge=0, le=1)
    keyword_density: float = Field(..., ge=0, le=1)
    overall_quality: float = Field(..., ge=0, le=1)
    recommendations: List[str] = []
