"""
Job Intelligence Service

Generates AI-powered job intelligence for every job listing.
Combines match analysis, skill gap analysis, and career fit assessment.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

from src.matcher import analyze_match
from src.services.skill_gap_engine import SkillGapEngine
from src.services.skill_categorizer import categorize_skill, SkillCategory

logger = logging.getLogger(__name__)


@dataclass
class JobIntelligence:
    """Result of job intelligence analysis."""
    
    match_score: float
    career_fit: str
    ats_probability: float
    matched_skills: List[str]
    missing_skills: List[str]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    category_analysis: Dict[str, Any]
    gap_severity: str
    priority_skills: List[str]


class JobIntelligenceService:
    """Service for generating comprehensive job intelligence."""
    
    def __init__(self) -> None:
        """Initialize job intelligence service."""
        self.skill_gap_engine = SkillGapEngine()
    
    def generate_intelligence(
        self,
        resume: Dict[str, Any],
        job: Dict[str, Any],
    ) -> JobIntelligence:
        """
        Generate comprehensive job intelligence.
        
        Args:
            resume: Parsed resume data
            job: Job data with description and metadata
            
        Returns:
            JobIntelligence object with complete analysis
        """
        try:
            # Extract job description
            job_description = job.get("description", "")
            
            # Perform match analysis using existing matcher
            match_analysis = analyze_match(resume, job_description)
            match_results = match_analysis["match_results"]
            recommendations = match_analysis["recommendations"]
            
            # Extract skills
            resume_skills = set(match_analysis["resume_skills"])
            job_skills = set(match_analysis["job_skills"])
            
            # Calculate match score
            match_score = match_results.get("weighted_match_percentage", 0.0)
            
            # Determine career fit level
            career_fit = self._determine_career_fit(match_score)
            
            # Calculate ATS probability
            ats_probability = self._calculate_ats_probability(
                match_score,
                len(resume_skills),
                len(job_skills),
            )
            
            # Get matched and missing skills
            matched_skills = sorted(match_results.get("matched_skills", set()))
            missing_skills = sorted(match_results.get("missing_skills", set()))
            
            # Analyze strengths and weaknesses
            strengths, weaknesses = self._analyze_strengths_weaknesses(
                resume_skills,
                job_skills,
                match_analysis.get("category_match", {}),
            )
            
            # Generate improvement recommendations
            improvement_recommendations = self._generate_improvement_recommendations(
                missing_skills,
                weaknesses,
                recommendations,
            )
            
            # Perform skill gap analysis
            gap_analysis = self.skill_gap_engine.analyze_gap(
                resume_skills,
                job_skills,
                job_description,
            )
            
            # Category analysis
            category_analysis = self._analyze_categories(
                match_analysis.get("category_match", {}),
                match_analysis.get("technical_vs_soft", {}),
            )
            
            # Determine gap severity
            gap_severity = self._determine_gap_severity(
                len(missing_skills),
                len(job_skills),
                match_score,
            )
            
            # Priority skills for learning
            priority_skills = self._prioritize_skills(
                missing_skills,
                category_analysis,
            )
            
            return JobIntelligence(
                match_score=match_score,
                career_fit=career_fit,
                ats_probability=ats_probability,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                strengths=strengths,
                weaknesses=weaknesses,
                recommendations=improvement_recommendations,
                category_analysis=category_analysis,
                gap_severity=gap_severity,
                priority_skills=priority_skills,
            )
            
        except Exception as e:
            logger.error(f"Error generating job intelligence: {e}")
            # Return fallback intelligence
            return self._generate_fallback_intelligence(resume, job)
    
    def _determine_career_fit(self, match_score: float) -> str:
        """Determine career fit level based on match score."""
        if match_score >= 80:
            return "Strong Match"
        elif match_score >= 60:
            return "Moderate Match"
        elif match_score >= 40:
            return "Potential Fit"
        else:
            return "Weak Match"
    
    def _calculate_ats_probability(
        self,
        match_score: float,
        resume_skill_count: int,
        job_skill_count: int,
    ) -> float:
        """
        Calculate ATS (Applicant Tracking System) probability.
        
        ATS systems look for keyword matches and skill coverage.
        """
        # Base probability from match score
        base_probability = match_score * 0.7
        
        # Skill coverage bonus
        if job_skill_count > 0:
            coverage_ratio = resume_skill_count / job_skill_count
            coverage_bonus = min(coverage_ratio * 20, 20)
        else:
            coverage_bonus = 0
        
        # ATS probability is slightly conservative
        ats_probability = min(base_probability + coverage_bonus, 95.0)
        
        return round(ats_probability, 1)
    
    def _analyze_strengths_weaknesses(
        self,
        resume_skills: Set[str],
        job_skills: Set[str],
        category_match: Dict[str, Any],
    ) -> tuple[List[str], List[str]]:
        """Analyze strengths and weaknesses based on skill categories."""
        strengths = []
        weaknesses = []
        
        # Analyze by category
        for category, data in category_match.items():
            match_pct = data.get("match_percentage", 0)
            matched = data.get("matched_skills", [])
            missing = data.get("missing_skills", [])
            
            if match_pct >= 70:
                if matched:
                    strengths.append(f"Strong {category} skills: {', '.join(matched[:3])}")
            elif match_pct < 40:
                if missing:
                    weaknesses.append(f"Missing critical {category} skills: {', '.join(missing[:3])}")
        
        # Overall strengths
        if len(resume_skills) > 10:
            strengths.append("Diverse skill set with broad technical knowledge")
        
        if len(resume_skills & job_skills) / len(job_skills) > 0.7:
            strengths.append("High skill alignment with job requirements")
        
        # Overall weaknesses
        missing_critical = {s for s in job_skills if categorize_skill(s) in [
            SkillCategory.PROGRAMMING_LANGUAGES,
            SkillCategory.DATABASES,
            SkillCategory.CLOUD,
        ]}
        if missing_critical:
            weaknesses.append(f"Missing critical technical skills: {', '.join(list(missing_critical)[:3])}")
        
        return strengths[:5], weaknesses[:5]
    
    def _generate_improvement_recommendations(
        self,
        missing_skills: List[str],
        weaknesses: List[str],
        existing_recommendations: Dict[str, Any],
    ) -> List[str]:
        """Generate actionable improvement recommendations."""
        recommendations = []
        
        # Add learning recommendations from existing engine
        learning_recs = existing_recommendations.get("learning_recommendations", [])
        if learning_recs:
            recommendations.extend(learning_recs[:3])
        
        # Add project recommendations
        if missing_skills:
            top_missing = missing_skills[:3]
            recommendations.append(f"Build projects showcasing: {', '.join(top_missing)}")
        
        # Add certification recommendations
        if weaknesses:
            recommendations.append("Consider certifications for missing core skills")
        
        # Add resume optimization
        recommendations.append("Optimize resume with relevant keywords from job description")
        
        return recommendations[:5]
    
    def _analyze_categories(
        self,
        category_match: Dict[str, Any],
        tech_vs_soft: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze skill categories and technical vs soft skill balance."""
        analysis = {
            "category_breakdown": category_match,
            "technical_match": tech_vs_soft.get("technical_match_percentage", 0),
            "soft_skill_match": tech_vs_soft.get("soft_skill_match_percentage", 0),
            "strongest_categories": [],
            "weakest_categories": [],
        }
        
        # Find strongest and weakest categories
        sorted_categories = sorted(
            category_match.items(),
            key=lambda x: x[1].get("match_percentage", 0),
            reverse=True,
        )
        
        if sorted_categories:
            analysis["strongest_categories"] = [
                cat for cat, _ in sorted_categories[:2]
            ]
            analysis["weakest_categories"] = [
                cat for cat, _ in sorted_categories[-2:]
            ]
        
        return analysis
    
    def _determine_gap_severity(
        self,
        missing_count: int,
        total_job_skills: int,
        match_score: float,
    ) -> str:
        """Determine severity of skill gap."""
        if total_job_skills == 0:
            return "low"
        
        missing_ratio = missing_count / total_job_skills
        
        if missing_ratio > 0.5 or match_score < 40:
            return "high"
        elif missing_ratio > 0.3 or match_score < 60:
            return "medium"
        else:
            return "low"
    
    def _prioritize_skills(
        self,
        missing_skills: List[str],
        category_analysis: Dict[str, Any],
    ) -> List[str]:
        """Prioritize missing skills for learning."""
        # Prioritize by category importance
        priority_order = [
            SkillCategory.PROGRAMMING_LANGUAGES.value,
            SkillCategory.DATABASES.value,
            SkillCategory.CLOUD.value,
            SkillCategory.BACKEND.value,
            SkillCategory.FRONTEND.value,
        ]
        
        prioritized = []
        for category in priority_order:
            category_skills = [
                skill for skill in missing_skills
                if categorize_skill(skill).value == category
            ]
            prioritized.extend(category_skills)
        
        # Add remaining skills
        remaining = [
            skill for skill in missing_skills
            if skill not in prioritized
        ]
        prioritized.extend(remaining)
        
        return prioritized[:10]
    
    def _generate_fallback_intelligence(
        self,
        resume: Dict[str, Any],
        job: Dict[str, Any],
    ) -> JobIntelligence:
        """Generate fallback intelligence when analysis fails."""
        return JobIntelligence(
            match_score=0.0,
            career_fit="Unable to Determine",
            ats_probability=0.0,
            matched_skills=[],
            missing_skills=[],
            strengths=["Analysis unavailable"],
            weaknesses=["Analysis unavailable"],
            recommendations=["Please try again with complete resume and job data"],
            category_analysis={},
            gap_severity="unknown",
            priority_skills=[],
        )
