# Render Deployment Guide

## Overview

Render is a modern cloud platform that provides excellent support for Python applications. This guide covers deploying HireFlow AI to Render.

## Prerequisites

- Render account (free tier available)
- GitHub repository
- PostgreSQL database (recommended for production)
- Google Gemini API key

## Step-by-Step Deployment

### 1. Prepare Repository

```bash
# Ensure all changes are committed
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. Create Render Account

1. Go to [render.com](https://render.com)
2. Click "Sign up"
3. Sign up with GitHub
4. Verify email address

### 3. Create PostgreSQL Database

1. Click "New +"
2. Select "PostgreSQL"
3. Configure database:
   - Database name: `hireflow`
   - User: `hireflow_user`
   - Region: Choose nearest region
4. Click "Create Database"
5. Copy connection string

### 4. Create Web Service

1. Click "New +"
2. Select "Web Service"
3. Connect your GitHub repository
4. Configure build:

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### 5. Configure Environment Variables

Add these in Render dashboard:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://hireflow_user:your_password@host:port/hireflow
PORT=8501
PYTHON_VERSION=3.12
```

### 6. Deploy

Click "Create Web Service" and wait for deployment.

## Configuration Files

### render.yaml

Create `render.yaml`:

```yaml
services:
  - type: web
    name: hireflow-ai
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      - key: DATABASE_URL
        sync: false
      - key: PORT
        value: 8501
      - key: PYTHON_VERSION
        value: 3.12

databases:
  - name: hireflow-db
    databaseName: hireflow
    user: hireflow_user
    plan: free
```

### requirements.txt

Ensure `requirements.txt` includes:

```txt
streamlit>=1.32.0
google-generativeai>=0.5.0
PyMuPDF>=1.24.0
pydantic>=2.6.0
pandas>=2.2.0
plotly>=5.19.0
python-dotenv>=1.0.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
```

## Database Setup

### PostgreSQL Configuration

Update `DATABASE_URL` in environment variables:

```env
DATABASE_URL=postgresql://hireflow_user:your_password@host:port/hireflow
```

### Run Migrations

Add to `render.yaml` or run manually:

```bash
python -c "from src.database import init_db; init_db()"
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `PORT` | Application port | `8501` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PYTHON_VERSION` | Python version | `3.12` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Performance Optimization

### Connection Pooling

Configure SQLAlchemy connection pooling:

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

### Caching

Add Redis for caching (optional):

```yaml
databases:
  - name: hireflow-redis
    type: redis
    plan: free
```

## Monitoring

### Logs

Access logs in Render dashboard:
- Click on your service
- Go to "Logs" tab
- Filter by severity

### Metrics

Render provides:
- CPU usage
- Memory usage
- Response time
- Request count

## Troubleshooting

### Build Failures

**Issue**: Build fails during deployment

**Solutions**:
- Check requirements.txt for version conflicts
- Ensure Python version is compatible
- Check build logs for specific errors
- Try building locally first

### Database Connection Issues

**Issue**: Can't connect to PostgreSQL

**Solutions**:
- Verify DATABASE_URL is correct
- Check database is running
- Verify network connectivity
- Check firewall rules

### Runtime Errors

**Issue**: Application crashes after deployment

**Solutions**:
- Check Render logs
- Verify environment variables
- Ensure API keys are valid
- Check database connection

## Updates

### Updating Application

```bash
# Make changes locally
git add .
git commit -m "Update features"
git push origin main

# Render auto-deploys on push
```

### Database Migrations

```bash
# Run migrations manually
render ssh
python -c "from src.database import init_db; init_db()"
```

## Best Practices

### Security

- Use environment variables for secrets
- Rotate API keys regularly
- Enable SSL for database connections
- Monitor access logs

### Performance

- Use connection pooling
- Enable caching
- Optimize database queries
- Monitor resource usage

### Reliability

- Implement health checks
- Add error handling
- Monitor application logs
- Set up alerts

## Cost

### Free Tier

- **Web Service**: $0 (limited resources)
- **PostgreSQL**: $0 (90 days free, then $7/month)
- **Redis**: $0 (limited)

### Paid Tier

- **Web Service**: $7/month (starter)
- **PostgreSQL**: $7/month
- **Redis**: $5/month

## Limitations

### Current Limitations

- Free tier has resource limits
- Cold starts on free tier
- Limited custom domains on free tier
- No background workers on free tier

## Next Steps

After successful deployment:

1. Set up monitoring
2. Configure custom domain
3. Set up analytics
4. Implement backup strategy
5. Document deployment process

---

**Last Updated**: June 20, 2026  
**Platform**: Render  
**Version**: 1.0.0
