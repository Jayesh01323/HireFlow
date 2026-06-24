# HireFlow AI - Developer Guide

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Database](#database)
- [API Development](#api-development)
- [UI Development](#ui-development)
- [AI Integration](#ai-integration)
- [Debugging](#debugging)
- [Performance Optimization](#performance-optimization)
- [Contributing](#contributing)

---

## Getting Started

### Prerequisites

- Python 3.12+
- Git
- PostgreSQL (for production development)
- Google Gemini API Key

### Initial Setup

```bash
# Clone repository
git clone https://github.com/Jayesh01323/HireFlow.git
cd HireFlow

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy pre-commit

# Setup pre-commit hooks
pre-commit install

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python -c "from src.database import init_db; init_db()"
```

---

## Development Environment

### IDE Setup

#### VS Code

Install recommended extensions:
- Python
- Pylance
- Black Formatter
- Python Test Explorer
- GitLens

#### PyCharm

Configure:
- Python interpreter to virtual environment
- Code style to PEP 8
- Test runner to pytest

### Development Tools

```bash
# Code formatting
black src/ pages/ tests/

# Linting
flake8 src/ pages/ tests/

# Type checking
mypy src/

# Run tests
pytest tests/

# Run specific test
pytest tests/test_job_connectors.py

# Run with coverage
pytest --cov=src tests/
```

---

## Project Structure

### Directory Layout

```
hireflow-ai/
├── app.py                      # Main Streamlit entry point
├── src/                        # Core application logic
│   ├── agents/                 # AI agents
│   ├── ai/                     # AI integration
│   ├── api/                    # FastAPI endpoints
│   ├── database/               # Database models and repositories
│   ├── jobs/                   # Job processing
│   ├── services/               # Business logic
│   └── utils/                  # Utility functions
├── pages/                      # Streamlit pages
├── tests/                      # Test files
├── docs/                       # Documentation
└── data/                       # Database and uploads
```

### Module Responsibilities

#### `src/agents/`
AI agents for specific tasks:
- `career_copilot_agent.py`: Career Q&A
- `job_discovery_agent.py`: Job search
- `resume_match_agent.py`: Resume-job matching

#### `src/ai/`
AI integration layer:
- `gemini_client.py`: Gemini API client
- `embeddings.py`: Text embeddings
- `prompts.py`: AI prompt templates

#### `src/api/`
FastAPI endpoints:
- `jobs_api.py`: Job-related endpoints
- `resume_api.py`: Resume endpoints
- `alerts_api.py`: Alert endpoints
- `tracker_api.py`: Application tracking

#### `src/database/`
Database layer:
- `models.py`: SQLAlchemy models
- `repositories.py`: Data access layer
- `migrations.py`: Database migrations

#### `src/jobs/`
Job processing:
- `connectors/`: Platform-specific scrapers
- `aggregator.py`: Job aggregation
- `deduplicator.py`: Duplicate removal
- `normalizer.py`: Data normalization

#### `src/services/`
Business logic:
- `match_engine.py`: Matching algorithm
- `skill_categorizer.py`: Skill classification
- `skill_extractor.py`: Skill extraction
- `ranking_engine.py`: Job ranking

#### `src/utils/`
Utilities:
- `text_cleaner.py`: Text processing
- `constants.py`: Application constants
- `skills.py`: Skill definitions

---

## Coding Standards

### Python Style Guide

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines:

```python
# Good
def process_jobs(jobs: List[Dict]) -> Optional[Dict]:
    """Process job listings and return results."""
    if not jobs:
        return None
    
    processed = []
    for job in jobs:
        processed.append(normalize_job(job))
    
    return {"jobs": processed, "count": len(processed)}

# Bad
def processJobs(jobs):
    if not jobs: return None
    p=[]
    for j in jobs: p.append(normalize(j))
    return {"jobs":p,"count":len(p)}
```

### Type Hints

Add type hints to all functions:

```python
from typing import List, Dict, Optional, Any

def analyze_resume(
    resume_text: str,
    job_description: str
) -> Dict[str, Any]:
    """Analyze resume against job description."""
    pass
```

### Docstrings

Use Google style docstrings:

```python
def extract_skills(text: str) -> List[str]:
    """Extract skills from text using NLP techniques.
    
    Args:
        text: Input text to extract skills from
        
    Returns:
        List of extracted skill names
        
    Raises:
        ValueError: If text is empty or invalid
        
    Example:
        >>> extract_skills("Python, Django, SQL")
        ['Python', 'Django', 'SQL']
    """
    pass
```

### Import Organization

```python
# Standard library imports
import os
from typing import List, Dict

# Third-party imports
import pandas as pd
from sqlalchemy import create_engine

# Local imports
from src.utils import get_env
from src.database import get_session
```

### Error Handling

```python
# Good
def process_resume(file_path: str) -> Dict:
    """Process resume file."""
    try:
        text = extract_text(file_path)
        parsed = parse_resume(text)
        return parsed
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error processing resume: {e}")
        raise

# Bad
def process_resume(file_path):
    text = extract_text(file_path)  # No error handling
    return parse_resume(text)
```

---

## Testing

### Test Structure

```
tests/
├── test_job_connectors.py
├── test_phase4_services.py
├── conftest.py                  # Pytest configuration
└── fixtures/                    # Test fixtures
```

### Writing Tests

```python
import pytest
from src.services.match_engine import analyze_match

def test_analyze_match_basic():
    """Test basic match analysis."""
    resume = {
        "skills": ["Python", "Django"],
        "experience": "2 years"
    }
    job_desc = "Python Developer with Django experience"
    
    result = analyze_match(resume, job_desc)
    
    assert "match_percentage" in result
    assert result["match_percentage"] >= 0
    assert result["match_percentage"] <= 100

def test_analyze_match_empty_resume():
    """Test match analysis with empty resume."""
    resume = {"skills": [], "experience": ""}
    job_desc = "Python Developer"
    
    result = analyze_match(resume, job_desc)
    
    assert result["match_percentage"] == 0
```

### Test Fixtures

```python
# conftest.py
import pytest
from src.database import init_db, get_session

@pytest.fixture
def db_session():
    """Create a test database session."""
    init_db()
    session = get_session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def sample_resume():
    """Provide sample resume data."""
    return {
        "name": "John Doe",
        "skills": ["Python", "Django", "SQL"],
        "experience": "Software Developer at Tech Corp"
    }
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_job_connectors.py

# Run specific test
pytest tests/test_job_connectors.py::test_linkedin_scraper

# Run with verbose output
pytest -v

# Run with markers
pytest -m integration
```

### Test Coverage

Aim for >70% coverage. Check coverage with:

```bash
pytest --cov=src --cov-report=term-missing
```

---

## Database

### Models

Define models in `src/database/models.py`:

```python
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

class Job(Base):
    """Job model for storing job listings."""
    
    __tablename__ = "jobs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
```

### Migrations

Create migrations in `src/database/migrations.py`:

```python
def upgrade():
    """Upgrade database schema."""
    # Add new columns
    op.add_column('jobs', sa.Column('new_field', sa.String(255)))

def downgrade():
    """Downgrade database schema."""
    # Remove columns
    op.drop_column('jobs', 'new_field')
```

### Queries

Use SQLAlchemy ORM for queries:

```python
from src.database import get_session
from src.database.models import Job

def get_jobs_by_location(location: str) -> List[Job]:
    """Get jobs by location."""
    session = get_session()
    jobs = session.query(Job).filter(Job.location == location).all()
    return jobs
```

### Best Practices

- Always use ORM, never raw SQL
- Use context managers for sessions
- Add indexes on frequently queried columns
- Use relationships for foreign keys
- Validate data before saving

---

## API Development

### Creating Endpoints

Add endpoints in `src/api/`:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

class JobRequest(BaseModel):
    title: str
    location: str

@router.post("/search")
async def search_jobs(request: JobRequest):
    """Search for jobs."""
    try:
        jobs = search_jobs(request.title, request.location)
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Validation

Use Pydantic for validation:

```python
from pydantic import BaseModel, Field, validator

class ResumeUpload(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    
    @validator('filename')
    def filename_must_be_pdf(cls, v):
        if not v.endswith('.pdf'):
            raise ValueError('Filename must end with .pdf')
        return v
```

### Error Handling

```python
from fastapi import HTTPException, status

@router.get("/jobs/{job_id}")
async def get_job(job_id: int):
    """Get job by ID."""
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return job
```

---

## UI Development

### Creating Pages

Add pages in `pages/`:

```python
import streamlit as st
from src.database import get_all_resumes

def main():
    """Main page function."""
    st.title("My Page")
    
    resumes = get_all_resumes()
    
    if resumes:
        st.write(f"Found {len(resumes)} resumes")
    else:
        st.info("No resumes found")

if __name__ == "__main__":
    main()
```

### State Management

```python
import streamlit as st

# Initialize session state
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

# Update state
st.session_state.user_data['name'] = 'John'

# Access state
name = st.session_state.user_data.get('name')
```

### Caching

```python
import streamlit as st

@st.cache_data(ttl=3600)
def get_jobs():
    """Get jobs with caching."""
    return fetch_jobs_from_db()

@st.cache_resource
def get_database_connection():
    """Cache database connection."""
    return create_connection()
```

### Best Practices

- Use caching for expensive operations
- Keep pages focused on single responsibility
- Use consistent styling
- Handle errors gracefully
- Provide loading indicators

---

## AI Integration

### Gemini Client

Use the Gemini client in `src/ai/gemini_client.py`:

```python
from src.ai.gemini_client import GeminiClient

client = GeminiClient()

# Generate response
response = client.generate_response("Your prompt here")

# Parse resume
parsed = client.parse_resume(resume_text)

# Generate career advice
advice = client.generate_career_advice(question, user_profile)
```

### Custom Prompts

Add prompts in `src/ai/prompts.py`:

```python
RESUME_PARSE_PROMPT = """
Parse the following resume text into structured JSON format:
- name
- email
- phone
- skills (list with name and level)
- education (list)
- experience (list)
- projects (list)

Resume text:
{resume_text}
"""

CAREER_ADVICE_PROMPT = """
Based on the following user profile, provide career advice:
User Profile: {user_profile}
Question: {question}
"""
```

### Error Handling

```python
try:
    response = client.generate_response(prompt)
    if not response:
        logger.warning("Empty response from Gemini")
        return fallback_response()
except Exception as e:
    logger.error(f"Gemini API error: {e}")
    return fallback_response()
```

---

## Debugging

### Logging

Configure logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def process_data(data):
    logger.info(f"Processing {len(data)} items")
    try:
        result = do_processing(data)
        logger.info("Processing completed successfully")
        return result
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise
```

### Debug Mode

Enable debug mode in development:

```python
import os

DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
    # Enable additional debug features
```

### Common Issues

#### Import Errors

```python
# Add project root to Python path
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
```

#### Database Connection Issues

```python
# Check database connection
from src.database import get_session

try:
    session = get_session()
    session.execute("SELECT 1")
    print("Database connection successful")
except Exception as e:
    print(f"Database connection failed: {e}")
```

---

## Performance Optimization

### Database Optimization

```python
# Use indexes
class Job(Base):
    __tablename__ = "jobs"
    title = Column(String(255), index=True)  # Add index
    location = Column(String(255), index=True)

# Use eager loading
from sqlalchemy.orm import eagerload

jobs = session.query(Job).options(eagerload(Job.skills)).all()

# Use pagination
def get_jobs(page: int = 1, per_page: int = 20):
    offset = (page - 1) * per_page
    return session.query(Job).offset(offset).limit(per_page).all()
```

### Caching Strategy

```python
from functools import lru_cache
import redis

# In-memory cache
@lru_cache(maxsize=128)
def get_skill_categories():
    return fetch_skill_categories()

# Redis cache
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_data(key: str):
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    
    data = fetch_data()
    redis_client.setex(key, 3600, json.dumps(data))
    return data
```

### Async Operations

```python
import asyncio

async def fetch_multiple_sources():
    """Fetch data from multiple sources concurrently."""
    tasks = [
        fetch_linkedin_jobs(),
        fetch_internshala_jobs(),
        fetch_naukri_jobs()
    ]
    results = await asyncio.gather(*tasks)
    return results
```

---

## Contributing

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Update documentation
6. Submit pull request

### Code Review Checklist

- [ ] Code follows PEP 8
- [ ] Type hints added
- [ ] Docstrings included
- [ ] Tests written
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Performance considered

### Commit Messages

Follow conventional commits:

```
feat: add job scraping for LinkedIn
fix: resolve memory leak in job matcher
docs: update installation guide
style: format code with black
refactor: simplify skill categorization
test: add unit tests for resume parser
chore: update dependencies
```

---

## Resources

### Documentation

- [Python Documentation](https://docs.python.org/3/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

### Tools

- [Black](https://black.readthedocs.io/) - Code formatter
- [Flake8](https://flake8.pycqa.org/) - Linter
- [MyPy](https://mypy.readthedocs.io/) - Type checker
- [Pytest](https://docs.pytest.org/) - Testing framework

### Community

- [GitHub Issues](https://github.com/Jayesh01323/HireFlow/issues)
- [GitHub Discussions](https://github.com/Jayesh01323/HireFlow/discussions)
- [Email](jayesh@example.com)

---

**Last Updated**: June 20, 2026  
**Maintained By**: Jayesh  
**Version**: 1.0.0
