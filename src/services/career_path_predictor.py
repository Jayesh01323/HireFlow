"""
Career Path Predictor Service

Predicts career trajectory based on skills, projects, and experience.
Identifies growth opportunities and alternative career paths.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class CareerPath:
    """Represents a career path option."""
    
    title: str
    description: str
    fit_score: float
    required_skills: List[str]
    missing_skills: List[str]
    growth_potential: str  # high, medium, low
    salary_range: str
    time_to_reach: str


@dataclass
class CareerPrediction:
    """Result of career path prediction."""
    
    top_career_path: str
    alternative_paths: List[CareerPath]
    growth_opportunities: List[str]
    recommended_next_steps: List[str]
    career_trajectory: List[str]


class CareerPathPredictor:
    """Predictor for career paths based on user profile."""
    
    def __init__(self) -> None:
        """Initialize career path predictor."""
        self.career_paths = self._load_career_paths()
    
    def _load_career_paths(self) -> Dict[str, Dict[str, Any]]:
        """Load career path definitions."""
        return {
            "Full Stack Developer": {
                "description": "Builds both frontend and backend applications",
                "required_skills": ["javascript", "react", "node.js", "sql", "git"],
                "optional_skills": ["typescript", "docker", "aws", "graphql"],
                "growth_potential": "high",
                "salary_range": "₹8-25 LPA",
                "time_to_reach": "2-4 years",
                "next_paths": ["Tech Lead", "Engineering Manager", "Solution Architect"],
            },
            "Backend Developer": {
                "description": "Builds server-side applications and APIs",
                "required_skills": ["python", "django", "sql", "git"],
                "optional_skills": ["fastapi", "postgresql", "redis", "docker", "kubernetes"],
                "growth_potential": "high",
                "salary_range": "₹6-20 LPA",
                "time_to_reach": "1-3 years",
                "next_paths": ["Senior Backend Engineer", "Tech Lead", "DevOps Engineer"],
            },
            "Frontend Developer": {
                "description": "Builds user interfaces and web applications",
                "required_skills": ["javascript", "html", "css", "react"],
                "optional_skills": ["typescript", "vue", "angular", "next.js", "tailwind"],
                "growth_potential": "high",
                "salary_range": "₹6-18 LPA",
                "time_to_reach": "1-3 years",
                "next_paths": ["Senior Frontend Engineer", "UI/UX Engineer", "Full Stack Developer"],
            },
            "Data Scientist": {
                "description": "Analyzes data and builds machine learning models",
                "required_skills": ["python", "pandas", "numpy", "sql"],
                "optional_skills": ["scikit-learn", "tensorflow", "pytorch", "machine learning"],
                "growth_potential": "high",
                "salary_range": "₹8-30 LPA",
                "time_to_reach": "2-4 years",
                "next_paths": ["Senior Data Scientist", "ML Engineer", "Data Science Manager"],
            },
            "Machine Learning Engineer": {
                "description": "Builds and deploys machine learning systems",
                "required_skills": ["python", "numpy", "scikit-learn"],
                "optional_skills": ["tensorflow", "pytorch", "docker", "kubernetes", "aws"],
                "growth_potential": "high",
                "salary_range": "₹10-35 LPA",
                "time_to_reach": "3-5 years",
                "next_paths": ["Senior ML Engineer", "AI Research Engineer", "ML Platform Engineer"],
            },
            "DevOps Engineer": {
                "description": "Manages infrastructure and deployment pipelines",
                "required_skills": ["git", "docker", "linux", "aws"],
                "optional_skills": ["kubernetes", "terraform", "ci/cd", "jenkins", "ansible"],
                "growth_potential": "high",
                "salary_range": "₹8-25 LPA",
                "time_to_reach": "2-4 years",
                "next_paths": ["Senior DevOps Engineer", "SRE Engineer", "Cloud Architect"],
            },
            "Cloud Architect": {
                "description": "Designs and manages cloud infrastructure",
                "required_skills": ["aws", "docker", "networking"],
                "optional_skills": ["kubernetes", "terraform", "azure", "gcp", "microservices"],
                "growth_potential": "high",
                "salary_range": "₹15-40 LPA",
                "time_to_reach": "4-6 years",
                "next_paths": ["Principal Cloud Architect", "CTO", "Enterprise Architect"],
            },
            "Mobile Developer": {
                "description": "Builds mobile applications for iOS and Android",
                "required_skills": ["javascript", "react"],
                "optional_skills": ["react native", "flutter", "swift", "kotlin", "mobile"],
                "growth_potential": "medium",
                "salary_range": "₹6-20 LPA",
                "time_to_reach": "1-3 years",
                "next_paths": ["Senior Mobile Developer", "Mobile Lead", "Full Stack Developer"],
            },
            "Software Engineer": {
                "description": "General software development role",
                "required_skills": ["python", "javascript", "git", "sql"],
                "optional_skills": ["react", "django", "docker", "aws"],
                "growth_potential": "medium",
                "salary_range": "₹5-15 LPA",
                "time_to_reach": "1-2 years",
                "next_paths": ["Senior Software Engineer", "Full Stack Developer", "Backend Developer"],
            },
            "QA Engineer": {
                "description": "Ensures software quality through testing",
                "required_skills": ["python", "testing"],
                "optional_skills": ["selenium", "automation", "api testing", "performance testing"],
                "growth_potential": "medium",
                "salary_range": "₹4-12 LPA",
                "time_to_reach": "1-2 years",
                "next_paths": ["Senior QA Engineer", "SDET", "QA Lead"],
            },
            "Product Manager": {
                "description": "Manages product development and strategy",
                "required_skills": ["communication", "analysis"],
                "optional_skills": ["agile", "scrum", "data analysis", "user research"],
                "growth_potential": "high",
                "salary_range": "₹10-35 LPA",
                "time_to_reach": "3-5 years",
                "next_paths": ["Senior Product Manager", "Product Director", "VP Product"],
            },
            "Technical Writer": {
                "description": "Creates technical documentation and content",
                "required_skills": ["writing", "communication"],
                "optional_skills": ["markdown", "api documentation", "technical concepts"],
                "growth_potential": "medium",
                "salary_range": "₹4-12 LPA",
                "time_to_reach": "1-2 years",
                "next_paths": ["Senior Technical Writer", "Developer Advocate", "Content Lead"],
            },
        }
    
    def predict_career_path(
        self,
        skills: List[str],
        projects: List[str],
        experience: List[str],
    ) -> CareerPrediction:
        """
        Predict career path based on user profile.
        
        Args:
            skills: List of user skills
            projects: List of project descriptions
            experience: List of work experience
            
        Returns:
            CareerPrediction with top path and alternatives
        """
        skills_lower = [s.lower() for s in skills]
        
        # Calculate fit scores for each career path
        career_scores = []
        for career_title, career_info in self.career_paths.items():
            fit_score = self._calculate_fit_score(
                skills_lower,
                career_info["required_skills"],
                career_info["optional_skills"],
            )
            
            missing_required = [
                s for s in career_info["required_skills"]
                if s.lower() not in skills_lower
            ]
            
            career_path = CareerPath(
                title=career_title,
                description=career_info["description"],
                fit_score=fit_score,
                required_skills=career_info["required_skills"],
                missing_skills=missing_required,
                growth_potential=career_info["growth_potential"],
                salary_range=career_info["salary_range"],
                time_to_reach=career_info["time_to_reach"],
            )
            career_scores.append(career_path)
        
        # Sort by fit score
        career_scores.sort(key=lambda x: x.fit_score, reverse=True)
        
        # Get top career path
        top_path = career_scores[0] if career_scores else None
        
        # Get alternative paths (top 5)
        alternative_paths = career_scores[1:6] if len(career_scores) > 1 else []
        
        # Generate growth opportunities
        growth_opportunities = self._generate_growth_opportunities(
            skills_lower,
            projects,
            experience,
        )
        
        # Generate recommended next steps
        recommended_next_steps = self._generate_next_steps(
            skills_lower,
            top_path if top_path else None,
        )
        
        # Generate career trajectory
        career_trajectory = self._generate_career_trajectory(
            top_path.title if top_path else "Software Engineer",
            self.career_paths.get(top_path.title if top_path else "Software Engineer", {}),
        )
        
        return CareerPrediction(
            top_career_path=top_path.title if top_path else "Software Engineer",
            alternative_paths=alternative_paths,
            growth_opportunities=growth_opportunities,
            recommended_next_steps=recommended_next_steps,
            career_trajectory=career_trajectory,
        )
    
    def _calculate_fit_score(
        self,
        user_skills: List[str],
        required_skills: List[str],
        optional_skills: List[str],
    ) -> float:
        """Calculate fit score for a career path."""
        required_lower = [s.lower() for s in required_skills]
        optional_lower = [s.lower() for s in optional_skills]
        
        # Calculate required skills match (70% weight)
        required_match = sum(1 for s in required_lower if s in user_skills)
        required_score = (required_match / len(required_lower) * 70) if required_lower else 0
        
        # Calculate optional skills match (30% weight)
        optional_match = sum(1 for s in optional_lower if s in user_skills)
        optional_score = (optional_match / len(optional_lower) * 30) if optional_lower else 0
        
        return round(required_score + optional_score, 1)
    
    def _generate_growth_opportunities(
        self,
        skills: List[str],
        projects: List[str],
        experience: List[str],
    ) -> List[str]:
        """Generate growth opportunities based on profile."""
        opportunities = []
        
        # Analyze skills for growth areas
        if "python" in skills and "machine learning" not in skills:
            opportunities.append("Transition to Data Science by learning ML frameworks")
        
        if "javascript" in skills and "react" in skills and "node.js" not in skills:
            opportunities.append("Expand to Full Stack by learning Node.js")
        
        if "docker" in skills and "kubernetes" not in skills:
            opportunities.append("Advance to DevOps by learning Kubernetes")
        
        if "python" in skills and "django" in skills and "fastapi" not in skills:
            opportunities.append("Modernize backend skills with FastAPI")
        
        # Analyze projects
        if len(projects) < 3:
            opportunities.append("Build more diverse projects to showcase skills")
        
        # Analyze experience
        if len(experience) == 0:
            opportunities.append("Gain internship or freelance experience")
        
        # General growth opportunities
        if len(opportunities) < 3:
            opportunities.extend([
                "Contribute to open source projects",
                "Build a portfolio website",
                "Write technical blog posts",
                "Participate in hackathons",
            ])
        
        return opportunities[:5]
    
    def _generate_next_steps(
        self,
        skills: List[str],
        top_path: Optional[CareerPath],
    ) -> List[str]:
        """Generate recommended next steps."""
        next_steps = []
        
        if top_path and top_path.missing_skills:
            for skill in top_path.missing_skills[:3]:
                next_steps.append(f"Learn {skill.title()}")
        
        if not next_steps:
            next_steps.extend([
                "Build a project in your target field",
                "Get certified in your primary technology",
                "Network with professionals in the field",
            ])
        
        return next_steps
    
    def _generate_career_trajectory(
        self,
        current_path: str,
        career_info: Dict[str, Any],
    ) -> List[str]:
        """Generate career trajectory for the next 5 years."""
        trajectory = [current_path]
        
        next_paths = career_info.get("next_paths", [])
        for i, path in enumerate(next_paths[:3]):
            trajectory.append(f"Year {i+2}: {path}")
        
        return trajectory
