# HireFlow AI - API Reference

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [API Endpoints](#api-endpoints)
- [Data Models](#data-models)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

---

## Overview

HireFlow AI provides a RESTful API for programmatic access to all features. The API allows developers to integrate resume parsing, job matching, career coaching, and other features into their applications.

### API Features

- **RESTful Design**: Standard HTTP methods and status codes
- **JSON Format**: Request and response in JSON
- **Authentication**: API key-based authentication (planned)
- **Rate Limiting**: Configurable rate limits per endpoint
- **Pagination**: Built-in pagination for list endpoints
- **Filtering**: Advanced filtering capabilities
- **Sorting**: Sort results by various fields

---

## Authentication

### Current Status

Currently, the API does not require authentication. This is suitable for development and personal use.

### Planned Authentication

Future versions will implement:

- **API Key Authentication**: Bearer token in headers
- **OAuth2**: For third-party integrations
- **JWT Tokens**: For session-based authentication

### Authentication Header (Planned)

```http
Authorization: Bearer YOUR_API_KEY
```

---

## Base URL

### Development

```
http://localhost:8000
```

### Production

```
https://api.hireflow.ai
```

---

## Response Format

### Success Response

```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Success message"
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message",
    "details": {}
  }
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

### Error Codes

| Code | Description |
|------|-------------|
| `INVALID_INPUT` | Invalid input data |
| `NOT_FOUND` | Resource not found |
| `UNAUTHORIZED` | Authentication required |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded |
| `INTERNAL_ERROR` | Internal server error |

---

## API Endpoints

### Jobs API

#### Get All Jobs

```http
GET /api/jobs
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | No | Page number (default: 1) |
| `limit` | integer | No | Items per page (default: 20) |
| `search` | string | No | Search query |
| `location` | string | No | Filter by location |
| `remote` | boolean | No | Filter remote jobs |
| `min_salary` | integer | No | Minimum salary |
| `max_salary` | integer | No | Maximum salary |
| `source` | string | No | Filter by source |

**Response:**

```json
{
  "success": true,
  "data": {
    "jobs": [
      {
        "id": 1,
        "title": "Python Developer",
        "company": "Tech Corp",
        "location": "Bangalore",
        "remote": true,
        "salary_min": 150000,
        "salary_max": 250000,
        "description": "Job description...",
        "source": "linkedin",
        "apply_url": "https://...",
        "posted_date": "2024-01-15"
      }
    ],
    "total": 100,
    "page": 1,
    "limit": 20
  }
}
```

#### Get Job by ID

```http
GET /api/jobs/{id}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Python Developer",
    "company": "Tech Corp",
    "location": "Bangalore",
    "remote": true,
    "salary_min": 150000,
    "salary_max": 250000,
    "description": "Job description...",
    "required_skills": ["Python", "Django", "SQL"],
    "source": "linkedin",
    "apply_url": "https://...",
    "posted_date": "2024-01-15"
  }
}
```

#### Search Jobs

```http
POST /api/jobs/search
```

**Request Body:**

```json
{
  "query": "Python developer",
  "location": "Bangalore",
  "remote": true,
  "experience_level": "mid",
  "salary_range": {
    "min": 150000,
    "max": 250000
  },
  "skills": ["Python", "Django"]
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "jobs": [...],
    "total": 50
  }
}
```

#### Get Job Sources

```http
GET /api/jobs/sources
```

**Response:**

```json
{
  "success": true,
  "data": {
    "sources": [
      {
        "name": "linkedin",
        "jobs_count": 1000,
        "last_sync": "2024-01-15T10:00:00Z"
      },
      {
        "name": "internshala",
        "jobs_count": 500,
        "last_sync": "2024-01-15T09:00:00Z"
      }
    ]
  }
}
```

---

### Resume API

#### Upload Resume

```http
POST /api/resume/upload
```

**Request Body:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | Yes | PDF resume file |

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "filename": "resume.pdf",
    "uploaded_at": "2024-01-15T10:00:00Z"
  }
}
```

#### Parse Resume

```http
POST /api/resume/parse
```

**Request Body:**

```json
{
  "resume_id": 1
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+91 9876543210",
    "skills": [
      {
        "name": "Python",
        "level": "advanced"
      }
    ],
    "education": [
      "B.Tech in Computer Science"
    ],
    "experience": [
      "Software Developer at Tech Corp (2022-2024)"
    ],
    "projects": [
      "Built a web application using Python and Django"
    ]
  }
}
```

#### Get Resume by ID

```http
GET /api/resume/{id}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "filename": "resume.pdf",
    "parsed_data": {
      // Parsed resume data
    },
    "created_at": "2024-01-15T10:00:00Z"
  }
}
```

#### Get All Resumes

```http
GET /api/resume
```

**Response:**

```json
{
  "success": true,
  "data": {
    "resumes": [...],
    "total": 10
  }
}
```

---

### Match API

#### Analyze Match

```http
POST /api/match/analyze
```

**Request Body:**

```json
{
  "resume_id": 1,
  "job_description": "Job description text..."
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "match_percentage": 75,
    "weighted_match_percentage": 80,
    "technical_match_percentage": 70,
    "soft_skill_match_percentage": 85,
    "matched_skills": ["Python", "Django"],
    "missing_skills": ["React", "AWS"],
    "recommendations": [
      "Learn React to improve frontend skills"
    ],
    "category_breakdown": {
      "programming_languages": {
        "match_percentage": 80,
        "matched": ["Python"],
        "missing": ["JavaScript"]
      }
    }
  }
}
```

#### Get Match History

```http
GET /api/match/history
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `resume_id` | integer | No | Filter by resume ID |
| `limit` | integer | No | Items per page |

**Response:**

```json
{
  "success": true,
  "data": {
    "matches": [...],
    "total": 50
  }
}
```

---

### Alerts API

#### Get Alerts

```http
GET /api/alerts
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | integer | No | Filter by user ID |
| `is_read` | boolean | No | Filter by read status |
| `limit` | integer | No | Items per page |

**Response:**

```json
{
  "success": true,
  "data": {
    "alerts": [
      {
        "id": 1,
        "type": "new_job",
        "title": "New Python Developer Job",
        "message": "A new job matching your profile...",
        "is_read": false,
        "created_at": "2024-01-15T10:00:00Z"
      }
    ],
    "total": 10
  }
}
```

#### Create Alert

```http
POST /api/alerts
```

**Request Body:**

```json
{
  "type": "new_job",
  "title": "Alert title",
  "message": "Alert message",
  "metadata": {
    "job_id": 1
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "type": "new_job",
    "title": "Alert title",
    "message": "Alert message",
    "is_read": false,
    "created_at": "2024-01-15T10:00:00Z"
  }
}
```

#### Mark Alert as Read

```http
PUT /api/alerts/{id}/read
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "is_read": true
  }
}
```

---

### Tracker API

#### Get Applications

```http
GET /api/applications
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | integer | No | Filter by user ID |
| `status` | string | No | Filter by status |
| `limit` | integer | No | Items per page |

**Response:**

```json
{
  "success": true,
  "data": {
    "applications": [
      {
        "id": 1,
        "job_title": "Python Developer",
        "company": "Tech Corp",
        "status": "applied",
        "applied_date": "2024-01-15",
        "notes": "Applied via LinkedIn"
      }
    ],
    "total": 25
  }
}
```

#### Create Application

```http
POST /api/applications
```

**Request Body:**

```json
{
  "job_id": 1,
  "resume_id": 1,
  "status": "saved",
  "notes": "Interesting position"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "job_id": 1,
    "resume_id": 1,
    "status": "saved",
    "notes": "Interesting position",
    "created_at": "2024-01-15T10:00:00Z"
  }
}
```

#### Update Application

```http
PUT /api/applications/{id}
```

**Request Body:**

```json
{
  "status": "applied",
  "notes": "Applied successfully"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "status": "applied",
    "notes": "Applied successfully",
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

#### Delete Application

```http
DELETE /api/applications/{id}
```

**Response:**

```json
{
  "success": true,
  "message": "Application deleted successfully"
}
```

---

### Career API

#### Get Career Advice

```http
POST /api/career/advice
```

**Request Body:**

```json
{
  "question": "How can I improve my chances of getting a Python developer job?",
  "user_profile": {
    "skills": ["Python", "Django"],
    "experience": "2 years",
    "education": "B.Tech"
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "advice": "To improve your chances...",
    "recommendations": [
      "Learn React for frontend",
      "Build more projects",
      "Contribute to open source"
    ]
  }
}
```

#### Analyze Career Fit

```http
POST /api/career/fit
```

**Request Body:**

```json
{
  "resume_id": 1,
  "target_roles": ["Python Developer", "Data Scientist"]
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "career_fits": [
      {
        "role": "Python Developer",
        "score": 85,
        "skills_match": 80,
        "recommendations": [
          "Learn AWS",
          "Improve system design skills"
        ]
      }
    ]
  }
}
```

---

## Data Models

### Job Model

```typescript
interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  remote: boolean;
  salary_min: number;
  salary_max: number;
  description: string;
  required_skills: string[];
  source: string;
  apply_url: string;
  posted_date: string;
  created_at: string;
}
```

### Resume Model

```typescript
interface Resume {
  id: number;
  filename: string;
  parsed_data: ParsedResume;
  created_at: string;
}

interface ParsedResume {
  name: string;
  email: string;
  phone: string;
  skills: Skill[];
  education: string[];
  experience: string[];
  projects: string[];
}

interface Skill {
  name: string;
  level: string;
}
```

### Match Result Model

```typescript
interface MatchResult {
  match_percentage: number;
  weighted_match_percentage: number;
  technical_match_percentage: number;
  soft_skill_match_percentage: number;
  matched_skills: string[];
  missing_skills: string[];
  recommendations: string[];
  category_breakdown: CategoryBreakdown;
}
```

---

## Rate Limiting

### Current Limits

- **Default**: 100 requests per minute
- **Burst**: 200 requests per minute
- **Daily**: 10,000 requests per day

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Rate Limit Error

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again later."
  }
}
```

---

## Examples

### Python Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Get all jobs
response = requests.get(f"{BASE_URL}/api/jobs")
jobs = response.json()

# Search jobs
search_data = {
    "query": "Python developer",
    "location": "Bangalore"
}
response = requests.post(f"{BASE_URL}/api/jobs/search", json=search_data)
results = response.json()

# Upload resume
files = {"file": open("resume.pdf", "rb")}
response = requests.post(f"{BASE_URL}/api/resume/upload", files=files)
resume = response.json()

# Parse resume
parse_data = {"resume_id": resume["data"]["id"]}
response = requests.post(f"{BASE_URL}/api/resume/parse", json=parse_data)
parsed = response.json()

# Analyze match
match_data = {
    "resume_id": resume["data"]["id"],
    "job_description": "Job description text..."
}
response = requests.post(f"{BASE_URL}/api/match/analyze", json=match_data)
match = response.json()
```

### JavaScript Example

```javascript
const BASE_URL = "http://localhost:8000";

// Get all jobs
async function getJobs() {
  const response = await fetch(`${BASE_URL}/api/jobs`);
  const data = await response.json();
  return data;
}

// Search jobs
async function searchJobs(query, location) {
  const response = await fetch(`${BASE_URL}/api/jobs/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, location }),
  });
  const data = await response.json();
  return data;
}

// Upload resume
async function uploadResume(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${BASE_URL}/api/resume/upload`, {
    method: 'POST',
    body: formData,
  });
  const data = await response.json();
  return data;
}
```

### cURL Example

```bash
# Get all jobs
curl http://localhost:8000/api/jobs

# Search jobs
curl -X POST http://localhost:8000/api/jobs/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Python developer", "location": "Bangalore"}'

# Upload resume
curl -X POST http://localhost:8000/api/resume/upload \
  -F "file=@resume.pdf"

# Parse resume
curl -X POST http://localhost:8000/api/resume/parse \
  -H "Content-Type: application/json" \
  -d '{"resume_id": 1}'

# Analyze match
curl -X POST http://localhost:8000/api/match/analyze \
  -H "Content-Type: application/json" \
  -d '{"resume_id": 1, "job_description": "Job description..."}'
```

---

## SDKs

### Python SDK (Planned)

```python
from hireflow import HireFlowClient

client = HireFlowClient(api_key="your_api_key")

# Get jobs
jobs = client.jobs.list()

# Search jobs
results = client.jobs.search(query="Python developer")

# Upload resume
resume = client.resume.upload("resume.pdf")

# Parse resume
parsed = client.resume.parse(resume.id)

# Analyze match
match = client.match.analyze(resume.id, job_description)
```

### JavaScript SDK (Planned)

```javascript
import { HireFlowClient } from 'hireflow-sdk';

const client = new HireFlowClient('your_api_key');

// Get jobs
const jobs = await client.jobs.list();

// Search jobs
const results = await client.jobs.search({
  query: 'Python developer',
  location: 'Bangalore'
});

// Upload resume
const resume = await client.resume.upload(file);

// Parse resume
const parsed = await client.resume.parse(resume.id);

// Analyze match
const match = await client.match.analyze(resume.id, jobDescription);
```

---

## Webhooks (Planned)

### Webhook Configuration

```http
POST /api/webhooks
```

**Request Body:**

```json
{
  "url": "https://your-server.com/webhook",
  "events": ["job.created", "alert.created"]
}
```

### Webhook Events

| Event | Description |
|-------|-------------|
| `job.created` | New job added |
| `alert.created` | New alert created |
| `application.updated` | Application status changed |
| `match.completed` | Match analysis completed |

---

## Changelog

### Version 1.0.0 (Current)

- Initial API release
- Jobs, Resume, Match, Alerts, Tracker endpoints
- Basic filtering and pagination
- JSON response format

### Version 1.1.0 (Planned)

- Authentication and authorization
- Rate limiting
- Webhook support
- Advanced filtering
- SDK releases

---

## Support

For API-related questions:

- **Documentation**: This reference guide
- **Issues**: [GitHub Issues](https://github.com/Jayesh01323/HireFlow/issues)
- **Email**: jayesh@example.com

---

**Last Updated**: June 20, 2026  
**Maintained By**: Jayesh  
**Version**: 1.0.0
