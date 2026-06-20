"""
Job Matcher Module

Handles skill extraction, matching logic, and recommendation generation
for comparing resumes against job descriptions using enhanced services.

This module now uses the new service architecture for improved accuracy:
- skill_extractor: Whitelist-based extraction with stopword filtering
- skill_normalizer: Proper capitalization and naming conventions
- match_engine: Weighted scoring with technical vs soft skill analysis
- recommendation_engine: Contextual, meaningful recommendations
- skill_categorizer: Skill grouping for category-based insights
"""

from __future__ import annotations

from typing import Any

from src.services.match_engine import (
    calculate_category_match,
    calculate_technical_vs_soft_match,
    calculate_weighted_match,
)
from src.services.recommendation_engine import generate_recommendations
from src.services.skill_categorizer import categorize_skills, get_category_breakdown
from src.services.skill_extractor import (
    extract_job_skills,
    extract_resume_skills,
)
from src.services.skill_normalizer import (
    normalize_job_skills,
    normalize_resume_skills,
)


def extract_resume_skills(parsed_data: dict[str, Any]) -> set[str]:
    """Extract skill names from parsed resume JSON using enhanced service."""
    from src.services.skill_extractor import extract_resume_skills as _extract
    return _extract(parsed_data)


def extract_job_skills(job_description: str) -> set[str]:
    """Extract skills from job description using enhanced service with whitelist."""
    from src.services.skill_extractor import extract_job_skills as _extract
    return _extract(job_description)


def calculate_match(resume_skills: set[str], job_skills: set[str]) -> dict[str, Any]:
    """Calculate match metrics between resume and job skills using weighted scoring."""
    return calculate_weighted_match(resume_skills, job_skills)


def generate_recommendations(
    missing_skills: set[str],
    resume_skills: set[str],
) -> dict[str, Any]:
    """Generate contextual improvement recommendations based on missing skills."""
    from src.services.recommendation_engine import generate_recommendations as _generate
    return _generate(missing_skills, resume_skills)


def analyze_match(
    parsed_resume: dict[str, Any],
    job_description: str,
) -> dict[str, Any]:
    """Perform complete match analysis between resume and job description using enhanced services."""
    # Extract skills using enhanced service
    resume_skills = extract_resume_skills(parsed_resume)
    job_skills = extract_job_skills(job_description)
    
    # Normalize skills for display and matching
    normalized_resume_skills = normalize_resume_skills(parsed_resume)
    normalized_job_skills = normalize_job_skills(job_skills)
    
    # Convert normalized lists back to sets for matching functions
    normalized_resume_set = set(normalized_resume_skills)
    normalized_job_set = set(normalized_job_skills)
    
    # Calculate weighted match using normalized skills
    match_results = calculate_weighted_match(normalized_resume_set, normalized_job_set)
    
    # Ensure match_results has all required keys
    if "weighted_match_percentage" not in match_results:
        match_results["weighted_match_percentage"] = match_results.get("match_percentage", 0.0)
    
    # Calculate technical vs soft skill match using normalized skills
    tech_vs_soft = calculate_technical_vs_soft_match(normalized_resume_set, normalized_job_set)
    
    # Calculate category-based match using normalized skills
    category_match = calculate_category_match(normalized_resume_set, normalized_job_set)
    
    # Generate contextual recommendations using normalized skills
    recommendations = generate_recommendations(
        match_results["missing_skills"],
        normalized_resume_set,
    )
    
    # Get category breakdown for visualization
    resume_category_breakdown = get_category_breakdown(normalized_resume_skills)
    job_category_breakdown = get_category_breakdown(normalized_job_skills)
    
    # Categorize skills for display
    categorized_resume = categorize_skills(normalized_resume_skills)
    categorized_job = categorize_skills(normalized_job_skills)
    
    return {
        "resume_skills": normalized_resume_skills,
        "job_skills": normalized_job_skills,
        "match_results": match_results,
        "recommendations": recommendations,
        "technical_vs_soft": tech_vs_soft,
        "category_match": category_match,
        "resume_category_breakdown": resume_category_breakdown,
        "job_category_breakdown": job_category_breakdown,
        "categorized_resume": categorized_resume,
        "categorized_job": categorized_job,
    }
