# HireFlow AI - Installation Guide

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Environment Setup](#environment-setup)
- [Database Setup](#database-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

---

## Prerequisites

### System Requirements

- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python Version**: 3.12 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: Minimum 500MB (1GB recommended)
- **Internet**: Required for API calls and package installation

### Required Software

1. **Python 3.12+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Verify installation: `python --version`

2. **pip** (Python Package Manager)
   - Usually included with Python
   - Verify installation: `pip --version`

3. **Git** (Optional but recommended)
   - Download from [git-scm.com](https://git-scm.com/downloads)
   - Verify installation: `git --version`

### API Keys

You'll need a **Google Gemini API Key**:
- Get it from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Free tier available for development
- Keep your API key secure

---

## Installation Methods

### Method 1: Clone from GitHub (Recommended)

```bash
# Clone the repository
git clone https://github.com/Jayesh01323/HireFlow.git
cd HireFlow
```

### Method 2: Download ZIP

1. Go to [GitHub Repository](https://github.com/Jayesh01323/HireFlow)
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Navigate to the extracted directory

---

## Environment Setup

### Step 1: Create Virtual Environment

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 2: Upgrade pip

```bash
pip install --upgrade pip
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env
```

Edit `.env` file and add your API key:

```env
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here

# Database
DATABASE_URL=sqlite:///data/hireflow.db

# Optional: Database Path
DATABASE_PATH=data/hireflow.db
```

**Security Note**: Never commit `.env` file to version control. It's already in `.gitignore`.

---

## Database Setup

### Step 1: Create Data Directory

```bash
mkdir -p data
```

### Step 2: Initialize Database

```bash
python -c "from src.database import init_db; init_db()"
```

This will:
- Create the SQLite database file
- Create all required tables
- Set up proper indexes and relationships

### Step 3: Verify Database

```bash
python -c "from src.database import get_session; print('Database connected successfully')"
```

---

## Verification

### Step 1: Run the Application

```bash
streamlit run app.py
```

The application should start and open in your browser at `http://localhost:8501`

### Step 2: Test Core Features

1. **Resume Parser**: Upload a PDF resume
2. **Job Matcher**: Test with sample job description
3. **Job Discovery**: Search for jobs
4. **Analytics Dashboard**: View visualizations

### Step 3: Check Dependencies

```bash
pip check
```

This will check for any dependency conflicts.

---

## Troubleshooting

### Common Issues

#### Issue 1: Python Version Incompatible

**Error**: `Python 3.12+ required`

**Solution**:
```bash
# Check your Python version
python --version

# Install Python 3.12 from python.org
# Update your PATH to use the new version
```

#### Issue 2: Virtual Environment Activation Fails

**Error**: `venv\Scripts\activate: No such file or directory`

**Solution**:
```bash
# Delete existing venv and recreate
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
```

#### Issue 3: Dependency Installation Fails

**Error**: `Could not find a version that satisfies the requirement`

**Solution**:
```bash
# Upgrade pip first
pip install --upgrade pip

# Try installing with specific version
pip install package_name==version

# Or use conda if available
conda install package_name
```

#### Issue 4: Gemini API Key Error

**Error**: `GEMINI_API_KEY not set`

**Solution**:
```bash
# Verify .env file exists
ls -la .env

# Check .env file content
cat .env

# Ensure API key is set correctly
GEMINI_API_KEY=your_actual_api_key_here
```

#### Issue 5: Database Initialization Fails

**Error**: `sqlite3.OperationalError: unable to open database file`

**Solution**:
```bash
# Create data directory
mkdir -p data

# Check permissions
chmod 755 data  # Linux/macOS

# Try initialization again
python -c "from src.database import init_db; init_db()"
```

#### Issue 6: Streamlit Won't Start

**Error**: `StreamlitRuntimeException`

**Solution**:
```bash
# Clear Streamlit cache
streamlit cache clear

# Reinstall Streamlit
pip install --upgrade streamlit

# Try with specific port
streamlit run app.py --server.port 8502
```

#### Issue 7: Import Errors

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Ensure you're in the project root
cd HireFlow

# Install in development mode
pip install -e .

# Or add project to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/macOS
set PYTHONPATH=%PYTHONPATH%;%CD%  # Windows
```

### Getting Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](https://github.com/Jayesh01323/HireFlow/issues)
2. Search existing issues for similar problems
3. Create a new issue with:
   - Error message
   - Steps to reproduce
   - Environment details (OS, Python version)
   - Log output

---

## Advanced Installation

### Development Installation

For contributors who want to modify the code:

```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest black flake8 mypy

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### Production Installation

For production deployment:

```bash
# Use production-grade dependencies
pip install -r requirements.txt

# Create production environment file
cp .env.example .env.production

# Use production database (PostgreSQL recommended)
# Update DATABASE_URL in .env.production
```

### Docker Installation (Optional)

If you prefer using Docker:

```bash
# Build Docker image
docker build -t hireflow-ai .

# Run container
docker run -p 8501:8501 --env-file .env hireflow-ai
```

---

## Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | - | Google Gemini API key |
| `DATABASE_URL` | No | `sqlite:///data/hireflow.db` | Database connection string |
| `DATABASE_PATH` | No | `data/hireflow.db` | Database file path |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `MAX_UPLOAD_SIZE` | No | `10485760` | Max file upload size in bytes |

### Streamlit Configuration

Create `.streamlit/config.toml`:

```toml
[server]
port = 8501
headless = true
enableCORS = false
enableXsrfProtection = true

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

---

## Updating

### Update Dependencies

```bash
# Update all dependencies
pip install --upgrade -r requirements.txt

# Or update specific package
pip install --upgrade package_name
```

### Update from Git

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install --upgrade -r requirements.txt

# Run database migrations if any
python -c "from src.database import init_db; init_db()"
```

---

## Uninstallation

### Remove Virtual Environment

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment directory
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows
```

### Remove Application Files

```bash
# Remove project directory
cd ..
rm -rf HireFlow  # Linux/macOS
rmdir /s HireFlow  # Windows
```

### Clean Global Packages (Optional)

```bash
# Remove globally installed packages
pip uninstall streamlit google-generativeai PyMuPDF pydantic pandas plotly
```

---

## Next Steps

After successful installation:

1. Read the [User Guide](./user-guide.md) to learn how to use the application
2. Check the [API Reference](./api-reference.md) for API documentation
3. Review the [Deployment Guide](./deployment.md) for production setup
4. Explore the [Developer Guide](./developer-guide.md) for contribution guidelines

---

**Last Updated**: June 20, 2026  
**Maintained By**: Jayesh  
**Version**: 1.0.0
