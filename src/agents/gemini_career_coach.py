"""
Gemini Career Coach Agent

Provides AI-powered career coaching using the Gemini API.
Integrates with career intelligence services for context-aware advice.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from src.ai.gemini_client import GeminiClient
from src.services.career_fit_score import CareerFitScoreEngine
from src.services.career_path_predictor import CareerPathPredictor
from src.services.course_recommender import CourseRecommender
from src.services.roadmap_generator import RoadmapGenerator
from src.services.skill_gap_engine import SkillGapEngine
from src.utils import get_env, load_env

logger = logging.getLogger(__name__)

load_env()


class GeminiCareerCoach:
    """AI Career Coach powered by Gemini API."""
    
    def __init__(self) -> None:
        """Initialize Gemini Career Coach."""
        self.gemini_client = GeminiClient()
        self.skill_gap_engine = SkillGapEngine()
        self.roadmap_generator = RoadmapGenerator()
        self.course_recommender = CourseRecommender()
        self.career_predictor = CareerPathPredictor()
        self.career_fit_score = CareerFitScoreEngine()
    
    def get_career_advice(
        self,
        question: str,
        skills: List[str],
        projects: List[str],
        experience: List[str],
        education: List[str],
    ) -> str:
        """
        Get career advice based on user profile and question.
        
        Args:
            question: User's career question
            skills: List of user skills
            projects: List of project descriptions
            experience: List of work experience
            education: List of education details
            
        Returns:
            AI-generated career advice
        """
        # Build context from user profile
        context = self._build_career_context(
            skills, projects, experience, education
        )
        
        # Generate prompt
        prompt = self._build_career_advice_prompt(question, context)
        
        # Get response from Gemini
        response = self.gemini_client.generate_response(prompt)
        
        return response
    
    def _build_career_context(
        self,
        skills: List[str],
        projects: List[str],
        experience: List[str],
        education: List[str],
    ) -> Dict[str, Any]:
        """Build comprehensive career context from user profile."""
        context = {
            "skills": skills,
            "skill_count": len(skills),
            "projects": projects,
            "project_count": len(projects),
            "experience": experience,
            "experience_count": len(experience),
            "education": education,
            "education_count": len(education),
        }
        
        # Add career fit score
        fit_score = self.career_fit_score.calculate_fit_score(
            skills=skills,
            projects=projects,
            experience=experience,
            education=education,
        )
        context["career_fit_score"] = fit_score.overall_score
        context["readiness_level"] = fit_score.readiness_level
        
        # Add career path prediction
        career_prediction = self.career_predictor.predict_career_path(
            skills=skills,
            projects=projects,
            experience=experience,
        )
        context["top_career_path"] = career_prediction.top_career_path
        context["alternative_paths"] = [p.title for p in career_prediction.alternative_paths[:3]]
        context["growth_opportunities"] = career_prediction.growth_opportunities
        
        return context
    
    def _build_career_advice_prompt(
        self,
        question: str,
        context: Dict[str, Any],
    ) -> str:
        """Build prompt for career advice generation."""
        prompt = f"""
You are an expert Career Coach with deep knowledge of the tech industry, career development, and skill acquisition.

USER PROFILE:
- Skills: {', '.join(context['skills'][:10])}... (Total: {context['skill_count']} skills)
- Projects: {context['project_count']} projects
- Experience: {context['experience_count']} work experiences
- Education: {context['education_count']} education entries
- Career Readiness Score: {context['career_fit_score']}% ({context['readiness_level']})
- Top Career Path: {context['top_career_path']}
- Alternative Paths: {', '.join(context['alternative_paths'])}
- Growth Opportunities: {', '.join(context['growth_opportunities'][:3])}

USER QUESTION:
{question}

Provide a comprehensive, actionable, and personalized career advice response. Your response should:
1. Directly address the user's question
2. Consider their current skill level and career readiness
3. Provide specific, actionable steps they can take
4. Be encouraging but realistic
5. Reference their specific skills and experience when relevant
6. Suggest concrete next steps with timelines when appropriate

Keep your response concise (under 300 words) and focused on practical advice.
"""
        return prompt
    
    def get_interview_preparation(
        self,
        job_title: str,
        job_description: str,
        skills: List[str],
    ) -> Dict[str, Any]:
        """
        Get interview preparation guidance for a specific job.
        
        Args:
            job_title: Target job title
            job_description: Job description
            skills: User's current skills
            
        Returns:
            Dictionary with interview preparation guidance
        """
        # Analyze skill gap for the job
        job_skills = self._extract_skills_from_jd(job_description)
        skill_set = set([s.lower() for s in skills])
        
        gap_analysis = self.skill_gap_engine.analyze_gap(
            resume_skills=skill_set,
            job_skills=set(job_skills),
            job_description=job_description,
        )
        
        # Generate prompt for interview questions
        prompt = f"""
Generate 5 technical interview questions for a {job_title} position.

JOB DESCRIPTION:
{job_description}

USER'S CURRENT SKILLS:
{', '.join(skills)}

MISSING SKILLS TO FOCUS ON:
{', '.join(gap_analysis.critical_gaps[:5])}

Provide questions that:
1. Test core skills required for the role
2. Are appropriate for the user's current skill level
3. Help them prepare for gaps they have
4. Include practical, scenario-based questions

Format each question with a brief explanation of what it tests.
"""
        
        response = self.gemini_client.generate_response(prompt)
        
        return {
            "job_title": job_title,
            "skill_gap_analysis": {
                "critical_gaps": gap_analysis.critical_gaps,
                "medium_gaps": gap_analysis.medium_gaps,
                "match_percentage": gap_analysis.match_percentage,
            },
            "interview_questions": response,
            "recommended_preparation": gap_analysis.recommended_learning_order[:5],
        }
    
    def _extract_skills_from_jd(self, job_description: str) -> List[str]:
        """Extract skills from job description."""
        # This is a simplified extraction - in production, use NLP
        common_skills = [
            "python", "javascript", "java", "go", "rust", "typescript", "c++", "c#", "php",
            "django", "flask", "fastapi", "react", "vue", "angular", "spring", "express",
            "node.js", "graphql", "rest", "microservices",
            "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
            "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
            "git", "ci/cd", "jenkins", "github actions",
            "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "machine learning",
        ]
        
        jd_lower = job_description.lower()
        found_skills = [skill for skill in common_skills if skill in jd_lower]
        
        return found_skills
    
    def get_learning_plan(
        self,
        target_skills: List[str],
        current_skills: List[str],
        timeline_weeks: int = 12,
    ) -> Dict[str, Any]:
        """
        Get personalized learning plan.
        
        Args:
            target_skills: Skills user wants to learn
            current_skills: User's current skills
            timeline_weeks: Timeline in weeks
            
        Returns:
            Dictionary with learning plan details
        """
        # Generate roadmap
        roadmap = self.roadmap_generator.generate_roadmap(
            missing_skills=target_skills,
            target_role="Software Developer",
        )
        
        # Get course recommendations
        courses = self.course_recommender.recommend_courses(
            skills=target_skills,
            free_only=True,
            limit=3,
        )
        
        # Select appropriate timeline plan
        timeline_key = "90_day" if timeline_weeks >= 12 else "30_day" if timeline_weeks >= 4 else "7_day"
        selected_plan = roadmap.get(timeline_key)
        
        return {
            "timeline": f"{timeline_weeks} weeks",
            "roadmap": selected_plan,
            "recommended_courses": [
                {
                    "title": course.title,
                    "platform": course.platform,
                    "url": course.url,
                    "duration": course.duration,
                }
                for course in courses
            ],
            "total_milestones": len(selected_plan.milestones) if selected_plan else 0,
        }
    
    def get_salary_insights(
        self,
        career_path: str,
        experience_years: float,
        location: str = "India",
    ) -> Dict[str, Any]:
        """
        Get salary insights for a career path.
        
        Args:
            career_path: Target career path
            experience_years: Years of experience
            location: Geographic location
            
        Returns:
            Dictionary with salary insights
        """
        # This is a simplified salary estimation
        # In production, integrate with real salary data APIs
        
        salary_ranges = {
            "Full Stack Developer": {"entry": 8, "mid": 15, "senior": 25},
            "Backend Developer": {"entry": 6, "mid": 12, "senior": 20},
            "Frontend Developer": {"entry": 6, "mid": 12, "senior": 18},
            "Data Scientist": {"entry": 8, "mid": 18, "senior": 30},
            "Machine Learning Engineer": {"entry": 10, "mid": 20, "senior": 35},
            "DevOps Engineer": {"entry": 8, "mid": 15, "senior": 25},
            "Cloud Architect": {"entry": 15, "mid": 25, "senior": 40},
            "Mobile Developer": {"entry": 6, "mid": 12, "senior": 20},
            "Software Engineer": {"entry": 5, "mid": 10, "senior": 15},
        }
        
        ranges = salary_ranges.get(career_path, {"entry": 5, "mid": 10, "senior": 15})
        
        # Determine level based on experience
        if experience_years < 2:
            level = "entry"
            multiplier = 1.0
        elif experience_years < 5:
            level = "mid"
            multiplier = 1.0 + (experience_years - 2) * 0.1
        else:
            level = "senior"
            multiplier = 1.0 + min(experience_years - 5, 5) * 0.05
        
        base_salary = ranges[level]
        estimated_salary = base_salary * multiplier
        
        # Location adjustment (simplified)
        location_multipliers = {
            "India": 1.0,
            "USA": 3.0,
            "UK": 2.0,
            "Germany": 1.8,
            "Singapore": 1.5,
        }
        loc_mult = location_multipliers.get(location, 1.0)
        
        return {
            "career_path": career_path,
            "experience_years": experience_years,
            "location": location,
            "estimated_salary_lpa": round(estimated_salary * loc_mult, 1),
            "salary_range_lpa": f"{ranges['entry']}-{ranges['senior']} LPA",
            "level": level,
            "factors": [
                f"Experience: {experience_years} years",
                f"Location: {location}",
                f"Career Level: {level}",
            ],
        }
