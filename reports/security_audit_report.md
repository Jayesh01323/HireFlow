# Security Audit Report - HireFlow AI

**Generated**: 2026-07-18 10:46 UTC  
**Repository**: HireFlow AI  
**Branch**: `main`  
**Latest Commit Hash**: `bb109b7`  
**Remote**: `origin/main` (https://github.com/Jayesh01323/HireFlow.git)

---

## Executive Summary

A comprehensive security audit was performed on the HireFlow AI repository. **No high-severity security issues were found in committed code.** All API keys and secrets are loaded from environment variables, and the `.env` file is properly excluded via `.gitignore`. One critical finding (hardcoded password in `docker-compose.yml`) was fixed as part of this audit.

---

## 1. Security Audit Results

### 1.1 Hardcoded API Keys & Secrets
- **Status**: ✅ No hardcoded API keys found in tracked files
- All API keys (`GEMINI_API_KEY`, `APIFY_API_KEY`) loaded via `python-dotenv` from `.env`
- `.env` file is **properly gitignored** and **not tracked** in git history
- `.env.example` contains placeholder values (`your_gemini_api_key_here`, `your_apify_api_key_here`)

### 1.2 .env File & Credentials
- **Status**: ✅ `.env` is listed in `.gitignore` (line 37) and confirmed not tracked
- Local `.env` contains a dev Apify API key - only stored locally, never committed

### 1.3 Certificates & Keys (*.pem, *.key, *.p12)
- **Status**: ✅ No certificate or key files found in repository
- `git ls-files` search for `.pem`, `.key`, `.p12`, `.pfx`, `.crt`, `.jks`, `.keystore` returned no results

### 1.4 .gitignore Review
- **Status**: ✅ Properly configured
- Excludes: `.env`, `__pycache__/`, `venv/`, IDE files, database files, etc.
- Updated in this commit to also exclude: `tests/*.html`, `secret_scan/`, `output.txt`

### 1.5 Sensitive User Data
- **Status**: ✅ No PII or sensitive user data found in tracked files
- Password storage uses `password_hash` field with planned bcrypt implementation (not yet active)

### 1.6 Existing Secret Scan Report Review
- **Status**: ✅ Report reviewed (`secret_scan/combined_report.json`)
- 67 total findings, all low severity, all from ignored/untracked files
- No secrets committed to git history

---

## 2. Critical Fixes Applied

### 2.1 Hardcoded Passwords in docker-compose.yml
- **Vulnerability**: `POSTGRES_PASSWORD=password` hardcoded in `docker-compose.yml` (lines 10, 20)
- **Fix**: Changed to `POSTGRES_PASSWORD=${POSTGRES_PASSWORD}` (environment variable)

### 2.2 Hardcoded Passwords in Deployment Docs
- **Files fixed**: `docs/deployment.md`, `docs/deployment/railway.md`, `docs/deployment/render.md`
- **Fix**: Replaced `password` placeholder values with `your_password` to make it clearer these are placeholders

### 2.3 .env.example Update
- Added `POSTGRES_PASSWORD=your_postgres_password_here` for Docker deployments

### 2.4 .gitignore Update
- Added `tests/*.html` (test fixtures may contain cookies/session data)
- Added `secret_scan/` and `output.txt`

---

## 3. Pre-existing Issues (Not Fixed)

### 3.1 Test Failures (11 failures, 5 errors)
These are **pre-existing test failures** unrelated to security changes:
- `test_job_discovery_engine.py`:
  - `TestJobNormalizer`: 8 normalization tests fail (normalize_title, company, location, experience, salary, remote, batch)
  - `TestJobDeduplicator::test_merge_duplicate_info`: Salary merging logic not extracting from string
  - `TestJobRepository::test_initialization`: Missing `session` attribute
  - `TestJobRepository::test_save_job`: Returns int instead of dict
  - `TestJobAggregator`: All 5 tests error - `JobAggregator` not imported in test fixture
- `test_job_connectors.py::TestLinkedInConnector::test_initialization`: Missing `base_url` attribute
- **125/141 tests pass** (88.7%)

### 3.2 Pydantic Deprecation Warnings
- `src/jobs/schemas.py`: 3 Pydantic deprecation warnings for class-based `config` (use `ConfigDict` instead)

### 3.3 datetime.utcnow() Deprecation
- Multiple files use deprecated `datetime.utcnow()` - should use `datetime.now(datetime.UTC)`

---

## 4. Test Results Summary

```
Total: 141 tests collected
Passed: 125 (88.7%)
Failed: 11 (pre-existing bugs)
Errors: 5 (TestJobAggregator - missing import in test fixture)
```

---

## 5. Files Changed in Commit `bb109b7`

| File | Change |
|------|--------|
| `.env.example` | Added `POSTGRES_PASSWORD` env var for Docker |
| `.gitignore` | Added test HTML fixtures, secret scan results |
| `docker-compose.yml` | Fixed hardcoded passwords → env vars |
| `docs/deployment.md` | Replaced placeholder passwords, updated Docker examples |
| `docs/deployment/railway.md` | Replaced placeholder passwords |
| `docs/deployment/render.md` | Replaced placeholder passwords |
| `tests/debug_wellfound_selectors.py` | New untracked test file |
| `tests/run_wellfound_actor_standalone.py` | New untracked test file |

---

## 6. Recommendations

1. **Rotate Apify API Key**: The key in `.env` (`apify_api_y6eM...`) has been exposed locally. If this key was ever committed to git history, rotate it immediately.
2. **Fix Pre-existing Test Failures**: Address the `JobNormalizer`, `JobRepository`, and `TestJobAggregator` failures to maintain test reliability.
3. **Fix Pydantic Deprecation**: Migrate from class-based `config` to `ConfigDict` in `src/jobs/schemas.py`.
4. **Replace `datetime.utcnow()`**: Use `datetime.now(datetime.UTC)` for Python 3.14+ compatibility.
5. **Add Secret Scanning CI**: Integrate tools like `gitleaks` or `trufflehog` into CI pipeline.
6. **Implement Password Hashing**: Complete bcrypt password hashing implementation for user authentication.

---

*Report generated as part of security audit on 2026-07-18*