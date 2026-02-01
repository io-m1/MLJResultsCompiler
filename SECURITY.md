# Security & Compliance

**Last Audit:** February 1, 2026  
**Status:** Active Hardening  
**Contact:** Open an issue for security concerns

---

## 🔐 Security Checklist

### Configuration Management

- [x] All secrets in environment variables
- [x] `.env` file is .gitignore'd
- [x] `.env.example` shows template (no real values)
- [x] No secrets in code or comments
- [x] No secrets in git history
- [x] Settings validated at startup

### Input Validation

- [x] File upload size limited (50MB default)
- [x] File type validated (Excel only)
- [x] Filename sanitized
- [ ] SQL injection protection (using ORM, not raw SQL)
- [ ] Path traversal protection - **TODO**
- [ ] Email validation - **TODO**
- [ ] Score range validation - **TODO**

### Authentication & Authorization

- [x] Session tokens are UUIDs (not sequential)
- [x] Sessions expire after 1 hour
- [x] No user enumeration
- [ ] Rate limiting - **TODO**
- [ ] API key management - **TODO**
- [ ] CORS properly configured - **TODO**

### Data Protection

- [x] Database persists data (no daily loss)
- [x] Temporary files cleaned up
- [ ] Data encryption at rest - **TODO**
- [ ] Data encryption in transit (HTTPS in production) - **TODO**
- [x] Audit logging in place
- [ ] GDPR compliance documented - **TODO**

### Dependency Security

- [x] Dependencies pinned in pyproject.toml
- [x] No dev dependencies in production
- [ ] Dependency audit with `pip-audit` - **TODO**
- [ ] CVE monitoring - **TODO**
- [ ] Regular updates - **Quarterly**

### Deployment Security

- [x] Environment-based configuration
- [x] Debug mode disabled in production
- [x] Graceful shutdown
- [x] Health check endpoint
- [ ] WAF configuration - **TODO**
- [ ] Security headers - **TODO**

### API Security

- [x] All endpoints documented
- [x] Error messages don't leak internals
- [ ] Request size limits - **TODO**
- [ ] Timeout on all operations - **TODO**
- [x] Telegram bot token is secret

---

## 🐛 Known Vulnerabilities

### MEDIUM: Path Traversal in Download Endpoint

**Location:** `src/hybrid_bridge.py` line ~250  
**Risk:** Attacker could access arbitrary files  
**Mitigation:** Add path validation  

```python
# TODO: Validate file path is within output directory
file_path = Path(stored_path)
output_dir = Path(settings.OUTPUT_DIR).resolve()

if not file_path.resolve().is_relative_to(output_dir):
    raise HTTPException(403, "Access denied")
```

**Priority:** HIGH - Fix in v0.2.1

### MEDIUM: Missing Email Validation

**Location:** `src/hybrid_bridge.py` consolidation endpoint  
**Risk:** Invalid emails could corrupt data merges  
**Mitigation:** Validate email format before processing

```python
import re

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

if not re.match(EMAIL_REGEX, email):
    raise ValueError("Invalid email format")
```

**Priority:** HIGH - Fix in v0.2.1

### LOW: No HTTPS Enforcement

**Location:** Render deployment  
**Risk:** Data transmitted unencrypted  
**Mitigation:** Render enforces HTTPS by default

**Priority:** OK - Render handles this

---

## 🛡️ Security Testing

### Run Security Scan

```bash
# Install security tools
pip install bandit safety pip-audit

# Scan code
bandit -r src/ -ll  # Ignore informational

# Scan dependencies
pip-audit
safety check
```

### Common Issues

```bash
# SQL Injection
# ✓ Using ORM (no raw SQL)

# Hardcoded Secrets
# ✓ Using env vars only
bandit -r src/ | grep "hardcoded"

# Insecure Random
# ✓ Using uuid.uuid4() for session IDs
bandit -r src/ | grep "random"
```

---

## 📋 Secure Coding Standards

### Rule 1: Never Hardcode Secrets

❌ BAD:
```python
TELEGRAM_BOT_TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
```

✅ GOOD:
```python
from src.config import get_settings
settings = get_settings()
token = settings.TELEGRAM_BOT_TOKEN  # From env var
if not token:
    raise ValueError("TELEGRAM_BOT_TOKEN not set")
```

### Rule 2: Validate All Input

❌ BAD:
```python
filename = request.files[0].filename  # User-controlled!
file_path = f"output/{filename}"  # Path traversal!
file_path.write_bytes(content)
```

✅ GOOD:
```python
from pathlib import Path
import uuid

filename = request.files[0].filename
# Validate
if not filename.endswith('.xlsx'):
    raise ValueError("Only .xlsx files allowed")

# Sanitize
safe_name = f"{uuid.uuid4()}.xlsx"
output_dir = Path("output")
file_path = output_dir / safe_name

# Verify path is within output_dir
if not file_path.resolve().is_relative_to(output_dir.resolve()):
    raise ValueError("Path traversal attempt blocked")

file_path.write_bytes(content)
```

### Rule 3: Use Timeouts

❌ BAD:
```python
response = requests.post(external_api)  # Could hang forever
```

✅ GOOD:
```python
try:
    response = requests.post(external_api, timeout=30)
except requests.Timeout:
    logger.error("API timeout")
    return fallback_response()
```

### Rule 4: Log Security Events

✅ GOOD:
```python
logger.warning(f"Failed login attempt from {ip}")
logger.info(f"User {user_id} exported {row_count} rows")
logger.error(f"Security breach attempt: {details}")
```

---

## 🔍 Audit Trail

All security-relevant events are logged:

```
logs/app.log
├─ Authentication events
├─ File uploads
├─ Data access
├─ Configuration changes
└─ Error conditions
```

---

## 🚨 Incident Response

### If You Discover a Vulnerability

1. **Do NOT open a public issue**
2. **Email security report privately** (contact maintainer)
3. **Include:**
   - Vulnerability description
   - Steps to reproduce
   - Proof-of-concept
   - Suggested fix

4. **Response SLA:**
   - Critical: 24 hours
   - High: 1 week
   - Medium: 2 weeks
   - Low: 1 month

---

## 📊 Compliance

### GDPR

- [x] Data collection is minimal
- [x] Data is persisted in database
- [ ] Data deletion implemented - **TODO**
- [ ] Privacy policy - **TODO**
- [ ] Data subject requests - **TODO**

### CCPA

- [x] California residents notified of data collection
- [ ] Data sale opt-out - **TODO**
- [ ] Deletion requests - **TODO**

---

## 🔄 Update Policy

### Security Patches

- **Released when:** Critical vulnerability discovered
- **Timeline:** ASAP (within 24 hours)
- **Distribution:** Automatic via GitHub Actions

### Dependency Updates

- **Frequency:** Monthly
- **Process:** Dependabot checks for updates
- **Testing:** All tests must pass
- **Deployment:** Automatic for patches, manual for minor

---

## 📚 Security References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)

---

## ✅ Production Checklist

Before deploying to production:

- [ ] All environment variables set correctly
- [ ] HTTPS enforced
- [ ] Debug mode disabled
- [ ] Security scan passed
- [ ] Dependencies audited
- [ ] Database backed up
- [ ] Monitoring configured
- [ ] Incident response plan ready

---

**Last Updated:** February 1, 2026

This document reflects ongoing security hardening efforts. Not all items are complete - they are tracked transparently.
