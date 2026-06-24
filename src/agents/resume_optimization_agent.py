"""
Resume Optimization Agent

Optimizes user's resume for a selected job using AI analysis.
Provides actionable recommendations to improve resume for specific job applications.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.ai.gemini_client import GeminiClient
from src.matcher import analyze_match
from src.services.skill_categorizer import categorize_skill, SkillCategory

logger = logging.getLogger(__name__)


@dataclass
class ResumeOptimization:
    """Result of resume optimization analysis."""
    
    add_skills: List[str]
    add_projects: List[str]
    rewrite_summary: str
    highlight_experience: List[str]
    ats_improvements: List[str]
    keyword_density: Dict[str, int]
    overall_recommendation: str
    priority_actions: List[str]


class ResumeOptimizationAgent:
    """Agent for optimizing resumes for specific job applications."""
    
    def __init__(self) -> None:
        """Initialize resume optimization agent."""
        self.gemini_client = GeminiClient()
    
    def optimize_resume(
        self,
        resume: Dict[str, Any],
        job: Dict[str, Any],
    ) -> ResumeOptimization:
        """
        Optimize resume for a specific job.
        
        Args:
            resume: Parsed resume data
            job: Job data with description and metadata
            
        Returns:
            ResumeOptimization with actionable recommendations
        """
        try:
            job_description = job.get("description", "")
            job_title = job.get("title", "")
            
            # Perform match analysis
            match_analysis = analyze_match(resume, job_description)
            match_results = match_analysis["match_results"]
            
            # Extract skills
            resume_skills = set(match_analysis["resume_skills"])
            job_skills = set(match_analysis["job_skills"])
            missing_skills = match_results.get("missing_skills", set())
            
            # Generate recommendations
            add_skills = self._recommend_skills_to_add(missing_skills, job_skills)
            add_projects = self._recommend_projects(resume, job, missing_skills)
            rewrite_summary = self._generate_summary_rewrite(resume, job, match_analysis)
            highlight_experience = self._recommend_experience_highlights(resume, job)
            ats_improvements = self._generate_ats_improvements(resume, job, job_description)
            keyword_density = self._analyze_keyword_density(resume, job_description)
            overall_recommendation = self._generate_overall_recommendation(
                match_results, missing_skills, resume_skills, job_skills
            )
            priority_actions = self._prioritize_actions(
                add_skills, add_projects, ats_improvements, match_results
            )
            
            return ResumeOptimization(
                add_skills=add_skills,
                add_projects=add_projects,
                rewrite_summary=rewrite_summary,
                highlight_experience=highlight_experience,
                ats_improvements=ats_improvements,
                keyword_density=keyword_density,
                overall_recommendation=overall_recommendation,
                priority_actions=priority_actions,
            )
            
        except Exception as e:
            logger.error(f"Error optimizing resume: {e}")
            return self._generate_fallback_optimization()
    
    def _recommend_skills_to_add(
        self,
        missing_skills: set,
        job_skills: set,
    ) -> List[str]:
        """Recommend skills to add to resume."""
        # Prioritize missing skills by category importance
        priority_categories = [
            SkillCategory.PROGRAMMING_LANGUAGES,
            SkillCategory.DATABASES,
            SkillCategory.CLOUD,
            SkillCategory.BACKEND,
        ]
        
        prioritized = []
        for category in priority_categories:
            category_skills = [
                skill for skill in missing_skills
                if categorize_skill(skill) == category
            ]
            prioritized.extend(category_skills)
        
        # Add remaining skills
        remaining = [skill for skill in missing_skills if skill not in prioritized]
        prioritized.extend(remaining)
        
        return prioritized[:10]
    
    def _recommend_projects(
        self,
        resume: Dict[str, Any],
        job: Dict[str, Any],
        missing_skills: set,
    ) -> List[str]:
        """Recommend projects to add based on missing skills and job requirements."""
        job_title = job.get("title", "").lower()
        job_description = job.get("description", "").lower()
        
        recommendations = []
        
        # Analyze job type and suggest relevant projects
        if any(term in job_title for term in ["backend", "api", "server"]):
            if "python" in missing_skills or "django" in missing_skills or "fastapi" in missing_skills:
                recommendations.append("Build a REST API using FastAPI or Django with PostgreSQL")
            if "docker" in missing_skills:
                recommendations.append("Containerize a web application using Docker")
        
        if any(term in job_title for term in ["frontend", "ui", "react"]):
            if "react" in missing_skills:
                recommendations.append("Build a responsive React application with state management")
            if "typescript" in missing_skills:
                recommendations.append("Convert an existing JavaScript project to TypeScript")
        
        if any(term in job_title for term in ["data", "ml", "ai"]):
            if "pandas" in missing_skills or "numpy" in missing_skills:
                recommendations.append("Create a data analysis project using Pandas and visualization")
            if "machine learning" in job_description or "ml" in job_description:
                recommendations.append("Build a machine learning model with scikit-learn")
        
        if any(term in job_title for term in ["devops", "cloud"]):
            if "aws" in missing_skills or "cloud" in missing_skills:
                recommendations.append("Deploy an application to AWS using EC2 or Lambda")
            if "kubernetes" in missing_skills:
                recommendations.append("Orchestrate containers using Kubernetes")
        
        # Generic project recommendations based on missing skills
        if len(recommendations) < 3:
            top_missing = list(missing_skills)[:3]
            if top_missing:
                recommendations.append(
                    f"Build a project showcasing: {', '.join(top_missing)}"
                )
        
        return recommendations[:5]
    
    def _generate_summary_rewrite(
        self,
        resume: Dict[str, Any],
        job: Dict[str, Any],
        match_analysis: Dict[str, Any],
    ) -> str:
        """Generate optimized professional summary."""
        job_title = job.get("title", "")
        job_description = job.get("description", "")
        
        # Extract key skills from job
        job_skills = match_analysis["job_skills"][:5]
        
        # Current resume summary (if exists)
        current_summary = resume.get("summary", "")
        
        # Generate optimized summary
        if current_summary:
            optimized = f"{current_summary} "
        else:
            optimized = ""
        
        # Add job-relevant elements
        optimized += f"Skilled professional with expertise in {', '.join(job_skills[:3])}. "
        optimized += f"Seeking {job_title} position to leverage technical skills and experience. "
        optimized += "Proven track record of delivering high-quality solutions and collaborating effectively in team environments."
        
        return optimized
    
    def _recommend_experience_highlights(
        self,
        resume: Dict[str, Any],
        job: Dict[str, Any],
    ) -> List[str]:
        """Recommend experience sections to highlight."""
        job_title = job.get("title", "").lower()
        job_description = job.get("description", "").lower()
        
        highlights = []
        
        # Analyze job requirements
        if "senior" in job_title or "lead" in job_title:
            highlights.append("Highlight leadership experience and team mentoring")
            highlights.append("Emphasize architectural decisions and technical leadership")
        
        if any(term in job_description for term in ["scale", "performance", "optimize"]):
            highlights.append("Showcase performance optimization achievements")
            highlights.append("Highlight experience with scalable systems")
        
        if any(term in job_description for term in ["agile", "scrum", "team"]):
            highlights.append("Emphasize collaboration and cross-functional teamwork")
            highlights.append("Highlight agile development experience")
        
        if any(term in job_description for term in ["database", "sql", "data"]):
            highlights.append("Showcase database design and optimization experience")
        
        # Generic highlights
        highlights.append("Quantify achievements with metrics and results")
        highlights.append("Highlight problem-solving and technical challenges overcome")
        
        return highlights[:5]
    
    def _generate_ats_improvements(
        self,
        resume: Dict[str, Any],
        job: Dict[str, Any],
        job_description: str,
    ) -> List[str]:
        """Generate ATS-specific improvements."""
        improvements = []
        
        # Extract keywords from job description
        job_keywords = self._extract_ats_keywords(job_description)
        
        # Check for keyword presence
        resume_text = str(resume).lower()
        missing_keywords = [kw for kw in job_keywords if kw.lower() not in resume_text]
        
        if missing_keywords:
            improvements.append(
                f"Add these keywords from job description: {', '.join(missing_keywords[:5])}"
            )
        
        # Format improvements
        improvements.append("Use standard section headings: Experience, Education, Skills")
        improvements.append("Avoid tables, graphics, and complex formatting")
        improvements.append("Include full job titles and company names")
        improvements.append("List skills in both bullet points and dedicated skills section")
        
        return improvements[:5]
    
    def _extract_ats_keywords(self, job_description: str) -> List[str]:
        """Extract important ATS keywords from job description."""
        # Common technical keywords to look for
        technical_keywords = [
            "python", "java", "javascript", "react", "node.js", "sql",
            "docker", "kubernetes", "aws", "azure", "git", "agile",
            "scrum", "api", "rest", "graphql", "microservices",
        ]
        
        found_keywords = []
        description_lower = job_description.lower()
        
        for keyword in technical_keywords:
            if keyword in description_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _analyze_keyword_density(
        self,
        resume: Dict[str, Any],
        job_description: str,
    ) -> Dict[str, int]:
        """Analyze keyword density in resume compared to job description."""
        job_keywords = self._extract_ats_keywords(job_description)
        
        resume_text = str(resume).lower()
        density = {}
        
        for keyword in job_keywords:
            count = resume_text.count(keyword.lower())
            density[keyword] = count
        
        return density
    
    def _generate_overall_recommendation(
        self,
        match_results: Dict[str, Any],
        missing_skills: set,
        resume_skills: set,
        job_skills: set,
    ) -> str:
        """Generate overall optimization recommendation."""
        match_score = match_results.get("weighted_match_percentage", 0)
        missing_count = len(missing_skills)
        total_job_skills = len(job_skills)
        
        if match_score >= 80:
            base = "Your resume is well-aligned with this job. "
        elif match_score >= 60:
            base = "Your resume shows good potential for this role. "
        elif match_score >= 40:
            base = "Your resume needs some improvements for this position. "
        else:
            base = "Your resume requires significant optimization for this role. "
        
        if missing_count > 0:
            gap_pct = (missing_count / total_job_skills * 100) if total_job_skills > 0 else 0
            base += f"You're missing {missing_count} out of {total_job_skills} key skills ({gap_pct:.0f}%). "
        
        base += "Focus on adding missing skills, relevant projects, and optimizing for ATS systems to increase your chances."
        
        return base
    
    def _prioritize_actions(
        self,
        add_skills: List[str],
        add_projects: List[str],
        ats_improvements: List[str],
        match_results: Dict[str, Any],
    ) -> List[str]:
        """Prioritize optimization actions."""
        actions = []
        
        # High priority: Critical missing skills
        if add_skills:
            actions.append(f"Add top missing skills: {', '.join(add_skills[:3])}")
        
        # High priority: ATS improvements
        if ats_improvements:
            actions.append(ats_improvements[0])
        
        # Medium priority: Projects
        if add_projects:
            actions.append(f"Build project: {add_projects[0]}")
        
        # Medium priority: Experience highlights
        actions.append("Highlight relevant experience with quantifiable achievements")
        
        # Low priority: Summary rewrite
        actions.append("Optimize professional summary for the role")
        
        return actions[:5]
    
    def _generate_fallback_optimization(self) -> ResumeOptimization:
        """Generate fallback optimization when analysis fails."""
        return ResumeOptimization(
            add_skills=["Unable to analyze"],
            add_projects=["Unable to analyze"],
            rewrite_summary="Unable to generate optimized summary",
            highlight_experience=["Unable to analyze"],
            ats_improvements=["Unable to analyze"],
            keyword_density={},
            overall_recommendation="Please try again with complete resume and job data",
            priority_actions=["Please provide complete data"],
        )
