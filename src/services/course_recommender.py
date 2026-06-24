"""
Course Recommender Service

Recommends learning courses based on skill gaps and learning goals.
Uses local dataset of free courses and resources.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class Course:
    """Represents a learning course."""
    
    title: str
    platform: str
    url: str
    duration: str
    difficulty: str  # beginner, intermediate, advanced
    skills: List[str]
    rating: float
    is_free: bool


class CourseRecommender:
    """Recommender for learning courses based on skills."""
    
    def __init__(self) -> None:
        """Initialize course recommender with local dataset."""
        self.course_database = self._load_course_database()
    
    def _load_course_database(self) -> List[Course]:
        """Load local course database."""
        return [
            # Python Courses
            Course(
                title="Python for Everybody",
                platform="Coursera",
                url="https://www.coursera.org/learn/python",
                duration="6 weeks",
                difficulty="beginner",
                skills=["python"],
                rating=4.8,
                is_free=True,
            ),
            Course(
                title="Automate the Boring Stuff with Python",
                platform="Udemy",
                url="https://www.udemy.com/course/automate-the-boring-stuff-with-python/",
                duration="9 hours",
                difficulty="beginner",
                skills=["python"],
                rating=4.7,
                is_free=True,
            ),
            Course(
                title="Complete Python Bootcamp",
                platform="Udemy",
                url="https://www.udemy.com/course/complete-python-bootcamp/",
                duration="22 hours",
                difficulty="beginner",
                skills=["python"],
                rating=4.6,
                is_free=False,
            ),
            Course(
                title="Python for Data Science",
                platform="Coursera",
                url="https://www.coursera.org/professional-certificates/ibm-data-science",
                duration="3 months",
                difficulty="intermediate",
                skills=["python", "pandas", "numpy"],
                rating=4.7,
                is_free=True,
            ),
            # JavaScript Courses
            Course(
                title="JavaScript.info",
                platform="FreeCodeCamp",
                url="https://javascript.info/",
                duration="Self-paced",
                difficulty="beginner",
                skills=["javascript"],
                rating=4.9,
                is_free=True,
            ),
            Course(
                title="JavaScript Algorithms and Data Structures",
                platform="FreeCodeCamp",
                url="https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/",
                duration="300 hours",
                difficulty="intermediate",
                skills=["javascript"],
                rating=4.8,
                is_free=True,
            ),
            Course(
                title="The Complete JavaScript Course",
                platform="Udemy",
                url="https://www.udemy.com/course/the-complete-javascript-course/",
                duration="42 hours",
                difficulty="intermediate",
                skills=["javascript"],
                rating=4.7,
                is_free=False,
            ),
            # React Courses
            Course(
                title="React - The Complete Guide",
                platform="Udemy",
                url="https://www.udemy.com/course/react-the-complete-guide-incl-redux/",
                duration="48 hours",
                difficulty="intermediate",
                skills=["react", "javascript"],
                rating=4.8,
                is_free=False,
            ),
            Course(
                title="React Tutorial",
                platform="React Official",
                url="https://react.dev/learn",
                duration="Self-paced",
                difficulty="beginner",
                skills=["react", "javascript"],
                rating=4.9,
                is_free=True,
            ),
            Course(
                title="Modern React with Redux",
                platform="Udemy",
                url="https://www.udemy.com/course/react-redux/",
                duration="22 hours",
                difficulty="intermediate",
                skills=["react", "redux", "javascript"],
                rating=4.7,
                is_free=False,
            ),
            # Django Courses
            Course(
                title="Django for Everybody",
                platform="Coursera",
                url="https://www.coursera.org/specializations/django",
                duration="4 months",
                difficulty="intermediate",
                skills=["django", "python"],
                rating=4.6,
                is_free=True,
            ),
            Course(
                title="Django Official Tutorial",
                platform="Django Project",
                url="https://docs.djangoproject.com/en/stable/intro/tutorial01/",
                duration="Self-paced",
                difficulty="beginner",
                skills=["django", "python"],
                rating=4.9,
                is_free=True,
            ),
            Course(
                title="Python and Django Full Stack Web Developer Bootcamp",
                platform="Udemy",
                url="https://www.udemy.com/course/python-and-django-full-stack-web-developer-bootcamp/",
                duration="32 hours",
                difficulty="intermediate",
                skills=["django", "python", "sql"],
                rating=4.6,
                is_free=False,
            ),
            # FastAPI Courses
            Course(
                title="FastAPI Official Tutorial",
                platform="FastAPI Docs",
                url="https://fastapi.tiangolo.com/tutorial/",
                duration="Self-paced",
                difficulty="beginner",
                skills=["fastapi", "python"],
                rating=4.9,
                is_free=True,
            ),
            Course(
                title="Build a REST API with FastAPI",
                platform="Real Python",
                url="https://realpython.com/fastapi-python-web-apis/",
                duration="2 hours",
                difficulty="intermediate",
                skills=["fastapi", "python"],
                rating=4.8,
                is_free=True,
            ),
            # Docker Courses
            Course(
                title="Docker for the Absolute Beginner",
                platform="Udemy",
                url="https://www.udemy.com/course/docker-for-the-absolute-beginner/",
                duration="2 hours",
                difficulty="beginner",
                skills=["docker"],
                rating=4.6,
                is_free=True,
            ),
            Course(
                title="Docker Official Tutorial",
                platform="Docker Docs",
                url="https://docs.docker.com/get-started/",
                duration="Self-paced",
                difficulty="beginner",
                skills=["docker"],
                rating=4.9,
                is_free=True,
            ),
            Course(
                title="Docker Mastery",
                platform="Udemy",
                url="https://www.udemy.com/course/docker-mastery/",
                duration="10 hours",
                difficulty="intermediate",
                skills=["docker"],
                rating=4.7,
                is_free=False,
            ),
            # Kubernetes Courses
            Course(
                title="Kubernetes Official Tutorial",
                platform="Kubernetes Docs",
                url="https://kubernetes.io/docs/tutorials/",
                duration="Self-paced",
                difficulty="intermediate",
                skills=["kubernetes", "docker"],
                rating=4.9,
                is_free=True,
            ),
            Course(
                title="Kubernetes for the Absolute Beginner",
                platform="Udemy",
                url="https://www.udemy.com/course/kubernetes-for-the-absolute-beginner-hands-on/",
                duration="4 hours",
                difficulty="beginner",
                skills=["kubernetes", "docker"],
                rating=4.6,
                is_free=True,
            ),
            # AWS Courses
            Course(
                title="AWS Cloud Practitioner",
                platform="AWS Training",
                url="https://aws.amazon.com/training/cloud-practitioner/",
                duration="Self-paced",
                difficulty="beginner",
                skills=["aws"],
                rating=4.8,
                is_free=True,
            ),
            Course(
                title="AWS Solutions Architect",
                platform="AWS Training",
                url="https://aws.amazon.com/training/solutions-architect/",
                duration="Self-paced",
                difficulty="intermediate",
                skills=["aws"],
                rating=4.7,
                is_free=True,
            ),
            Course(
                title="Ultimate AWS Certified Solutions Architect",
                platform="Udemy",
                url="https://www.udemy.com/course/aws-certified-solutions-architect-associate/",
                duration="18 hours",
                difficulty="intermediate",
                skills=["aws"],
                rating=4.8,
                is_free=False,
            ),
            # SQL Courses
            Course(
                title="SQLBolt",
                platform="SQLBolt",
                url="https://sqlbolt.com/",
                duration="Self-paced",
                difficulty="beginner",
                skills=["sql"],
                rating=4.8,
                is_free=True,
            ),
            Course(
                title="SQL Tutorial",
                platform="W3Schools",
                url="https://www.w3schools.com/sql/",
                duration="Self-paced",
                difficulty="beginner",
                skills=["sql"],
                rating=4.7,
                is_free=True,
            ),
            Course(
                title="PostgreSQL Tutorial",
                platform="PostgreSQL Tutorial",
                url="https://www.postgresqltutorial.com/",
                duration="Self-paced",
                difficulty="beginner",
                skills=["postgresql", "sql"],
                rating=4.8,
                is_free=True,
            ),
            # MongoDB Courses
            Course(
                title="MongoDB University",
                platform="MongoDB",
                url="https://university.mongodb.com/",
                duration="Self-paced",
                difficulty="beginner",
                skills=["mongodb"],
                rating=4.8,
                is_free=True,
            ),
            Course(
                title="MongoDB Tutorial",
                platform="MongoDB Docs",
                url="https://www.mongodb.com/docs/manual/tutorial/",
                duration="Self-paced",
                difficulty="beginner",
                skills=["mongodb"],
                rating=4.9,
                is_free=True,
            ),
            # Git Courses
            Course(
                title="Git Documentation",
                platform="Git",
                url="https://git-scm.com/doc",
                duration="Self-paced",
                difficulty="beginner",
                skills=["git"],
                rating=4.9,
                is_free=True,
            ),
            Course(
                title="Learn Git Branching",
                platform="Learn Git Branching",
                url="https://learngitbranching.js.org/",
                duration="Self-paced",
                difficulty="beginner",
                skills=["git"],
                rating=4.9,
                is_free=True,
            ),
            Course(
                title="GitHub Guides",
                platform="GitHub",
                url="https://guides.github.com/",
                duration="Self-paced",
                difficulty="beginner",
                skills=["git"],
                rating=4.8,
                is_free=True,
            ),
            # TypeScript Courses
            Course(
                title="TypeScript Documentation",
                platform="TypeScript",
                url="https://www.typescriptlang.org/docs/",
                duration="Self-paced",
                difficulty="beginner",
                skills=["typescript", "javascript"],
                rating=4.9,
                is_free=True,
            ),
            Course(
                title="TypeScript Deep Dive",
                platform="TypeScript Deep Dive",
                url="https://basarat.gitbook.io/typescript/",
                duration="Self-paced",
                difficulty="intermediate",
                skills=["typescript", "javascript"],
                rating=4.8,
                is_free=True,
            ),
            # Node.js Courses
            Course(
                title="Node.js Documentation",
                platform="Node.js",
                url="https://nodejs.org/en/docs/",
                duration="Self-paced",
                difficulty="beginner",
                skills=["node.js", "javascript"],
                rating=4.9,
                is_free=True,
            ),
            Course(
                title="The Complete Node.js Developer Course",
                platform="Udemy",
                url="https://www.udemy.com/course/the-complete-nodejs-developer-course-2/",
                duration="44 hours",
                difficulty="intermediate",
                skills=["node.js", "javascript"],
                rating=4.7,
                is_free=False,
            ),
            # GraphQL Courses
            Course(
                title="GraphQL Documentation",
                platform="GraphQL",
                url="https://graphql.org/learn/",
                duration="Self-paced",
                difficulty="beginner",
                skills=["graphql"],
                rating=4.9,
                is_free=True,
            ),
            Course(
                title="GraphQL Tutorial",
                platform="GraphQL Tutorial",
                url="https://www.howtographql.com/",
                duration="Self-paced",
                difficulty="beginner",
                skills=["graphql", "javascript"],
                rating=4.8,
                is_free=True,
            ),
            # Data Science Courses
            Course(
                title="Pandas Documentation",
                platform="Pandas",
                url="https://pandas.pydata.org/docs/",
                duration="Self-paced",
                difficulty="intermediate",
                skills=["pandas", "python"],
                rating=4.9,
                is_free=True,
            ),
            Course(
                title="NumPy Documentation",
                platform="NumPy",
                url="https://numpy.org/doc/",
                duration="Self-paced",
                difficulty="intermediate",
                skills=["numpy", "python"],
                rating=4.9,
                is_free=True,
            ),
            Course(
                title="Scikit-learn Documentation",
                platform="Scikit-learn",
                url="https://scikit-learn.org/stable/documentation.html",
                duration="Self-paced",
                difficulty="intermediate",
                skills=["scikit-learn", "python"],
                rating=4.9,
                is_free=True,
            ),
            Course(
                title="TensorFlow Documentation",
                platform="TensorFlow",
                url="https://www.tensorflow.org/learn",
                duration="Self-paced",
                difficulty="advanced",
                skills=["tensorflow", "python"],
                rating=4.8,
                is_free=True,
            ),
            Course(
                title="PyTorch Documentation",
                platform="PyTorch",
                url="https://pytorch.org/docs/",
                duration="Self-paced",
                difficulty="advanced",
                skills=["pytorch", "python"],
                rating=4.8,
                is_free=True,
            ),
        ]
    
    def recommend_courses(
        self,
        skills: List[str],
        difficulty: str = "any",
        free_only: bool = False,
        limit: int = 5,
    ) -> List[Course]:
        """
        Recommend courses based on skills.
        
        Args:
            skills: List of skills to learn
            difficulty: Filter by difficulty (beginner, intermediate, advanced, any)
            free_only: Only return free courses
            limit: Maximum number of courses to return
            
        Returns:
            List of recommended courses
        """
        recommendations = []
        skills_lower = [s.lower() for s in skills]
        
        for course in self.course_database:
            # Check if course covers any of the skills
            course_skills_lower = [s.lower() for s in course.skills]
            if not any(skill in course_skills_lower for skill in skills_lower):
                continue
            
            # Filter by difficulty
            if difficulty != "any" and course.difficulty != difficulty:
                continue
            
            # Filter by free only
            if free_only and not course.is_free:
                continue
            
            recommendations.append(course)
        
        # Sort by rating and limit
        recommendations.sort(key=lambda x: x.rating, reverse=True)
        return recommendations[:limit]
    
    def get_course_by_skill(self, skill: str, difficulty: str = "any") -> List[Course]:
        """Get all courses for a specific skill."""
        skill_lower = skill.lower()
        courses = []
        
        for course in self.course_database:
            if skill_lower in [s.lower() for s in course.skills]:
                if difficulty == "any" or course.difficulty == difficulty:
                    courses.append(course)
        
        return courses
    
    def get_free_courses(self, limit: int = 10) -> List[Course]:
        """Get all free courses."""
        free_courses = [c for c in self.course_database if c.is_free]
        free_courses.sort(key=lambda x: x.rating, reverse=True)
        return free_courses[:limit]
