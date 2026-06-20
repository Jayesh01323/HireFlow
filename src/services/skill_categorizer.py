"""
Skill Categorizer Service

Categorizes skills into logical groups for analysis and visualization.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class SkillCategory(Enum):
    """Skill categories for grouping and analysis."""
    PROGRAMMING_LANGUAGES = "Programming Languages"
    FRONTEND = "Frontend"
    BACKEND = "Backend"
    DATABASES = "Databases"
    CLOUD = "Cloud"
    DEVOPS = "DevOps"
    DATA_SCIENCE = "Data Science"
    TESTING = "Testing"
    MOBILE = "Mobile"
    TOOLS = "Tools"
    SOFT_SKILLS = "Soft Skills"
    OTHER = "Other"


# Skill to category mapping
SKILL_CATEGORY_MAP = {
    # Programming Languages
    "Python": SkillCategory.PROGRAMMING_LANGUAGES,
    "Java": SkillCategory.PROGRAMMING_LANGUAGES,
    "JavaScript": SkillCategory.PROGRAMMING_LANGUAGES,
    "TypeScript": SkillCategory.PROGRAMMING_LANGUAGES,
    "C++": SkillCategory.PROGRAMMING_LANGUAGES,
    "C#": SkillCategory.PROGRAMMING_LANGUAGES,
    "Go": SkillCategory.PROGRAMMING_LANGUAGES,
    "Rust": SkillCategory.PROGRAMMING_LANGUAGES,
    "Swift": SkillCategory.PROGRAMMING_LANGUAGES,
    "Kotlin": SkillCategory.PROGRAMMING_LANGUAGES,
    "Scala": SkillCategory.PROGRAMMING_LANGUAGES,
    "Ruby": SkillCategory.PROGRAMMING_LANGUAGES,
    "PHP": SkillCategory.PROGRAMMING_LANGUAGES,
    "Perl": SkillCategory.PROGRAMMING_LANGUAGES,
    "R": SkillCategory.PROGRAMMING_LANGUAGES,
    "MATLAB": SkillCategory.PROGRAMMING_LANGUAGES,
    "Shell": SkillCategory.PROGRAMMING_LANGUAGES,
    "Bash": SkillCategory.PROGRAMMING_LANGUAGES,
    
    # Frontend
    "React": SkillCategory.FRONTEND,
    "Angular": SkillCategory.FRONTEND,
    "Vue": SkillCategory.FRONTEND,
    "Next.js": SkillCategory.FRONTEND,
    "Nuxt.js": SkillCategory.FRONTEND,
    "Svelte": SkillCategory.FRONTEND,
    "Ember": SkillCategory.FRONTEND,
    "Backbone": SkillCategory.FRONTEND,
    "jQuery": SkillCategory.FRONTEND,
    "Redux": SkillCategory.FRONTEND,
    "MobX": SkillCategory.FRONTEND,
    "Webpack": SkillCategory.FRONTEND,
    "Vite": SkillCategory.FRONTEND,
    "Parcel": SkillCategory.FRONTEND,
    "HTML": SkillCategory.FRONTEND,
    "CSS": SkillCategory.FRONTEND,
    "Sass": SkillCategory.FRONTEND,
    "SCSS": SkillCategory.FRONTEND,
    "Tailwind": SkillCategory.FRONTEND,
    "Bootstrap": SkillCategory.FRONTEND,
    "Material UI": SkillCategory.FRONTEND,
    "Chakra UI": SkillCategory.FRONTEND,
    "Ant Design": SkillCategory.FRONTEND,
    "Styled Components": SkillCategory.FRONTEND,
    "CSS-in-JS": SkillCategory.FRONTEND,
    "Responsive Design": SkillCategory.FRONTEND,
    
    # Backend
    "Django": SkillCategory.BACKEND,
    "Flask": SkillCategory.BACKEND,
    "FastAPI": SkillCategory.BACKEND,
    "Spring": SkillCategory.BACKEND,
    "Spring Boot": SkillCategory.BACKEND,
    "Express": SkillCategory.BACKEND,
    "Nest.js": SkillCategory.BACKEND,
    "Laravel": SkillCategory.BACKEND,
    "Rails": SkillCategory.BACKEND,
    "Fiber": SkillCategory.BACKEND,
    "Gin": SkillCategory.BACKEND,
    "Echo": SkillCategory.BACKEND,
    "Actix": SkillCategory.BACKEND,
    "Tornado": SkillCategory.BACKEND,
    "AIOHTTP": SkillCategory.BACKEND,
    "Node.js": SkillCategory.BACKEND,
    "REST API": SkillCategory.BACKEND,
    "GraphQL": SkillCategory.BACKEND,
    "gRPC": SkillCategory.BACKEND,
    
    # Databases
    "SQL": SkillCategory.DATABASES,
    "MySQL": SkillCategory.DATABASES,
    "PostgreSQL": SkillCategory.DATABASES,
    "MongoDB": SkillCategory.DATABASES,
    "Redis": SkillCategory.DATABASES,
    "Elasticsearch": SkillCategory.DATABASES,
    "SQLite": SkillCategory.DATABASES,
    "Oracle": SkillCategory.DATABASES,
    "Cassandra": SkillCategory.DATABASES,
    "DynamoDB": SkillCategory.DATABASES,
    "Firebase": SkillCategory.DATABASES,
    "Supabase": SkillCategory.DATABASES,
    
    # Cloud
    "AWS": SkillCategory.CLOUD,
    "Azure": SkillCategory.CLOUD,
    "GCP": SkillCategory.CLOUD,
    "Heroku": SkillCategory.CLOUD,
    "Vercel": SkillCategory.CLOUD,
    "Netlify": SkillCategory.CLOUD,
    "DigitalOcean": SkillCategory.CLOUD,
    
    # DevOps
    "Docker": SkillCategory.DEVOPS,
    "Kubernetes": SkillCategory.DEVOPS,
    "Terraform": SkillCategory.DEVOPS,
    "Ansible": SkillCategory.DEVOPS,
    "Jenkins": SkillCategory.DEVOPS,
    "Git": SkillCategory.DEVOPS,
    "GitHub": SkillCategory.DEVOPS,
    "GitLab": SkillCategory.DEVOPS,
    "CI/CD": SkillCategory.DEVOPS,
    "Linux": SkillCategory.DEVOPS,
    "Unix": SkillCategory.DEVOPS,
    "Nginx": SkillCategory.DEVOPS,
    "Apache": SkillCategory.DEVOPS,
    
    # Data Science
    "Machine Learning": SkillCategory.DATA_SCIENCE,
    "Deep Learning": SkillCategory.DATA_SCIENCE,
    "NLP": SkillCategory.DATA_SCIENCE,
    "Data Science": SkillCategory.DATA_SCIENCE,
    "Pandas": SkillCategory.DATA_SCIENCE,
    "NumPy": SkillCategory.DATA_SCIENCE,
    "TensorFlow": SkillCategory.DATA_SCIENCE,
    "PyTorch": SkillCategory.DATA_SCIENCE,
    "Scikit-learn": SkillCategory.DATA_SCIENCE,
    "Apache Spark": SkillCategory.DATA_SCIENCE,
    "Hadoop": SkillCategory.DATA_SCIENCE,
    "Jupyter": SkillCategory.DATA_SCIENCE,
    "Tableau": SkillCategory.DATA_SCIENCE,
    "Power BI": SkillCategory.DATA_SCIENCE,
    "Matplotlib": SkillCategory.DATA_SCIENCE,
    "Seaborn": SkillCategory.DATA_SCIENCE,
    
    # Testing
    "JUnit": SkillCategory.TESTING,
    "Pytest": SkillCategory.TESTING,
    "Selenium": SkillCategory.TESTING,
    "Cypress": SkillCategory.TESTING,
    "Jest": SkillCategory.TESTING,
    "Mocha": SkillCategory.TESTING,
    "Chai": SkillCategory.TESTING,
    "Testing": SkillCategory.TESTING,
    
    # Mobile
    "React Native": SkillCategory.MOBILE,
    "Flutter": SkillCategory.MOBILE,
    "Android": SkillCategory.MOBILE,
    "iOS": SkillCategory.MOBILE,
    
    # Tools
    "Agile": SkillCategory.TOOLS,
    "Scrum": SkillCategory.TOOLS,
    "Jira": SkillCategory.TOOLS,
    "Confluence": SkillCategory.TOOLS,
    "Figma": SkillCategory.TOOLS,
    "Adobe XD": SkillCategory.TOOLS,
    "Sketch": SkillCategory.TOOLS,
    
    # Soft Skills
    "Communication": SkillCategory.SOFT_SKILLS,
    "Teamwork": SkillCategory.SOFT_SKILLS,
    "Problem Solving": SkillCategory.SOFT_SKILLS,
    "Time Management": SkillCategory.SOFT_SKILLS,
    "Leadership": SkillCategory.SOFT_SKILLS,
    "Organization": SkillCategory.SOFT_SKILLS,
    "Collaboration": SkillCategory.SOFT_SKILLS,
}


def categorize_skill(skill: str) -> SkillCategory:
    """
    Categorize a skill into its logical group.
    
    Returns the category enum for the given skill.
    Defaults to OTHER if not found in the mapping.
    """
    return SKILL_CATEGORY_MAP.get(skill, SkillCategory.OTHER)


def categorize_skills(skills: set[str] | list[str]) -> dict[str, list[str]]:
    """
    Categorize a collection of skills into groups.
    
    Returns a dictionary mapping category names to lists of skills.
    """
    categorized = {}
    
    for skill in skills:
        category = categorize_skill(skill)
        category_name = category.value
        
        if category_name not in categorized:
            categorized[category_name] = []
        
        categorized[category_name].append(skill)
    
    # Sort skills within each category
    for category_name in categorized:
        categorized[category_name].sort()
    
    return categorized


def get_category_breakdown(skills: set[str] | list[str]) -> dict[str, Any]:
    """
    Get a detailed breakdown of skills by category.
    
    Returns category names, counts, and percentages.
    """
    categorized = categorize_skills(skills)
    total_skills = len(skills)
    
    breakdown = {}
    for category_name, category_skills in categorized.items():
        breakdown[category_name] = {
            "count": len(category_skills),
            "percentage": round(len(category_skills) / total_skills * 100, 1) if total_skills > 0 else 0.0,
            "skills": category_skills,
        }
    
    return breakdown
