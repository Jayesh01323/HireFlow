"""
Database Models Module

SQLAlchemy-ready ORM models for HireFlow AI database.
Defines tables: users, resumes, jobs, job_matches, applications, alerts.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class User(Base):
    """User account model for authentication and preferences."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    resumes: Mapped[list["Resume"]] = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    applications: Mapped[list["Application"]] = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    saved_jobs: Mapped[list["SavedJob"]] = relationship("SavedJob", back_populates="user", cascade="all, delete-orphan")
    career_fits: Mapped[list["CareerFit"]] = relationship("CareerFit", back_populates="user", cascade="all, delete-orphan")
    career_conversations: Mapped[list["CareerConversation"]] = relationship("CareerConversation", back_populates="user", cascade="all, delete-orphan")
    learning_roadmaps: Mapped[list["LearningRoadmap"]] = relationship("LearningRoadmap", back_populates="user", cascade="all, delete-orphan")
    career_paths: Mapped[list["CareerPath"]] = relationship("CareerPath", back_populates="user", cascade="all, delete-orphan")
    career_fit_scores: Mapped[list["CareerFitScore"]] = relationship("CareerFitScore", back_populates="user", cascade="all, delete-orphan")


class Resume(Base):
    """Resume model for storing parsed resume data."""
    
    __tablename__ = "resumes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="resumes")
    job_matches: Mapped[list["JobMatch"]] = relationship("JobMatch", back_populates="resume", cascade="all, delete-orphan")


class Job(Base):
    """Job posting model for storing job listings from various sources."""
    
    __tablename__ = "jobs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    remote: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    salary_min: Mapped[Optional[int]] = mapped_column(Integer)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer)
    experience_min: Mapped[Optional[int]] = mapped_column(Integer)  # years
    experience_max: Mapped[Optional[int]] = mapped_column(Integer)  # years
    required_skills: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    description: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # linkedin, internshala, etc.
    source_job_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)  # ID from source platform
    apply_url: Mapped[str] = mapped_column(String(500), nullable=False)
    posted_date: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Legacy fields for backward compatibility
    salary: Mapped[Optional[str]] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    external_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False)
    experience_level: Mapped[Optional[str]] = mapped_column(String(50))
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    job_matches: Mapped[list["JobMatch"]] = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")
    applications: Mapped[list["Application"]] = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    job_skills: Mapped[list["JobSkill"]] = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")


class JobMatch(Base):
    """Job match model for storing resume-job matching results."""
    
    __tablename__ = "job_matches"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resume_id: Mapped[int] = mapped_column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id"), nullable=False)
    match_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    weighted_match_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    technical_match_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    soft_skill_match_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    matched_skills: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    missing_skills: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    recommendations: Mapped[Optional[str]] = mapped_column(Text)  # JSON object
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resume: Mapped["Resume"] = relationship("Resume", back_populates="job_matches")
    job: Mapped["Job"] = relationship("Job", back_populates="job_matches")


class Application(Base):
    """Application tracking model for job application status."""
    
    __tablename__ = "applications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("resumes.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="saved")  # saved, applied, interview, offer, rejected
    notes: Mapped[Optional[str]] = mapped_column(Text)
    applied_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="applications")
    job: Mapped["Job"] = relationship("Job", back_populates="applications")


class Alert(Base):
    """Alert model for job notifications and updates."""
    
    __tablename__ = "alerts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)  # new_job, application_update, skill_gap
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    alert_metadata: Mapped[Optional[str]] = mapped_column(Text)  # JSON object for additional data
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="alerts")


class SavedJob(Base):
    """Saved job model for bookmarking job opportunities."""
    
    __tablename__ = "saved_jobs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    job_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)  # External job ID from Job schema
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    salary: Mapped[Optional[str]] = mapped_column(String(255))
    work_mode: Mapped[Optional[str]] = mapped_column(String(50))
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    saved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="saved_jobs")


class CareerFit(Base):
    """Career fit model for storing career path analysis results."""
    
    __tablename__ = "career_fits"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    career_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    skills_match: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    projects_match: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    experience_match: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    recommendations: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="career_fits")


class ResumeOptimization(Base):
    """Resume optimization model for storing optimization recommendations."""
    
    __tablename__ = "resume_optimizations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resume_id: Mapped[int] = mapped_column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("jobs.id"), nullable=True)
    add_skills: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    add_projects: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    rewrite_summary: Mapped[Optional[str]] = mapped_column(Text)
    highlight_experience: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    ats_improvements: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    overall_recommendation: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resume: Mapped["Resume"] = relationship("Resume")
    job: Mapped[Optional["Job"]] = relationship("Job")


class CareerConversation(Base):
    """Career conversation model for storing AI career copilot interactions."""
    
    __tablename__ = "career_conversations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[Optional[str]] = mapped_column(Text)  # JSON - context data used
    conversation_type: Mapped[Optional[str]] = mapped_column(String(50))  # job_advice, skill_gap, career_path, etc.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="career_conversations")


class JobIntelligence(Base):
    """Job intelligence model for storing AI-powered job analysis results."""
    
    __tablename__ = "job_intelligence"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id: Mapped[int] = mapped_column(Integer, ForeignKey("resumes.id"), nullable=False)
    match_score: Mapped[float] = mapped_column(Float, nullable=False)
    career_fit: Mapped[str] = mapped_column(String(50), nullable=False)  # Strong Match, Moderate Match, Weak Match
    ats_probability: Mapped[float] = mapped_column(Float, nullable=False)
    strengths: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    weaknesses: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    recommendations: Mapped[Optional[str]] = mapped_column(Text)  # JSON object
    matched_skills: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    missing_skills: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    job: Mapped["Job"] = relationship("Job")
    resume: Mapped["Resume"] = relationship("Resume")


class LearningRoadmap(Base):
    """Learning roadmap model for storing personalized learning plans."""
    
    __tablename__ = "learning_roadmaps"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    resume_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("resumes.id"), nullable=True)
    target_role: Mapped[str] = mapped_column(String(255), nullable=False)
    timeline: Mapped[str] = mapped_column(String(50), nullable=False)  # 7_day, 30_day, 90_day
    roadmap_data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON - milestones and details
    missing_skills: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    start_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="learning_roadmaps")
    resume: Mapped[Optional["Resume"]] = relationship("Resume")


class CareerPath(Base):
    """Career path model for storing career trajectory predictions."""
    
    __tablename__ = "career_paths"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    resume_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("resumes.id"), nullable=True)
    top_career_path: Mapped[str] = mapped_column(String(255), nullable=False)
    alternative_paths: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    growth_opportunities: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    recommended_next_steps: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    career_trajectory: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="career_paths")
    resume: Mapped[Optional["Resume"]] = relationship("Resume")


class CourseRecommendation(Base):
    """Course recommendation model for storing personalized course suggestions."""
    
    __tablename__ = "course_recommendations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    skill: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    course_title: Mapped[str] = mapped_column(String(255), nullable=False)
    platform: Mapped[str] = mapped_column(String(255), nullable=False)
    course_url: Mapped[str] = mapped_column(String(500), nullable=False)
    duration: Mapped[Optional[str]] = mapped_column(String(100))
    difficulty: Mapped[Optional[str]] = mapped_column(String(50))
    rating: Mapped[Optional[float]] = mapped_column(Float)
    is_free: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User")


class CareerFitScore(Base):
    """Career fit score model for storing overall career readiness scores."""
    
    __tablename__ = "career_fit_scores"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    resume_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("resumes.id"), nullable=True)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    skills_score: Mapped[float] = mapped_column(Float, nullable=False)
    projects_score: Mapped[float] = mapped_column(Float, nullable=False)
    experience_score: Mapped[float] = mapped_column(Float, nullable=False)
    education_score: Mapped[float] = mapped_column(Float, nullable=False)
    readiness_level: Mapped[str] = mapped_column(String(50), nullable=False)  # beginner, intermediate, advanced, expert
    breakdown: Mapped[Optional[str]] = mapped_column(Text)  # JSON - detailed breakdown
    recommendations: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="career_fit_scores")
    resume: Mapped[Optional["Resume"]] = relationship("Resume")


class JobSkill(Base):
    """Job skill model for storing skills associated with job postings."""
    
    __tablename__ = "job_skills"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    skill: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    job: Mapped["Job"] = relationship("Job")


class JobSearchHistory(Base):
    """Job search history model for tracking user job searches."""
    
    __tablename__ = "job_search_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    query: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    total_results: Mapped[int] = mapped_column(Integer, default=0)
    filters: Mapped[Optional[str]] = mapped_column(Text)  # JSON - search filters used
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User")


class JobSource(Base):
    """Job source model for tracking job platform statistics."""
    
    __tablename__ = "job_sources"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)  # linkedin, internshala, etc.
    jobs_fetched: Mapped[int] = mapped_column(Integer, default=0)
    jobs_stored: Mapped[int] = mapped_column(Integer, default=0)
    last_sync: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    api_endpoint: Mapped[Optional[str]] = mapped_column(String(500))
    rate_limit: Mapped[Optional[int]] = mapped_column(Integer)  # requests per hour
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
