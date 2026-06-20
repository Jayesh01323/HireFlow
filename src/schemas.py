"""
Pydantic Schemas Module

Defines data models for resumes, job postings, skill gaps,
interview sessions, and other domain entities.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class Skill(BaseModel):
    """Represents a single skill with optional proficiency level."""

    name: str
    level: Optional[str] = None


class Resume(BaseModel):
    """Structured representation of a parsed resume."""

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[Skill] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    experience: List[str] = Field(default_factory=list)

    @field_validator("skills", mode="before")
    @classmethod
    def normalize_skills(cls, value: object) -> object:
        if not value:
            return []
        if not isinstance(value, list):
            return value

        normalized: list[object] = []
        for item in value:
            if isinstance(item, str):
                normalized.append({"name": item.strip()})
            else:
                normalized.append(item)
        return normalized

    @field_validator("education", "projects", "experience", mode="before")
    @classmethod
    def normalize_string_lists(cls, value: object) -> object:
        if value is None:
            return []
        if isinstance(value, str):
            return [value.strip()] if value.strip() else []
        return value


class JobPosting(BaseModel):
    """Represents a job opening for matching."""

    title: str
    company: str
    required_skills: List[str] = Field(default_factory=list)
    description: Optional[str] = None
