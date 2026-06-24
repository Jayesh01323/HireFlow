# HireFlow AI - Architecture Diagrams

This document contains comprehensive Mermaid diagrams for HireFlow AI's system architecture, workflows, and database design.

---

## 1. System Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        A[Web Browser]
        B[Mobile App]
    end
    
    subgraph "Presentation Layer"
        C[Streamlit UI]
        D[FastAPI REST API]
    end
    
    subgraph "Service Layer"
        E[Resume Parser Service]
        F[Job Matcher Service]
        G[Job Discovery Service]
        H[Career Coach Service]
        I[Analytics Service]
        J[Application Tracker Service]
    end
    
    subgraph "AI Layer"
        K[Gemini Client]
        L[Skill Categorizer]
        M[Ranking Engine]
        N[Embedding Service]
    end
    
    subgraph "Data Layer"
        O[(SQLite Database)]
        P[SQLAlchemy ORM]
        Q[Redis Cache]
    end
    
    subgraph "External Services"
        R[Job Platforms]
        S[Gemini API]
        T[Email Service]
    end
    
    A --> C
    B --> D
    C --> E
    C --> F
    C --> G
    C --> H
    C --> I
    C --> J
    
    D --> E
    D --> F
    D --> G
    D --> H
    D --> I
    D --> J
    
    E --> K
    F --> L
    F --> M
    G --> R
    H --> K
    I --> N
    
    E --> P
    F --> P
    G --> P
    H --> P
    I --> P
    J --> P
    
    P --> O
    E --> Q
    F --> Q
    G --> Q
    
    K --> S
    J --> T
    G --> R
```

### Component Architecture

```mermaid
graph LR
    subgraph "Frontend Components"
        A[Resume Parser Page]
        B[Job Matcher Page]
        C[Job Discovery Page]
        D[Career Coach Page]
        E[Analytics Dashboard]
    end
    
    subgraph "Backend Services"
        F[Resume Parser Service]
        G[Job Matcher Service]
        H[Job Discovery Service]
        I[Career Coach Service]
        J[Analytics Service]
    end
    
    subgraph "Data Models"
        K[Resume Model]
        L[Job Model]
        M[JobMatch Model]
        N[User Model]
        O[Application Model]
    end
    
    A --> F
    B --> G
    C --> H
    D --> I
    E --> J
    
    F --> K
    G --> K
    G --> L
    G --> M
    H --> L
    I --> N
    J --> O
```

---

## 2. User Flow

### Complete User Journey

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant Parser
    participant Matcher
    participant Discovery
    participant Coach
    participant DB
    
    User->>UI: Upload Resume
    UI->>Parser: Parse Resume
    Parser->>Parser: Extract Text
    Parser->>Parser: AI Analysis
    Parser->>DB: Store Parsed Data
    DB->>UI: Confirmation
    
    User->>UI: Search Jobs
    UI->>Discovery: Search Jobs
    Discovery->>Discovery: Scrape Platforms
    Discovery->>DB: Store Jobs
    DB->>UI: Job Listings
    
    User->>UI: Select Job
    UI->>Matcher: Analyze Match
    Matcher->>DB: Get Resume Data
    Matcher->>Matcher: Extract Skills
    Matcher->>Matcher: Calculate Match
    Matcher->>DB: Store Match Results
    DB->>UI: Match Analysis
    
    User->>UI: Ask Career Question
    UI->>Coach: Get Advice
    Coach->>Coach: AI Analysis
    Coach->>UI: Career Advice
    
    User->>UI: Track Application
    UI->>DB: Update Application Status
    DB->>UI: Confirmation
```

### Resume Upload Flow

```mermaid
flowchart TD
    A[User Uploads Resume] --> B{File Valid?}
    B -->|No| C[Show Error]
    B -->|Yes| D[Extract Text]
    D --> E{Text Extracted?}
    E -->|No| F[Retry Extraction]
    E -->|Yes| G[AI Parsing]
    G --> H{Parsing Successful?}
    H -->|No| I[Manual Review]
    H -->|Yes| J[Store in Database]
    J --> K[Display Results]
    K --> L{User Satisfied?}
    L -->|No| M[Edit Data]
    M --> J
    L -->|Yes| N[Complete]
```

---

## 3. Resume Analysis Workflow

### Resume Processing Pipeline

```mermaid
flowchart LR
    A[PDF Resume] --> B[Text Extraction]
    B --> C[Text Cleaning]
    C --> D[Skill Extraction]
    D --> E[Skill Categorization]
    E --> F[Experience Parsing]
    F --> G[Education Parsing]
    G --> H[Project Extraction]
    H --> I[AI Enhancement]
    I --> J[Data Validation]
    J --> K[Structured JSON]
    K --> L[Database Storage]
```

### Skill Extraction Process

```mermaid
flowchart TD
    A[Resume Text] --> B[NLP Processing]
    B --> C[Tokenization]
    C --> D[Named Entity Recognition]
    D --> E[Skill Matching]
    E --> F{Skill in Database?}
    F -->|Yes| G[Use Standard Name]
    F -->|No| H[Add to Database]
    G --> I[Categorize Skill]
    H --> I
    I --> J[Assign Proficiency Level]
    J --> K[Output Structured Skills]
```

---

## 4. Job Matching Workflow

### Matching Algorithm Flow

```mermaid
flowchart TD
    A[Resume + Job Description] --> B[Extract Resume Skills]
    A --> C[Extract Job Skills]
    B --> D[Categorize Resume Skills]
    C --> E[Categorize Job Skills]
    D --> F[Calculate Skill Matches]
    E --> F
    F --> G[Apply Priority Weights]
    G --> H[Calculate Technical Match]
    G --> I[Calculate Soft Skill Match]
    H --> J[Calculate Weighted Match]
    I --> J
    J --> K[Identify Missing Skills]
    K --> L[Generate Recommendations]
    L --> M[Output Match Results]
```

### Priority-Based Scoring

```mermaid
flowchart LR
    A[Matched Skills] --> B{Priority Level}
    B -->|HIGH| C[Weight: 3.0]
    B -->|MEDIUM| D[Weight: 2.0]
    B -->|LOW| E[Weight: 1.0]
    C --> F[Calculate Score]
    D --> F
    E --> F
    F --> G[Technical Match %]
    F --> H[Soft Skill Match %]
    G --> I[Weighted Match %]
    H --> I
```

---

## 5. Database ER Diagram

### Complete Entity Relationship Diagram

```mermaid
erDiagram
    User ||--o{ Resume : "uploads"
    User ||--o{ Application : "tracks"
    User ||--o{ Alert : "receives"
    User ||--o{ SavedJob : "saves"
    User ||--o{ CareerFit : "analyzes"
    User ||--o{ CareerConversation : "has"
    User ||--o{ LearningRoadmap : "creates"
    User ||--o{ CareerPath : "explores"
    User ||--o{ CareerFitScore : "receives"
    
    Resume ||--o{ JobMatch : "generates"
    Resume ||--o{ ResumeOptimization : "receives"
    Resume ||--o{ JobIntelligence : "analyzes"
    Resume ||--o{ LearningRoadmap : "based on"
    Resume ||--o{ CareerPath : "analyzes"
    Resume ||--o{ CareerFitScore : "evaluates"
    
    Job ||--o{ JobMatch : "matches with"
    Job ||--o{ Application : "applied to"
    Job ||--o{ JobSkill : "requires"
    Job ||--o{ JobIntelligence : "analyzed for"
    Job ||--o{ ResumeOptimization : "optimized for"
    
    Job ||--|| JobSource : "belongs to"
    Job ||--o{ JobSearchHistory : "found in"
    
    User {
        int id PK
        string email UK
        string name
        string password_hash
        datetime created_at
        datetime updated_at
        boolean is_active
    }
    
    Resume {
        int id PK
        int user_id FK
        string filename
        text raw_text
        text parsed_json
        datetime created_at
        datetime updated_at
    }
    
    Job {
        int id PK
        string title
        string company
        string location
        boolean remote
        int salary_min
        int salary_max
        int experience_min
        int experience_max
        text required_skills
        text description
        string source
        string source_job_id
        string apply_url
        datetime posted_date
        datetime fetched_at
        datetime created_at
        datetime updated_at
    }
    
    JobMatch {
        int id PK
        int resume_id FK
        int job_id FK
        float match_percentage
        float weighted_match_percentage
        float technical_match_percentage
        float soft_skill_match_percentage
        text matched_skills
        text missing_skills
        text recommendations
        datetime created_at
    }
    
    Application {
        int id PK
        int user_id FK
        int job_id FK
        int resume_id FK
        string status
        text notes
        datetime applied_date
        datetime created_at
        datetime updated_at
    }
    
    Alert {
        int id PK
        int user_id FK
        string alert_type
        string title
        text message
        text metadata
        boolean is_read
        datetime created_at
    }
    
    SavedJob {
        int id PK
        int user_id FK
        string job_id
        string job_title
        string company
        string location
        string salary
        string work_mode
        string source
        string source_url
        datetime saved_at
    }
    
    CareerFit {
        int id PK
        int user_id FK
        string career_name
        float score
        text skills_match
        text projects_match
        text experience_match
        text recommendations
        datetime created_at
    }
    
    CareerConversation {
        int id PK
        int user_id FK
        text question
        text answer
        text context
        string conversation_type
        datetime created_at
    }
    
    LearningRoadmap {
        int id PK
        int user_id FK
        int resume_id FK
        string target_role
        string timeline
        text roadmap_data
        text missing_skills
        datetime start_date
        datetime end_date
        float progress_percentage
        datetime created_at
        datetime updated_at
    }
    
    CareerPath {
        int id PK
        int user_id FK
        int resume_id FK
        string top_career_path
        text alternative_paths
        text growth_opportunities
        text recommended_next_steps
        text career_trajectory
        datetime created_at
    }
    
    CareerFitScore {
        int id PK
        int user_id FK
        int resume_id FK
        float overall_score
        float skills_score
        float projects_score
        float experience_score
        float education_score
        string readiness_level
        text breakdown
        text recommendations
        datetime created_at
    }
    
    JobSkill {
        int id PK
        int job_id FK
        string skill
        datetime created_at
    }
    
    JobSource {
        int id PK
        string source_name
        int jobs_fetched
        int jobs_stored
        datetime last_sync
        boolean is_active
        string api_endpoint
        int rate_limit
        datetime created_at
        datetime updated_at
    }
    
    JobSearchHistory {
        int id PK
        int user_id FK
        string query
        string location
        int total_results
        text filters
        datetime created_at
    }
```

---

## 6. Component Diagram

### Service Component Diagram

```mermaid
graph TB
    subgraph "Presentation Components"
        A[Streamlit Pages]
        B[API Endpoints]
    end
    
    subgraph "Business Logic Components"
        C[Resume Parser]
        D[Job Matcher]
        E[Job Discovery]
        F[Career Coach]
        G[Analytics Engine]
    end
    
    subgraph "Data Access Components"
        H[Resume Repository]
        I[Job Repository]
        J[User Repository]
        K[Application Repository]
    end
    
    subgraph "External Integration Components"
        L[Gemini Client]
        M[Job Scrapers]
        N[Email Service]
    end
    
    subgraph "Utility Components"
        O[Text Cleaner]
        P[Skill Categorizer]
        Q[Ranking Engine]
        R[Embedding Service]
    end
    
    A --> C
    A --> D
    A --> E
    A --> F
    A --> G
    
    B --> C
    B --> D
    B --> E
    B --> F
    B --> G
    
    C --> H
    C --> L
    C --> O
    
    D --> H
    D --> I
    D --> P
    D --> Q
    
    E --> I
    E --> M
    E --> Q
    
    F --> J
    F --> L
    F --> R
    
    G --> J
    G --> K
    G --> R
    
    H -->[(Database)]
    I -->[(Database)]
    J -->[(Database)]
    K -->[(Database)]
```

---

## 7. Data Flow Diagram

### Resume Processing Data Flow

```mermaid
graph LR
    A[PDF File] --> B[PyMuPDF]
    B --> C[Raw Text]
    C --> D[Text Cleaner]
    D --> E[Cleaned Text]
    E --> F[Gemini API]
    F --> G[Structured JSON]
    G --> H[Pydantic Validator]
    H --> I[Validated Data]
    I --> J[SQLAlchemy ORM]
    J --> K[Database]
```

### Job Discovery Data Flow

```mermaid
graph LR
    A[Search Query] --> B[Search Engine]
    B --> C[Platform Connectors]
    C --> D[Selenium Scrapers]
    D --> E[Raw HTML]
    E --> F[BeautifulSoup Parser]
    F --> G[Job Data]
    G --> H[Deduplicator]
    H --> I[Unique Jobs]
    I --> J[Normalizer]
    J --> K[Normalized Jobs]
    K --> L[Database]
```

---

## 8. Deployment Architecture

### Production Deployment Diagram

```mermaid
graph TB
    subgraph "CDN"
        A[Cloudflare CDN]
    end
    
    subgraph "Load Balancer"
        B[Nginx Load Balancer]
    end
    
    subgraph "Application Servers"
        C[Streamlit Instance 1]
        D[Streamlit Instance 2]
        E[Streamlit Instance 3]
    end
    
    subgraph "API Servers"
        F[FastAPI Instance 1]
        G[FastAPI Instance 2]
    end
    
    subgraph "Database Layer"
        H[PostgreSQL Primary]
        I[PostgreSQL Replica 1]
        J[PostgreSQL Replica 2]
    end
    
    subgraph "Cache Layer"
        K[Redis Cluster]
    end
    
    subgraph "External Services"
        L[Gemini API]
        M[Job Platforms]
        N[Email Service]
    end
    
    A --> B
    B --> C
    B --> D
    B --> E
    B --> F
    B --> G
    
    C --> K
    D --> K
    E --> K
    F --> K
    G --> K
    
    C --> H
    D --> H
    E --> H
    F --> H
    G --> H
    
    H --> I
    H --> J
    
    C --> L
    F --> L
    D --> M
    G --> M
    E --> N
```

---

## 9. Security Architecture

### Authentication & Authorization Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Auth Service
    participant Database
    
    User->>Frontend: Login Request
    Frontend->>API: POST /auth/login
    API->>Auth Service: Validate Credentials
    Auth Service->>Database: Query User
    Database->>Auth Service: User Data
    Auth Service->>Auth Service: Generate JWT
    Auth Service->>API: JWT Token
    API->>Frontend: JWT Token
    Frontend->>Frontend: Store Token
    Frontend->>API: Protected Request + JWT
    API->>Auth Service: Validate JWT
    Auth Service->>API: Valid/Invalid
    API->>Frontend: Response
```

---

## 10. Microservices Architecture (Future)

### Planned Microservices Design

```mermaid
graph TB
    subgraph "API Gateway"
        A[API Gateway]
    end
    
    subgraph "Core Services"
        B[Resume Service]
        C[Job Service]
        D[Match Service]
        E[Career Service]
        F[Analytics Service]
    end
    
    subgraph "Support Services"
        G[Auth Service]
        H[Notification Service]
        I[Search Service]
    end
    
    subgraph "Data Layer"
        J[PostgreSQL]
        K[Redis]
        L[Elasticsearch]
    end
    
    subgraph "Message Queue"
        M[RabbitMQ]
    end
    
    A --> B
    A --> C
    A --> D
    A --> E
    A --> F
    A --> G
    
    B --> M
    C --> M
    D --> M
    E --> M
    F --> M
    
    B --> J
    C --> J
    D --> J
    E --> J
    F --> J
    
    B --> K
    C --> K
    D --> K
    
    C --> L
    I --> L
    
    G --> J
    H --> M
```

---

## Diagram Usage Guide

### How to View These Diagrams

1. **GitHub**: These diagrams render automatically in GitHub markdown
2. **VS Code**: Install Mermaid preview extension
3. **Online**: Use [Mermaid Live Editor](https://mermaid.live/)
4. **Documentation**: These are included in the architecture.md file

### Modifying Diagrams

1. Edit this file directly
2. Use Mermaid syntax
3. Test in Mermaid Live Editor
4. Commit changes to repository

### Adding New Diagrams

1. Follow the existing structure
2. Use appropriate diagram type (flowchart, sequence, erDiagram, etc.)
3. Add descriptive titles
4. Update this table of contents

---

## Diagram Standards

### Naming Conventions

- Use clear, descriptive names
- Follow camelCase for components
- Use PascalCase for classes/entities
- Use UPPER_CASE for constants

### Color Coding

- **Blue**: User/Client components
- **Green**: Service components
- **Orange**: Data components
- **Purple**: External services
- **Red**: Error/exception paths

### Complexity Guidelines

- Keep diagrams focused on single responsibility
- Avoid overcrowding with too many elements
- Use subgraphs for organization
- Provide clear labels and connections

---

**Last Updated**: June 20, 2026  
**Maintained By**: Jayesh  
**Version**: 1.0.0
