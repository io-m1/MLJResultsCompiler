# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Monolithic architecture → Service-oriented design
- In-memory sessions → Persistent SQLite database
- Manual testing → Automated CI/CD pipeline

### Added
- GitHub Actions workflows (test, security, lint)
- pyproject.toml for proper dependency management
- ARCHITECTURE.md with system design
- Persistent session storage (fixes daily data loss)

### Fixed
- Chat endpoint not executing data transformations (BUG-007)
- Missing pandas/numpy in requirements.txt (BUG-001)
- Output directory not created (BUG-002)
- Environment validation missing (CONFIG-002)

## [0.1.0] - 2025-01-15

### Initial Release
- Excel consolidation core functionality
- Telegram bot integration
- FastAPI web server
- Participation bonus calculation
- Basic UI

### Known Issues
- In-memory session storage (data lost on restart)
- Monolithic architecture (no separation of concerns)
- No CI/CD pipeline
- Incomplete test coverage
