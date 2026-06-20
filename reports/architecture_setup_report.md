# HireFlow AI - Architecture Setup Report

**Date:** June 20, 2026  
**Task:** Create production-ready architecture and folder structure for HireFlow AI

---

## Overview

Successfully created a complete modular architecture for HireFlow AI, an AI-powered Career Operating System. The architecture follows best practices with clear separation of concerns, service-oriented design, and scalable structure for future development.

---

## Files Created

### Database Layer (`src/database/`)
- **models.py** - SQLAlchemy-ready ORM models for users, resumes, jobs, job_matches, applications, and alerts
- **repositories.py** - Repository pattern implementation for CRUD operations on all models
- **migrations.py** - Database migration management skeleton with version control

### Services Layer (`src/services/`)
- **skill_gap_engine.py** - Skill gap analysis and learning recommendations
- **roadmap_engine.py** - Personalized learning roadmap generation
- **ranking_engine.py** - Job opportunity ranking and scoring
- **application_tracker.py** - Job application tracking and analytics

### Jobs Module (`src/jobs/`)
- **schemas.py** - Pydantic models for job postings and search queries
- **aggregator.py** - Multi-source job aggregation coordinator
- **normalizer.py** - Job posting normalization and standardization
- **deduplicator.py** - Duplicate job detection and removal
- **search_engine.py** - Advanced job search with filtering and relevance scoring

### Job Connectors (`src/jobs/connectors/`)
- **linkedin.py** - LinkedIn job connector placeholder
- **internshala.py** - Internshala job connector placeholder
- **naukri.py** - Naukri job connector placeholder
- **indeed.py** - Indeed job connector placeholder
- **glassdoor.py** - Glassdoor job connector placeholder
- **wellfound.py** - Wellfound job connector placeholder
- **company_careers.py** - Direct company career pages connector placeholder

### Agents Layer (`src/agents/`)
- **job_discovery_agent.py** - Autonomous job discovery agent
- **resume_match_agent.py** - Resume-job matching agent
- **skill_gap_agent.py** - Skill gap analysis agent
- **roadmap_agent.py** - Learning roadmap generation agent
- **ranking_agent.py** - Job ranking agent
- **tracker_agent.py** - Application tracking agent
- **alert_agent.py** - Alert generation and management agent

### AI Module (`src/ai/`)
- **gemini_client.py** - Unified Gemini API client for AI interactions
- **prompts.py** - Prompt templates for resume parsing, career coaching, interview prep
- **embeddings.py** - Text embeddings for semantic search and similarity matching

### API Layer (`src/api/`)
- **jobs_api.py** - FastAPI router for job-related endpoints
- **resume_api.py** - FastAPI router for resume-related endpoints
- **tracker_api.py** - FastAPI router for application tracking endpoints
- **alerts_api.py** - FastAPI router for alert management endpoints

### Utils Module (`src/utils/`)
- **skills.py** - Skill extraction, normalization, and categorization utilities
- **text_cleaner.py** - Text cleaning and preprocessing utilities
- **constants.py** - Application-wide constants and configuration values

### Streamlit Pages (`pages/`)
- **Job_Discovery.py** - Job discovery and search page
- **Skill_Gap.py** - Skill gap analysis page
- **Learning_Roadmap.py** - Learning roadmap generation page
- **Application_Tracker.py** - Application tracking and analytics page

---

## Dependencies Introduced

Updated `requirements.txt` with the following new dependencies:

- **sqlalchemy>=2.0.0** - ORM for database models
- **fastapi>=0.100.0** - Modern web framework for API layer
- **uvicorn>=0.23.0** - ASGI server for FastAPI

Existing dependencies preserved:
- streamlit>=1.32.0
- google-generativeai>=0.5.0
- PyMuPDF>=1.24.0
- pydantic>=2.6.0
- pandas>=2.2.0
- plotly>=5.19.0
- python-dotenv>=1.0.0

---

## Architecture Summary

### Folder Structure
```
hireflow-ai/
├── app.py                          # Main Streamlit entry point
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── data/                           # SQLite database and uploads
│   └── hireflow.db                # Existing database (preserved)
├── reports/                        # Generated reports
│   └── architecture_setup_report.md
├── pages/                          # Streamlit multi-page modules
│   ├── Analytics_Dashboard.py     # ✅ Working (preserved)
│   ├── Career_Coach.py            # ⏸️ Placeholder (preserved)
│   ├── Interview_Prep.py          # ⏸️ Placeholder (preserved)
│   ├── Job_Matcher.py             # ✅ Working (preserved)
│   ├── Resume_Parser.py           # ✅ Working (preserved)
│   ├── Job_Discovery.py           # 🆕 New placeholder
│   ├── Skill_Gap.py              # 🆕 New placeholder
│   ├── Learning_Roadmap.py        # 🆕 New placeholder
│   └── Application_Tracker.py     # 🆕 New placeholder
└── src/                            # Core application logic
    ├── database/                   # 🆕 Database layer
    │   ├── models.py
    │   ├── repositories.py
    │   └── migrations.py
    ├── services/                   # 🔄 Enhanced with new services
    │   ├── match_engine.py        # ✅ Existing (Job Matcher v2)
    │   ├── recommendation_engine.py # ✅ Existing (Job Matcher v2)
    │   ├── skill_extractor.py     # ✅ Existing (Job Matcher v2)
    │   ├── skill_normalizer.py    # ✅ Existing (Job Matcher v2)
    │   ├── skill_categorizer.py   # ✅ Existing (Job Matcher v2)
    │   ├── skill_gap_engine.py    # 🆕 New
    │   ├── roadmap_engine.py      # 🆕 New
    │   ├── ranking_engine.py     # 🆕 New
    │   └── application_tracker.py # 🆕 New
    ├── jobs/                       # 🆕 Jobs module
    │   ├── schemas.py
    │   ├── aggregator.py
    │   ├── normalizer.py
    │   ├── deduplicator.py
    │   └── search_engine.py
    │   └── connectors/            # 🆕 Job connectors
    │       ├── linkedin.py
    │       ├── internshala.py
    │       ├── naukri.py
    │       ├── indeed.py
    │       ├── glassdoor.py
    │       ├── wellfound.py
    │       └── company_careers.py
    ├── agents/                     # 🆕 Agents layer
    │   ├── job_discovery_agent.py
    │   ├── resume_match_agent.py
    │   ├── skill_gap_agent.py
    │   ├── roadmap_agent.py
    │   ├── ranking_agent.py
    │   ├── tracker_agent.py
    │   └── alert_agent.py
    ├── ai/                         # 🆕 AI module
    │   ├── gemini_client.py
    │   ├── prompts.py
    │   └── embeddings.py
    ├── api/                        # 🆕 API layer
    │   ├── jobs_api.py
    │   ├── resume_api.py
    │   ├── tracker_api.py
    │   └── alerts_api.py
    ├── utils/                      # 🆕 Utils module
    │   ├── skills.py
    │   ├── text_cleaner.py
    │   └── constants.py
    ├── database.py                 # ✅ Existing (preserved)
    ├── gemini.py                   # ✅ Existing (preserved)
    ├── matcher.py                  # ✅ Existing (preserved)
    ├── parser.py                   # ✅ Existing (preserved)
    ├── schemas.py                  # ✅ Existing (preserved)
    └── utils.py                    # ✅ Existing (preserved)
```

---

## Preserved Functionality

All existing working functionality has been preserved:
- ✅ Resume Parser (pages/Resume_Parser.py + src/parser.py)
- ✅ Analytics Dashboard (pages/Analytics_Dashboard.py)
- ✅ Job Matcher (pages/Job_Matcher.py + src/matcher.py + src/services/)

No existing files were deleted or overwritten. The architecture was extended, not replaced.

---

## Next Recommended Module

**Recommended: Job Discovery Module**

**Rationale:**
- The job discovery infrastructure is now in place (connectors, aggregator, search engine)
- This module will enable users to search and discover job opportunities across multiple sources
- Builds upon the connector architecture already created
- Provides immediate value to users by expanding job search capabilities

**Implementation Steps:**
1. Implement job connector scraping logic for LinkedIn, Internshala, Naukri
2. Complete job aggregator to coordinate multi-source searches
3. Implement job search engine with relevance scoring
4. Connect Job_Discovery.py page to the backend services
5. Add job saving and bookmarking functionality

**Alternative Modules:**
- Skill Gap Analysis (builds on existing Job Matcher skill analysis)
- Learning Roadmap (requires skill gap analysis first)
- Application Tracker (standalone, can be implemented independently)

---

## Coding Standards Applied

- ✅ Python 3.12+ type hints throughout
- ✅ Pydantic models for data validation
- ✅ Dataclasses where appropriate
- ✅ Structured logging with logger instances
- ✅ Clear docstrings for all classes and functions
- ✅ TODO comments for future implementation
- ✅ Consistent naming conventions
- ✅ Proper import organization

---

## Verification

- ✅ All Python files compile successfully
- ✅ Streamlit app.py launches without errors
- ✅ All new page files compile successfully
- ✅ No import errors in the architecture
- ✅ Existing functionality preserved

---

## Notes

- All new files are skeleton implementations with TODO comments
- No business logic has been implemented yet (as requested)
- Database models are SQLAlchemy-ready but no migration has been run
- API routers are FastAPI-ready but no FastAPI server is launched
- Job connectors are placeholders with no scraping logic
- The architecture is ready for incremental feature development
- Existing SQLite database (hireflow.db) has not been migrated or modified

---

## Summary

Successfully created a production-ready modular architecture for HireFlow AI with 40+ new files across 8 major modules. The architecture supports future development of job discovery, skill gap analysis, learning roadmaps, and application tracking while preserving all existing functionality. The codebase is well-organized, follows best practices, and is ready for incremental implementation of business logic.
