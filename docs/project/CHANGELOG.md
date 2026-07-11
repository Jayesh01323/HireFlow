# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and setup
- Core database models with SQLAlchemy
- Resume parsing functionality with Gemini AI
- Job matching engine with weighted scoring
- Skill categorization and gap analysis
- Multi-platform job scraping (LinkedIn, Internshala, Naukri, Glassdoor, Wellfound)
- Career coaching and copilot features
- Application tracking system
- Analytics dashboard with visualizations
- Learning roadmap generation
- Career fit analysis
- Interview preparation tools
- REST API endpoints for all major features

### Changed
- Improved error handling across all modules
- Enhanced type hints coverage
- Optimized database queries
- Improved UI/UX for all Streamlit pages

### Fixed
- Fixed memory leak in job scraping
- Resolved PDF parsing issues for certain formats
- Fixed skill extraction edge cases
- Corrected database migration issues

## [1.0.0] - 2026-06-20

### Added
- Initial release of HireFlow AI
- Complete feature set for career intelligence platform
- AI-powered resume parsing and analysis
- Intelligent job matching with skill gap analysis
- Multi-platform job aggregation
- Career coaching and guidance
- Application tracking and management
- Analytics and insights dashboard
- Learning roadmaps and skill development
- Interview preparation tools
- REST API for all features
- Comprehensive documentation

### Security
- Proper environment variable management
- API key protection
- Input validation for user uploads
- SQL injection prevention through ORM

### Documentation
- Complete README with installation guide
- API documentation
- Architecture documentation
- User guide and developer guide

## [0.9.0] - 2026-05-15

### Added
- Beta release with core features
- Resume parsing and analysis
- Basic job matching
- Job discovery from multiple platforms
- Application tracking
- Analytics dashboard

### Known Issues
- Limited job scraping reliability
- Some edge cases in skill extraction
- Performance optimization needed

## [0.5.0] - 2026-04-01

### Added
- Alpha release
- Basic resume parsing
- Simple job matching
- Database setup
- Initial UI components

### Known Issues
- Limited feature set
- No job scraping
- Basic UI only

---

## Versioning Strategy

We follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html):

- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible functionality additions
- **PATCH**: Backwards-compatible bug fixes

### Release Cadence

- **Major releases**: Every 6-12 months
- **Minor releases**: Every 2-3 months
- **Patch releases**: As needed for bug fixes

### Pre-release Versions

Pre-release versions use the format: `MAJOR.MINOR.PATCH-prerelease.1`

Examples:
- `1.1.0-alpha.1`
- `1.1.0-beta.1`
- `1.1.0-rc.1`

---

## Categories

### Added
New features, functionality, or capabilities

### Changed
Changes to existing functionality that don't break compatibility

### Deprecated
Features that will be removed in future versions

### Removed
Features removed in this version

### Fixed
Bug fixes and corrections

### Security
Security-related fixes and improvements

### Documentation
Documentation updates and improvements

---

## How to Update Changelog

When making changes:

1. Add entries to the `[Unreleased]` section
2. Use appropriate category (Added, Changed, Fixed, etc.)
3. Be specific about what changed
4. When releasing, move entries to new version section
5. Update version number and release date

Example entry:

```markdown
### Added
- New feature description
- Another new feature

### Fixed
- Bug description
- Another bug fix
```
