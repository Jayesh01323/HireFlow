"""
Career Fit Score Service

Calculates overall career readiness score based on skills, projects, experience, and education.
Provides detailed breakdown and recommendations for improvement.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class CareerFitScore:
    """Result of career fit score calculation."""
    
    overall_score: float
    skills_score: float
    projects_score: float
    experience_score: float
    education_score: float
    breakdown: Dict[str, Any]
    recommendations: List[str]
    readiness_level: str  # beginner, intermediate, advanced, expert


class CareerFitScoreEngine:
    """Engine for calculating career fit scores."""
    
    def __init__(self) -> None:
        """Initialize career fit score engine."""
        self.skill_weights = {
            "programming_languages": 0.3,
            "frameworks": 0.25,
            "databases": 0.2,
            "tools": 0.15,
            "soft_skills": 0.1,
        }
    
    def calculate_fit_score(
        self,
        skills: List[str],
        projects: List[str],
        experience: List[str],
        education: List[str],
    ) -> CareerFitScore:
        """
        Calculate overall career fit score.
        
        Args:
            skills: List of user skills
            projects: List of project descriptions
            experience: List of work experience
            education: List of education details
            
        Returns:
            CareerFitScore with detailed breakdown
        """
        # Calculate individual component scores
        skills_score = self._calculate_skills_score(skills)
        projects_score = self._calculate_projects_score(projects)
        experience_score = self._calculate_experience_score(experience)
        education_score = self._calculate_education_score(education)
        
        # Calculate overall score (weighted average)
        overall_score = (
            skills_score * 0.4 +
            projects_score * 0.25 +
            experience_score * 0.25 +
            education_score * 0.1
        )
        
        # Determine readiness level
        readiness_level = self._determine_readiness_level(overall_score)
        
        # Generate breakdown
        breakdown = {
            "skills": {
                "score": skills_score,
                "count": len(skills),
                "categories": self._categorize_skills(skills),
            },
            "projects": {
                "score": projects_score,
                "count": len(projects),
                "diversity": self._assess_project_diversity(projects),
            },
            "experience": {
                "score": experience_score,
                "count": len(experience),
                "years": self._estimate_experience_years(experience),
            },
            "education": {
                "score": education_score,
                "count": len(education),
                "level": self._determine_education_level(education),
            },
        }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            skills_score,
            projects_score,
            experience_score,
            education_score,
            skills,
            projects,
        )
        
        return CareerFitScore(
            overall_score=round(overall_score, 1),
            skills_score=round(skills_score, 1),
            projects_score=round(projects_score, 1),
            experience_score=round(experience_score, 1),
            education_score=round(education_score, 1),
            breakdown=breakdown,
            recommendations=recommendations,
            readiness_level=readiness_level,
        )
    
    def _calculate_skills_score(self, skills: List[str]) -> float:
        """Calculate skills score based on quantity and quality."""
        if not skills:
            return 0.0
        
        # Base score from skill count (max 20 skills = 100%)
        count_score = min(len(skills) / 20 * 100, 100)
        
        # Bonus for diverse skill categories
        categories = self._categorize_skills(skills)
        category_bonus = min(len(categories) / 5 * 20, 20)
        
        # Bonus for high-value skills
        high_value_skills = [
            "python", "javascript", "react", "django", "fastapi", "docker",
            "kubernetes", "aws", "machine learning", "tensorflow", "pytorch",
            "sql", "postgresql", "mongodb", "redis", "graphql", "typescript",
        ]
        high_value_count = sum(1 for s in skills if s.lower() in high_value_skills)
        high_value_bonus = min(high_value_count / 5 * 15, 15)
        
        total_score = count_score + category_bonus + high_value_bonus
        return min(total_score, 100)
    
    def _calculate_projects_score(self, projects: List[str]) -> float:
        """Calculate projects score based on quantity and quality."""
        if not projects:
            return 0.0
        
        # Base score from project count (max 10 projects = 100%)
        count_score = min(len(projects) / 10 * 100, 100)
        
        # Bonus for project diversity
        diversity_score = self._assess_project_diversity(projects)
        
        # Bonus for complex projects (based on description length)
        avg_length = sum(len(p.split()) for p in projects) / len(projects) if projects else 0
        complexity_bonus = min(avg_length / 50 * 20, 20)
        
        total_score = (count_score * 0.6) + (diversity_score * 0.2) + (complexity_bonus * 0.2)
        return min(total_score, 100)
    
    def _calculate_experience_score(self, experience: List[str]) -> float:
        """Calculate experience score based on quantity and quality."""
        if not experience:
            return 0.0
        
        # Base score from experience count (max 5 experiences = 100%)
        count_score = min(len(experience) / 5 * 100, 100)
        
        # Bonus for years of experience
        years = self._estimate_experience_years(experience)
        years_bonus = min(years / 5 * 30, 30)
        
        # Bonus for diverse roles
        roles = set()
        for exp in experience:
            words = exp.lower().split()
            role_keywords = ["developer", "engineer", "manager", "lead", "intern", "analyst"]
            for keyword in role_keywords:
                if keyword in words:
                    roles.add(keyword)
        diversity_bonus = min(len(roles) / 3 * 20, 20)
        
        total_score = (count_score * 0.5) + (years_bonus * 0.3) + (diversity_bonus * 0.2)
        return min(total_score, 100)
    
    def _calculate_education_score(self, education: List[str]) -> float:
        """Calculate education score based on level and relevance."""
        if not education:
            return 0.0
        
        # Base score from education count (max 3 = 100%)
        count_score = min(len(education) / 3 * 100, 100)
        
        # Bonus for degree level
        level_score = self._determine_education_level(education)
        level_bonus = {
            "phd": 30,
            "master": 25,
            "bachelor": 20,
            "diploma": 15,
            "certification": 10,
            "other": 5,
        }.get(level_score.lower(), 5)
        
        total_score = (count_score * 0.7) + (level_bonus * 0.3)
        return min(total_score, 100)
    
    def _categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills by domain."""
        categories = {
            "programming_languages": [],
            "frameworks": [],
            "databases": [],
            "tools": [],
            "soft_skills": [],
        }
        
        programming_langs = ["python", "javascript", "java", "go", "rust", "typescript", "c++", "c#", "php"]
        frameworks = ["django", "flask", "fastapi", "react", "vue", "angular", "spring", "express", "next.js"]
        databases = ["sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch"]
        tools = ["docker", "kubernetes", "git", "aws", "azure", "gcp", "terraform", "jenkins"]
        soft_skills = ["communication", "leadership", "teamwork", "problem-solving"]
        
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower in programming_langs:
                categories["programming_languages"].append(skill)
            elif skill_lower in frameworks:
                categories["frameworks"].append(skill)
            elif skill_lower in databases:
                categories["databases"].append(skill)
            elif skill_lower in tools:
                categories["tools"].append(skill)
            elif skill_lower in soft_skills:
                categories["soft_skills"].append(skill)
        
        return {k: v for k, v in categories.items() if v}
    
    def _assess_project_diversity(self, projects: List[str]) -> float:
        """Assess diversity of projects based on technologies used."""
        if not projects:
            return 0.0
        
        # Extract technologies from project descriptions
        tech_keywords = [
            "python", "javascript", "react", "django", "fastapi", "docker",
            "sql", "mongodb", "aws", "machine learning", "api", "web",
            "mobile", "frontend", "backend", "database", "cloud",
        ]
        
        unique_techs = set()
        for project in projects:
            project_lower = project.lower()
            for tech in tech_keywords:
                if tech in project_lower:
                    unique_techs.add(tech)
        
        diversity_score = min(len(unique_techs) / 5 * 100, 100)
        return diversity_score
    
    def _estimate_experience_years(self, experience: List[str]) -> float:
        """Estimate total years of experience from descriptions."""
        total_years = 0.0
        
        for exp in experience:
            exp_lower = exp.lower()
            # Look for year mentions
            import re
            year_matches = re.findall(r'(\d+)\s*years?', exp_lower)
            if year_matches:
                total_years += float(year_matches[0])
            else:
                # Default estimate per experience entry
                total_years += 0.5
        
        return total_years
    
    def _determine_education_level(self, education: List[str]) -> str:
        """Determine highest education level."""
        levels = ["phd", "master", "bachelor", "diploma", "certification"]
        
        for level in levels:
            for edu in education:
                if level in edu.lower():
                    return level
        
        return "other"
    
    def _determine_readiness_level(self, overall_score: float) -> str:
        """Determine career readiness level based on score."""
        if overall_score >= 80:
            return "expert"
        elif overall_score >= 60:
            return "advanced"
        elif overall_score >= 40:
            return "intermediate"
        else:
            return "beginner"
    
    def _generate_recommendations(
        self,
        skills_score: float,
        projects_score: float,
        experience_score: float,
        education_score: float,
        skills: List[str],
        projects: List[str],
    ) -> List[str]:
        """Generate personalized recommendations for improvement."""
        recommendations = []
        
        if skills_score < 60:
            recommendations.append("Focus on learning more diverse skills across different categories")
            if len(skills) < 10:
                recommendations.append("Aim to learn at least 10 relevant skills")
        
        if projects_score < 60:
            recommendations.append("Build more diverse projects to showcase your skills")
            if len(projects) < 5:
                recommendations.append("Aim to complete at least 5 significant projects")
        
        if experience_score < 60:
            recommendations.append("Gain more work experience through internships or freelance work")
            recommendations.append("Consider contributing to open source projects")
        
        if education_score < 60:
            recommendations.append("Consider pursuing relevant certifications or courses")
            recommendations.append("Complete a formal degree or diploma program")
        
        # Specific skill recommendations
        if "python" not in [s.lower() for s in skills]:
            recommendations.append("Learn Python - it's a versatile language with high demand")
        
        if "javascript" not in [s.lower() for s in skills]:
            recommendations.append("Learn JavaScript - essential for web development")
        
        if "docker" not in [s.lower() for s in skills]:
            recommendations.append("Learn Docker - important for modern development workflows")
        
        if len(recommendations) == 0:
            recommendations.append("You have a strong profile! Focus on specialization and advanced skills")
        
        return recommendations[:5]
