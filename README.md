<div align="center">

# 🚀 HireFlow AI

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](https://github.com/Jayesh01323/HireFlow)
[![GitHub Stars](https://img.shields.io/github/stars/Jayesh01323/HireFlow?style=social)](https://github.com/Jayesh01323/HireFlow)

**AI-Powered Career Intelligence Platform for Freshers & Entry-Level Engineers**

[Features](#-key-features) • [Architecture](#-system-architecture) • [Installation](#-installation) • [Demo](#-screenshots) • [Documentation](#-documentation)

</div>

---

## 📋 Project Overview

**HireFlow AI** is an intelligent career platform that leverages artificial intelligence to help freshers and entry-level software engineers navigate their job search journey. The platform provides comprehensive tools for resume analysis, job matching, skill gap identification, career coaching, and interview preparation.

### 🎯 Problem Statement

Fresh graduates and entry-level developers face significant challenges:
- **Resume Optimization**: Difficulty tailoring resumes to specific job requirements
- **Skill Gap Analysis**: Uncertainty about which skills to prioritize for target roles
- **Job Discovery**: Overwhelming number of job platforms with inconsistent information
- **Career Guidance**: Lack of personalized career advice and interview preparation
- **Application Tracking**: Difficulty managing multiple job applications efficiently

### 💡 Solution

HireFlow AI addresses these challenges through:
- **AI-Powered Resume Parsing**: Extract and analyze resume data using Google Gemini API
- **Intelligent Job Matching**: Match resumes against job descriptions with weighted scoring
- **Skill Gap Analysis**: Identify missing skills with learning recommendations
- **Career Coaching**: AI-driven personalized career guidance
- **Job Aggregation**: Scrape jobs from multiple platforms (LinkedIn, Internshala, Naukri, etc.)
- **Application Tracking**: Manage job applications with status tracking

---

## ✨ Key Features

### 📄 Resume Intelligence
- **Smart Parsing**: Extract structured data from PDF resumes using AI
- **ATS Optimization**: Improve resume compatibility with applicant tracking systems
- **Skill Extraction**: Automatically identify and categorize technical and soft skills
- **Resume Scoring**: Get actionable feedback on resume quality

### 🎯 Job Matching Engine
- **Intelligent Matching**: Compare resume skills against job requirements
- **Weighted Scoring**: Priority-based skill matching (High/Medium/Low)
- **Category Analysis**: Break down matches by skill categories (Frontend, Backend, DevOps, etc.)
- **Gap Analysis**: Identify missing skills with learning recommendations

### 📊 Job Discovery
- **Multi-Platform Aggregation**: Scrape jobs from LinkedIn, Internshala, Naukri, Glassdoor, Wellfound
- **Smart Filtering**: Filter by location, salary, experience, work mode
- **Deduplication**: Remove duplicate job postings automatically
- **Real-time Updates**: Fresh job data with regular scraping

### 🧠 Career Coaching
- **AI Career Assistant**: Get personalized career advice and guidance
- **Interactive Chat**: AI-powered career Q&A interface
- **Career Fit Analysis**: Match profile against various career paths
- **Interview Preparation**: Generate role-specific interview questions

### 📈 Analytics Dashboard
- **Application Tracking**: Monitor job application status and progress
- **Skill Analytics**: Visualize skill distribution and growth
- **Learning Roadmaps**: Personalized learning plans with milestones
- **Performance Metrics**: Track career readiness scores

### 🔧 Additional Features
- **Application Workflow**: End-to-end application management
- **Alert System**: Notifications for new jobs and application updates
- **Export Functionality**: Generate reports and summaries
- **Responsive Design**: Clean, intuitive user interface

---

## 🏗️ System Architecture

```mermaid
graph TB
    A[User Interface - Streamlit] --> B[API Layer - FastAPI]
    A --> C[Database - SQLite]
    B --> D[Service Layer]
    D --> E[AI Agents]
    D --> F[Job Services]
    D --> G[Matcher Engine]
    E --> H[Gemini API]
    F --> I[Job Scrapers]
    I --> J[External Job Platforms]
    G --> K[Skill Categorizer]
    G --> L[Ranking Engine]
    C --> M[ORM - SQLAlchemy]
```

### Component Overview

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit | Interactive web interface |
| **Backend API** | FastAPI | RESTful API endpoints |
| **Database** | SQLite + SQLAlchemy | Data persistence and ORM |
| **AI Engine** | Google Gemini API | Resume parsing and career coaching |
| **Job Scraping** | Selenium + BeautifulSoup | Multi-platform job aggregation |
| **Matching Engine** | Custom Algorithm | Weighted skill matching |
| **Visualization** | Plotly | Interactive charts and graphs |

---

## 🛠️ Technology Stack

### Core Technologies
- **Python 3.12**: Modern Python with type hints and async support
- **Streamlit 1.32+**: Rapid web application development
- **FastAPI**: High-performance API framework
- **SQLAlchemy 2.0**: Modern Python SQL toolkit and ORM

### AI & Machine Learning
- **Google Gemini API**: Advanced AI for resume parsing and coaching
- **FuzzyWuzzy/RapidFuzz**: String matching and similarity scoring
- **Custom Matching Algorithm**: Weighted skill matching with priority levels

### Data Processing
- **Pandas**: Data manipulation and analysis
- **PyMuPDF**: PDF parsing for resume extraction
- **Pydantic**: Data validation and settings management

### Web Scraping
- **Selenium**: Browser automation for dynamic content
- **BeautifulSoup4**: HTML parsing and data extraction
- **Requests**: HTTP library for web scraping

### Visualization
- **Plotly**: Interactive charts and graphs
- **Streamlit Components**: Custom UI components

### Development Tools
- **python-dotenv**: Environment variable management
- **Logging**: Comprehensive logging system
- **Type Hints**: Full type annotation coverage

---

## 📦 Installation

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)
- Google Gemini API Key

### Step 1: Clone the Repository
```bash
git clone https://github.com/Jayesh01323/HireFlow.git
cd HireFlow
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///data/hireflow.db
```

### Step 5: Initialize Database
```bash
python -c "from src.database import init_db; init_db()"
```

### Step 6: Run the Application
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

---

## 🚀 Usage Guide

### 1. Upload and Parse Resume
- Navigate to **Resume Parser** page
- Upload your PDF resume
- AI will extract and structure your data
- Review parsed information and skills

### 2. Discover Jobs
- Go to **Job Discovery** page
- Search for jobs by title, location, or skills
- Apply filters (remote, salary, experience)
- Save interesting jobs to your list

### 3. Match Your Resume to Jobs
- Visit **Job Matcher** page
- Select your parsed resume
- Paste job description
- Get detailed match analysis with skill gaps

### 4. Get Career Guidance
- Use **Career Assistant** for personalized advice
- Try interactive AI chat for career Q&A
- Check **Career Fit** for role compatibility

### 5. Track Applications
- Use **Application Tracker** to manage applications
- Update status (Saved, Applied, Interview, Offer, Rejected)
- Add notes and follow-up reminders

### 6. View Analytics
- Check **Analytics Dashboard** for insights
- Monitor skill distribution and growth
- Track application success rates

---

## 📸 Screenshots

### Main Dashboard
![Dashboard](screenshots/dashboard.png)
*Central hub for navigating all features*

### Resume Parser
![Resume Parser](screenshots/resume_parser.png)
*AI-powered resume extraction and analysis*

### Job Matcher
![Job Matcher](screenshots/job_matcher.png)
*Intelligent skill matching with gap analysis*

### Analytics Dashboard
![Analytics](screenshots/analytics.png)
*Comprehensive career analytics and insights*

> 📸 **Note**: Screenshots will be added in Phase 6. For now, placeholders are shown.

---

## 📁 Project Structure

```
hireflow-ai/
├── app.py                          # Main Streamlit entry point
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore rules
├── LICENSE                         # MIT License
├── README.md                       # This file
│
├── data/                           # Database and uploads
│   ├── hireflow.db                # SQLite database
│   └── uploads/                   # User uploaded files
│
├── docs/                          # Documentation
│   ├── architecture.md            # System architecture
│   ├── installation.md            # Installation guide
│   ├── deployment.md              # Deployment guide
│   ├── api-reference.md           # API documentation
│   ├── user-guide.md              # User guide
│   ├── developer-guide.md         # Developer guide
│   └── roadmap.md                 # Project roadmap
│
├── pages/                         # Streamlit multi-page modules
│   ├── Resume_Parser.py           # Resume upload and parsing
│   ├── Job_Matcher.py             # Job matching engine
│   ├── Job_Discovery.py           # Job search and aggregation
│   ├── Skill_Gap.py               # Skill gap analysis
│   ├── Career_Assistant.py        # AI career assistant
│   ├── Application_Tracker.py     # Application management
│   ├── Analytics_Dashboard.py     # Analytics and insights
│   ├── Learning_Roadmap.py        # Learning path generation
│   ├── Career_Fit.py              # Career compatibility
│   ├── Interview_Prep.py          # Interview preparation
│   └── Learning_Dashboard.py      # Learning progress
│
├── src/                           # Core application logic
│   ├── agents/                    # AI agents
│   │   ├── career_copilot_agent.py
│   │   ├── career_coach_agent.py
│   │   ├── job_discovery_agent.py
│   │   ├── ranking_agent.py
│   │   ├── resume_match_agent.py
│   │   ├── skill_gap_agent.py
│   │   └── ...
│   ├── ai/                        # AI integration
│   │   ├── gemini_client.py       # Gemini API client
│   │   ├── embeddings.py          # Text embeddings
│   │   └── prompts.py             # AI prompt templates
│   ├── api/                       # API endpoints
│   │   ├── jobs_api.py
│   │   ├── resume_api.py
│   │   ├── alerts_api.py
│   │   └── tracker_api.py
│   ├── database/                  # Database layer
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── repositories.py        # Data access layer
│   │   └── migrations.py          # Database migrations
│   ├── jobs/                      # Job processing
│   │   ├── connectors/            # Platform-specific scrapers
│   │   │   ├── linkedin.py
│   │   │   ├── internshala.py
│   │   │   ├── naukri.py
│   │   │   ├── glassdoor.py
│   │   │   └── wellfound.py
│   │   ├── aggregator.py          # Job aggregation
│   │   ├── deduplicator.py        # Duplicate removal
│   │   ├── normalizer.py          # Data normalization
│   │   ├── search_engine.py       # Job search
│   │   └── schemas.py             # Job data models
│   ├── services/                  # Business logic
│   │   ├── match_engine.py        # Matching algorithm
│   │   ├── skill_categorizer.py   # Skill classification
│   │   ├── skill_extractor.py     # Skill extraction
│   │   ├── ranking_engine.py      # Job ranking
│   │   ├── recommendation_engine.py
│   │   └── ...
│   ├── utils/                     # Utilities
│   │   ├── text_cleaner.py        # Text processing
│   │   ├── constants.py           # Application constants
│   │   └── skills.py              # Skill definitions
│   ├── database.py                # Database initialization
│   ├── matcher.py                 # Resume-job matching
│   ├── parser.py                  # Resume parsing
│   ├── gemini.py                  # Gemini integration
│   └── utils.py                   # Common utilities
│
├── tests/                         # Test suite
│   ├── test_job_connectors.py
│   └── test_phase4_services.py
│
├── reports/                       # Generated reports
│   ├── architecture_setup_report.md
│   ├── job_discovery_phase1_report.md
│   └── phase4_implementation_report.md
│
├── screenshots/                   # Demo assets
│   ├── dashboard.png
│   ├── resume_parser.png
│   ├── job_matcher.png
│   └── analytics.png
│
└── .github/                       # GitHub configuration
    ├── workflows/                 # CI/CD workflows
    ├── ISSUE_TEMPLATE/            # Issue templates
    └── PULL_REQUEST_TEMPLATE/     # PR templates
```

---

## 🔌 API Overview

### REST API Endpoints

#### Jobs API
- `GET /api/jobs` - List all jobs with filters
- `GET /api/jobs/{id}` - Get job details
- `POST /api/jobs/search` - Search jobs
- `GET /api/jobs/sources` - List job sources

#### Resume API
- `POST /api/resume/upload` - Upload resume
- `GET /api/resume/{id}` - Get resume details
- `POST /api/resume/parse` - Parse resume text

#### Alerts API
- `GET /api/alerts` - Get user alerts
- `POST /api/alerts` - Create alert
- `PUT /api/alerts/{id}/read` - Mark as read

#### Tracker API
- `GET /api/applications` - List applications
- `POST /api/applications` - Create application
- `PUT /api/applications/{id}` - Update application status

### API Documentation
Detailed API documentation is available in [docs/api-reference.md](docs/api-reference.md)

---

## 🗺️ Future Roadmap

### Version 1.1 (Q3 2026)
- [ ] User authentication and authorization
- [ ] Email notifications for job alerts
- [ ] Export to PDF/Excel functionality
- [ ] Mobile-responsive design improvements
- [ ] Advanced filtering options

### Version 1.2 (Q4 2026)
- [ ] Real-time job updates with WebSocket
- [ ] Integration with LinkedIn API
- [ ] Collaborative features for teams
- [ ] Advanced analytics with ML insights
- [ ] Performance optimization and caching

### Version 2.0 (Q1 2027)
- [ ] Mobile app (React Native)
- [ ] Premium subscription tier
- [ ] Company profiles and reviews
- [ ] Salary estimation tool
- [ ] Video interview preparation

### Version 2.1 (Q2 2027)
- [ ] AI-powered cover letter generation
- [ ] Resume templates and builder
- [ ] Community features and forums
- [ ] Integration with ATS systems
- [ ] White-label solution for companies

---

## 🤝 Contributing

We welcome contributions from the community! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write tests for new features
- Update documentation as needed
- Keep commits focused and atomic

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary
- ✅ Free to use for personal and commercial projects
- ✅ Free to modify and distribute
- ✅ No warranty or liability
- ✅ Must include license and copyright notice

---

## 👨‍💻 Author

**Jayesh**
- GitHub: [@Jayesh01323](https://github.com/Jayesh01323)
- LinkedIn: [Jayesh](https://www.linkedin.com/in/jayesh-patil-5a2a082b5)
- Email: jayesh@example.com

### Acknowledgments
- Google Gemini API for AI capabilities
- Streamlit team for the amazing framework
- Open source community for various libraries

---

## 📊 Project Stats

- **Total Files**: 70+ Python files
- **Lines of Code**: 15,000+
- **Test Coverage**: Expanding
- **API Endpoints**: 15+
- **Job Sources**: 6 platforms
- **Skill Categories**: 12 categories
- **Supported Formats**: PDF, JSON

---

## 🙏 Support

If you find this project helpful, please consider:
- ⭐ Starring the repository on GitHub
- 🐛 Reporting bugs via [Issues](https://github.com/Jayesh01323/HireFlow/issues)
- 💡 Suggesting features via [Discussions](https://github.com/Jayesh01323/HireFlow/discussions)
- 📢 Sharing with your network

---

## 📞 Contact

For questions, support, or collaboration:
- Open an [Issue](https://github.com/Jayesh01323/HireFlow/issues)
- Email: jayesh@example.com
- LinkedIn: [Jayesh](https://www.linkedin.com/in/jayesh-patil-5a2a082b5)

---

<div align="center">

**Built with ❤️ for the developer community**

[⬆ Back to Top](#-hireflow-ai)

</div>
