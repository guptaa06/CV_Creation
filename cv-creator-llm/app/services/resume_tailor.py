"""
Resume tailoring service - Core engine for customizing resumes for specific jobs
"""
import logging
import copy
from typing import Dict, Any, List
from app.services.llm_service import llm_service
from app.models.schemas import (
    ResumeData,
    JobRequirements,
    TailoredResume,
    ATSAnalysis,
)
from app.services.job_parser import job_parser
from app.config import settings

logger = logging.getLogger(__name__)


class ResumeTailor:
    """Tailor resumes to match specific job requirements"""

    def __init__(self):
        self.llm = llm_service

    def tailor_resume(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements,
        optimization_level: str = "balanced",
    ) -> TailoredResume:
        """
        Tailor resume to match job requirements

        Args:
            resume_data: Original resume data
            job_requirements: Job requirements
            optimization_level: Level of optimization (minimal, balanced, aggressive)

        Returns:
            TailoredResume with optimized content and ATS analysis
        """
        logger.info(f"Tailoring resume with {optimization_level} optimization")

        # Create a deep copy to avoid modifying the original
        tailored_data = resume_data.copy(deep=True)

        customizations = []

        # 1. Generate tailored professional summary
        if not tailored_data.summary:
            tailored_data.summary = self._generate_summary(
                tailored_data, job_requirements
            )
            customizations.append("Generated professional summary aligned with job role")
        else:
            tailored_data.summary = self._optimize_summary(
                tailored_data.summary, job_requirements
            )
            customizations.append("Optimized professional summary with job keywords")

        # 2. Optimize experience descriptions
        tailored_data.experience = self._optimize_experience(
            tailored_data.experience, job_requirements, optimization_level
        )
        customizations.append(
            f"Enhanced {len(tailored_data.experience)} work experience entries"
        )

        # 3. Reorder and optimize skills
        tailored_data.skills = self._optimize_skills(
            tailored_data.skills, job_requirements, optimization_level
        )
        customizations.append("Reordered skills to prioritize job-relevant keywords")

        # 4. Optimize projects if present
        if tailored_data.projects:
            tailored_data.projects = self._optimize_projects(
                tailored_data.projects, job_requirements
            )
            customizations.append("Enhanced project descriptions with relevant keywords")

        # 5. Calculate ATS score and analysis
        ats_analysis = self._analyze_ats_compliance(tailored_data, job_requirements)

        # 6. Calculate relevance score
        relevance_score = self._calculate_relevance_score(
            tailored_data, job_requirements, ats_analysis
        )

        return TailoredResume(
            resume_data=tailored_data,
            ats_analysis=ats_analysis,
            customizations_made=customizations,
            relevance_score=relevance_score,
        )

    def _generate_summary(
        self, resume_data: ResumeData, job_requirements: JobRequirements
    ) -> str:
        """Generate professional summary aligned with job"""

        system_prompt = """You are an expert resume writer. Create compelling, ATS-friendly professional summaries that highlight relevant experience and skills for the target role."""

        # Build context about candidate
        experience_summary = ", ".join(
            [f"{exp.position} at {exp.company}" for exp in resume_data.experience[:3]]
        )
        skills_summary = ", ".join(resume_data.skills[:10])

        prompt = f"""Create a compelling professional summary for this candidate applying to: {job_requirements.job_title}

Candidate Background:
- Recent Experience: {experience_summary}
- Key Skills: {skills_summary}
- Education: {resume_data.education[0].degree if resume_data.education else 'Not specified'}

Job Requirements:
- Required Skills: {', '.join(job_requirements.required_skills[:10])}
- Key Responsibilities: {', '.join(job_requirements.responsibilities[:5])}

Write a 3-4 sentence professional summary that:
1. Highlights years of relevant experience
2. Mentions key skills matching the job (use exact keywords from required skills)
3. Emphasizes value proposition for this specific role
4. Uses strong action words and quantifiable achievements if possible

Return ONLY the professional summary text, no additional commentary."""

        try:
            summary = self.llm.generate_text(
                prompt=prompt, system_prompt=system_prompt, temperature=0.7,
                model=settings.GENERATION_MODEL
            )
            return summary.strip()
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return f"Experienced professional with expertise in {', '.join(resume_data.skills[:5])}."

    def _optimize_summary(self, original_summary: str, job_requirements: JobRequirements) -> str:
        """Optimize existing summary for job"""

        system_prompt = """You are an expert resume writer. Optimize professional summaries to include relevant keywords while maintaining natural flow and authenticity."""

        prompt = f"""Optimize this professional summary for a {job_requirements.job_title} position:

Original Summary:
{original_summary}

Job Requirements:
- Required Skills: {', '.join(job_requirements.required_skills[:10])}
- Key Keywords: {', '.join(job_requirements.keywords[:15])}

Rewrite the summary to:
1. Incorporate relevant job keywords naturally
2. Maintain the candidate's authentic voice and achievements
3. Keep it to 3-4 sentences
4. Make it ATS-friendly with exact keyword matches
5. Emphasize experience relevant to this role

Return ONLY the optimized summary, no additional text."""

        try:
            optimized = self.llm.generate_text(
                prompt=prompt, system_prompt=system_prompt, temperature=0.6,
                model=settings.GENERATION_MODEL
            )
            return optimized.strip()
        except Exception as e:
            logger.error(f"Error optimizing summary: {str(e)}")
            return original_summary

    def _optimize_experience(
        self, experiences: List, job_requirements: JobRequirements, optimization_level: str
    ) -> List:
        """Optimize work experience descriptions based on optimization level"""

        # Define different levels of optimization
        if optimization_level == "minimal":
            system_prompt = """You are a resume editor. Make light, natural improvements to bullet points while preserving the original content and style."""
            experience_limit = 2  # Only optimize first 2 jobs
            num_bullets = "4-5"
            temperature = 0.7
        elif optimization_level == "aggressive":
            system_prompt = """You are an expert ATS optimizer. Aggressively rewrite bullet points to maximize keyword matching and impact. Include as many relevant job keywords as naturally possible."""
            experience_limit = len(experiences)  # Optimize all
            num_bullets = "5-7"
            temperature = 0.5
        else:  # balanced
            system_prompt = """You are an expert at writing impactful, ATS-optimized resume bullet points. Use strong action verbs, include quantifiable achievements, and incorporate relevant keywords naturally."""
            experience_limit = min(3, len(experiences))  # Optimize first 3
            num_bullets = "4-6"
            temperature = 0.6

        for i, exp in enumerate(experiences):
            # Limit based on optimization level
            if i >= experience_limit:
                continue

            prompt = f"""Optimize these work responsibilities for a {job_requirements.job_title} position:

Position: {exp.position} at {exp.company}
Original Responsibilities:
{chr(10).join(['- ' + resp for resp in exp.responsibilities])}

Job Requirements:
- Required Skills: {', '.join(job_requirements.required_skills[:8])}
- Keywords to include: {', '.join(job_requirements.keywords[:12])}

Rewrite responsibilities to:
1. Start with strong action verbs
2. Include quantifiable achievements where possible
3. Incorporate relevant job keywords naturally
4. Highlight skills that match the target role
5. Keep each bullet point concise (1-2 lines)
6. Return {num_bullets} most impactful bullet points

Return as a JSON array of strings: ["bullet 1", "bullet 2", ...]
Return ONLY the JSON array."""

            try:
                optimized = self.llm.generate_structured(
                    prompt=prompt, system_prompt=system_prompt, temperature=temperature,
                    model=settings.GENERATION_MODEL
                )

                if isinstance(optimized, list):
                    exp.responsibilities = optimized
                elif isinstance(optimized, dict) and "bullets" in optimized:
                    exp.responsibilities = optimized["bullets"]

            except Exception as e:
                logger.warning(f"Error optimizing experience {i}: {str(e)}")
                continue

        return experiences

    def _optimize_skills(
        self, skills: List[str], job_requirements: JobRequirements, optimization_level: str
    ) -> List[str]:
        """Reorder and optimize skills list based on optimization level"""

        # Combine required and preferred skills
        job_skills = job_requirements.required_skills + job_requirements.preferred_skills
        job_skills_lower = [s.lower() for s in job_skills]

        # Separate matching and non-matching skills
        matching_skills = []
        other_skills = []

        for skill in skills:
            if skill.lower() in job_skills_lower:
                matching_skills.append(skill)
            else:
                other_skills.append(skill)

        # Add missing required skills based on optimization level
        additional_skills = []

        if optimization_level == "minimal":
            # Only add exact matches from required skills
            for req_skill in job_requirements.required_skills[:3]:
                if req_skill.lower() not in [s.lower() for s in skills]:
                    additional_skills.append(req_skill)
        elif optimization_level == "aggressive":
            # Add all missing required and some preferred skills
            for req_skill in job_requirements.required_skills + job_requirements.preferred_skills[:5]:
                if req_skill.lower() not in [s.lower() for s in skills]:
                    additional_skills.append(req_skill)
        else:  # balanced
            # Add missing required skills if they seem transferable
            for req_skill in job_requirements.required_skills:
                if req_skill.lower() not in [s.lower() for s in skills]:
                    # Only add if it's a common/transferable skill
                    if any(
                        keyword in req_skill.lower()
                        for keyword in ["agile", "scrum", "git", "communication", "leadership", "python", "java", "sql", "aws"]
                    ):
                        additional_skills.append(req_skill)

        # Combine: matching skills first, then other skills, then additional
        optimized_skills = matching_skills + other_skills + additional_skills

        # Limit based on optimization level
        max_skills = 35 if optimization_level == "aggressive" else 30
        return optimized_skills[:max_skills]

    def _optimize_projects(self, projects: List, job_requirements: JobRequirements) -> List:
        """Optimize project descriptions"""

        for proj in projects[:3]:  # Focus on top 3 projects
            system_prompt = """You are an expert at writing compelling project descriptions that highlight relevant technical skills and achievements."""

            prompt = f"""Optimize this project description for a {job_requirements.job_title} role:

Project: {proj.name}
Original Description: {proj.description}
Technologies: {', '.join(proj.technologies)}

Job Requirements:
- Required Skills: {', '.join(job_requirements.required_skills[:8])}
- Keywords: {', '.join(job_requirements.keywords[:10])}

Rewrite the description (2-3 sentences) to:
1. Emphasize technologies and skills relevant to the job
2. Include specific accomplishments or metrics
3. Use keywords from the job description
4. Highlight problem-solving and impact

Return ONLY the optimized description."""

            try:
                optimized_desc = self.llm.generate_text(
                    prompt=prompt, system_prompt=system_prompt, temperature=0.6,
                    model=settings.GENERATION_MODEL
                )
                proj.description = optimized_desc.strip()
            except Exception as e:
                logger.warning(f"Error optimizing project: {str(e)}")

        return projects

    def _analyze_ats_compliance(
        self, resume_data: ResumeData, job_requirements: JobRequirements
    ) -> ATSAnalysis:
        """Analyze ATS compliance and keyword matching"""

        # Extract all keywords from resume
        resume_keywords = []
        resume_keywords.extend(resume_data.skills)
        resume_keywords.extend(
            [exp.position for exp in resume_data.experience]
        )

        # Add keywords from descriptions
        for exp in resume_data.experience:
            resume_keywords.extend(exp.responsibilities)

        resume_text = " ".join(resume_keywords).lower()

        # Calculate keyword matches
        job_keywords = job_requirements.keywords + job_requirements.required_skills
        matched_keywords = []
        missing_keywords = []

        for keyword in job_keywords:
            if keyword.lower() in resume_text:
                matched_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)

        # Calculate scores
        keyword_match_score = (
            len(matched_keywords) / len(job_keywords) if job_keywords else 0
        )

        # Check section coverage
        section_coverage = {
            "summary": bool(resume_data.summary),
            "experience": len(resume_data.experience) > 0,
            "education": len(resume_data.education) > 0,
            "skills": len(resume_data.skills) > 0,
            "contact_info": bool(resume_data.personal_info.email),
        }

        coverage_score = sum(section_coverage.values()) / len(section_coverage)

        # Overall score (weighted average)
        overall_score = (keyword_match_score * 0.6) + (coverage_score * 0.4)

        # Generate suggestions
        suggestions = []
        if keyword_match_score < 0.7:
            suggestions.append(
                f"Add {len(missing_keywords[:5])} missing keywords: {', '.join(missing_keywords[:5])}"
            )
        if not resume_data.summary:
            suggestions.append("Add a professional summary section")
        if len(resume_data.skills) < 10:
            suggestions.append("Expand skills section with more relevant skills")

        return ATSAnalysis(
            overall_score=round(overall_score, 2),
            keyword_match_score=round(keyword_match_score, 2),
            matched_keywords=matched_keywords,
            missing_keywords=missing_keywords,
            suggestions=suggestions,
            format_compliance=True,
            section_coverage=section_coverage,
        )

    def _calculate_relevance_score(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements,
        ats_analysis: ATSAnalysis,
    ) -> float:
        """Calculate overall relevance score"""

        # Factors to consider
        keyword_score = ats_analysis.keyword_match_score
        section_score = sum(ats_analysis.section_coverage.values()) / len(
            ats_analysis.section_coverage
        )

        # Experience relevance (simple heuristic)
        experience_score = min(len(resume_data.experience) / 3, 1.0)

        # Weighted combination
        relevance = (keyword_score * 0.5) + (section_score * 0.3) + (experience_score * 0.2)

        return round(relevance, 2)


# Global instance
resume_tailor = ResumeTailor()
