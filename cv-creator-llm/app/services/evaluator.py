"""
Resume evaluation and metrics service
"""
import logging
from typing import Dict, List
from app.models.schemas import ResumeData, JobRequirements, EvaluationMetrics, ATSAnalysis

logger = logging.getLogger(__name__)


class ResumeEvaluator:
    """Evaluate resume quality and relevance"""

    def evaluate(
        self,
        original_resume: ResumeData,
        tailored_resume: ResumeData,
        job_requirements: JobRequirements,
        ats_analysis: ATSAnalysis,
    ) -> EvaluationMetrics:
        """
        Comprehensive resume evaluation

        Args:
            original_resume: Original resume data
            tailored_resume: Tailored resume data
            job_requirements: Job requirements
            ats_analysis: ATS analysis results

        Returns:
            EvaluationMetrics with detailed scores
        """
        # 1. Relevance to job
        relevance_score = self._calculate_relevance(tailored_resume, job_requirements)

        # 2. Experience coverage
        experience_coverage = self._calculate_experience_coverage(
            tailored_resume, job_requirements
        )

        # 3. Achievement coverage
        achievement_coverage = self._calculate_achievement_coverage(tailored_resume)

        # 4. ATS compliance
        ats_score = ats_analysis.overall_score

        # 5. Keyword density
        keyword_density = ats_analysis.keyword_match_score

        # 6. Overall quality (weighted average)
        overall_quality = (
            relevance_score * 0.25
            + experience_coverage * 0.20
            + achievement_coverage * 0.15
            + ats_score * 0.25
            + keyword_density * 0.15
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            tailored_resume,
            job_requirements,
            ats_analysis,
            relevance_score,
            experience_coverage,
            achievement_coverage,
        )

        return EvaluationMetrics(
            relevance_to_job=round(relevance_score, 2),
            experience_coverage=round(experience_coverage, 2),
            achievement_coverage=round(achievement_coverage, 2),
            ats_compliance_score=round(ats_score, 2),
            keyword_density=round(keyword_density, 2),
            overall_quality=round(overall_quality, 2),
            recommendations=recommendations,
        )

    def _calculate_relevance(
        self, resume: ResumeData, job_req: JobRequirements
    ) -> float:
        """Calculate job relevance score"""
        score = 0.0
        factors = 0

        # Skills match
        resume_skills_lower = [s.lower() for s in resume.skills]
        required_skills_lower = [s.lower() for s in job_req.required_skills]

        if required_skills_lower:
            skills_match = sum(
                1 for skill in required_skills_lower if skill in resume_skills_lower
            )
            score += skills_match / len(required_skills_lower)
            factors += 1

        # Experience match (check if position titles match job title)
        if job_req.job_title and resume.experience:
            job_title_words = set(job_req.job_title.lower().split())
            for exp in resume.experience:
                position_words = set(exp.position.lower().split())
                if job_title_words & position_words:
                    score += 0.3
                    break
            factors += 1

        return score / factors if factors > 0 else 0.0

    def _calculate_experience_coverage(
        self, resume: ResumeData, job_req: JobRequirements
    ) -> float:
        """Calculate how well experience covers job requirements"""
        if not resume.experience:
            return 0.0

        coverage_points = 0
        total_points = 0

        # Check if responsibilities match job requirements
        all_responsibilities = []
        for exp in resume.experience:
            all_responsibilities.extend([r.lower() for r in exp.responsibilities])

        resp_text = " ".join(all_responsibilities)

        # Check coverage of job responsibilities
        for req_resp in job_req.responsibilities[:10]:
            total_points += 1
            if any(word in resp_text for word in req_resp.lower().split() if len(word) > 4):
                coverage_points += 1

        # Check coverage of required skills
        for skill in job_req.required_skills[:10]:
            total_points += 1
            if skill.lower() in resp_text:
                coverage_points += 1

        return coverage_points / total_points if total_points > 0 else 0.0

    def _calculate_achievement_coverage(self, resume: ResumeData) -> float:
        """Calculate achievement and impact coverage"""
        achievement_indicators = [
            "increased",
            "decreased",
            "improved",
            "generated",
            "saved",
            "reduced",
            "achieved",
            "delivered",
            "%",
            "million",
            "thousand",
        ]

        total_bullets = 0
        bullets_with_achievements = 0

        for exp in resume.experience:
            for resp in exp.responsibilities:
                total_bullets += 1
                resp_lower = resp.lower()
                if any(indicator in resp_lower for indicator in achievement_indicators):
                    bullets_with_achievements += 1

        return bullets_with_achievements / total_bullets if total_bullets > 0 else 0.0

    def _generate_recommendations(
        self,
        resume: ResumeData,
        job_req: JobRequirements,
        ats_analysis: ATSAnalysis,
        relevance: float,
        experience_cov: float,
        achievement_cov: float,
    ) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []

        # Relevance recommendations
        if relevance < 0.7:
            recommendations.append(
                f"Increase relevance by adding {len(ats_analysis.missing_keywords[:3])} key skills: {', '.join(ats_analysis.missing_keywords[:3])}"
            )

        # Experience recommendations
        if experience_cov < 0.6:
            recommendations.append(
                "Add more details to work experience that align with job responsibilities"
            )

        # Achievement recommendations
        if achievement_cov < 0.5:
            recommendations.append(
                "Include more quantifiable achievements (metrics, percentages, impact)"
            )

        # ATS recommendations
        if ats_analysis.overall_score < 0.75:
            recommendations.extend(ats_analysis.suggestions[:2])

        # Summary recommendation
        if not resume.summary:
            recommendations.append("Add a professional summary targeting this role")

        return recommendations[:5]  # Top 5 recommendations


# Global instance
evaluator = ResumeEvaluator()
