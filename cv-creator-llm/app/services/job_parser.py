"""
Job description parsing service
"""
import logging
import re
from typing import List, Dict, Any
from app.services.llm_service import llm_service
from app.models.schemas import JobRequirements

logger = logging.getLogger(__name__)


class JobDescriptionParser:
    """Parse job descriptions and extract requirements"""

    def __init__(self):
        self.llm = llm_service

    def parse_job_description(self, job_description: str) -> JobRequirements:
        """
        Parse job description and extract structured requirements

        Args:
            job_description: Raw job description text

        Returns:
            JobRequirements object
        """
        logger.info("Parsing job description")

        system_prompt = """You are an expert at analyzing job descriptions. Extract key requirements, skills, and qualifications accurately.
Always respond with valid JSON. Focus on identifying specific technical skills, soft skills, experience requirements, and keywords that would be important for ATS systems."""

        parsing_prompt = f"""Analyze this job description and extract structured information:

Job Description:
{job_description}

Extract and return JSON with this structure:
{{
    "job_title": "job title/position",
    "company": "company name if mentioned",
    "required_skills": ["must-have skill 1", "must-have skill 2"],
    "preferred_skills": ["nice-to-have skill 1", "nice-to-have skill 2"],
    "responsibilities": ["key responsibility 1", "key responsibility 2"],
    "qualifications": ["qualification 1", "qualification 2"],
    "keywords": ["important keyword 1", "important keyword 2", "acronym 1"],
    "experience_required": "X years experience requirement"
}}

Focus on:
1. Technical skills and tools mentioned
2. Soft skills and competencies
3. Educational requirements
4. Years of experience needed
5. Key responsibilities
6. Important keywords and acronyms that should appear in a tailored resume
7. Industry-specific terms

Extract ALL skills, keywords, and requirements. Be comprehensive.
Return ONLY valid JSON, no additional text."""

        try:
            # Get structured response from LLM
            structured_data = self.llm.generate_structured(
                prompt=parsing_prompt,
                system_prompt=system_prompt,
                temperature=0.2,
            )

            # Additional keyword extraction
            additional_keywords = self._extract_additional_keywords(job_description)

            # Merge with LLM-extracted keywords
            all_keywords = list(
                set(structured_data.get("keywords", []) + additional_keywords)
            )
            structured_data["keywords"] = all_keywords

            # Convert to JobRequirements object
            job_requirements = JobRequirements(**structured_data)

            logger.info(
                f"Successfully parsed job description. Found {len(job_requirements.keywords)} keywords"
            )
            return job_requirements

        except Exception as e:
            logger.error(f"Error parsing job description: {str(e)}")
            raise ValueError(f"Failed to parse job description: {str(e)}")

    def _extract_additional_keywords(self, text: str) -> List[str]:
        """
        Extract additional keywords using pattern matching

        Args:
            text: Job description text

        Returns:
            List of keywords
        """
        keywords = []

        # Common skill patterns
        skill_patterns = [
            r'\b(?:proficient|experience|skilled|knowledge)\s+(?:in|with)\s+([\w\s\+\#\.]+)',
            r'\b([\w\+\#]+)\s+(?:developer|engineer|specialist|expert)',
            r'\b(?:using|including|such as)\s+([\w\s,\+\#\.]+)',
        ]

        for pattern in skill_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                keyword = match.group(1).strip()
                if len(keyword) > 2 and len(keyword) < 50:
                    keywords.append(keyword)

        # Extract acronyms (2-5 uppercase letters)
        acronyms = re.findall(r'\b[A-Z]{2,5}\b', text)
        keywords.extend(acronyms)

        # Extract common programming languages and technologies
        tech_keywords = [
            'Python',
            'Java',
            'JavaScript',
            'C++',
            'C#',
            'Ruby',
            'PHP',
            'Swift',
            'Kotlin',
            'Go',
            'Rust',
            'TypeScript',
            'SQL',
            'NoSQL',
            'React',
            'Angular',
            'Vue',
            'Node.js',
            'Django',
            'Flask',
            'Spring',
            'AWS',
            'Azure',
            'GCP',
            'Docker',
            'Kubernetes',
            'Git',
            'CI/CD',
            'Agile',
            'Scrum',
            'REST',
            'GraphQL',
            'Machine Learning',
            'Deep Learning',
            'AI',
            'Data Science',
            'DevOps',
        ]

        for tech in tech_keywords:
            if re.search(r'\b' + re.escape(tech) + r'\b', text, re.IGNORECASE):
                keywords.append(tech)

        # Remove duplicates and clean
        keywords = list(set([k.strip() for k in keywords if k.strip()]))

        return keywords

    def calculate_keyword_match(
        self, resume_keywords: List[str], job_keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate keyword match between resume and job description

        Args:
            resume_keywords: Keywords from resume
            job_keywords: Keywords from job description

        Returns:
            Match analysis
        """
        # Normalize keywords for comparison
        resume_kw_lower = [kw.lower() for kw in resume_keywords]
        job_kw_lower = [kw.lower() for kw in job_keywords]

        # Find matches
        matched = [kw for kw in job_kw_lower if kw in resume_kw_lower]
        missing = [kw for kw in job_kw_lower if kw not in resume_kw_lower]

        # Calculate match score
        match_score = len(matched) / len(job_kw_lower) if job_kw_lower else 0

        return {
            "match_score": round(match_score, 2),
            "matched_keywords": matched,
            "missing_keywords": missing,
            "total_job_keywords": len(job_kw_lower),
            "matched_count": len(matched),
        }

    def extract_key_phrases(self, text: str, top_n: int = 20) -> List[str]:
        """
        Extract key phrases from text

        Args:
            text: Input text
            top_n: Number of top phrases to return

        Returns:
            List of key phrases
        """
        # Simple phrase extraction using n-grams
        words = re.findall(r'\b\w+\b', text.lower())

        # Bigrams and trigrams
        phrases = []
        for i in range(len(words) - 1):
            phrases.append(f"{words[i]} {words[i + 1]}")

        for i in range(len(words) - 2):
            phrases.append(f"{words[i]} {words[i + 1]} {words[i + 2]}")

        # Count frequency
        phrase_counts = {}
        for phrase in phrases:
            phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1

        # Get top phrases
        sorted_phrases = sorted(
            phrase_counts.items(), key=lambda x: x[1], reverse=True
        )

        return [phrase for phrase, count in sorted_phrases[:top_n]]


# Global instance
job_parser = JobDescriptionParser()
