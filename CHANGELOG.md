# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for v0.3.0
- Service boundary extraction (Tier 2)
- 80%+ integration test coverage
- Real user validation

## [0.2.0] - 2026-02-01

### Major
- **Production Foundation**: Tier 1 hardening complete
- **Decision Debt Eliminated**: Ruthless cleanup (2,234 lines of duplicates deleted)
- **Honest Documentation**: Removed marketing claims, established single source of truth

### Added
- GitHub Actions CI/CD (Python 3.10, 3.11, 3.12 matrix)
  - Automated testing, linting, type checking, security scanning
  - Coverage reporting, caching for fast builds
- Persistent session storage (SQLite)
  - Fixes daily data loss on Render restart
  - Automatic expiration cleanup
  - Audit logging for all operations
- Pydantic BaseSettings configuration management
  - Environment-based configuration (no hardcoded secrets)
  - Validation at startup (fail-fast)
- Single deployment entrypoint (src/main.py)
  - Health check endpoints (/health, /status)
  - Graceful shutdown handling
- Comprehensive governance documentation
  - ARCHITECTURE.md: Honest system design (428 lines)
  - SECURITY.md: Vulnerability audit (235 lines)
  - AI_FEATURE_GOVERNANCE.md: Cost/safety transparency
  - PATH_B_EXECUTION_GUIDE.md: 6-week roadmap to v1.0
- Service architecture stubs (core_compiler, api_server, adapters)
- Test infrastructure (unit/, integration/, e2e/)

### Changed
- README: Marketing removed, scope clarified, limitations listed
- Deleted duplicate implementations: web_ui.py, integration_v2.py, COMPILER_V2_DEPLOYMENT.py
- Deleted shallow tests: test_web_live.py, test_production_ready.py, test_groq_simple.py
- Deleted 11 redundant docs (2,608 lines): Kept only core docs

### Fixed
- Chat endpoint not executing data transformations (BUG-007)
- Missing pandas/numpy in requirements.txt (BUG-001)
- Output directory not created (BUG-002)
- No environment variable validation (CONFIG-002)

### Status
- ✅ Tier 1: Complete (foundation solid)
- 🟡 Tier 2: Ready (architecture refactor planned)
- 🟡 Tier 3: Ready (security hardening planned)
- 🟡 Tier 4: Ready (deployment planned)
- 🎯 Path B: Activated (real user validation starting)

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
