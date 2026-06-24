"""
Career Fit Engine Service

Predicts best career paths based on skills, projects, experience, and education.
Supports multiple career tracks and provides scoring and recommendations.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

from src.services.skill_categorizer import categorize_skill, SkillCategory

logger = logging.getLogger(__name__)


# Supported career tracks with their required skill patterns
CAREER_TRACKS = {
    "Backend Developer": {
        "core_skills": {
            SkillCategory.PROGRAMMING_LANGUAGES: ["Python", "Java", "Node.js", "Go"],
            SkillCategory.BACKEND: ["API", "REST", "Microservices", "Django", "Flask", "FastAPI", "Spring"],
            SkillCategory.DATABASES: ["SQL", "PostgreSQL", "MongoDB", "Redis"],
        },
        "weight": 1.0,
    },
    "Frontend Developer": {
        "core_skills": {
            SkillCategory.PROGRAMMING_LANGUAGES: ["JavaScript", "TypeScript"],
            SkillCategory.FRONTEND: ["React", "Vue", "Angular", "HTML", "CSS", "Next.js"],
        },
        "weight": 1.0,
    },
    "Full Stack Developer": {
        "core_skills": {
            SkillCategory.PROGRAMMING_LANGUAGES: ["Python", "JavaScript", "TypeScript", "Java"],
            SkillCategory.FRONTEND: ["React", "Vue", "Angular"],
            SkillCategory.BACKEND: ["API", "REST", "Node.js", "Django", "Flask"],
            SkillCategory.DATABASES: ["SQL", "PostgreSQL", "MongoDB"],
        },
        "weight": 1.0,
    },
    "Python Developer": {
        "core_skills": {
            SkillCategory.PROGRAMMING_LANGUAGES: ["Python"],
            SkillCategory.BACKEND: ["Django", "Flask", "FastAPI"],
            SkillCategory.DATABASES: ["SQL", "PostgreSQL"],
            SkillCategory.DATA_SCIENCE: ["Pandas", "NumPy"],
        },
        "weight": 1.0,
    },
    "Software Engineer": {
        "core_skills": {
            SkillCategory.PROGRAMMING_LANGUAGES: ["Python", "Java", "JavaScript", "C++", "Go"],
            SkillCategory.BACKEND: ["API", "REST", "Microservices"],
            SkillCategory.DATABASES: ["SQL", "PostgreSQL", "MongoDB"],
            SkillCategory.DEVOPS: ["Git", "Docker", "CI/CD"],
        },
        "weight": 1.0,
    },
    "Data Analyst": {
        "core_skills": {
            SkillCategory.PROGRAMMING_LANGUAGES: ["Python", "R", "SQL"],
            SkillCategory.DATA_SCIENCE: ["Pandas", "NumPy", "Excel"],
            SkillCategory.DATABASES: ["SQL", "PostgreSQL", "MySQL"],
        },
        "weight": 1.0,
    },
    "Data Scientist": {
        "core_skills": {
            SkillCategory.PROGRAMMING_LANGUAGES: ["Python", "R"],
            SkillCategory.DATA_SCIENCE: ["Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch"],
            SkillCategory.DATABASES: ["SQL", "PostgreSQL", "MongoDB"],
        },
        "weight": 1.0,
    },
    "AI Engineer": {
        "core_skills": {
            SkillCategory.PROGRAMMING_LANGUAGES: ["Python"],
            SkillCategory.DATA_SCIENCE: ["TensorFlow", "PyTorch", "Scikit-learn", "Machine Learning"],
            SkillCategory.CLOUD: ["AWS", "GCP", "Azure"],
        },
        "weight": 1.0,
    },
    "ML Engineer": {
        "core_skills": {
            SkillCategory.PROGRAMMING_LANGUAGES: ["Python"],
            SkillCategory.DATA_SCIENCE: ["TensorFlow", "PyTorch", "Scikit-learn", "Machine Learning"],
            SkillCategory.DEVOPS: ["Docker", "Kubernetes", "MLOps"],
        },
        "weight": 1.0,
    },
    "Cloud Engineer": {
        "core_skills": {
            SkillCategory.CLOUD: ["AWS", "Azure", "GCP"],
            SkillCategory.DEVOPS: ["Docker", "Kubernetes", "Terraform", "CI/CD"],
            SkillCategory.PROGRAMMING_LANGUAGES: ["Python", "Go"],
        },
        "weight": 1.0,
    },
    "DevOps Engineer": {
        "core_skills": {
            SkillCategory.DEVOPS: ["Docker", "Kubernetes", "CI/CD", "Jenkins", "Git"],
            SkillCategory.CLOUD: ["AWS", "Azure", "GCP"],
            SkillCategory.PROGRAMMING_LANGUAGES: ["Python", "Bash", "Go"],
        },
        "weight": 1.0,
    },
    "QA Engineer": {
        "core_skills": {
            SkillCategory.TESTING: ["Selenium", "Cypress", "Jest", "Testing"],
            SkillCategory.PROGRAMMING_LANGUAGES: ["Python", "JavaScript", "Java"],
        },
        "weight": 1.0,
    },
    "Cyber Security Engineer": {
        "core_skills": {
            SkillCategory.DEVOPS: ["Security", "Network Security", "Penetration Testing"],
            SkillCategory.CLOUD: ["AWS", "Azure", "GCP"],
            SkillCategory.PROGRAMMING_LANGUAGES: ["Python", "Bash"],
        },
        "weight": 1.0,
    },
    "Prompt Engineer": {
        "core_skills": {
            SkillCategory.DATA_SCIENCE: ["Machine Learning", "AI", "NLP"],
            SkillCategory.PROGRAMMING_LANGUAGES: ["Python"],
        },
        "weight": 1.0,
    },
    "Automation Engineer": {
        "core_skills": {
            SkillCategory.PROGRAMMING_LANGUAGES: ["Python", "JavaScript", "Bash"],
            SkillCategory.DEVOPS: ["CI/CD", "Jenkins", "Docker"],
            SkillCategory.TESTING: ["Selenium", "Testing"],
        },
        "weight": 1.0,
    },
}


@dataclass
class CareerFitScore:
    """Result of career fit analysis for a single career track."""
    
    career_name: str
    score: float
    skills_match: Dict[str, Any]
    projects_match: float
    experience_match: float
    recommendations: List[str]
    missing_requirements: List[str]
    growth_opportunities: List[str]


@dataclass
class CareerFitAnalysis:
    """Complete career fit analysis across all tracks."""
    
    top_career_path: str
    career_scores: Dict[str, float]
    top_5_careers: List[tuple[str, float]]
    detailed_scores: Dict[str, CareerFitScore]
    radar_chart_data: Dict[str, List[float]]
    overall_recommendations: List[str]


class CareerFitEngine:
    """Engine for predicting best career paths based on user profile."""
    
    def __init__(self) -> None:
        """Initialize career fit engine."""
        self.career_tracks = CAREER_TRACKS
    
    def analyze_career_fit(
        self,
        resume: Dict[str, Any],
    ) -> CareerFitAnalysis:
        """
        Analyze career fit across all supported career tracks.
        
        Args:
            resume: Parsed resume data with skills, projects, experience, education
            
        Returns:
            CareerFitAnalysis with complete analysis
        """
        try:
            # Extract resume components
            skills = self._extract_skills(resume)
            projects = resume.get("projects", [])
            experience = resume.get("experience", [])
            education = resume.get("education", [])
            
            # Calculate scores for each career track
            career_scores = {}
            detailed_scores = {}
            
            for career_name, career_config in self.career_tracks.items():
                score_data = self._calculate_career_score(
                    skills,
                    projects,
                    experience,
                    education,
                    career_name,
                    career_config,
                )
                career_scores[career_name] = score_data.score
                detailed_scores[career_name] = score_data
            
            # Find top career path
            sorted_careers = sorted(career_scores.items(), key=lambda x: x[1], reverse=True)
            top_career_path = sorted_careers[0][0] if sorted_careers else "Unknown"
            top_5_careers = sorted_careers[:5]
            
            # Generate radar chart data
            radar_chart_data = self._generate_radar_chart_data(detailed_scores)
            
            # Generate overall recommendations
            overall_recommendations = self._generate_overall_recommendations(
                top_career_path,
                detailed_scores[top_career_path] if top_career_path in detailed_scores else None,
                skills,
            )
            
            return CareerFitAnalysis(
                top_career_path=top_career_path,
                career_scores=career_scores,
                top_5_careers=top_5_careers,
                detailed_scores=detailed_scores,
                radar_chart_data=radar_chart_data,
                overall_recommendations=overall_recommendations,
            )
            
        except Exception as e:
            logger.error(f"Error analyzing career fit: {e}")
            return self._generate_fallback_analysis()
    
    def _extract_skills(self, resume: Dict[str, Any]) -> Set[str]:
        """Extract skills from resume."""
        skills_data = resume.get("skills", [])
        skills = set()
        
        for skill in skills_data:
            if isinstance(skill, str):
                skills.add(skill)
            elif isinstance(skill, dict):
                skills.add(skill.get("name", ""))
        
        return skills
    
    def _calculate_career_score(
        self,
        skills: Set[str],
        projects: List[str],
        experience: List[str],
        education: List[str],
        career_name: str,
        career_config: Dict[str, Any],
    ) -> CareerFitScore:
        """Calculate fit score for a specific career track."""
        core_skills = career_config["core_skills"]
        
        # Calculate skills match
        skills_match = self._calculate_skills_match(skills, core_skills)
        skills_score = skills_match["overall_score"]
        
        # Calculate projects match
        projects_score = self._calculate_projects_match(projects, career_name)
        
        # Calculate experience match
        experience_score = self._calculate_experience_match(experience, career_name)
        
        # Calculate education match
        education_score = self._calculate_education_match(education, career_name)
        
        # Overall score (weighted)
        overall_score = (
            skills_score * 0.5 +
            projects_score * 0.2 +
            experience_score * 0.2 +
            education_score * 0.1
        )
        
        # Generate recommendations
        recommendations = self._generate_career_recommendations(
            skills_match,
            projects_score,
            experience_score,
            career_name,
        )
        
        # Identify missing requirements
        missing_requirements = self._identify_missing_requirements(
            skills,
            core_skills,
        )
        
        # Identify growth opportunities
        growth_opportunities = self._identify_growth_opportunities(
            skills,
            career_name,
            missing_requirements,
        )
        
        return CareerFitScore(
            career_name=career_name,
            score=round(overall_score, 1),
            skills_match=skills_match,
            projects_match=projects_score,
            experience_match=experience_score,
            recommendations=recommendations,
            missing_requirements=missing_requirements,
            growth_opportunities=growth_opportunities,
        )
    
    def _calculate_skills_match(
        self,
        user_skills: Set[str],
        core_skills: Dict[SkillCategory, List[str]],
    ) -> Dict[str, Any]:
        """Calculate skills match score by category."""
        category_scores = {}
        total_required = 0
        total_matched = 0
        
        for category, required_skills in core_skills.items():
            matched = 0
            for req_skill in required_skills:
                total_required += 1
                # Check if user has this skill (case-insensitive)
                if any(req_skill.lower() in skill.lower() for skill in user_skills):
                    matched += 1
                    total_matched += 1
            
            category_score = (matched / len(required_skills) * 100) if required_skills else 0
            category_scores[category.value] = {
                "score": round(category_score, 1),
                "matched": matched,
                "required": len(required_skills),
            }
        
        overall_score = (total_matched / total_required * 100) if total_required > 0 else 0
        
        return {
            "overall_score": round(overall_score, 1),
            "category_breakdown": category_scores,
        }
    
    def _calculate_projects_match(self, projects: List[str], career_name: str) -> float:
        """Calculate projects match score for career."""
        if not projects:
            return 0.0
        
        career_keywords = career_name.lower().split()
        relevant_projects = 0
        
        for project in projects:
            project_lower = project.lower()
            if any(keyword in project_lower for keyword in career_keywords):
                relevant_projects += 1
        
        return (relevant_projects / len(projects) * 100) if projects else 0.0
    
    def _calculate_experience_match(self, experience: List[str], career_name: str) -> float:
        """Calculate experience match score for career."""
        if not experience:
            return 0.0
        
        career_keywords = career_name.lower().split()
        relevant_experience = 0
        
        for exp in experience:
            exp_lower = exp.lower()
            if any(keyword in exp_lower for keyword in career_keywords):
                relevant_experience += 1
        
        return (relevant_experience / len(experience) * 100) if experience else 0.0
    
    def _calculate_education_match(self, education: List[str], career_name: str) -> float:
        """Calculate education match score for career."""
        if not education:
            return 50.0  # Neutral score
        
        career_keywords = career_name.lower().split()
        relevant_education = 0
        
        for edu in education:
            edu_lower = edu.lower()
            if any(keyword in edu_lower for keyword in career_keywords):
                relevant_education += 1
        
        return (relevant_education / len(education) * 100) if education else 50.0
    
    def _generate_career_recommendations(
        self,
        skills_match: Dict[str, Any],
        projects_score: float,
        experience_score: float,
        career_name: str,
    ) -> List[str]:
        """Generate career-specific recommendations."""
        recommendations = []
        
        skills_score = skills_match["overall_score"]
        
        if skills_score >= 80:
            recommendations.append(f"Strong foundation for {career_name}. Focus on advanced skills.")
        elif skills_score >= 60:
            recommendations.append(f"Good potential for {career_name}. Strengthen core skills.")
        else:
            recommendations.append(f"Significant skill development needed for {career_name}.")
        
        if projects_score < 50:
            recommendations.append(f"Build more {career_name}-related projects to demonstrate expertise.")
        
        if experience_score < 50:
            recommendations.append(f"Gain more {career_name}-specific experience through internships or projects.")
        
        return recommendations[:3]
    
    def _identify_missing_requirements(
        self,
        user_skills: Set[str],
        core_skills: Dict[SkillCategory, List[str]],
    ) -> List[str]:
        """Identify missing requirements for a career track."""
        missing = []
        
        for category, required_skills in core_skills.items():
            for req_skill in required_skills:
                if not any(req_skill.lower() in skill.lower() for skill in user_skills):
                    missing.append(req_skill)
        
        return missing[:10]
    
    def _identify_growth_opportunities(
        self,
        skills: Set[str],
        career_name: str,
        missing_requirements: List[str],
    ) -> List[str]:
        """Identify growth opportunities for a career track."""
        opportunities = []
        
        if missing_requirements:
            opportunities.append(f"Learn top missing skills: {', '.join(missing_requirements[:3])}")
        
        opportunities.append(f"Build portfolio projects specific to {career_name}")
        opportunities.append(f"Consider certifications for {career_name}")
        opportunities.append(f"Network with professionals in {career_name}")
        
        return opportunities[:4]
    
    def _generate_radar_chart_data(
        self,
        detailed_scores: Dict[str, CareerFitScore],
    ) -> Dict[str, List[float]]:
        """Generate radar chart data for top careers."""
        # Get top 5 careers
        top_careers = sorted(
            detailed_scores.items(),
            key=lambda x: x[1].score,
            reverse=True,
        )[:5]
        
        # Dimensions for radar chart
        dimensions = ["Skills", "Projects", "Experience", "Education"]
        
        radar_data = {}
        for career_name, score_data in top_careers:
            radar_data[career_name] = [
                score_data.skills_match["overall_score"],
                score_data.projects_match,
                score_data.experience_match,
                50.0,  # Education score placeholder (not calculated in detail)
            ]
        
        return radar_data
    
    def _generate_overall_recommendations(
        self,
        top_career: str,
        top_score: Optional[CareerFitScore],
        skills: Set[str],
    ) -> List[str]:
        """Generate overall career recommendations."""
        recommendations = []
        
        if top_score:
            if top_score.score >= 80:
                recommendations.append(
                    f"Your profile strongly aligns with {top_career}. You're well-positioned for this career path."
                )
            elif top_score.score >= 60:
                recommendations.append(
                    f"Your profile shows good potential for {top_career}. Focus on strengthening core skills."
                )
            else:
                recommendations.append(
                    f"Consider {top_career} but invest in skill development first."
                )
        
        if len(skills) > 10:
            recommendations.append("Your diverse skill set opens multiple career opportunities.")
        else:
            recommendations.append("Expand your skill set to increase career options.")
        
        recommendations.append("Build a portfolio of projects to demonstrate your capabilities.")
        recommendations.append("Consider internships or freelance work to gain practical experience.")
        
        return recommendations[:5]
    
    def _generate_fallback_analysis(self) -> CareerFitAnalysis:
        """Generate fallback analysis when calculation fails."""
        return CareerFitAnalysis(
            top_career_path="Unable to Determine",
            career_scores={},
            top_5_careers=[],
            detailed_scores={},
            radar_chart_data={},
            overall_recommendations=["Please provide complete resume data for analysis"],
        )
