# Streamlit Cloud Deployment Guide

## Overview

Streamlit Cloud is the easiest way to deploy HireFlow AI. This guide covers the complete deployment process.

## Prerequisites

- GitHub account
- Streamlit Cloud account (free)
- Application pushed to GitHub
- Google Gemini API key

## Step-by-Step Deployment

### 1. Prepare Repository

```bash
# Ensure all changes are committed
git add .
git commit -m "Ready for Streamlit Cloud deployment"
git push origin main
```

### 2. Create Streamlit Cloud Account

1. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
2. Click "Sign up"
3. Sign up with GitHub
4. Verify email address

### 3. Deploy Application

1. Click "New app" in Streamlit Cloud
2. Select your GitHub repository
3. Select branch: `main`
4. Main file path: `app.py`
5. Click "Deploy"

### 4. Configure Environment Variables

In Streamlit Cloud settings, add:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///data/hireflow.db
```

### 5. Verify Deployment

- Wait for deployment to complete
- Click the provided URL
- Test all major features
- Monitor logs for errors

## Configuration Files

### .streamlit/config.toml

Create `.streamlit/config.toml`:

```toml
[server]
port = 8501
headless = true
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 200
maxMessageSize = 200

[browser]
gatherUsageStats = false
serverAddress = "localhost"
serverPort = 8501

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[logger]
level = "info"
```

### .streamlit/credentials.toml

Create `.streamlit/credentials.toml` (optional):

```toml
[general]
email = "your-email@example.com"
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |
| `DATABASE_URL` | Database connection string | `sqlite:///data/hireflow.db` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level | `INFO` |
| `MAX_UPLOAD_SIZE` | Max file upload size (MB) | `200` |

## Performance Optimization

### Caching

Enable caching in your app:

```python
import streamlit as st

@st.cache_data(ttl=3600)
def get_jobs():
    """Get jobs with caching."""
    return fetch_jobs()
```

### Resource Limits

Streamlit Cloud free tier:
- **CPU**: 1 core
- **Memory**: 1 GB
- **Disk**: 1 GB

## Troubleshooting

### Build Failures

**Issue**: Build fails during deployment

**Solutions**:
- Check requirements.txt for version conflicts
- Ensure all dependencies are compatible
- Check build logs for specific errors
- Try building locally first

### Runtime Errors

**Issue**: Application crashes after deployment

**Solutions**:
- Check Streamlit Cloud logs
- Verify environment variables are set
- Ensure API keys are valid
- Check database connection

### Performance Issues

**Issue**: Application is slow

**Solutions**:
- Enable caching
- Optimize database queries
- Reduce data size
- Use pagination

## Monitoring

### Logs

Access logs in Streamlit Cloud dashboard:
- Click on your app
- Go to "Logs" tab
- Filter by severity

### Metrics

Streamlit Cloud provides:
- CPU usage
- Memory usage
- Request count
- Response time

## Updates

### Updating Application

```bash
# Make changes locally
git add .
git commit -m "Update features"
git push origin main

# Streamlit Cloud auto-deploys on push
```

### Rollback

If deployment fails:
1. Streamlit Cloud keeps previous version
2. Click "Rollback" in dashboard
3. Select previous deployment

## Best Practices

### Security

- Never commit `.env` files
- Use environment variables for secrets
- Rotate API keys regularly
- Monitor access logs

### Performance

- Use caching for expensive operations
- Optimize database queries
- Implement pagination
- Monitor resource usage

### Reliability

- Implement error handling
- Add health checks
- Monitor application logs
- Set up alerts

## Cost

### Free Tier

- **Cost**: $0
- **Resources**: 1 CPU, 1 GB RAM
- **Limitations**: Community support, no custom domain

### Paid Tier

- **Cost**: $12/month
- **Resources**: 2 CPUs, 2 GB RAM
- **Features**: Priority support, custom domain

## Limitations

### Current Limitations

- SQLite only (no PostgreSQL)
- No custom domain on free tier
- Limited resources on free tier
- No background workers
- Limited customization

## Next Steps

After successful deployment:

1. Set up monitoring
2. Configure custom domain (paid tier)
3. Set up analytics
4. Implement backup strategy
5. Document deployment process

---

**Last Updated**: June 20, 2026  
**Platform**: Streamlit Cloud  
**Version**: 1.0.0
