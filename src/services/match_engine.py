"""
Match Engine Service

Handles weighted skill matching with:
- High/Medium/Low priority skill weights
- Technical vs soft skill scoring
- Category-based match analysis
"""

from __future__ import annotations

from typing import Any

from src.services.skill_categorizer import SkillCategory, categorize_skill


# Skill priority weights
HIGH_PRIORITY_WEIGHT = 3.0
MEDIUM_PRIORITY_WEIGHT = 2.0
LOW_PRIORITY_WEIGHT = 1.0

# High priority skills (critical technical skills) - include both lowercase and proper case
HIGH_PRIORITY_SKILLS = {
    "Python", "python", "Java", "java", "JavaScript", "javascript", "TypeScript", "typescript",
    "React", "react", "Node.js", "node.js", "SQL", "sql", "Django", "django",
    "Flask", "flask", "FastAPI", "fastapi", "Spring", "spring", "Express", "express",
    "C++", "c++", "C#", "c#", "Go", "go", "Rust", "rust", "Swift", "swift", "Kotlin", "kotlin",
    "Docker", "docker", "AWS", "aws", "Git", "git", "GitHub", "github",
    "PostgreSQL", "postgresql", "MongoDB", "mongodb", "Redis", "redis",
    "GraphQL", "graphql", "REST API", "rest api",
}

# Medium priority skills (important but not critical) - include both lowercase and proper case
MEDIUM_PRIORITY_SKILLS = {
    "Azure", "azure", "GCP", "gcp", "Kubernetes", "kubernetes", "Terraform", "terraform", "Linux", "linux",
    "MySQL", "mysql", "Elasticsearch", "elasticsearch", "Vue", "vue", "Angular", "angular",
    "Next.js", "next.js", "Nest.js", "nest.js", "Laravel", "laravel", "Rails", "rails",
    "Jenkins", "jenkins", "CI/CD", "ci/cd", "Nginx", "nginx", "Apache", "apache",
    "Pandas", "pandas", "NumPy", "numpy", "TensorFlow", "tensorflow", "PyTorch", "pytorch",
}

# Low priority skills (soft skills and general tools) - include both lowercase and proper case
LOW_PRIORITY_SKILLS = {
    "Communication", "communication", "Teamwork", "teamwork", "Problem Solving", "problem solving",
    "Time Management", "time management", "Agile", "agile", "Scrum", "scrum",
    "Jira", "jira", "Confluence", "confluence", "Testing", "testing",
    "Bootstrap", "bootstrap", "Sass", "sass", "Webpack", "webpack", "Babel", "babel",
    "Jest", "jest", "Mocha", "mocha", "Cypress", "cypress", "Selenium", "selenium",
}


def get_skill_weight(skill: str) -> float:
    """
    Get the weight for a skill based on its priority.
    
    High priority: 3.0
    Medium priority: 2.0
    Low priority: 1.0
    Default: 1.5
    """
    if skill in HIGH_PRIORITY_SKILLS:
        return HIGH_PRIORITY_WEIGHT
    elif skill in MEDIUM_PRIORITY_SKILLS:
        return MEDIUM_PRIORITY_WEIGHT
    elif skill in LOW_PRIORITY_SKILLS:
        return LOW_PRIORITY_WEIGHT
    else:
        return 1.5  # Default weight for uncategorized skills


def calculate_weighted_match(
    resume_skills: set[str],
    job_skills: set[str],
) -> dict[str, Any]:
    """
    Calculate weighted match metrics between resume and job skills.
    
    Returns match percentage, matched skills, missing skills,
    and breakdown by priority level.
    """
    try:
        if not job_skills:
            return {
                "match_percentage": 0.0,
                "weighted_match_percentage": 0.0,
                "matched_skills": set(),
                "missing_skills": set(),
                "total_job_skills": 0,
                "matched_count": 0,
                "high_priority_match": 0.0,
                "medium_priority_match": 0.0,
                "low_priority_match": 0.0,
            }
        
        matched = resume_skills & job_skills
        missing = job_skills - resume_skills
        
        # Calculate weighted match
        total_weight = sum(get_skill_weight(skill) for skill in job_skills)
        matched_weight = sum(get_skill_weight(skill) for skill in matched)
        
        weighted_match_percentage = (matched_weight / total_weight * 100) if total_weight > 0 else 0.0
        
        # Simple match percentage (unweighted)
        simple_match_percentage = (len(matched) / len(job_skills) * 100) if job_skills else 0.0
        
        # Calculate priority-specific matches
        high_priority_job = {s for s in job_skills if s in HIGH_PRIORITY_SKILLS}
        medium_priority_job = {s for s in job_skills if s in MEDIUM_PRIORITY_SKILLS}
        low_priority_job = {s for s in job_skills if s in LOW_PRIORITY_SKILLS}
        
        high_priority_matched = matched & high_priority_job
        medium_priority_matched = matched & medium_priority_job
        low_priority_matched = matched & low_priority_job
        
        high_priority_match = (
            len(high_priority_matched) / len(high_priority_job) * 100
            if high_priority_job else 0.0
        )
        medium_priority_match = (
            len(medium_priority_matched) / len(medium_priority_job) * 100
            if medium_priority_job else 0.0
        )
        low_priority_match = (
            len(low_priority_matched) / len(low_priority_job) * 100
            if low_priority_job else 0.0
        )
        
        return {
            "match_percentage": round(simple_match_percentage, 1),
            "weighted_match_percentage": round(weighted_match_percentage, 1),
            "matched_skills": matched,
            "missing_skills": missing,
            "total_job_skills": len(job_skills),
            "matched_count": len(matched),
            "high_priority_match": round(high_priority_match, 1),
            "medium_priority_match": round(medium_priority_match, 1),
            "low_priority_match": round(low_priority_match, 1),
        }
    except Exception:
        # Fallback to ensure the function always returns the expected keys
        return {
            "match_percentage": 0.0,
            "weighted_match_percentage": 0.0,
            "matched_skills": set(),
            "missing_skills": set(),
            "total_job_skills": 0,
            "matched_count": 0,
            "high_priority_match": 0.0,
            "medium_priority_match": 0.0,
            "low_priority_match": 0.0,
        }


def calculate_category_match(
    resume_skills: set[str],
    job_skills: set[str],
) -> dict[str, Any]:
    """
    Calculate match percentage by skill category.
    
    Returns breakdown of match scores for each category.
    """
    categories = {}
    
    # Get all unique categories from job skills
    job_categories = set()
    for skill in job_skills:
        category = categorize_skill(skill)
        if category:
            job_categories.add(category)
    
    # Calculate match for each category
    for category in job_categories:
        category_job_skills = {s for s in job_skills if categorize_skill(s) == category}
        category_resume_skills = {s for s in resume_skills if categorize_skill(s) == category}
        
        matched = category_resume_skills & category_job_skills
        match_pct = (
            len(matched) / len(category_job_skills) * 100
            if category_job_skills else 0.0
        )
        
        categories[category.value] = {
            "match_percentage": round(match_pct, 1),
            "matched_count": len(matched),
            "missing_count": len(category_job_skills - category_resume_skills),
            "total_count": len(category_job_skills),
            "matched_skills": sorted(matched),
            "missing_skills": sorted(category_job_skills - category_resume_skills),
        }
    
    return categories


def calculate_technical_vs_soft_match(
    resume_skills: set[str],
    job_skills: set[str],
) -> dict[str, Any]:
    """
    Calculate separate match scores for technical vs soft skills.
    
    Technical skills: Programming, Frameworks, Databases, Cloud, DevOps, Frontend, Backend
    Soft skills: Communication, Teamwork, Leadership, etc.
    """
    technical_categories = {
        SkillCategory.PROGRAMMING_LANGUAGES,
        SkillCategory.DATABASES,
        SkillCategory.CLOUD,
        SkillCategory.DEVOPS,
        SkillCategory.FRONTEND,
        SkillCategory.BACKEND,
        SkillCategory.MOBILE,
        SkillCategory.DATA_SCIENCE,
        SkillCategory.TESTING,
    }
    
    soft_categories = {
        SkillCategory.SOFT_SKILLS,
    }
    
    # Separate job skills by type
    technical_job_skills = set()
    soft_job_skills = set()
    
    for skill in job_skills:
        category = categorize_skill(skill)
        if category in technical_categories:
            technical_job_skills.add(skill)
        elif category in soft_categories:
            soft_job_skills.add(skill)
        else:
            # Default to technical if uncategorized
            technical_job_skills.add(skill)
    
    # Calculate matches
    technical_matched = resume_skills & technical_job_skills
    soft_matched = resume_skills & soft_job_skills
    
    technical_match = (
        len(technical_matched) / len(technical_job_skills) * 100
        if technical_job_skills else 0.0
    )
    soft_match = (
        len(soft_matched) / len(soft_job_skills) * 100
        if soft_job_skills else 0.0
    )
    
    return {
        "technical_match_percentage": round(technical_match, 1),
        "soft_skill_match_percentage": round(soft_match, 1),
        "technical_matched_count": len(technical_matched),
        "technical_total_count": len(technical_job_skills),
        "soft_matched_count": len(soft_matched),
        "soft_total_count": len(soft_job_skills),
    }
