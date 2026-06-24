"""
Roadmap Generator Service

Generates personalized learning roadmaps with 7/30/90 day plans.
Provides structured learning paths with milestones and timelines.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class LearningMilestone:
    """Represents a milestone in a learning roadmap."""
    
    title: str
    description: str
    skills: List[str]
    resources: List[str]
    estimated_duration: str


@dataclass
class LearningPlan:
    """Represents a complete learning plan."""
    
    timeline: str  # "7_day", "30_day", "90_day"
    milestones: List[LearningMilestone]
    total_duration: str
    start_date: datetime
    end_date: datetime


class RoadmapGenerator:
    """Generator for personalized learning roadmaps."""
    
    def __init__(self) -> None:
        """Initialize roadmap generator."""
        self.skill_learning_paths = self._load_skill_learning_paths()
    
    def _load_skill_learning_paths(self) -> Dict[str, Dict[str, Any]]:
        """Load learning paths for common skills."""
        return {
            "python": {
                "difficulty": 2,
                "duration_days": 7,
                "resources": [
                    "Python Official Tutorial",
                    "Automate the Boring Stuff with Python",
                    "Real Python",
                ],
                "prerequisites": [],
            },
            "javascript": {
                "difficulty": 2,
                "duration_days": 7,
                "resources": [
                    "MDN JavaScript Guide",
                    "JavaScript.info",
                    "Eloquent JavaScript",
                ],
                "prerequisites": [],
            },
            "react": {
                "difficulty": 2,
                "duration_days": 10,
                "resources": [
                    "React Official Documentation",
                    "React Tutorial",
                    "Build a React App",
                ],
                "prerequisites": ["javascript", "html", "css"],
            },
            "django": {
                "difficulty": 2,
                "duration_days": 10,
                "resources": [
                    "Django Official Tutorial",
                    "Django Girls Tutorial",
                    "Build a Django App",
                ],
                "prerequisites": ["python", "sql"],
            },
            "fastapi": {
                "difficulty": 2,
                "duration_days": 7,
                "resources": [
                    "FastAPI Official Docs",
                    "FastAPI Tutorial",
                    "Build an API with FastAPI",
                ],
                "prerequisites": ["python"],
            },
            "docker": {
                "difficulty": 2,
                "duration_days": 5,
                "resources": [
                    "Docker Official Tutorial",
                    "Docker Documentation",
                    "Docker Compose Guide",
                ],
                "prerequisites": [],
            },
            "kubernetes": {
                "difficulty": 4,
                "duration_days": 14,
                "resources": [
                    "Kubernetes Official Tutorial",
                    "Kubernetes Documentation",
                    "Kubernetes in Action",
                ],
                "prerequisites": ["docker"],
            },
            "aws": {
                "difficulty": 3,
                "duration_days": 14,
                "resources": [
                    "AWS Cloud Practitioner",
                    "AWS Solutions Architect",
                    "AWS Documentation",
                ],
                "prerequisites": [],
            },
            "sql": {
                "difficulty": 2,
                "duration_days": 5,
                "resources": [
                    "SQLBolt",
                    "SQL Tutorial",
                    "PostgreSQL Tutorial",
                ],
                "prerequisites": [],
            },
            "postgresql": {
                "difficulty": 2,
                "duration_days": 7,
                "resources": [
                    "PostgreSQL Official Tutorial",
                    "PostgreSQL Documentation",
                    "Build a Database App",
                ],
                "prerequisites": ["sql"],
            },
            "mongodb": {
                "difficulty": 2,
                "duration_days": 7,
                "resources": [
                    "MongoDB University",
                    "MongoDB Documentation",
                    "Build a NoSQL App",
                ],
                "prerequisites": [],
            },
            "redis": {
                "difficulty": 2,
                "duration_days": 5,
                "resources": [
                    "Redis Documentation",
                    "Redis Tutorial",
                    "Redis in Action",
                ],
                "prerequisites": [],
            },
            "git": {
                "difficulty": 1,
                "duration_days": 3,
                "resources": [
                    "Git Documentation",
                    "GitHub Guides",
                    "Learn Git Branching",
                ],
                "prerequisites": [],
            },
            "typescript": {
                "difficulty": 2,
                "duration_days": 7,
                "resources": [
                    "TypeScript Documentation",
                    "TypeScript Deep Dive",
                    "Build a TypeScript App",
                ],
                "prerequisites": ["javascript"],
            },
            "node.js": {
                "difficulty": 2,
                "duration_days": 7,
                "resources": [
                    "Node.js Documentation",
                    "Node.js Tutorial",
                    "Build a Node.js App",
                ],
                "prerequisites": ["javascript"],
            },
            "graphql": {
                "difficulty": 3,
                "duration_days": 7,
                "resources": [
                    "GraphQL Documentation",
                    "GraphQL Tutorial",
                    "Build a GraphQL API",
                ],
                "prerequisites": ["javascript", "node.js"],
            },
            "pandas": {
                "difficulty": 2,
                "duration_days": 7,
                "resources": [
                    "Pandas Documentation",
                    "Pandas Tutorial",
                    "Data Analysis with Pandas",
                ],
                "prerequisites": ["python"],
            },
            "numpy": {
                "difficulty": 2,
                "duration_days": 5,
                "resources": [
                    "NumPy Documentation",
                    "NumPy Tutorial",
                    "Numerical Python",
                ],
                "prerequisites": ["python"],
            },
            "scikit-learn": {
                "difficulty": 3,
                "duration_days": 14,
                "resources": [
                    "Scikit-learn Documentation",
                    "Machine Learning with Python",
                    "Build ML Models",
                ],
                "prerequisites": ["python", "numpy", "pandas"],
            },
            "tensorflow": {
                "difficulty": 4,
                "duration_days": 21,
                "resources": [
                    "TensorFlow Documentation",
                    "TensorFlow Tutorial",
                    "Deep Learning with TensorFlow",
                ],
                "prerequisites": ["python", "numpy"],
            },
            "pytorch": {
                "difficulty": 4,
                "duration_days": 21,
                "resources": [
                    "PyTorch Documentation",
                    "PyTorch Tutorial",
                    "Deep Learning with PyTorch",
                ],
                "prerequisites": ["python", "numpy"],
            },
        }
    
    def generate_roadmap(
        self,
        missing_skills: List[str],
        target_role: str = "Software Developer",
    ) -> Dict[str, Any]:
        """
        Generate comprehensive learning roadmap with 7/30/90 day plans.
        
        Args:
            missing_skills: List of skills to learn
            target_role: Target career role
            
        Returns:
            Dictionary with 7_day, 30_day, and 90_day plans
        """
        # Sort skills by dependencies and difficulty
        ordered_skills = self._order_skills_by_priority(missing_skills)
        
        # Generate different timeline plans
        roadmap = {
            "7_day": self._generate_7_day_plan(ordered_skills[:3], target_role),
            "30_day": self._generate_30_day_plan(ordered_skills[:6], target_role),
            "90_day": self._generate_90_day_plan(ordered_skills, target_role),
        }
        
        return roadmap
    
    def _order_skills_by_priority(self, skills: List[str]) -> List[str]:
        """Order skills by dependencies and difficulty."""
        if not skills:
            return []
        
        # Group by difficulty
        easy = []
        medium = []
        hard = []
        
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower in self.skill_learning_paths:
                difficulty = self.skill_learning_paths[skill_lower]["difficulty"]
                if difficulty <= 2:
                    easy.append(skill)
                elif difficulty <= 3:
                    medium.append(skill)
                else:
                    hard.append(skill)
            else:
                medium.append(skill)  # Default to medium for unknown skills
        
        # Sort by dependencies within each group
        def sort_with_deps(skill_list: List[str]) -> List[str]:
            ordered = []
            remaining = set(skill_list)
            
            while remaining:
                ready = []
                for skill in remaining:
                    skill_lower = skill.lower()
                    if skill_lower in self.skill_learning_paths:
                        prereqs = self.skill_learning_paths[skill_lower]["prerequisites"]
                        unmet = [p for p in prereqs if p in remaining]
                        if not unmet:
                            ready.append(skill)
                    else:
                        ready.append(skill)
                
                if not ready:
                    ready = list(remaining)
                
                for skill in ready:
                    ordered.append(skill)
                    remaining.remove(skill)
            
            return ordered
        
        # Combine in order
        ordered = []
        ordered.extend(sort_with_deps(easy))
        ordered.extend(sort_with_deps(medium))
        ordered.extend(sort_with_deps(hard))
        
        return ordered
    
    def _generate_7_day_plan(
        self,
        skills: List[str],
        target_role: str,
    ) -> LearningPlan:
        """Generate 7-day learning plan."""
        milestones = []
        current_day = 1
        
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower in self.skill_learning_paths:
                skill_info = self.skill_learning_paths[skill_lower]
                duration = min(skill_info["duration_days"], 7 - current_day + 1)
                
                if current_day <= 7:
                    milestone = LearningMilestone(
                        title=f"Day {current_day}-{current_day + duration - 1}: {skill.title()} Fundamentals",
                        description=f"Learn {skill} basics through tutorials and hands-on practice",
                        skills=[skill],
                        resources=skill_info["resources"],
                        estimated_duration=f"{duration} days",
                    )
                    milestones.append(milestone)
                    current_day += duration
            else:
                if current_day <= 7:
                    milestone = LearningMilestone(
                        title=f"Day {current_day}: {skill.title()} Introduction",
                        description=f"Get started with {skill}",
                        skills=[skill],
                        resources=["Online tutorials", "Documentation"],
                        estimated_duration="1 day",
                    )
                    milestones.append(milestone)
                    current_day += 1
        
        return LearningPlan(
            timeline="7_day",
            milestones=milestones,
            total_duration="7 days",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7),
        )
    
    def _generate_30_day_plan(
        self,
        skills: List[str],
        target_role: str,
    ) -> LearningPlan:
        """Generate 30-day learning plan."""
        milestones = []
        current_day = 1
        
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower in self.skill_learning_paths:
                skill_info = self.skill_learning_paths[skill_lower]
                duration = skill_info["duration_days"]
                
                if current_day + duration <= 30:
                    milestone = LearningMilestone(
                        title=f"Day {current_day}-{current_day + duration - 1}: {skill.title()}",
                        description=f"Master {skill} through comprehensive learning and projects",
                        skills=[skill],
                        resources=skill_info["resources"],
                        estimated_duration=f"{duration} days",
                    )
                    milestones.append(milestone)
                    current_day += duration
            else:
                if current_day <= 30:
                    milestone = LearningMilestone(
                        title=f"Day {current_day}-{min(current_day + 4, 30)}: {skill.title()}",
                        description=f"Learn {skill} fundamentals",
                        skills=[skill],
                        resources=["Online courses", "Documentation"],
                        estimated_duration="5 days",
                    )
                    milestones.append(milestone)
                    current_day += 5
        
        return LearningPlan(
            timeline="30_day",
            milestones=milestones,
            total_duration="30 days",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
        )
    
    def _generate_90_day_plan(
        self,
        skills: List[str],
        target_role: str,
    ) -> LearningPlan:
        """Generate 90-day learning plan with weekly structure."""
        milestones = []
        current_week = 1
        
        # Week 1-2: Fundamentals
        fundamentals = skills[:2]
        for skill in fundamentals:
            milestone = LearningMilestone(
                title=f"Week {current_week}: {skill.title()}",
                description=f"Build strong foundation in {skill}",
                skills=[skill],
                resources=self._get_resources_for_skill(skill),
                estimated_duration="1 week",
            )
            milestones.append(milestone)
            current_week += 1
        
        # Week 3-4: Intermediate skills
        intermediate = skills[2:4]
        for skill in intermediate:
            milestone = LearningMilestone(
                title=f"Week {current_week}: {skill.title()}",
                description=f"Develop intermediate skills in {skill}",
                skills=[skill],
                resources=self._get_resources_for_skill(skill),
                estimated_duration="1 week",
            )
            milestones.append(milestone)
            current_week += 1
        
        # Week 5-8: Advanced skills
        advanced = skills[4:8]
        for skill in advanced:
            milestone = LearningMilestone(
                title=f"Week {current_week}: {skill.title()}",
                description=f"Master advanced concepts in {skill}",
                skills=[skill],
                resources=self._get_resources_for_skill(skill),
                estimated_duration="1 week",
            )
            milestones.append(milestone)
            current_week += 1
        
        # Week 9-12: Projects and integration
        if current_week <= 12:
            milestone = LearningMilestone(
                title=f"Week {current_week}-12: Capstone Project",
                description=f"Build a comprehensive project for {target_role} using all learned skills",
                skills=skills,
                resources=["GitHub Projects", "Portfolio Building"],
                estimated_duration="4 weeks",
            )
            milestones.append(milestone)
        
        return LearningPlan(
            timeline="90_day",
            milestones=milestones,
            total_duration="12 weeks",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(weeks=12),
        )
    
    def _get_resources_for_skill(self, skill: str) -> List[str]:
        """Get learning resources for a skill."""
        skill_lower = skill.lower()
        if skill_lower in self.skill_learning_paths:
            return self.skill_learning_paths[skill_lower]["resources"]
        return ["Online tutorials", "Documentation", "Practice projects"]
