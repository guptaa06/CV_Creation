"""
Resume data extraction service using LLM
"""
import json
import logging
from typing import Dict, Any
from app.services.llm_service import llm_service
from app.models.schemas import ResumeData, PersonalInfo, Education, Experience, Project, Certification
from app.utils.document_extractor import extract_contact_info

logger = logging.getLogger(__name__)


class ResumeExtractor:
    """Extract structured data from resume text using LLM"""

    def __init__(self):
        self.llm = llm_service

    def extract_resume_data(self, resume_text: str) -> ResumeData:
        """
        Extract structured resume data from raw text

        Args:
            resume_text: Raw resume text

        Returns:
            Structured ResumeData object
        """
        logger.info("Extracting structured data from resume")

        # Extract contact info using regex first
        contact_info = extract_contact_info(resume_text)

        # Use LLM to extract structured information
        system_prompt = """You are an expert resume parser. Extract structured information from resumes accurately.
CRITICAL: You MUST respond with ONLY valid JSON. No explanations, no markdown, no extra text.
Ensure all JSON is properly formatted with correct quotes, commas, and brackets.
Be thorough and capture all relevant details."""

        extraction_prompt = f"""Extract ALL information from this resume comprehensively and return it as JSON.

IMPORTANT:
- Extract EVERY detail - do not skip or summarize anything
- Capture ALL bullet points, achievements, responsibilities completely
- Include ALL skills, certifications, languages mentioned
- Preserve exact wording and details from the resume
- Read the ENTIRE resume from start to finish

Resume Text:
{resume_text}

Extract and return JSON with this EXACT structure:
{{
    "personal_info": {{
        "name": "full name exactly as written",
        "email": "email address",
        "phone": "phone number with format",
        "location": "complete city, state/country",
        "linkedin": "full LinkedIn URL",
        "github": "full GitHub URL",
        "website": "personal website URL"
    }},
    "summary": "complete professional summary or objective - extract word-for-word",
    "education": [
        {{
            "institution": "exact institution name",
            "degree": "exact degree name",
            "field_of_study": "specific major/specialization",
            "start_date": "month year or year",
            "end_date": "month year or 'Present'",
            "gpa": "exact GPA score if mentioned",
            "achievements": ["ALL academic achievements, honors, awards - extract every single one"]
        }}
    ],
    "experience": [
        {{
            "company": "exact company name",
            "position": "exact job title",
            "location": "city, state/country",
            "start_date": "month year",
            "end_date": "month year or 'Present'",
            "current": true or false,
            "responsibilities": ["Extract EVERY responsibility/duty listed - include all bullet points"],
            "achievements": ["Extract EVERY achievement, result, metric, award - do not skip any"]
        }}
    ],
    "skills": ["Extract EVERY skill mentioned - technical, soft skills, tools, technologies, frameworks, languages, etc. - be exhaustive"],
    "projects": [
        {{
            "name": "exact project name",
            "description": "complete project description with all details",
            "technologies": ["ALL technologies, tools, frameworks used"],
            "link": "project URL/GitHub if available",
            "achievements": ["project outcomes, metrics, recognition - extract all"]
        }}
    ],
    "certifications": [
        {{
            "name": "exact certification name",
            "issuer": "issuing organization",
            "date": "completion/issue date if mentioned",
            "description": "brief description or focus area if mentioned"
        }}
    ],
    "languages": ["Extract ALL languages with proficiency level if mentioned"],
    "achievements": ["Extract ALL general achievements, awards, honors not covered in other sections"]
}}

CRITICAL INSTRUCTIONS:
1. Read the ENTIRE resume - do not stop early
2. Extract EVERYTHING - be thorough and complete
3. Do not summarize or paraphrase - extract exact content
4. Include ALL bullet points under each section
5. Capture ALL skills, even if there are many
6. If a field is truly not present, use null or [] as appropriate
7. Ensure all arrays have ALL items, not just examples

Return ONLY valid JSON with NO additional text before or after."""

        try:
            # Import settings to get parsing model
            from app.config import settings

            # Get structured response from LLM using parsing model
            structured_data = self.llm.generate_structured(
                prompt=extraction_prompt,
                system_prompt=system_prompt,
                temperature=0.2,  # Low temperature for consistent extraction
                model=settings.PARSING_MODEL,
            )

            # Merge regex-extracted contact info with LLM extracted data
            if "personal_info" in structured_data:
                for key, value in contact_info.items():
                    if value and not structured_data["personal_info"].get(key):
                        structured_data["personal_info"][key] = value

            # Convert to ResumeData object
            resume_data = self._parse_resume_data(structured_data)

            logger.info("Successfully extracted resume data")
            return resume_data

        except Exception as e:
            logger.error(f"Error extracting resume data: {str(e)}")
            raise ValueError(f"Failed to extract resume data: {str(e)}")

    def _parse_resume_data(self, data: Dict[str, Any]) -> ResumeData:
        """
        Parse dictionary to ResumeData object

        Args:
            data: Dictionary with resume data

        Returns:
            ResumeData object
        """
        try:
            # Parse personal info
            personal_info_data = data.get("personal_info", {})
            personal_info = PersonalInfo(**personal_info_data)

            # Parse education
            education = []
            for edu in data.get("education", []):
                education.append(Education(**edu))

            # Parse experience
            experience = []
            for exp in data.get("experience", []):
                experience.append(Experience(**exp))

            # Parse projects
            projects = []
            for proj in data.get("projects", []):
                projects.append(Project(**proj))

            # Parse certifications
            certifications = []
            for cert in data.get("certifications", []):
                if isinstance(cert, str):
                    # Handle legacy string format
                    certifications.append(Certification(name=cert))
                elif isinstance(cert, dict):
                    certifications.append(Certification(**cert))

            # Create ResumeData object
            resume_data = ResumeData(
                personal_info=personal_info,
                summary=data.get("summary"),
                education=education,
                experience=experience,
                skills=data.get("skills", []),
                projects=projects if projects else None,
                certifications=certifications if certifications else None,
                languages=data.get("languages"),
                achievements=data.get("achievements"),
            )

            return resume_data

        except Exception as e:
            logger.error(f"Error parsing resume data: {str(e)}")
            raise ValueError(f"Failed to parse resume data: {str(e)}")

    def enhance_extraction_with_vision(
        self, resume_text: str, image_path: str
    ) -> Dict[str, Any]:
        """
        Enhance extraction using vision model to understand layout

        Args:
            resume_text: Extracted text
            image_path: Path to resume image/PDF page

        Returns:
            Additional insights from visual analysis
        """
        vision_prompt = f"""Analyze this resume document and provide insights about:
1. Overall layout and formatting quality
2. Visual hierarchy and readability
3. ATS-friendliness of the format
4. Any visual elements that might not be captured in text extraction

Resume text for context:
{resume_text[:500]}...

Provide your analysis as JSON with keys: layout_quality, formatting_score, ats_friendly, visual_elements, recommendations"""

        try:
            response = self.llm.analyze_with_vision(
                prompt=vision_prompt,
                image_path=image_path,
            )
            return {"visual_analysis": response}

        except Exception as e:
            logger.warning(f"Vision analysis failed: {str(e)}")
            return {}


# Global instance
resume_extractor = ResumeExtractor()
