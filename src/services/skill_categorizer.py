"""
Skill Categorizer Service

Categorizes skills into logical groups for analysis and visualization.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class SkillCategory(Enum):
    """Skill categories for grouping and analysis."""
    PROGRAMMING_LANGUAGES = "Programming Languages"
    FRONTEND = "Frontend"
    BACKEND = "Backend"
    DATABASES = "Databases"
    CLOUD = "Cloud"
    DEVOPS = "DevOps"
    DATA_SCIENCE = "Data Science"
    TESTING = "Testing"
    MOBILE = "Mobile"
    TOOLS = "Tools"
    SOFT_SKILLS = "Soft Skills"
    OTHER = "Other"


# Skill to category mapping
SKILL_CATEGORY_MAP = {
    # Programming Languages
    "Python": SkillCategory.PROGRAMMING_LANGUAGES,
    "Java": SkillCategory.PROGRAMMING_LANGUAGES,
    "JavaScript": SkillCategory.PROGRAMMING_LANGUAGES,
    "TypeScript": SkillCategory.PROGRAMMING_LANGUAGES,
    "C++": SkillCategory.PROGRAMMING_LANGUAGES,
    "C#": SkillCategory.PROGRAMMING_LANGUAGES,
    "Go": SkillCategory.PROGRAMMING_LANGUAGES,
    "Rust": SkillCategory.PROGRAMMING_LANGUAGES,
    "Swift": SkillCategory.PROGRAMMING_LANGUAGES,
    "Kotlin": SkillCategory.PROGRAMMING_LANGUAGES,
    "Scala": SkillCategory.PROGRAMMING_LANGUAGES,
    "Ruby": SkillCategory.PROGRAMMING_LANGUAGES,
    "PHP": SkillCategory.PROGRAMMING_LANGUAGES,
    "Perl": SkillCategory.PROGRAMMING_LANGUAGES,
    "R": SkillCategory.PROGRAMMING_LANGUAGES,
    "MATLAB": SkillCategory.PROGRAMMING_LANGUAGES,
    "Shell": SkillCategory.PROGRAMMING_LANGUAGES,
    "Bash": SkillCategory.PROGRAMMING_LANGUAGES,
    "Objective-C": SkillCategory.PROGRAMMING_LANGUAGES,
    "Dart": SkillCategory.PROGRAMMING_LANGUAGES,
    "Lua": SkillCategory.PROGRAMMING_LANGUAGES,
    "Haskell": SkillCategory.PROGRAMMING_LANGUAGES,
    "Elixir": SkillCategory.PROGRAMMING_LANGUAGES,
    "Erlang": SkillCategory.PROGRAMMING_LANGUAGES,
    "Clojure": SkillCategory.PROGRAMMING_LANGUAGES,
    "F#": SkillCategory.PROGRAMMING_LANGUAGES,
    "Groovy": SkillCategory.PROGRAMMING_LANGUAGES,
    
    # Frontend
    "React": SkillCategory.FRONTEND,
    "Angular": SkillCategory.FRONTEND,
    "Vue": SkillCategory.FRONTEND,
    "Next.js": SkillCategory.FRONTEND,
    "Nuxt.js": SkillCategory.FRONTEND,
    "Svelte": SkillCategory.FRONTEND,
    "Ember": SkillCategory.FRONTEND,
    "Backbone": SkillCategory.FRONTEND,
    "jQuery": SkillCategory.FRONTEND,
    "Redux": SkillCategory.FRONTEND,
    "MobX": SkillCategory.FRONTEND,
    "Webpack": SkillCategory.FRONTEND,
    "Vite": SkillCategory.FRONTEND,
    "Parcel": SkillCategory.FRONTEND,
    "Gatsby": SkillCategory.FRONTEND,
    "Astro": SkillCategory.FRONTEND,
    "Solid.js": SkillCategory.FRONTEND,
    "Qwik": SkillCategory.FRONTEND,
    "Alpine.js": SkillCategory.FRONTEND,
    "HTMX": SkillCategory.FRONTEND,
    "Lit": SkillCategory.FRONTEND,
    "Stimulus": SkillCategory.FRONTEND,
    "HTML": SkillCategory.FRONTEND,
    "CSS": SkillCategory.FRONTEND,
    "Sass": SkillCategory.FRONTEND,
    "SCSS": SkillCategory.FRONTEND,
    "Tailwind": SkillCategory.FRONTEND,
    "Bootstrap": SkillCategory.FRONTEND,
    "Material UI": SkillCategory.FRONTEND,
    "Chakra UI": SkillCategory.FRONTEND,
    "Ant Design": SkillCategory.FRONTEND,
    "Styled Components": SkillCategory.FRONTEND,
    "CSS-in-JS": SkillCategory.FRONTEND,
    "Responsive Design": SkillCategory.FRONTEND,
    "Less": SkillCategory.FRONTEND,
    "Stylus": SkillCategory.FRONTEND,
    "PostCSS": SkillCategory.FRONTEND,
    "Babel": SkillCategory.FRONTEND,
    "ESLint": SkillCategory.FRONTEND,
    "Prettier": SkillCategory.FRONTEND,
    
    # Backend
    "Django": SkillCategory.BACKEND,
    "Flask": SkillCategory.BACKEND,
    "FastAPI": SkillCategory.BACKEND,
    "Spring": SkillCategory.BACKEND,
    "Spring Boot": SkillCategory.BACKEND,
    "Express": SkillCategory.BACKEND,
    "Nest.js": SkillCategory.BACKEND,
    "Laravel": SkillCategory.BACKEND,
    "Rails": SkillCategory.BACKEND,
    "Fiber": SkillCategory.BACKEND,
    "Gin": SkillCategory.BACKEND,
    "Echo": SkillCategory.BACKEND,
    "Actix": SkillCategory.BACKEND,
    "Tornado": SkillCategory.BACKEND,
    "AIOHTTP": SkillCategory.BACKEND,
    "Sanic": SkillCategory.BACKEND,
    "Quart": SkillCategory.BACKEND,
    "Falcon": SkillCategory.BACKEND,
    "Bottle": SkillCategory.BACKEND,
    "CherryPy": SkillCategory.BACKEND,
    "Pyramid": SkillCategory.BACKEND,
    "TurboGears": SkillCategory.BACKEND,
    "Web2py": SkillCategory.BACKEND,
    "Node.js": SkillCategory.BACKEND,
    "REST API": SkillCategory.BACKEND,
    "GraphQL": SkillCategory.BACKEND,
    "gRPC": SkillCategory.BACKEND,
    
    # Databases
    "SQL": SkillCategory.DATABASES,
    "MySQL": SkillCategory.DATABASES,
    "PostgreSQL": SkillCategory.DATABASES,
    "MongoDB": SkillCategory.DATABASES,
    "Redis": SkillCategory.DATABASES,
    "Elasticsearch": SkillCategory.DATABASES,
    "SQLite": SkillCategory.DATABASES,
    "Oracle": SkillCategory.DATABASES,
    "Cassandra": SkillCategory.DATABASES,
    "DynamoDB": SkillCategory.DATABASES,
    "Firebase": SkillCategory.DATABASES,
    "Supabase": SkillCategory.DATABASES,
    "MariaDB": SkillCategory.DATABASES,
    "CockroachDB": SkillCategory.DATABASES,
    "TimescaleDB": SkillCategory.DATABASES,
    "InfluxDB": SkillCategory.DATABASES,
    "Neo4j": SkillCategory.DATABASES,
    "CouchDB": SkillCategory.DATABASES,
    "RabbitMQ": SkillCategory.DATABASES,
    "Kafka": SkillCategory.DATABASES,
    "Pulsar": SkillCategory.DATABASES,
    
    # Cloud
    "AWS": SkillCategory.CLOUD,
    "Azure": SkillCategory.CLOUD,
    "GCP": SkillCategory.CLOUD,
    "Heroku": SkillCategory.CLOUD,
    "Vercel": SkillCategory.CLOUD,
    "Netlify": SkillCategory.CLOUD,
    "DigitalOcean": SkillCategory.CLOUD,
    "Cloudflare": SkillCategory.CLOUD,
    "Linode": SkillCategory.CLOUD,
    "Scaleway": SkillCategory.CLOUD,
    "IBM Cloud": SkillCategory.CLOUD,
    "Alibaba Cloud": SkillCategory.CLOUD,
    "Oracle Cloud": SkillCategory.CLOUD,
    
    # DevOps
    "Docker": SkillCategory.DEVOPS,
    "Kubernetes": SkillCategory.DEVOPS,
    "Terraform": SkillCategory.DEVOPS,
    "Ansible": SkillCategory.DEVOPS,
    "Jenkins": SkillCategory.DEVOPS,
    "Git": SkillCategory.DEVOPS,
    "GitHub": SkillCategory.DEVOPS,
    "GitLab": SkillCategory.DEVOPS,
    "CI/CD": SkillCategory.DEVOPS,
    "Linux": SkillCategory.DEVOPS,
    "Unix": SkillCategory.DEVOPS,
    "Nginx": SkillCategory.DEVOPS,
    "Apache": SkillCategory.DEVOPS,
    "Prometheus": SkillCategory.DEVOPS,
    "Grafana": SkillCategory.DEVOPS,
    "ELK Stack": SkillCategory.DEVOPS,
    "Logstash": SkillCategory.DEVOPS,
    "Kibana": SkillCategory.DEVOPS,
    "Fluentd": SkillCategory.DEVOPS,
    "Helm": SkillCategory.DEVOPS,
    "ArgoCD": SkillCategory.DEVOPS,
    "Pulumi": SkillCategory.DEVOPS,
    "Packer": SkillCategory.DEVOPS,
    "Consul": SkillCategory.DEVOPS,
    "Nomad": SkillCategory.DEVOPS,
    "Vault": SkillCategory.DEVOPS,
    
    # Data Science
    "Machine Learning": SkillCategory.DATA_SCIENCE,
    "Deep Learning": SkillCategory.DATA_SCIENCE,
    "NLP": SkillCategory.DATA_SCIENCE,
    "Data Science": SkillCategory.DATA_SCIENCE,
    "Pandas": SkillCategory.DATA_SCIENCE,
    "NumPy": SkillCategory.DATA_SCIENCE,
    "TensorFlow": SkillCategory.DATA_SCIENCE,
    "PyTorch": SkillCategory.DATA_SCIENCE,
    "Scikit-learn": SkillCategory.DATA_SCIENCE,
    "Apache Spark": SkillCategory.DATA_SCIENCE,
    "Hadoop": SkillCategory.DATA_SCIENCE,
    "Jupyter": SkillCategory.DATA_SCIENCE,
    "Tableau": SkillCategory.DATA_SCIENCE,
    "Power BI": SkillCategory.DATA_SCIENCE,
    "Matplotlib": SkillCategory.DATA_SCIENCE,
    "Seaborn": SkillCategory.DATA_SCIENCE,
    "Keras": SkillCategory.DATA_SCIENCE,
    "Theano": SkillCategory.DATA_SCIENCE,
    "MXNet": SkillCategory.DATA_SCIENCE,
    "Caffe": SkillCategory.DATA_SCIENCE,
    "OpenCV": SkillCategory.DATA_SCIENCE,
    "NLTK": SkillCategory.DATA_SCIENCE,
    "spaCy": SkillCategory.DATA_SCIENCE,
    "Gensim": SkillCategory.DATA_SCIENCE,
    "XGBoost": SkillCategory.DATA_SCIENCE,
    "LightGBM": SkillCategory.DATA_SCIENCE,
    "CatBoost": SkillCategory.DATA_SCIENCE,
    "Ray": SkillCategory.DATA_SCIENCE,
    "Dask": SkillCategory.DATA_SCIENCE,
    "Polars": SkillCategory.DATA_SCIENCE,
    "Apache Beam": SkillCategory.DATA_SCIENCE,
    "Airflow": SkillCategory.DATA_SCIENCE,
    "dbt": SkillCategory.DATA_SCIENCE,
    "Prefect": SkillCategory.DATA_SCIENCE,
    
    # Testing
    "JUnit": SkillCategory.TESTING,
    "Pytest": SkillCategory.TESTING,
    "Selenium": SkillCategory.TESTING,
    "Cypress": SkillCategory.TESTING,
    "Jest": SkillCategory.TESTING,
    "Mocha": SkillCategory.TESTING,
    "Chai": SkillCategory.TESTING,
    "Testing": SkillCategory.TESTING,
    "Playwright": SkillCategory.TESTING,
    "Puppeteer": SkillCategory.TESTING,
    "WebDriver": SkillCategory.TESTING,
    "TestNG": SkillCategory.TESTING,
    "RSpec": SkillCategory.TESTING,
    "Vitest": SkillCategory.TESTING,
    "Karma": SkillCategory.TESTING,
    
    # Mobile
    "React Native": SkillCategory.MOBILE,
    "Flutter": SkillCategory.MOBILE,
    "Android": SkillCategory.MOBILE,
    "iOS": SkillCategory.MOBILE,
    "Xamarin": SkillCategory.MOBILE,
    "Ionic": SkillCategory.MOBILE,
    "Capacitor": SkillCategory.MOBILE,
    "Expo": SkillCategory.MOBILE,
    "Cordova": SkillCategory.MOBILE,
    
    # Tools
    "Agile": SkillCategory.TOOLS,
    "Scrum": SkillCategory.TOOLS,
    "Jira": SkillCategory.TOOLS,
    "Confluence": SkillCategory.TOOLS,
    "Figma": SkillCategory.TOOLS,
    "Adobe XD": SkillCategory.TOOLS,
    "Sketch": SkillCategory.TOOLS,
    "Trello": SkillCategory.TOOLS,
    "Asana": SkillCategory.TOOLS,
    "Slack": SkillCategory.TOOLS,
    "Microsoft Teams": SkillCategory.TOOLS,
    "Zoom": SkillCategory.TOOLS,
    "Notion": SkillCategory.TOOLS,
    
    # Soft Skills
    "Communication": SkillCategory.SOFT_SKILLS,
    "Teamwork": SkillCategory.SOFT_SKILLS,
    "Problem Solving": SkillCategory.SOFT_SKILLS,
    "Time Management": SkillCategory.SOFT_SKILLS,
    "Leadership": SkillCategory.SOFT_SKILLS,
    "Organization": SkillCategory.SOFT_SKILLS,
    "Collaboration": SkillCategory.SOFT_SKILLS,
    "Critical Thinking": SkillCategory.SOFT_SKILLS,
    "Adaptability": SkillCategory.SOFT_SKILLS,
    "Creativity": SkillCategory.SOFT_SKILLS,
}


def categorize_skill(skill: str) -> SkillCategory:
    """
    Categorize a skill into its logical group.
    
    Returns the category enum for the given skill.
    Defaults to OTHER if not found in the mapping.
    """
    return SKILL_CATEGORY_MAP.get(skill, SkillCategory.OTHER)


def categorize_skills(skills: set[str] | list[str]) -> dict[str, list[str]]:
    """
    Categorize a collection of skills into groups.
    
    Returns a dictionary mapping category names to lists of skills.
    """
    categorized = {}
    
    for skill in skills:
        category = categorize_skill(skill)
        category_name = category.value
        
        if category_name not in categorized:
            categorized[category_name] = []
        
        categorized[category_name].append(skill)
    
    # Sort skills within each category
    for category_name in categorized:
        categorized[category_name].sort()
    
    return categorized


def get_category_breakdown(skills: set[str] | list[str]) -> dict[str, Any]:
    """
    Get a detailed breakdown of skills by category.
    
    Returns category names, counts, and percentages.
    """
    categorized = categorize_skills(skills)
    total_skills = len(skills)
    
    breakdown = {}
    for category_name, category_skills in categorized.items():
        breakdown[category_name] = {
            "count": len(category_skills),
            "percentage": round(len(category_skills) / total_skills * 100, 1) if total_skills > 0 else 0.0,
            "skills": category_skills,
        }
    
    return breakdown
