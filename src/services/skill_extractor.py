"""
Skill Extractor Service

Handles skill extraction from job descriptions with:
- Technical skill whitelist
- Stopword filtering
- Skill normalization
"""

from __future__ import annotations

import re
from typing import Any


# Technical skill whitelist - only these will be extracted
TECHNICAL_SKILL_WHITELIST = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "swift",
    "kotlin", "scala", "ruby", "php", "perl", "r", "matlab", "shell", "bash",
    
    # Frontend Frameworks & Libraries
    "react", "angular", "vue", "next.js", "nuxt.js", "svelte", "ember", "backbone",
    "jquery", "redux", "mobx", "webpack", "vite", "parcel",
    
    # Backend Frameworks
    "django", "flask", "fastapi", "spring", "express", "nest.js", "laravel", "rails",
    "fiber", "gin", "echo", "actix", "tornado", "aiohttp",
    
    # Databases
    "sql", "mysql", "postgresql", "postgres", "mongodb", "redis", "elasticsearch",
    "sqlite", "oracle", "cassandra", "dynamodb", "firebase", "supabase",
    
    # Cloud Platforms
    "aws", "azure", "gcp", "google cloud", "heroku", "vercel", "netlify", "digitalocean",
    
    # DevOps & Tools
    "docker", "kubernetes", "terraform", "ansible", "jenkins", "git", "github", "gitlab",
    "ci/cd", "linux", "unix", "nginx", "apache", "graphql", "rest api", "grpc",
    
    # Data Science & ML
    "machine learning", "deep learning", "nlp", "data science", "pandas", "numpy",
    "tensorflow", "pytorch", "scikit-learn", "spark", "hadoop", "jupyter", "tableau",
    "power bi", "matplotlib", "seaborn",
    
    # Frontend Technologies
    "html", "css", "sass", "scss", "tailwind", "bootstrap", "material ui", "chakra ui",
    "ant design", "styled-components", "css-in-js", "responsive design",
    
    # Testing
    "junit", "pytest", "selenium", "cypress", "jest", "mocha", "chai", "testing",
    
    # Mobile
    "react native", "flutter", "swift", "kotlin", "android", "ios",
    
    # Other Technologies
    "agile", "scrum", "jira", "confluence", "figma", "adobe xd", "sketch",
}


# Stopwords - these should never be extracted as skills
STOPWORDS = {
    "multiple", "object", "required", "preferred", "knowledge", "experience",
    "testing", "frameworks", "responsible", "candidate", "ability", "strong",
    "excellent", "good", "solid", "working", "using", "including", "various",
    "several", "many", "different", "related", "relevant", "basic", "advanced",
    "proficient", "familiar", "understanding", "ability", "skills", "skill",
    "technologies", "technology", "tools", "tool", "platforms", "platform",
    "systems", "system", "applications", "application", "software", "development",
    "design", "management", "support", "maintenance", "deployment", "integration",
    "implementation", "architecture", "engineering", "programming", "coding",
    "analysis", "analytical", "communication", "teamwork", "collaboration",
    "problem-solving", "leadership", "organization", "planning", "execution",
    "documentation", "reporting", "monitoring", "optimization", "performance",
    "security", "quality", "assurance", "compliance", "regulatory", "standards",
    "best", "practices", "methodologies", "processes", "procedures", "policies",
    "strategies", "strategy", "goals", "objectives", "requirements", "specifications",
    "deliverables", "milestones", "deadlines", "budget", "resources", "stakeholders",
    "clients", "customers", "users", "business", "commercial", "enterprise",
    "industry", "sector", "domain", "field", "area", "environment", "context",
    "background", "education", "degree", "certification", "training", "learning",
    "self-motivated", "detail-oriented", "results-driven", "fast-paced", "dynamic",
    "innovative", "creative", "strategic", "analytical", "technical", "professional",
}


def preprocess_job_description(job_description: str) -> str:
    """
    Clean and normalize job description before skill extraction.
    
    - Remove duplicate lines
    - Remove excessive whitespace
    - Normalize line endings
    """
    if not job_description:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', job_description)
    
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove duplicate lines (case-insensitive)
    lines = text.split('\n')
    seen = set()
    unique_lines = []
    for line in lines:
        normalized = line.strip().lower()
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique_lines.append(line.strip())
    
    return ' '.join(unique_lines)


def extract_skills_from_text(text: str) -> set[str]:
    """
    Extract skills from text using whitelist and stopword filtering.
    
    Returns only skills that match the technical whitelist and are not stopwords.
    """
    if not text:
        return set()
    
    text_lower = text.lower()
    found_skills = set()
    
    # Check for whitelisted skills
    for skill in TECHNICAL_SKILL_WHITELIST:
        if skill in text_lower:
            found_skills.add(skill)
    
    # Filter out stopwords
    filtered_skills = {skill for skill in found_skills if skill not in STOPWORDS}
    
    return filtered_skills


def extract_resume_skills(parsed_data: dict[str, Any]) -> set[str]:
    """
    Extract skill names from parsed resume JSON.
    
    Returns normalized, filtered skills from the resume.
    """
    skills = parsed_data.get("skills", [])
    skill_names = set()
    
    for skill in skills:
        if isinstance(skill, str):
            skill_names.add(skill.lower().strip())
        elif isinstance(skill, dict):
            name = skill.get("name", "")
            if name:
                skill_names.add(name.lower().strip())
    
    # Filter to only whitelisted skills
    filtered_skills = {skill for skill in skill_names if skill in TECHNICAL_SKILL_WHITELIST}
    
    return filtered_skills


def extract_job_skills(job_description: str) -> set[str]:
    """
    Extract skills from job description using whitelist and stopword filtering.
    
    Preprocesses the description and extracts only valid technical skills.
    """
    if not job_description:
        return set()
    
    # Preprocess the job description
    cleaned_text = preprocess_job_description(job_description)
    
    # Extract skills using whitelist
    return extract_skills_from_text(cleaned_text)
