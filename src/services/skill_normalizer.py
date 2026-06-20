"""
Skill Normalizer Service

Handles skill normalization with:
- Proper capitalization
- Consistent naming conventions
- Duplicate removal
"""

from __future__ import annotations

from typing import Any


# Skill normalization dictionary - maps variations to canonical names
SKILL_NORMALIZATION_MAP = {
    # Programming Languages
    "python": "Python",
    "py": "Python",
    "java": "Java",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "go": "Go",
    "golang": "Go",
    "rust": "Rust",
    "swift": "Swift",
    "kotlin": "Kotlin",
    "scala": "Scala",
    "ruby": "Ruby",
    "php": "PHP",
    "perl": "Perl",
    "r": "R",
    "matlab": "MATLAB",
    "shell": "Shell",
    "bash": "Bash",
    "objective-c": "Objective-C",
    "dart": "Dart",
    "lua": "Lua",
    "haskell": "Haskell",
    "elixir": "Elixir",
    "erlang": "Erlang",
    "clojure": "Clojure",
    "f#": "F#",
    "fsharp": "F#",
    "groovy": "Groovy",
    
    # Frontend Frameworks & Libraries
    "react": "React",
    "reactjs": "React",
    "angular": "Angular",
    "angularjs": "Angular",
    "vue": "Vue",
    "vuejs": "Vue",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "nuxt.js": "Nuxt.js",
    "nuxtjs": "Nuxt.js",
    "svelte": "Svelte",
    "ember": "Ember",
    "backbone": "Backbone",
    "jquery": "jQuery",
    "redux": "Redux",
    "mobx": "MobX",
    "webpack": "Webpack",
    "vite": "Vite",
    "parcel": "Parcel",
    "gatsby": "Gatsby",
    "astro": "Astro",
    "solid.js": "Solid.js",
    "solidjs": "Solid.js",
    "qwik": "Qwik",
    "alpine.js": "Alpine.js",
    "alpine": "Alpine.js",
    "htmx": "HTMX",
    "lit": "Lit",
    "stimulus": "Stimulus",
    
    # Backend Frameworks
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "spring": "Spring",
    "spring boot": "Spring Boot",
    "express": "Express",
    "express.js": "Express",
    "nest.js": "Nest.js",
    "nestjs": "Nest.js",
    "laravel": "Laravel",
    "rails": "Rails",
    "ruby on rails": "Rails",
    "fiber": "Fiber",
    "gin": "Gin",
    "echo": "Echo",
    "actix": "Actix",
    "tornado": "Tornado",
    "aiohttp": "AIOHTTP",
    "sanic": "Sanic",
    "quart": "Quart",
    "falcon": "Falcon",
    "bottle": "Bottle",
    "cherrypy": "CherryPy",
    "pyramid": "Pyramid",
    "turbo gears": "TurboGears",
    "turbogears": "TurboGears",
    "web2py": "Web2py",
    
    # Databases
    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
    "sqlite": "SQLite",
    "oracle": "Oracle",
    "cassandra": "Cassandra",
    "dynamodb": "DynamoDB",
    "firebase": "Firebase",
    "supabase": "Supabase",
    "mariadb": "MariaDB",
    "cockroachdb": "CockroachDB",
    "timescaledb": "TimescaleDB",
    "influxdb": "InfluxDB",
    "neo4j": "Neo4j",
    "couchdb": "CouchDB",
    "rabbitmq": "RabbitMQ",
    "kafka": "Kafka",
    "pulsar": "Pulsar",
    
    # Cloud Platforms
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "heroku": "Heroku",
    "vercel": "Vercel",
    "netlify": "Netlify",
    "digitalocean": "DigitalOcean",
    "cloudflare": "Cloudflare",
    "linode": "Linode",
    "scaleway": "Scaleway",
    "ibm cloud": "IBM Cloud",
    "alibaba cloud": "Alibaba Cloud",
    "oracle cloud": "Oracle Cloud",
    
    # DevOps & Tools
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "jenkins": "Jenkins",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "linux": "Linux",
    "unix": "Unix",
    "nginx": "Nginx",
    "apache": "Apache",
    "graphql": "GraphQL",
    "rest api": "REST API",
    "rest": "REST API",
    "grpc": "gRPC",
    "prometheus": "Prometheus",
    "grafana": "Grafana",
    "elk stack": "ELK Stack",
    "logstash": "Logstash",
    "kibana": "Kibana",
    "fluentd": "Fluentd",
    "helm": "Helm",
    "argocd": "ArgoCD",
    "pulumi": "Pulumi",
    "packer": "Packer",
    "consul": "Consul",
    "nomad": "Nomad",
    "vault": "Vault",
    
    # Data Science & ML
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "data science": "Data Science",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "spark": "Apache Spark",
    "apache spark": "Apache Spark",
    "hadoop": "Hadoop",
    "jupyter": "Jupyter",
    "jupyter notebook": "Jupyter",
    "tableau": "Tableau",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "matplotlib": "Matplotlib",
    "seaborn": "Seaborn",
    "keras": "Keras",
    "theano": "Theano",
    "mxnet": "MXNet",
    "caffe": "Caffe",
    "opencv": "OpenCV",
    "nltk": "NLTK",
    "spacy": "spaCy",
    "gensim": "Gensim",
    "xgboost": "XGBoost",
    "lightgbm": "LightGBM",
    "catboost": "CatBoost",
    "ray": "Ray",
    "dask": "Dask",
    "polars": "Polars",
    "apache beam": "Apache Beam",
    "airflow": "Airflow",
    "dbt": "dbt",
    "prefect": "Prefect",
    
    # Frontend Technologies
    "html": "HTML",
    "css": "CSS",
    "sass": "Sass",
    "scss": "SCSS",
    "tailwind": "Tailwind",
    "tailwind css": "Tailwind",
    "bootstrap": "Bootstrap",
    "material ui": "Material UI",
    "mui": "Material UI",
    "chakra ui": "Chakra UI",
    "ant design": "Ant Design",
    "antd": "Ant Design",
    "styled-components": "Styled Components",
    "css-in-js": "CSS-in-JS",
    "responsive design": "Responsive Design",
    "less": "Less",
    "stylus": "Stylus",
    "postcss": "PostCSS",
    "babel": "Babel",
    "eslint": "ESLint",
    "prettier": "Prettier",
    
    # Testing
    "junit": "JUnit",
    "pytest": "Pytest",
    "selenium": "Selenium",
    "cypress": "Cypress",
    "jest": "Jest",
    "mocha": "Mocha",
    "chai": "Chai",
    "testing": "Testing",
    "playwright": "Playwright",
    "puppeteer": "Puppeteer",
    "webdriver": "WebDriver",
    "testng": "TestNG",
    "rspec": "RSpec",
    "vitest": "Vitest",
    "karma": "Karma",
    
    # Mobile
    "react native": "React Native",
    "flutter": "Flutter",
    "android": "Android",
    "ios": "iOS",
    "xamarin": "Xamarin",
    "ionic": "Ionic",
    "capacitor": "Capacitor",
    "expo": "Expo",
    "cordova": "Cordova",
    
    # Other Technologies
    "agile": "Agile",
    "scrum": "Scrum",
    "jira": "Jira",
    "confluence": "Confluence",
    "figma": "Figma",
    "adobe xd": "Adobe XD",
    "sketch": "Sketch",
    "trello": "Trello",
    "asana": "Asana",
    "slack": "Slack",
    "microsoft teams": "Microsoft Teams",
    "teams": "Microsoft Teams",
    "zoom": "Zoom",
    "notion": "Notion",
    
    # Soft Skills
    "communication": "Communication",
    "teamwork": "Teamwork",
    "leadership": "Leadership",
    "problem-solving": "Problem Solving",
    "problem solving": "Problem Solving",
    "time management": "Time Management",
    "critical thinking": "Critical Thinking",
    "adaptability": "Adaptability",
    "collaboration": "Collaboration",
    "creativity": "Creativity",
    "organization": "Organization",
}


def normalize_skill(skill: str) -> str:
    """
    Normalize a skill name to its canonical form.
    
    Converts lowercase variations to proper capitalization
    and maps common abbreviations to full names.
    """
    if not skill:
        return skill
    
    # Convert to lowercase for lookup
    skill_lower = skill.lower().strip()
    
    # Look up in normalization map
    if skill_lower in SKILL_NORMALIZATION_MAP:
        return SKILL_NORMALIZATION_MAP[skill_lower]
    
    # If not found, capitalize first letter of each word
    return skill.strip().title()


def normalize_skills(skills: set[str] | list[str] | set[str]) -> list[str]:
    """
    Normalize a collection of skills.
    
    Returns a sorted list of unique, normalized skill names.
    """
    if not skills:
        return []
    
    # Normalize each skill
    normalized = {normalize_skill(skill) for skill in skills}
    
    # Remove empty strings
    normalized.discard("")
    
    # Return sorted list
    return sorted(normalized)


def normalize_resume_skills(parsed_data: dict[str, Any]) -> list[str]:
    """
    Extract and normalize skills from parsed resume data.
    
    Returns a sorted list of unique, normalized skill names.
    """
    skills = parsed_data.get("skills", [])
    skill_names = set()
    
    for skill in skills:
        if isinstance(skill, str):
            skill_names.add(skill)
        elif isinstance(skill, dict):
            name = skill.get("name", "")
            if name:
                skill_names.add(name)
    
    return normalize_skills(skill_names)


def normalize_job_skills(job_skills: set[str]) -> list[str]:
    """
    Normalize extracted job skills.
    
    Returns a sorted list of unique, normalized skill names.
    """
    return normalize_skills(job_skills)
