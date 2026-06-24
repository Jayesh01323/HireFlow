"""
Skill Gap Analyzer Module

Integrates skill gap analysis with job discovery.
Analyzes skill gaps between resume and job requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set

from src.jobs.job_matcher import JobMatcher
from src.matcher import extract_job_skills, extract_resume_skills

logger = logging.getLogger(__name__)


class SkillGapAnalyzer:
    """Analyzes skill gaps between resume and job requirements."""
    
    def __init__(self, job_matcher: Optional[JobMatcher] = None) -> None:
        """Initialize skill gap analyzer.
        
        Args:
            job_matcher: Job matcher instance for resume-job matching
        """
        self.job_matcher = job_matcher or JobMatcher()
    
    def analyze_skill_gap(
        self,
        parsed_resume: Dict[str, Any],
        job_description: str,
    ) -> Dict[str, Any]:
        """Analyze skill gap between resume and job description.
        
        Args:
            parsed_resume: Parsed resume data
            job_description: Job description text
            
        Returns:
            Detailed skill gap analysis
        """
        # Extract skills
        resume_skills = extract_resume_skills(parsed_resume)
        job_skills = extract_job_skills(job_description)
        
        # Calculate skill gap
        missing_skills = job_skills - resume_skills
        matched_skills = resume_skills & job_skills
        
        # Calculate gap percentage
        if job_skills:
            gap_percentage = (len(missing_skills) / len(job_skills)) * 100
        else:
            gap_percentage = 0.0
        
        # Categorize skills
        skill_categories = self._categorize_skills(missing_skills, job_description)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(missing_skills, skill_categories)
        
        return {
            "resume_skills": list(resume_skills),
            "job_skills": list(job_skills),
            "matched_skills": list(matched_skills),
            "missing_skills": list(missing_skills),
            "gap_percentage": gap_percentage,
            "match_percentage": 100 - gap_percentage,
            "skill_categories": skill_categories,
            "recommendations": recommendations,
            "priority": self._calculate_priority(gap_percentage, len(missing_skills)),
        }
    
    def _categorize_skills(self, missing_skills: Set[str], job_description: str) -> Dict[str, List[str]]:
        """Categorize missing skills by type.
        
        Args:
            missing_skills: Set of missing skills
            job_description: Job description for context
            
        Returns:
            Dictionary mapping skill categories to skill lists
        """
        categories = {
            "programming_languages": [],
            "frameworks_libraries": [],
            "tools_platforms": [],
            "soft_skills": [],
            "domain_knowledge": [],
        }
        
        # Skill categorization keywords
        programming_keywords = ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'swift', 'kotlin', 'php', 'ruby']
        framework_keywords = ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'rails', 'laravel', 'next.js', 'nuxt']
        tool_keywords = ['docker', 'kubernetes', 'git', 'jenkins', 'aws', 'azure', 'gcp', 'linux', 'webpack', 'babel']
        soft_skill_keywords = ['communication', 'leadership', 'teamwork', 'problem-solving', 'analytical', 'collaboration']
        
        for skill in missing_skills:
            skill_lower = skill.lower()
            
            if any(kw in skill_lower for kw in programming_keywords):
                categories["programming_languages"].append(skill)
            elif any(kw in skill_lower for kw in framework_keywords):
                categories["frameworks_libraries"].append(skill)
            elif any(kw in skill_lower for kw in tool_keywords):
                categories["tools_platforms"].append(skill)
            elif any(kw in skill_lower for kw in soft_skill_keywords):
                categories["soft_skills"].append(skill)
            else:
                categories["domain_knowledge"].append(skill)
        
        return categories
    
    def _generate_recommendations(
        self,
        missing_skills: Set[str],
        skill_categories: Dict[str, List[str]],
    ) -> List[Dict[str, Any]]:
        """Generate learning recommendations for missing skills.
        
        Args:
            missing_skills: Set of missing skills
            skill_categories: Categorized skills
            
        Returns:
            List of recommendation objects
        """
        recommendations = []
        
        # Prioritize programming languages and frameworks
        high_priority = skill_categories.get("programming_languages", []) + skill_categories.get("frameworks_libraries", [])
        medium_priority = skill_categories.get("tools_platforms", [])
        low_priority = skill_categories.get("soft_skills", []) + skill_categories.get("domain_knowledge", [])
        
        for skill in high_priority[:5]:
            recommendations.append({
                "skill": skill,
                "priority": "high",
                "estimated_time": self._estimate_learning_time(skill),
                "resources": self._get_learning_resources(skill),
            })
        
        for skill in medium_priority[:3]:
            recommendations.append({
                "skill": skill,
                "priority": "medium",
                "estimated_time": self._estimate_learning_time(skill),
                "resources": self._get_learning_resources(skill),
            })
        
        for skill in low_priority[:2]:
            recommendations.append({
                "skill": skill,
                "priority": "low",
                "estimated_time": self._estimate_learning_time(skill),
                "resources": self._get_learning_resources(skill),
            })
        
        return recommendations
    
    def _estimate_learning_time(self, skill: str) -> str:
        """Estimate learning time for a skill.
        
        Args:
            skill: Skill name
            
        Returns:
            Estimated learning time string
        """
        # Simple estimation based on skill complexity
        skill_lower = skill.lower()
        
        if skill_lower in ['python', 'javascript', 'git']:
            return "2-4 weeks"
        elif skill_lower in ['java', 'c++', 'react', 'docker']:
            return "4-8 weeks"
        elif skill_lower in ['kubernetes', 'aws', 'machine learning']:
            return "8-12 weeks"
        else:
            return "4-6 weeks"
    
    def _get_learning_resources(self, skill: str) -> List[str]:
        """Get learning resources for a skill.
        
        Args:
            skill: Skill name
            
        Returns:
            List of resource names/URLs
        """
        skill_lower = skill.lower()
        
        # Common learning resources
        resources = {
            'python': ['Coursera Python for Everybody', 'FreeCodeCamp', 'Real Python'],
            'javascript': ['MDN Web Docs', 'JavaScript.info', 'FreeCodeCamp'],
            'react': ['React Documentation', 'React Tutorial', 'Egghead.io'],
            'docker': ['Docker Documentation', 'Docker Tutorial', 'Udemy Docker Course'],
            'aws': ['AWS Certification Prep', 'AWS Documentation', 'A Cloud Guru'],
        }
        
        return resources.get(skill_lower, ['Official Documentation', 'Online Courses', 'YouTube Tutorials'])
    
    def _calculate_priority(self, gap_percentage: float, missing_count: int) -> str:
        """Calculate overall priority level.
        
        Args:
            gap_percentage: Skill gap percentage
            missing_count: Number of missing skills
            
        Returns:
            Priority level string
        """
        if gap_percentage > 50 or missing_count > 10:
            return "critical"
        elif gap_percentage > 30 or missing_count > 5:
            return "high"
        elif gap_percentage > 15 or missing_count > 2:
            return "medium"
        else:
            return "low"
    
    def analyze_skill_gaps_for_jobs(
        self,
        parsed_resume: Dict[str, Any],
        jobs: List[Any],
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Analyze skill gaps for multiple jobs.
        
        Args:
            parsed_resume: Parsed resume data
            jobs: List of jobs to analyze
            limit: Maximum number of results
            
        Returns:
            List of skill gap analyses sorted by match percentage
        """
        gap_analyses = []
        
        for job in jobs:
            job_description = getattr(job, 'description', '')
            if not job_description:
                continue
            
            analysis = self.analyze_skill_gap(parsed_resume, job_description)
            
            gap_analysis = {
                "job_id": getattr(job, 'id', None),
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "url": job.url,
                "source": job.source,
                "match_percentage": analysis["match_percentage"],
                "gap_percentage": analysis["gap_percentage"],
                "matched_skills": analysis["matched_skills"],
                "missing_skills": analysis["missing_skills"],
                "priority": analysis["priority"],
                "recommendations": analysis["recommendations"],
            }
            
            gap_analyses.append(gap_analysis)
        
        # Sort by match percentage (highest first)
        gap_analyses.sort(key=lambda x: x["match_percentage"], reverse=True)
        
        return gap_analyses[:limit]
    
    def get_skill_gap_summary(
        self,
        parsed_resume: Dict[str, Any],
        job_descriptions: List[str],
    ) -> Dict[str, Any]:
        """Get summary of skill gaps across multiple job descriptions.
        
        Args:
            parsed_resume: Parsed resume data
            job_descriptions: List of job description texts
            
        Returns:
            Summary of common skill gaps
        """
        all_missing_skills: Set[str] = set()
        skill_frequency: Dict[str, int] = {}
        
        for job_desc in job_descriptions:
            analysis = self.analyze_skill_gap(parsed_resume, job_desc)
            for skill in analysis["missing_skills"]:
                all_missing_skills.add(skill)
                skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
        
        # Sort skills by frequency
        sorted_skills = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_jobs_analyzed": len(job_descriptions),
            "total_missing_skills": len(all_missing_skills),
            "most_common_gaps": sorted_skills[:10],
            "all_missing_skills": list(all_missing_skills),
        }
