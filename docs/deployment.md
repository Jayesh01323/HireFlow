# HireFlow AI - Deployment Guide

## Table of Contents

- [Deployment Options](#deployment-options)
- [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
- [Render Deployment](#render-deployment)
- [Railway Deployment](#railway-deployment)
- [Docker Deployment](#docker-deployment)
- [Production Checklist](#production-checklist)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

---

## Deployment Options

### Comparison

| Platform | Ease of Use | Cost | Scalability | Customization |
|----------|-------------|------|-------------|--------------|
| **Streamlit Cloud** | ⭐⭐⭐⭐⭐ | Free tier available | Limited | Low |
| **Render** | ⭐⭐⭐⭐ | Free tier available | Good | Medium |
| **Railway** | ⭐⭐⭐⭐ | Free tier available | Good | Medium |
| **AWS/GCP/Azure** | ⭐⭐ | Pay-as-you-go | Excellent | High |
| **Self-hosted** | ⭐ | Varies | Varies | Excellent |

### Recommended

- **For Development**: Streamlit Cloud (easiest)
- **For Production**: Render or Railway (good balance)
- **For Enterprise**: AWS/GCP/Azure (full control)

---

## Streamlit Cloud Deployment

### Prerequisites

- GitHub account
- Streamlit Cloud account (free)
- Application pushed to GitHub

### Step-by-Step Guide

#### 1. Prepare Repository

```bash
# Ensure all changes are committed
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### 2. Create Streamlit Cloud Account

1. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
2. Sign up with GitHub
3. Verify email

#### 3. Connect Repository

1. Click "New app"
2. Select your GitHub repository
3. Select branch: `main`
4. Main file path: `app.py`

#### 4. Configure Environment Variables

Add these in Streamlit Cloud settings:

```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///data/hireflow.db
```

#### 5. Deploy

Click "Deploy" and wait for deployment to complete.

### Streamlit Cloud Configuration

Create `.streamlit/config.toml`:

```toml
[server]
port = 8501
headless = true
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 200

[browser]
gatherUsageStats = false
serverAddress = "localhost"
serverPort = 8501

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### Streamlit Cloud Limitations

- **Free Tier**: Limited resources, community support
- **Database**: Only SQLite supported (no PostgreSQL)
- **Custom Domains**: Not available on free tier
- **Scaling**: Limited horizontal scaling

---

## Render Deployment

### Prerequisites

- Render account (free tier available)
- GitHub repository
- PostgreSQL database (recommended for production)

### Step-by-Step Guide

#### 1. Prepare Repository

```bash
# Create requirements.txt if not exists
pip freeze > requirements.txt

# Create .render directory
mkdir -p .render
```

#### 2. Create Render Configuration

Create `render.yaml`:

```yaml
services:
  - type: web
    name: hireflow-ai
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port=$PORT
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      - key: DATABASE_URL
        sync: false
      - key: PORT
        value: 8501

databases:
  - name: hireflow-db
    databaseName: hireflow
    user: hireflow_user
```

#### 3. Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Create new web service

#### 4. Connect Repository

1. Click "New +"
2. Select "Web Service"
3. Connect your GitHub repository
4. Select branch: `main`

#### 5. Configure Build & Start

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app.py --server.port=$PORT`

#### 6. Add Environment Variables

Add these in Render dashboard:

```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=postgresql://user:your_password@host:port/database
PORT=8501
```

#### 7. Deploy

Click "Create Web Service" and wait for deployment.

### Render Database Setup

#### Create PostgreSQL Database

1. In Render dashboard, click "New +"
2. Select "PostgreSQL"
3. Configure database settings
4. Copy connection string

#### Update Environment Variables

```env
DATABASE_URL=postgresql://hireflow_user:your_password@host:port/hireflow
```

#### Run Migrations

Render will automatically run migrations if you add:

```bash
# In package.json or render.yaml
scripts:
  deploy: python -c "from src.database import init_db; init_db()"
```

---

## Railway Deployment

### Prerequisites

- Railway account (free trial available)
- GitHub repository
- Railway CLI (optional)

### Step-by-Step Guide

#### 1. Install Railway CLI (Optional)

```bash
npm install -g @railway/cli
railway login
```

#### 2. Initialize Project

```bash
railway init
railway link
```

#### 3. Add Service

```bash
railway add streamlit
```

#### 4. Configure Service

Create `railway.toml`:

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "streamlit run app.py --server.port=$PORT"
healthcheckPath = "/"
healthcheckTimeout = 300

[env]
PORT = "8501"
```

#### 5. Add Environment Variables

```bash
railway variables set GEMINI_API_KEY=your_api_key
railway variables set DATABASE_URL=postgresql://...
railway variables set PORT=8501
```

#### 6. Add Database

```bash
railway add postgresql
```

#### 7. Deploy

```bash
railway up
```

### Railway Web Interface

Alternatively, use Railway web interface:

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Click "Deploy from GitHub repo"
4. Select your repository
5. Configure environment variables
6. Add PostgreSQL database
7. Deploy

---

## Docker Deployment

### Prerequisites

- Docker installed
- Docker Hub account (optional)
- Server or cloud provider

### Step-by-Step Guide

#### 1. Create Dockerfile

Create `Dockerfile`:

```dockerfile
# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data

# Expose port
EXPOSE 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run the application
CMD ["streamlit", "run", "app.py"]
```

#### 2. Create .dockerignore

Create `.dockerignore`:

```
.git
.gitignore
.env
__pycache__
*.pyc
venv
.venv
data/*.db
*.log
.DS_Store
```

#### 3. Build Docker Image

```bash
docker build -t hireflow-ai:latest .
```

#### 4. Run Docker Container

```bash
docker run -d \
  --name hireflow-ai \
  -p 8501:8501 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  hireflow-ai:latest
```

#### 5. Push to Docker Hub (Optional)

```bash
# Login to Docker Hub
docker login

# Tag image
docker tag hireflow-ai:latest yourusername/hireflow-ai:latest

# Push image
docker push yourusername/hireflow-ai:latest
```

#### 6. Docker Compose (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/hireflow
    volumes:
      - ./data:/app/data
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=hireflow
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run with Docker Compose:

```bash
docker-compose up -d
```

---

## Production Checklist

### Security

- [ ] Change default passwords
- [ ] Use HTTPS/SSL certificates
- [ ] Implement rate limiting
- [ ] Add CORS protection
- [ ] Enable security headers
- [ ] Use environment variables for secrets
- [ ] Regular security audits
- [ ] Dependency vulnerability scanning

### Performance

- [ ] Enable caching (Redis)
- [ ] Use CDN for static assets
- [ ] Optimize database queries
- [ ] Enable compression
- [ ] Monitor performance metrics
- [ ] Load testing
- [ ] Database indexing
- [ ] Connection pooling

### Reliability

- [ ] Automated backups
- [ ] Health checks
- [ ] Error monitoring (Sentry)
- [ ] Log aggregation
- [ ] Disaster recovery plan
- [ ] High availability setup
- [ ] Load balancing
- [ ] Failover mechanisms

### Monitoring

- [ ] Application monitoring
- [ ] Database monitoring
- [ ] Server monitoring
- [ ] Error tracking
- [ ] Performance metrics
- [ ] User analytics
- [ ] Uptime monitoring
- [ ] Alert notifications

---

## Monitoring & Maintenance

### Application Monitoring

#### Health Checks

Create health check endpoint:

```python
# In app.py or separate health.py
import streamlit as st

def health_check():
    """Health check endpoint for monitoring."""
    try:
        from src.database import get_session
        session = get_session()
        session.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

#### Logging

Configure production logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### Database Maintenance

#### Backups

```bash
# SQLite backup
cp data/hireflow.db data/hireflow.db.backup

# PostgreSQL backup
pg_dump -U user -h host -d database > backup.sql
```

#### Migrations

```bash
# Run database migrations
python -c "from src.database import init_db; init_db()"
```

### Performance Optimization

#### Caching Strategy

```python
# Add Redis caching
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_key(key):
    return f"hireflow:{key}"

def get_cached(key):
    return redis_client.get(cache_key(key))

def set_cached(key, value, ttl=3600):
    redis_client.setex(cache_key(key), ttl, value)
```

---

## Troubleshooting

### Common Deployment Issues

#### Issue 1: Build Fails

**Symptoms**: Deployment fails during build

**Solutions**:
- Check requirements.txt for version conflicts
- Ensure all dependencies are compatible
- Check build logs for specific errors
- Try building locally first

#### Issue 2: Database Connection Fails

**Symptoms**: Application can't connect to database

**Solutions**:
- Verify DATABASE_URL is correct
- Check database is running
- Verify network connectivity
- Check firewall rules
- Ensure database credentials are correct

#### Issue 3: Environment Variables Not Loading

**Symptoms**: Application behaves as if env vars are missing

**Solutions**:
- Verify env vars are set in platform dashboard
- Check variable names match exactly
- Restart application after adding env vars
- Check for typos in variable names

#### Issue 4: Application Crashes on Startup

**Symptoms**: Application starts but crashes immediately

**Solutions**:
- Check application logs for errors
- Verify all dependencies are installed
- Check for missing configuration files
- Ensure database is initialized
- Verify API keys are valid

#### Issue 5: Performance Issues

**Symptoms**: Application is slow or unresponsive

**Solutions**:
- Enable caching
- Optimize database queries
- Add database indexes
- Increase server resources
- Implement lazy loading
- Monitor resource usage

---

## Scaling Strategies

### Horizontal Scaling

- **Load Balancer**: Nginx or cloud load balancer
- **Multiple Instances**: Run multiple app instances
- **Session Management**: Use Redis for session storage
- **Database Replication**: Read replicas for read-heavy workloads

### Vertical Scaling

- **Increase Resources**: More CPU, RAM, storage
- **Optimize Code**: Profile and optimize bottlenecks
- **Database Optimization**: Indexing, query optimization
- **Caching**: Reduce database load

### Database Scaling

- **Connection Pooling**: Reuse database connections
- **Read Replicas**: Distribute read operations
- **Sharding**: Split data across multiple databases
- **Caching Layer**: Redis for frequently accessed data

---

## Cost Optimization

### Free Tier Usage

- **Streamlit Cloud**: Free for personal projects
- **Render**: $5 free credit monthly
- **Railway**: $5 free trial
- **PostgreSQL**: Free tier on most platforms

### Cost Reduction Tips

- Use free tiers whenever possible
- Optimize resource usage
- Implement caching to reduce API calls
- Use efficient algorithms
- Monitor and optimize database queries
- Use CDN for static assets

---

## Security Best Practices

### API Security

- [ ] Use HTTPS only
- [ ] Implement rate limiting
- [ ] Add API authentication
- [ ] Validate all inputs
- [ ] Use parameterized queries
- [ ] Keep dependencies updated
- [ ] Regular security audits

### Data Protection

- [ ] Encrypt sensitive data
- [ ] Use secure database connections
- [ ] Implement backup encryption
- [ ] Regular security updates
- [ ] Access control
- [ ] Audit logging

---

## Backup & Disaster Recovery

### Backup Strategy

- **Database Backups**: Daily automated backups
- **Code Backups**: Git repository
- **Configuration Backups**: Version control
- **Off-site Backups**: Cloud storage

### Recovery Plan

1. **Identify Failure**: Determine what failed
2. **Assess Impact**: Evaluate business impact
3. **Restore from Backup**: Use recent backup
4. **Verify Recovery**: Test restored system
5. **Communicate**: Notify stakeholders
6. **Document**: Record incident and resolution

---

## Next Steps

After successful deployment:

1. Set up monitoring and alerting
2. Configure automated backups
3. Implement logging and error tracking
4. Set up CI/CD pipeline
5. Configure performance monitoring
6. Set up security scanning
7. Document deployment process
8. Create runbooks for common issues

---

**Last Updated**: June 20, 2026  
**Maintained By**: Jayesh  
**Version**: 1.0.0
