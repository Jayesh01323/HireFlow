"""
Recommendation Engine Service

Generates contextual, meaningful recommendations based on:
- Missing skills
- Skill categories
- Career direction
- Learning priorities
"""

from __future__ import annotations

from typing import Any

from src.services.skill_categorizer import SkillCategory, categorize_skill


# Skill-specific learning recommendations
SKILL_LEARNING_RECOMMENDATIONS = {
    # Backend Frameworks
    "Django": "Learn Django to strengthen backend web development skills with Python.",
    "Flask": "Learn Flask for lightweight, flexible Python web development.",
    "FastAPI": "Learn FastAPI for modern, high-performance Python APIs with automatic documentation.",
    "Spring": "Learn Spring for enterprise-grade Java application development.",
    "Express": "Learn Express for building robust Node.js backend applications.",
    "Nest.js": "Learn Nest.js for scalable, modular Node.js server-side applications.",
    
    # Databases
    "SQL": "Learn SQL and database fundamentals for data manipulation and querying.",
    "PostgreSQL": "Learn PostgreSQL for advanced relational database features and performance.",
    "MySQL": "Learn MySQL for reliable, widely-used relational database management.",
    "MongoDB": "Learn MongoDB for flexible NoSQL document storage and scalability.",
    "Redis": "Learn Redis for high-performance caching and real-time data processing.",
    
    # Frontend
    "React": "Learn React for building modern, component-based user interfaces.",
    "Angular": "Learn Angular for comprehensive, enterprise-scale frontend applications.",
    "Vue": "Learn Vue for progressive, approachable frontend development.",
    "Next.js": "Learn Next.js for React with server-side rendering and optimization.",
    "TypeScript": "Learn TypeScript for type-safe JavaScript development.",
    
    # DevOps & Cloud
    "Docker": "Learn Docker for containerization and consistent application deployment.",
    "Kubernetes": "Learn Kubernetes for orchestrating containerized applications at scale.",
    "AWS": "Learn AWS for comprehensive cloud computing services and infrastructure.",
    "Azure": "Learn Azure for Microsoft's cloud platform and enterprise solutions.",
    "GCP": "Learn GCP for Google's cloud services and data/analytics capabilities.",
    "Terraform": "Learn Terraform for infrastructure as code and cloud resource management.",
    
    # Tools
    "Git": "Learn Git version control for team collaboration and code management.",
    "GitHub": "Learn GitHub for hosting code repositories and collaboration features.",
    "CI/CD": "Learn CI/CD practices for automated testing and deployment pipelines.",
    
    # Data Science
    "Machine Learning": "Learn Machine Learning fundamentals for predictive modeling and AI.",
    "Deep Learning": "Learn Deep Learning for neural networks and advanced AI applications.",
    "TensorFlow": "Learn TensorFlow for building and deploying machine learning models.",
    "PyTorch": "Learn PyTorch for flexible deep learning research and production.",
    "Pandas": "Learn Pandas for data manipulation and analysis in Python.",
    "NumPy": "Learn NumPy for numerical computing and array operations.",
    
    # Testing
    "Testing": "Learn software testing principles and methodologies for quality assurance.",
    "Selenium": "Learn Selenium for automated web browser testing.",
    "Cypress": "Learn Cypress for modern, fast end-to-end testing.",
}


# Category-based career direction recommendations
CATEGORY_CAREER_DIRECTIONS = {
    SkillCategory.PROGRAMMING_LANGUAGES: "Focus on mastering core programming languages as your foundation.",
    SkillCategory.FRONTEND: "Consider a Frontend Developer career path focusing on user interfaces.",
    SkillCategory.BACKEND: "Consider a Backend Developer career path focusing on server-side logic.",
    SkillCategory.DATABASES: "Strengthen database skills for Data Engineering or Backend Development roles.",
    SkillCategory.CLOUD: "Pursue Cloud Engineering or DevOps roles with cloud platform expertise.",
    SkillCategory.DEVOPS: "Consider DevOps Engineering for infrastructure and deployment automation.",
    SkillCategory.DATA_SCIENCE: "Explore Data Science or Machine Learning Engineering career paths.",
    SkillCategory.MOBILE: "Consider Mobile App Development for iOS or Android platforms.",
}


def generate_skill_recommendation(skill: str) -> str:
    """
    Generate a contextual learning recommendation for a specific skill.
    
    Returns a meaningful recommendation message.
    """
    return SKILL_LEARNING_RECOMMENDATIONS.get(
        skill,
        f"Learn {skill} to expand your technical capabilities.",
    )


def generate_recommendations(
    missing_skills: set[str],
    resume_skills: set[str],
) -> dict[str, Any]:
    """
    Generate comprehensive recommendations based on missing skills.
    
    Returns:
    - Top priority skills to learn
    - Learning recommendations
    - Suggested career direction
    - Category-based insights
    """
    if not missing_skills:
        return {
            "top_priority_skills": [],
            "learning_recommendations": ["Your skill set is a great match for this position!"],
            "career_direction": "Continue building on your existing strengths.",
            "category_insights": {},
        }
    
    # Prioritize missing skills by category and importance
    prioritized_skills = prioritize_missing_skills(missing_skills, resume_skills)
    
    # Generate learning recommendations for top skills
    top_priority = prioritized_skills[:5]
    learning_recommendations = [
        generate_skill_recommendation(skill) for skill in top_priority
    ]
    
    # Generate career direction based on missing categories
    career_direction = generate_career_direction(missing_skills)
    
    # Generate category insights
    category_insights = generate_category_insights(missing_skills)
    
    return {
        "top_priority_skills": top_priority,
        "learning_recommendations": learning_recommendations,
        "career_direction": career_direction,
        "category_insights": category_insights,
    }


def prioritize_missing_skills(
    missing_skills: set[str],
    resume_skills: set[str],
) -> list[str]:
    """
    Prioritize missing skills based on category and strategic value.
    
    Returns a sorted list of skills in priority order.
    """
    # Score each missing skill
    skill_scores = {}
    
    for skill in missing_skills:
        score = 0
        category = categorize_skill(skill)
        
        # Higher priority for backend, databases, and cloud
        if category in [SkillCategory.BACKEND, SkillCategory.DATABASES, SkillCategory.CLOUD]:
            score += 3
        elif category in [SkillCategory.FRONTEND, SkillCategory.PROGRAMMING_LANGUAGES]:
            score += 2
        elif category in [SkillCategory.DEVOPS, SkillCategory.DATA_SCIENCE]:
            score += 2
        else:
            score += 1
        
        # Bonus for foundational skills
        if skill in ["Python", "JavaScript", "SQL", "Git", "Docker"]:
            score += 2
        
        skill_scores[skill] = score
    
    # Sort by score (descending), then alphabetically
    sorted_skills = sorted(
        skill_scores.items(),
        key=lambda x: (-x[1], x[0]),
    )
    
    return [skill for skill, _ in sorted_skills]


def generate_career_direction(missing_skills: set[str]) -> str:
    """
    Generate career direction suggestion based on missing skill categories.
    
    Returns a career path recommendation.
    """
    if not missing_skills:
        return "Continue building on your existing strengths."
    
    # Analyze missing categories
    missing_categories = {}
    for skill in missing_skills:
        category = categorize_skill(skill)
        if category not in missing_categories:
            missing_categories[category] = []
        missing_categories[category].append(skill)
    
    # Find the category with most missing skills
    if missing_categories:
        top_category = max(missing_categories.items(), key=lambda x: len(x[1]))[0]
        return CATEGORY_CAREER_DIRECTIONS.get(
            top_category,
            "Focus on addressing your skill gaps in the most relevant areas.",
        )
    
    return "Focus on addressing your skill gaps in the most relevant areas."


def generate_category_insights(missing_skills: set[str]) -> dict[str, Any]:
    """
    Generate insights about missing skills by category.
    
    Returns category-specific recommendations and counts.
    """
    insights = {}
    
    for skill in missing_skills:
        category = categorize_skill(skill)
        category_name = category.value
        
        if category_name not in insights:
            insights[category_name] = {
                "missing_count": 0,
                "skills": [],
                "recommendation": "",
            }
        
        insights[category_name]["missing_count"] += 1
        insights[category_name]["skills"].append(skill)
    
    # Add category-specific recommendations
    for category_name, data in insights.items():
        data["skills"].sort()
        if data["missing_count"] >= 3:
            data["recommendation"] = f"Significant gap in {category_name}. Consider focused learning in this area."
        elif data["missing_count"] >= 2:
            data["recommendation"] = f"Moderate gap in {category_name}. Address these skills for better alignment."
        else:
            data["recommendation"] = f"Minor gap in {category_name}. Optional enhancement."
    
    return insights
