"""
Constants Module

Contains application-wide constants and configuration values.
Includes database paths, API endpoints, and feature flags.
"""

from __future__ import annotations

# Database Configuration
DEFAULT_DB_PATH = "data/hireflow.db"
DB_BACKUP_PATH = "data/backups/"

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_VERSION = "v1"

# Gemini AI Configuration
GEMINI_MODEL = "gemini-3.1-flash-lite"
GEMINI_MAX_TOKENS = 4096
GEMINI_TEMPERATURE = 0.7

# Job Search Configuration
DEFAULT_JOB_SEARCH_LIMIT = 50
MAX_JOB_SEARCH_LIMIT = 200
SUPPORTED_JOB_SOURCES = [
    "linkedin",
    "internshala",
    "naukri",
    "indeed",
    "glassdoor",
    "wellfound",
    "company_careers",
]

# Application Status Values
APPLICATION_STATUSES = [
    "saved",
    "applied",
    "screening",
    "interview",
    "technical",
    "behavioral",
    "offer",
    "rejected",
    "withdrawn",
]

# Experience Levels
EXPERIENCE_LEVELS = [
    "entry",
    "mid",
    "senior",
    "lead",
    "principal",
]

# Alert Types
ALERT_TYPES = [
    "new_job",
    "application_update",
    "skill_gap",
    "reminder",
]

# File Upload Configuration
MAX_FILE_SIZE_MB = 10
ALLOWED_FILE_EXTENSIONS = [".pdf"]
RESUME_UPLOAD_PATH = "data/uploads/"

# Pagination Configuration
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Cache Configuration
CACHE_TTL_SECONDS = 3600  # 1 hour
ENABLE_CACHE = True

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "logs/hireflow.log"

# Feature Flags
ENABLE_JOB_SCRAPING = False
ENABLE_AI_FEATURES = True
ENABLE_EMAIL_NOTIFICATIONS = False
ENABLE_SMS_NOTIFICATIONS = False

# Skill Categories
SKILL_CATEGORIES = [
    "Programming Languages",
    "Frontend",
    "Backend",
    "Databases",
    "Cloud",
    "DevOps",
    "Data Science",
    "Testing",
    "Mobile",
    "Tools",
    "Soft Skills",
]

# Match Score Thresholds
EXCELLENT_MATCH_THRESHOLD = 80
GOOD_MATCH_THRESHOLD = 60
FAIR_MATCH_THRESHOLD = 40

# Learning Roadmap Configuration
DEFAULT_ROADMAP_WEEKS = 12
MIN_ROADMAP_WEEKS = 4
MAX_ROADMAP_WEEKS = 52

# Application Tracker Configuration
REMINDER_DEFAULT_DAYS = 7
REMINDER_MAX_DAYS = 30
