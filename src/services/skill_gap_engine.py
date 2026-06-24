"""
Skill Gap Engine Service V2

Analyzes skill gaps between resume skills and job requirements.
Provides detailed gap analysis with critical gaps and recommended learning order.
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

from src.services.skill_categorizer import categorize_skill, SkillCategory
from src.services.match_engine import HIGH_PRIORITY_SKILLS, MEDIUM_PRIORITY_SKILLS, LOW_PRIORITY_SKILLS

logger = logging.getLogger(__name__)


@dataclass
class SkillGapAnalysis:
    """Result of skill gap analysis V2."""
    
    matched_skills: List[str]
    missing_skills: List[str]
    match_percentage: float
    critical_gaps: List[str]
    medium_gaps: List[str]
    optional_gaps: List[str]
    recommended_learning_order: List[str]
    gap_severity: str  # low, medium, high


class SkillGapEngine:
    """Engine for analyzing skill gaps between resumes and job requirements V2."""
    
    def __init__(self) -> None:
        """Initialize skill gap engine."""
        self.skill_difficulty: Dict[str, int] = self._load_skill_difficulty()
        self.skill_dependencies: Dict[str, List[str]] = self._load_skill_dependencies()
    
    def _load_skill_difficulty(self) -> Dict[str, int]:
        """Load skill difficulty ratings (1-5 scale)."""
        return {
            # Programming Languages
            "python": 2, "javascript": 2, "java": 3, "go": 3, "rust": 4,
            "typescript": 2, "c++": 4, "c#": 3, "php": 2,
            # Backend
            "django": 2, "flask": 2, "fastapi": 2, "spring": 3, "express": 2,
            "node.js": 2, "graphql": 3, "rest": 1, "microservices": 4,
            # Frontend
            "react": 2, "vue": 2, "angular": 3, "html": 1, "css": 1,
            "next.js": 2, "tailwind": 1, "redux": 3,
            # Databases
            "sql": 2, "postgresql": 2, "mysql": 2, "mongodb": 2, "redis": 2,
            "elasticsearch": 3,
            # Cloud
            "aws": 3, "azure": 3, "gcp": 3, "docker": 2, "kubernetes": 4,
            "terraform": 3,
            # DevOps
            "git": 1, "ci/cd": 3, "jenkins": 3, "github actions": 2,
            # Data Science
            "pandas": 2, "numpy": 2, "scikit-learn": 3, "tensorflow": 4,
            "pytorch": 4, "machine learning": 4,
        }
    
    def _load_skill_dependencies(self) -> Dict[str, List[str]]:
        """Load skill dependencies for learning order."""
        return {
            "django": ["python", "sql"],
            "flask": ["python"],
            "fastapi": ["python"],
            "spring": ["java"],
            "react": ["javascript", "html", "css"],
            "vue": ["javascript", "html", "css"],
            "angular": ["typescript", "html", "css"],
            "next.js": ["react", "javascript"],
            "kubernetes": ["docker"],
            "tensorflow": ["python", "numpy"],
            "pytorch": ["python", "numpy"],
            "scikit-learn": ["python", "numpy", "pandas"],
            "machine learning": ["python", "numpy", "pandas"],
        }
    
    def analyze_gap(
        self,
        resume_skills: Set[str],
        job_skills: Set[str],
        job_description: Optional[str] = None,
    ) -> SkillGapAnalysis:
        """
        Analyze skill gap between resume and job requirements.
        
        Args:
            resume_skills: Set of skills from resume
            job_skills: Set of skills from job requirements
            job_description: Optional job description text for frequency analysis
            
        Returns:
            SkillGapAnalysis with comprehensive gap information
        """
        # Normalize skills to lowercase for comparison
        resume_lower = {s.lower() for s in resume_skills}
        job_lower = {s.lower() for s in job_skills}
        
        # Find matched and missing skills
        matched = sorted(list(resume_lower & job_lower))
        missing = sorted(list(job_lower - resume_lower))
        
        # Calculate match percentage
        total_skills = len(job_lower) if job_lower else 1
        match_percentage = (len(matched) / total_skills * 100) if total_skills > 0 else 0.0
        
        # Categorize gaps
        critical_gaps, medium_gaps, optional_gaps = self._categorize_gaps(missing, job_description)
        
        # Generate recommended learning order
        learning_order = self._generate_learning_order(missing)
        
        # Calculate gap severity
        gap_severity = self._calculate_gap_severity(critical_gaps, medium_gaps, optional_gaps, match_percentage)
        
        return SkillGapAnalysis(
            matched_skills=matched,
            missing_skills=missing,
            match_percentage=round(match_percentage, 1),
            critical_gaps=critical_gaps,
            medium_gaps=medium_gaps,
            optional_gaps=optional_gaps,
            recommended_learning_order=learning_order,
            gap_severity=gap_severity,
        )
    
    def _categorize_gaps(
        self,
        missing_skills: List[str],
        job_description: Optional[str] = None,
    ) -> tuple[List[str], List[str], List[str]]:
        """
        Categorize missing skills into Critical, Medium, and Optional gaps.
        
        Critical Skills:
        - Skills appearing in High Priority category
        - Skills appearing multiple times in job description
        
        Returns:
            Tuple of (critical_gaps, medium_gaps, optional_gaps)
        """
        critical = []
        medium = []
        optional = []
        
        # Count skill frequency in job description
        skill_frequency = Counter()
        if job_description:
            job_desc_lower = job_description.lower()
            for skill in missing_skills:
                skill_frequency[skill] = job_desc_lower.count(skill.lower())
        
        for skill in missing_skills:
            # Check if high priority skill
            if skill in [s.lower() for s in HIGH_PRIORITY_SKILLS]:
                critical.append(skill)
            # Check if appears multiple times in JD
            elif skill_frequency.get(skill, 0) > 1:
                critical.append(skill)
            # Check if medium priority
            elif skill in [s.lower() for s in MEDIUM_PRIORITY_SKILLS]:
                medium.append(skill)
            # Check category importance
            elif self._is_critical_category(skill):
                medium.append(skill)
            else:
                optional.append(skill)
        
        return critical, medium, optional
    
    def _is_critical_category(self, skill: str) -> bool:
        """Check if skill belongs to a critical category."""
        category = categorize_skill(skill)
        critical_categories = [
            SkillCategory.PROGRAMMING_LANGUAGES,
            SkillCategory.BACKEND,
            SkillCategory.DATABASES,
            SkillCategory.CLOUD,
        ]
        return category in critical_categories
    
    def _generate_learning_order(self, missing_skills: List[str]) -> List[str]:
        """
        Generate recommended learning order based on dependencies and difficulty.
        
        Returns:
            Ordered list of skills to learn
        """
        if not missing_skills:
            return []
        
        # Group by difficulty
        easy_skills = []
        medium_skills = []
        hard_skills = []
        
        for skill in missing_skills:
            difficulty = self.skill_difficulty.get(skill.lower(), 3)
            if difficulty <= 2:
                easy_skills.append(skill)
            elif difficulty <= 3:
                medium_skills.append(skill)
            else:
                hard_skills.append(skill)
        
        # Sort within difficulty by dependencies
        def sort_by_dependencies(skills: List[str]) -> List[str]:
            """Sort skills considering dependencies."""
            ordered = []
            remaining = set(skills)
            
            while remaining:
                # Find skills with no unmet dependencies
                ready = []
                for skill in remaining:
                    deps = self.skill_dependencies.get(skill.lower(), [])
                    unmet_deps = [d for d in deps if d in remaining]
                    if not unmet_deps:
                        ready.append(skill)
                
                if not ready:
                    # Circular dependency or missing deps, add remaining
                    ready = list(remaining)
                
                # Add to ordered list
                for skill in ready:
                    ordered.append(skill)
                    remaining.remove(skill)
            
            return ordered
        
        # Combine in order: easy -> medium -> hard
        ordered = []
        ordered.extend(sort_by_dependencies(easy_skills))
        ordered.extend(sort_by_dependencies(medium_skills))
        ordered.extend(sort_by_dependencies(hard_skills))
        
        return ordered
    
    def _calculate_gap_severity(
        self,
        critical: List[str],
        medium: List[str],
        optional: List[str],
        match_percentage: float,
    ) -> str:
        """Calculate overall gap severity."""
        total_missing = len(critical) + len(medium) + len(optional)
        
        if len(critical) > 3 or match_percentage < 40:
            return "high"
        elif len(critical) > 0 or len(medium) > 3 or match_percentage < 60:
            return "medium"
        else:
            return "low"
