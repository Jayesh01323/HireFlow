"""
Tests for Phase 4 Career Intelligence Services.

Tests for:
- Career Path Predictor
- Roadmap Generator
- Course Recommender
- Career Fit Score Engine
- Skill Gap Engine V2
"""

import pytest

from src.services.career_path_predictor import CareerPathPredictor
from src.services.roadmap_generator import RoadmapGenerator
from src.services.course_recommender import CourseRecommender
from src.services.career_fit_score import CareerFitScoreEngine
from src.services.skill_gap_engine import SkillGapEngine


class TestCareerPathPredictor:
    """Tests for Career Path Predictor service."""
    
    def test_initialization(self):
        """Test that Career Path Predictor initializes correctly."""
        predictor = CareerPathPredictor()
        assert predictor is not None
        assert len(predictor.career_paths) > 0
    
    def test_predict_career_path(self):
        """Test career path prediction."""
        predictor = CareerPathPredictor()
        
        skills = ["python", "javascript", "react", "django"]
        projects = ["E-commerce website", "Blog platform"]
        experience = ["Junior Developer at Tech Corp"]
        
        prediction = predictor.predict_career_path(skills, projects, experience)
        
        assert prediction.top_career_path is not None
        assert isinstance(prediction.alternative_paths, list)
        assert isinstance(prediction.growth_opportunities, list)
        assert isinstance(prediction.recommended_next_steps, list)
        assert isinstance(prediction.career_trajectory, list)
    
    def test_predict_career_path_empty_profile(self):
        """Test career path prediction with empty profile."""
        predictor = CareerPathPredictor()
        
        prediction = predictor.predict_career_path([], [], [])
        
        assert prediction.top_career_path is not None
        assert len(prediction.alternative_paths) >= 0


class TestRoadmapGenerator:
    """Tests for Roadmap Generator service."""
    
    def test_initialization(self):
        """Test that Roadmap Generator initializes correctly."""
        generator = RoadmapGenerator()
        assert generator is not None
        assert len(generator.skill_learning_paths) > 0
    
    def test_generate_roadmap(self):
        """Test roadmap generation."""
        generator = RoadmapGenerator()
        
        missing_skills = ["python", "react", "docker"]
        roadmap = generator.generate_roadmap(missing_skills, "Full Stack Developer")
        
        assert "7_day" in roadmap
        assert "30_day" in roadmap
        assert "90_day" in roadmap
        
        # Check 7-day plan structure
        assert roadmap["7_day"].timeline == "7_day"
        assert len(roadmap["7_day"].milestones) > 0
        assert roadmap["7_day"].total_duration == "7 days"
    
    def test_generate_roadmap_empty_skills(self):
        """Test roadmap generation with empty skills."""
        generator = RoadmapGenerator()
        
        roadmap = generator.generate_roadmap([], "Software Developer")
        
        assert "7_day" in roadmap
        assert "30_day" in roadmap
        assert "90_day" in roadmap


class TestCourseRecommender:
    """Tests for Course Recommender service."""
    
    def test_initialization(self):
        """Test that Course Recommender initializes correctly."""
        recommender = CourseRecommender()
        assert recommender is not None
        assert len(recommender.course_database) > 0
    
    def test_recommend_courses(self):
        """Test course recommendation."""
        recommender = CourseRecommender()
        
        courses = recommender.recommend_courses(
            skills=["python", "react"],
            free_only=True,
            limit=5,
        )
        
        assert isinstance(courses, list)
        assert len(courses) <= 5
        if courses:
            assert all(course.is_free for course in courses)
    
    def test_recommend_courses_by_skill(self):
        """Test getting courses by specific skill."""
        recommender = CourseRecommender()
        
        python_courses = recommender.get_course_by_skill("python")
        
        assert isinstance(python_courses, list)
        assert len(python_courses) > 0
    
    def test_get_free_courses(self):
        """Test getting free courses."""
        recommender = CourseRecommender()
        
        free_courses = recommender.get_free_courses(limit=10)
        
        assert isinstance(free_courses, list)
        assert len(free_courses) <= 10
        assert all(course.is_free for course in free_courses)


class TestCareerFitScoreEngine:
    """Tests for Career Fit Score Engine."""
    
    def test_initialization(self):
        """Test that Career Fit Score Engine initializes correctly."""
        engine = CareerFitScoreEngine()
        assert engine is not None
        assert engine.skill_weights is not None
    
    def test_calculate_fit_score(self):
        """Test career fit score calculation."""
        engine = CareerFitScoreEngine()
        
        skills = ["python", "javascript", "react", "django", "sql"]
        projects = ["E-commerce site", "API backend"]
        experience = ["Junior Developer"]
        education = ["B.Tech in Computer Science"]
        
        fit_score = engine.calculate_fit_score(skills, projects, experience, education)
        
        assert fit_score.overall_score >= 0
        assert fit_score.overall_score <= 100
        assert fit_score.skills_score >= 0
        assert fit_score.projects_score >= 0
        assert fit_score.experience_score >= 0
        assert fit_score.education_score >= 0
        assert fit_score.readiness_level in ["beginner", "intermediate", "advanced", "expert"]
        assert isinstance(fit_score.recommendations, list)
    
    def test_calculate_fit_score_empty_profile(self):
        """Test career fit score with empty profile."""
        engine = CareerFitScoreEngine()
        
        fit_score = engine.calculate_fit_score([], [], [], [])
        
        assert fit_score.overall_score == 0
        assert fit_score.readiness_level == "beginner"


class TestSkillGapEngineV2:
    """Tests for Skill Gap Engine V2."""
    
    def test_initialization(self):
        """Test that Skill Gap Engine V2 initializes correctly."""
        engine = SkillGapEngine()
        assert engine is not None
        assert len(engine.skill_difficulty) > 0
        assert len(engine.skill_dependencies) > 0
    
    def test_analyze_gap(self):
        """Test skill gap analysis."""
        engine = SkillGapEngine()
        
        resume_skills = {"python", "javascript", "react"}
        job_skills = {"python", "javascript", "react", "django", "docker", "aws"}
        
        gap_analysis = engine.analyze_gap(resume_skills, job_skills)
        
        assert gap_analysis.matched_skills is not None
        assert gap_analysis.missing_skills is not None
        assert gap_analysis.match_percentage >= 0
        assert gap_analysis.match_percentage <= 100
        assert isinstance(gap_analysis.critical_gaps, list)
        assert isinstance(gap_analysis.medium_gaps, list)
        assert isinstance(gap_analysis.optional_gaps, list)
        assert isinstance(gap_analysis.recommended_learning_order, list)
        assert gap_analysis.gap_severity in ["low", "medium", "high"]
    
    def test_analyze_gap_no_gaps(self):
        """Test skill gap analysis with no gaps."""
        engine = SkillGapEngine()
        
        resume_skills = {"python", "javascript", "react"}
        job_skills = {"python", "javascript", "react"}
        
        gap_analysis = engine.analyze_gap(resume_skills, job_skills)
        
        assert gap_analysis.match_percentage == 100
        assert len(gap_analysis.missing_skills) == 0
        assert gap_analysis.gap_severity == "low"
    
    def test_analyze_gap_all_missing(self):
        """Test skill gap analysis with all skills missing."""
        engine = SkillGapEngine()
        
        resume_skills = set()
        job_skills = {"python", "javascript", "react", "django"}
        
        gap_analysis = engine.analyze_gap(resume_skills, job_skills)
        
        assert gap_analysis.match_percentage == 0
        assert len(gap_analysis.missing_skills) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
