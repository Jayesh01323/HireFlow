"""
Prompts Module

Contains prompt templates for various AI-powered features.
Provides structured prompts for resume parsing, career coaching, and interview preparation.
"""

from __future__ import annotations

from typing import Dict, List


class PromptTemplates:
    """Collection of prompt templates for AI interactions."""
    
    # Resume Parsing Prompts
    RESUME_PARSE_PROMPT = """
    Parse the following resume text into structured JSON format with the following schema:
    {{
        "name": "string",
        "email": "string",
        "phone": "string",
        "skills": [
            {{"name": "string", "level": "string"}}
        ],
        "education": ["string"],
        "projects": ["string"],
        "experience": ["string"]
    }}
    
    Resume text:
    {resume_text}
    
    Return only valid JSON without any additional text.
    """
    
    # Career Coaching Prompts
    CAREER_ADVICE_PROMPT = """
    Based on the following user profile, provide career advice:
    
    User Profile:
    {user_profile}
    
    Question: {question}
    
    Provide specific, actionable advice tailored to the user's background.
    """
    
    SKILL_GAP_ANALYSIS_PROMPT = """
    Analyze the skill gap between the following resume skills and job requirements:
    
    Resume Skills: {resume_skills}
    Job Required Skills: {job_skills}
    
    Provide:
    1. Missing skills
    2. Learning recommendations for each missing skill
    3. Priority order for learning
    4. Estimated time to learn each skill
    """
    
    # Interview Preparation Prompts
    TECHNICAL_INTERVIEW_QUESTIONS = """
    Generate 5 technical interview questions for the following role:
    
    Job Title: {job_title}
    Job Description: {job_description}
    
    Questions should be relevant to the role and include expected answers.
    """
    
    BEHAVIORAL_INTERVIEW_QUESTIONS = """
    Generate 5 behavioral interview questions for the following role:
    
    Job Title: {job_title}
    Job Description: {job_description}
    
    Questions should focus on soft skills, teamwork, and problem-solving.
    """
    
    SYSTEM_DESIGN_INTERVIEW_QUESTIONS = """
    Generate 5 system design interview questions for the following role:
    
    Job Title: {job_title}
    Job Description: {job_description}
    
    Questions should focus on architecture, scalability, and design patterns.
    """
    
    # Job Analysis Prompts
    JOB_SKILL_EXTRACTION_PROMPT = """
    Extract technical skills from the following job description:
    
    Job Description:
    {job_description}
    
    Return a list of technical skills required for this role.
    """
    
    JOB_SUMMARY_PROMPT = """
    Summarize the following job description in 2-3 sentences:
    
    Job Description:
    {job_description}
    
    Focus on the key responsibilities and requirements.
    """
    
    # Learning Roadmap Prompts
    LEARNING_ROADMAP_PROMPT = """
    Generate a learning roadmap for the following target role:
    
    Target Role: {target_role}
    Current Skills: {current_skills}
    Missing Skills: {missing_skills}
    
    Provide:
    1. Learning sequence (order of skills to learn)
    2. Estimated time for each skill
    3. Recommended resources for each skill
    4. Milestones to track progress
    """
    
    @staticmethod
    def get_resume_parse_prompt(resume_text: str) -> str:
        """Get resume parsing prompt with resume text."""
        return PromptTemplates.RESUME_PARSE_PROMPT.format(resume_text=resume_text)
    
    @staticmethod
    def get_career_advice_prompt(user_profile: Dict, question: str) -> str:
        """Get career advice prompt with user profile."""
        return PromptTemplates.CAREER_ADVICE_PROMPT.format(
            user_profile=user_profile,
            question=question,
        )
    
    @staticmethod
    def get_skill_gap_prompt(resume_skills: List[str], job_skills: List[str]) -> str:
        """Get skill gap analysis prompt."""
        return PromptTemplates.SKILL_GAP_ANALYSIS_PROMPT.format(
            resume_skills=resume_skills,
            job_skills=job_skills,
        )
    
    @staticmethod
    def get_interview_questions_prompt(
        job_title: str,
        job_description: str,
        question_type: str = "technical",
    ) -> str:
        """Get interview questions prompt based on type."""
        if question_type == "technical":
            return PromptTemplates.TECHNICAL_INTERVIEW_QUESTIONS.format(
                job_title=job_title,
                job_description=job_description,
            )
        elif question_type == "behavioral":
            return PromptTemplates.BEHAVIORAL_INTERVIEW_QUESTIONS.format(
                job_title=job_title,
                job_description=job_description,
            )
        elif question_type == "system_design":
            return PromptTemplates.SYSTEM_DESIGN_INTERVIEW_QUESTIONS.format(
                job_title=job_title,
                job_description=job_description,
            )
        else:
            return PromptTemplates.TECHNICAL_INTERVIEW_QUESTIONS.format(
                job_title=job_title,
                job_description=job_description,
            )
