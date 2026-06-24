# Contributing to HireFlow AI

Thank you for your interest in contributing to HireFlow AI! We welcome contributions from the community and are excited to have you join us.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming environment for all contributors.

## How to Contribute

### Ways to Contribute

1. **Report Bugs**: Help us fix issues by reporting bugs
2. **Suggest Features**: Share your ideas for new features
3. **Submit Pull Requests**: Fix bugs, add features, or improve documentation
4. **Improve Documentation**: Help make our documentation better
5. **Review Code**: Provide feedback on pull requests
6. **Answer Questions**: Help other users in issues and discussions

### Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/HireFlow.git
   cd HireFlow
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Environment Configuration

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Add your API keys to `.env`:
   ```env
   GEMINI_API_KEY=your_api_key_here
   DATABASE_URL=sqlite:///data/hireflow.db
   ```

3. Initialize the database:
   ```bash
   python -c "from src.database import init_db; init_db()"
   ```

### Running the Application

```bash
streamlit run app.py
```

### Running Tests

```bash
python -m pytest tests/
```

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use descriptive variable and function names
- Add docstrings to all functions and classes

### Type Hints

- Add type hints to all function signatures
- Use `typing` module for complex types
- Return types should be explicitly declared

```python
from typing import List, Dict, Optional

def process_jobs(jobs: List[Dict]) -> Optional[Dict]:
    """Process job listings and return results."""
    pass
```

### Documentation

- Add docstrings to all modules, classes, and functions
- Use Google style docstrings
- Include parameter descriptions and return types

```python
def analyze_resume(resume_text: str) -> Dict[str, Any]:
    """Analyze resume text and extract structured data.
    
    Args:
        resume_text: Raw text extracted from resume PDF
        
    Returns:
        Dictionary containing parsed resume data including skills,
        experience, education, and projects.
        
    Raises:
        ValueError: If resume_text is empty or invalid
    """
    pass
```

### Git Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
feat: add job scraping for LinkedIn
fix: resolve memory leak in job matcher
docs: update installation guide
style: format code with black
refactor: simplify skill categorization logic
test: add unit tests for resume parser
chore: update dependencies
```

### Code Organization

- Keep functions focused and single-purpose
- Use meaningful file and directory names
- Separate concerns (UI, business logic, data access)
- Follow the existing project structure

## Submitting Changes

### Pull Request Process

1. Ensure your code follows the coding standards
2. Write tests for new functionality
3. Update documentation as needed
4. Commit your changes with clear messages
5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
6. Open a pull request on GitHub

### Pull Request Checklist

- [ ] Code follows project coding standards
- [ ] Tests added/updated for new features
- [ ] Documentation updated
- [ ] Commit messages follow conventional commits
- [ ] No merge conflicts
- [ ] All tests pass
- [ ] Added appropriate labels to PR

### Pull Request Template

When opening a pull request, please provide:

- **Description**: What changes you made and why
- **Type**: Bug fix, feature, documentation, etc.
- **Testing**: How you tested your changes
- **Screenshots**: For UI changes (if applicable)
- **Related Issues**: Link to related issues

## Reporting Bugs

### Before Reporting

1. Check existing issues to avoid duplicates
2. Ensure you're using the latest version
3. Try to reproduce the bug consistently

### Bug Report Template

```markdown
**Description**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected Behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment**
- OS: [e.g. Windows 10, macOS 12.0]
- Python Version: [e.g. 3.12]
- Browser: [e.g. Chrome 120]

**Additional Context**
Add any other context about the problem here.
```

## Suggesting Features

### Feature Request Template

```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Problem Statement**
What problem does this feature solve?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
What alternative solutions did you consider?

**Additional Context**
Any other context, screenshots, or examples.
```

## Recognition

Contributors will be recognized in:
- Contributors section in README
- Release notes
- Project documentation

## Questions?

If you have questions about contributing:
- Open an issue with the "question" label
- Start a discussion in GitHub Discussions
- Contact the maintainers

Thank you for contributing to HireFlow AI! 🚀
