"""
Skills Utility Module

Provides utility functions for skill-related operations.
Includes skill extraction, normalization, and categorization helpers.
"""

from __future__ import annotations

import logging
import re
from typing import List

logger = logging.getLogger(__name__)


def extract_skills_from_text(text: str) -> List[str]:
    """Extract potential skills from text using regex patterns."""
    # TODO: Implement skill extraction logic
    if not text:
        return []
    
    # Common skill patterns
    patterns = [
        r"\b(?:Python|Java|JavaScript|TypeScript|C\+\+|C#|Go|Rust|Swift|Kotlin|PHP|Ruby|Perl|R|MATLAB|Bash)\b",
        r"\b(?:React|Angular|Vue|Django|Flask|Spring|Express|Node\.js|Docker|Kubernetes|AWS|Azure|GCP)\b",
        r"\b(?:SQL|MySQL|PostgreSQL|MongoDB|Redis|Elasticsearch|GraphQL|REST API)\b",
    ]
    
    skills = set()
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        skills.update(matches)
    
    return list(skills)


def normalize_skill_name(skill: str) -> str:
    """Normalize a skill name to standard format."""
    # TODO: Implement skill normalization logic
    if not skill:
        return ""
    
    # Capitalize first letter of each word
    return skill.strip().title()


def deduplicate_skills(skills: List[str]) -> List[str]:
    """Remove duplicate skills while preserving order."""
    # TODO: Implement skill deduplication with fuzzy matching
    seen = set()
    unique = []
    
    for skill in skills:
        normalized = normalize_skill_name(skill)
        if normalized not in seen:
            seen.add(normalized)
            unique.append(skill)
    
    return unique


def categorize_skill(skill: str) -> str:
    """Categorize a skill into a domain."""
    # TODO: Implement skill categorization logic
    skill_lower = skill.lower()
    
    categories = {
        "programming": ["python", "java", "javascript", "typescript", "c++", "c#", "go", "rust"],
        "frontend": ["react", "angular", "vue", "html", "css", "tailwind"],
        "backend": ["django", "flask", "spring", "express", "node.js"],
        "database": ["sql", "mysql", "postgresql", "mongodb", "redis"],
        "cloud": ["aws", "azure", "gcp", "docker", "kubernetes"],
        "devops": ["git", "jenkins", "ci/cd", "linux"],
    }
    
    for category, category_skills in categories.items():
        if any(cat_skill in skill_lower for cat_skill in category_skills):
            return category
    
    return "other"


def calculate_skill_overlap(skills1: List[str], skills2: List[str]) -> float:
    """Calculate overlap percentage between two skill lists."""
    # TODO: Implement skill overlap calculation
    if not skills1 or not skills2:
        return 0.0
    
    set1 = set(normalize_skill_name(s) for s in skills1)
    set2 = set(normalize_skill_name(s) for s in skills2)
    
    intersection = set1 & set2
    union = set1 | set2
    
    return len(intersection) / len(union) * 100 if union else 0.0
