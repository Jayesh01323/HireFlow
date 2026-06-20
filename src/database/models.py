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
    salary: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # linkedin, internshala, etc.
    external_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)  # ID from source platform
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False)
    experience_level: Mapped[Optional[str]] = mapped_column(String(50))  # entry, mid, senior
    posted_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job_matches: Mapped[list["JobMatch"]] = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")
    applications: Mapped[list["Application"]] = relationship("Application", back_populates="job", cascade="all, delete-orphan")


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
    metadata: Mapped[Optional[str]] = mapped_column(Text)  # JSON object for additional data
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="alerts")
