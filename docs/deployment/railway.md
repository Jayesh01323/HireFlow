# Railway Deployment Guide

## Overview

Railway is a modern cloud platform with excellent developer experience. This guide covers deploying HireFlow AI to Railway.

## Prerequisites

- Railway account (free trial available)
- GitHub repository
- PostgreSQL database (recommended)
- Google Gemini API key

## Step-by-Step Deployment

### 1. Prepare Repository

```bash
# Ensure all changes are committed
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### 2. Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Sign up with GitHub
4. Verify email address

### 3. Initialize Project

```bash
# Install Railway CLI (optional)
npm install -g @railway/cli
railway login
```

### 4. Create Project from GitHub

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository
4. Select branch: `main`

### 5. Add PostgreSQL Database

1. Click "New Service"
2. Select "PostgreSQL"
3. Configure database settings
4. Copy connection string

### 6. Configure Application

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### 7. Add Environment Variables

Add these in Railway dashboard:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://postgres:your_password@host:port/railway
PORT=8501
```

### 8. Deploy

Click "Deploy" and wait for deployment to complete.

## Configuration Files

### railway.toml

Create `railway.toml`:

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0"
healthcheckPath = "/"
healthcheckTimeout = 300

[env]
PORT = "8501"
PYTHON_VERSION = "3.12"
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `PORT` | Application port | `8501` |

---

**Last Updated**: June 20, 2026  
**Platform**: Railway  
**Version**: 1.0.0
