"""
Skill Extractor Service

Handles skill extraction from job descriptions with:
- Technical skill whitelist
- Stopword filtering
- Skill normalization
"""

from __future__ import annotations

import re
from typing import Any


# Technical skill whitelist - only these will be extracted
TECHNICAL_SKILL_WHITELIST = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "swift",
    "kotlin", "scala", "ruby", "php", "perl", "r", "matlab", "shell", "bash",
    "objective-c", "dart", "lua", "haskell", "elixir", "erlang", "clojure", "f#", "groovy",
    
    # Frontend Frameworks & Libraries
    "react", "angular", "vue", "next.js", "nuxt.js", "svelte", "ember", "backbone",
    "jquery", "redux", "mobx", "webpack", "vite", "parcel", "gatsby", "astro",
    "solid.js", "qwik", "alpine.js", "htmx", "lit", "stimulus",
    
    # Backend Frameworks
    "django", "flask", "fastapi", "spring", "express", "nest.js", "laravel", "rails",
    "fiber", "gin", "echo", "actix", "tornado", "aiohttp", "sanic", "quart",
    "falcon", "bottle", "cherrypy", "pyramid", "turbo gears", "web2py",
    
    # Databases
    "sql", "mysql", "postgresql", "postgres", "mongodb", "redis", "elasticsearch",
    "sqlite", "oracle", "cassandra", "dynamodb", "firebase", "supabase",
    "mariadb", "cockroachdb", "timescaledb", "influxdb", "neo4j", "couchdb",
    "rabbitmq", "kafka", "pulsar",
    
    # Cloud Platforms
    "aws", "azure", "gcp", "google cloud", "heroku", "vercel", "netlify", "digitalocean",
    "cloudflare", "linode", "scaleway", "ibm cloud", "alibaba cloud", "oracle cloud",
    
    # DevOps & Tools
    "docker", "kubernetes", "terraform", "ansible", "jenkins", "git", "github", "gitlab",
    "ci/cd", "linux", "unix", "nginx", "apache", "graphql", "rest api", "grpc",
    "prometheus", "grafana", "elk stack", "logstash", "kibana", "fluentd",
    "helm", "argocd", "pulumi", "packer", "consul", "nomad", "vault",
    
    # Data Science & ML
    "machine learning", "deep learning", "nlp", "data science", "pandas", "numpy",
    "tensorflow", "pytorch", "scikit-learn", "spark", "hadoop", "jupyter", "tableau",
    "power bi", "matplotlib", "seaborn", "keras", "theano", "mxnet", "caffe",
    "opencv", "nltk", "spacy", "gensim", "xgboost", "lightgbm", "catboost",
    "ray", "dask", "polars", "apache beam", "airflow", "dbt", "prefect",
    
    # Frontend Technologies
    "html", "css", "sass", "scss", "tailwind", "bootstrap", "material ui", "chakra ui",
    "ant design", "styled-components", "css-in-js", "responsive design",
    "less", "stylus", "postcss", "babel", "eslint", "prettier",
    
    # Testing
    "junit", "pytest", "selenium", "cypress", "jest", "mocha", "chai", "testing",
    "playwright", "puppeteer", "webdriver", "testng", "rspec", "vitest", "karma",
    
    # Mobile
    "react native", "flutter", "swift", "kotlin", "android", "ios",
    "xamarin", "ionic", "capacitor", "expo", "react native", "cordova",
    
    # Other Technologies
    "agile", "scrum", "jira", "confluence", "figma", "adobe xd", "sketch",
    "trello", "asana", "slack", "microsoft teams", "zoom", "notion",
}


# Stopwords - these should never be extracted as skills
STOPWORDS = {
    "multiple", "object", "required", "preferred", "knowledge", "experience",
    "testing", "frameworks", "responsible", "candidate", "ability", "strong",
    "excellent", "good", "solid", "working", "using", "including", "various",
    "several", "many", "different", "related", "relevant", "basic", "advanced",
    "proficient", "familiar", "understanding", "ability", "skills", "skill",
    "technologies", "technology", "tools", "tool", "platforms", "platform",
    "systems", "system", "applications", "application", "software", "development",
    "design", "management", "support", "maintenance", "deployment", "integration",
    "implementation", "architecture", "engineering", "programming", "coding",
    "analysis", "analytical", "communication", "teamwork", "collaboration",
    "problem-solving", "leadership", "organization", "planning", "execution",
    "documentation", "reporting", "monitoring", "optimization", "performance",
    "security", "quality", "assurance", "compliance", "regulatory", "standards",
    "best", "practices", "methodologies", "processes", "procedures", "policies",
    "strategies", "strategy", "goals", "objectives", "requirements", "specifications",
    "deliverables", "milestones", "deadlines", "budget", "resources", "stakeholders",
    "clients", "customers", "users", "business", "commercial", "enterprise",
    "industry", "sector", "domain", "field", "area", "environment", "context",
    "background", "education", "degree", "certification", "training", "learning",
    "self-motivated", "detail-oriented", "results-driven", "fast-paced", "dynamic",
    "innovative", "creative", "strategic", "analytical", "technical", "professional",
}


def preprocess_job_description(job_description: str) -> str:
    """
    Clean and normalize job description before skill extraction.
    
    - Remove duplicate lines
    - Remove excessive whitespace
    - Normalize line endings
    """
    if not job_description:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', job_description)
    
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove duplicate lines (case-insensitive)
    lines = text.split('\n')
    seen = set()
    unique_lines = []
    for line in lines:
        normalized = line.strip().lower()
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique_lines.append(line.strip())
    
    return ' '.join(unique_lines)


def extract_skills_from_text(text: str) -> set[str]:
    """
    Extract skills from text using whitelist and stopword filtering.
    
    Returns only skills that match the technical whitelist and are not stopwords.
    Uses word-boundary matching to prevent false positives.
    """
    if not text:
        return set()
    
    text_lower = text.lower()
    found_skills = set()
    
    # Check for whitelisted skills using word boundaries
    for skill in TECHNICAL_SKILL_WHITELIST:
        # Use regex word boundary matching
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower, re.IGNORECASE):
            found_skills.add(skill)
    
    # Filter out stopwords
    filtered_skills = {skill for skill in found_skills if skill not in STOPWORDS}
    
    return filtered_skills


def extract_skills_from_text_with_confidence(text: str) -> dict[str, Any]:
    """
    Extract skills from text with confidence scoring and logging.
    
    Returns:
        dict with:
        - skills: set of extracted skills
        - confidence_scores: dict mapping skill to confidence score (0-1)
        - extraction_log: list of tuples (skill, confidence, reason)
    """
    if not text:
        return {
            "skills": set(),
            "confidence_scores": {},
            "extraction_log": []
        }
    
    text_lower = text.lower()
    found_skills = {}
    extraction_log = []
    
    # Check for whitelisted skills using word boundaries
    for skill in TECHNICAL_SKILL_WHITELIST:
        # Use regex word boundary matching
        pattern = r'\b' + re.escape(skill) + r'\b'
        matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
        
        if matches:
            # Calculate confidence based on context
            confidence = 0.5  # Base confidence
            reason = "Found in text"
            
            # Boost confidence for multi-word skills
            if len(skill.split()) > 1:
                confidence += 0.2
                reason += " (multi-word)"
            
            # Boost confidence if appears in technical context
            technical_contexts = [
                "experience with", "knowledge of", "proficient in", 
                "skilled in", "expert in", "familiar with",
                "required", "preferred", "must have"
            ]
            for context in technical_contexts:
                if context in text_lower:
                    # Check if skill appears near technical context
                    for match in matches:
                        context_window = text_lower[max(0, match.start()-50):match.end()+50]
                        if context in context_window:
                            confidence += 0.3
                            reason += f" (near '{context}')"
                            break
            
            # Cap confidence at 1.0
            confidence = min(confidence, 1.0)
            
            found_skills[skill] = confidence
            extraction_log.append((skill, confidence, reason))
    
    # Filter out stopwords and low-confidence skills
    filtered_skills = {}
    filtered_log = []
    
    for skill, confidence in found_skills.items():
        if skill not in STOPWORDS and confidence >= 0.5:
            filtered_skills[skill] = confidence
            filtered_log.append((skill, confidence, 
                next(r for s, c, r in extraction_log if s == skill)))
    
    return {
        "skills": set(filtered_skills.keys()),
        "confidence_scores": filtered_skills,
        "extraction_log": filtered_log
    }


def extract_resume_skills(parsed_data: dict[str, Any]) -> set[str]:
    """
    Extract skill names from parsed resume JSON.
    
    Returns normalized, filtered skills from the resume.
    """
    skills = parsed_data.get("skills", [])
    skill_names = set()
    
    for skill in skills:
        if isinstance(skill, str):
            skill_names.add(skill.lower().strip())
        elif isinstance(skill, dict):
            name = skill.get("name", "")
            if name:
                skill_names.add(name.lower().strip())
    
    # Filter to only whitelisted skills
    filtered_skills = {skill for skill in skill_names if skill in TECHNICAL_SKILL_WHITELIST}
    
    return filtered_skills


def extract_job_skills(job_description: str) -> set[str]:
    """
    Extract skills from job description using whitelist and stopword filtering.
    
    Preprocesses the description and extracts only valid technical skills.
    Uses confidence-based extraction to reduce false positives.
    """
    if not job_description:
        return set()
    
    # Preprocess the job description
    cleaned_text = preprocess_job_description(job_description)
    
    # Extract skills using confidence-based extraction
    result = extract_skills_from_text_with_confidence(cleaned_text)
    
    return result["skills"]
