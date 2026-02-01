# MLJ Results Compiler - System Architecture

**Version:** 0.2.0  
**Status:** Alpha (Under Active Refactoring)  
**Last Updated:** February 1, 2026

---

## 🏗️ **Current Architecture (Monolithic)**

```
┌─────────────────────────────────────────────────────────┐
│  MLJResultsCompiler (Monolith)                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐│
│  │  Telegram    │  │  FastAPI     │  │  Excel         ││
│  │  Bot Handler │  │  Web Server  │  │  Processor     ││
│  └──────────────┘  └──────────────┘  └────────────────┘│
│         │                │                  │           │
│         └────────────────┼──────────────────┘           │
│                          │                              │
│         ┌────────────────┴──────────────────┐           │
│         │                                   │           │
│    ┌────▼─────┐                    ┌───────▼────┐     │
│    │  AI       │                    │  Data      │     │
│    │  Assistant│                    │  Agent     │     │
│    └───────────┘                    └────────────┘     │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  In-Memory Session Storage (LOST ON RESTART!)  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
        ↓
    Render (daily restart = daily data loss)
```

### ⚠️ **Critical Issues**

1. **Single failure point** - Bot down = entire system down
2. **Session data loss** - In-memory storage lost on daily Render restart
3. **No service boundaries** - Can't scale individual components
4. **Monolithic deployment** - Must redeploy everything for 1 line change
5. **No clear interfaces** - Components tightly coupled

---

## 🚀 **Target Architecture (Service-Oriented)**

```
┌─────────────────────────────────────────────────────────────┐
│  Distributed Service Architecture                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  API Gateway (FastAPI server.py)                   │   │
│  │  - Routes requests to appropriate service          │   │
│  │  - Handles session management                      │   │
│  │  - Manages authentication                          │   │
│  └─────────────┬──────────────────────────────────────┘   │
│                │                                           │
│    ┌───────────┼────────────┬───────────────┐              │
│    │           │            │               │              │
│    ▼           ▼            ▼               ▼              │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│ │ Core     │ │ Telegram │ │ Web UI   │ │ AI       │      │
│ │ Compiler │ │ Bot      │ │ Server   │ │ Assistant│      │
│ │ Service  │ │ Adapter  │ │ (Next.js)│ │ Service  │      │
│ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘      │
│      │            │            │            │             │
│      └────────────┼────────────┼────────────┘             │
│                   │            │                          │
│                   ▼            ▼                          │
│            ┌──────────────────────┐                       │
│            │  Persistent Storage  │                       │
│            │  ┌────────────────┐  │                       │
│            │  │ SQLite DB      │  │  (Fixed data loss)   │
│            │  │ Sessions       │  │                       │
│            │  │ Results        │  │                       │
│            │  │ Logs           │  │                       │
│            │  └────────────────┘  │                       │
│            │  ┌────────────────┐  │                       │
│            │  │ Redis Cache    │  │  (Performance)       │
│            │  │ (Optional)     │  │                       │
│            │  └────────────────┘  │                       │
│            └──────────────────────┘                       │
│                                                             │
│            ┌──────────────────────┐                       │
│            │  Monitoring Stack    │                       │
│            │  ┌────────────────┐  │                       │
│            │  │ Structured Logs│  │                       │
│            │  │ Error Tracking │  │                       │
│            │  │ Metrics        │  │                       │
│            │  └────────────────┘  │                       │
│            └──────────────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
    ┌────▼──┐      ┌────▼──┐      ┌───▼────┐   ┌────▼──┐
    │ AWS   │      │ GCP   │      │ Render │   │ Local │
    │ ECS   │      │ Cloud │      │ (prod) │   │ Dev   │
    │       │      │ Run   │      │        │   │       │
    └───────┘      └───────┘      └────────┘   └───────┘
```

---

## 📦 **Service Breakdown**

### **1. Core Compiler Service** (`services/core_compiler/`)
**Responsibility:** Excel processing, consolidation, data validation

- ✅ Zero external dependencies on bot/web
- ✅ Pure data transformation logic
- ✅ Fully testable
- ✅ Can run in isolation or as library

**Files:**
```
services/core_compiler/
├── __init__.py
├── compiler.py          # Main compilation logic
├── validators.py        # Input validation
├── data_processor.py    # Excel reading/writing
├── consolidator.py      # Score consolidation
└── tests/
    ├── test_compiler.py
    ├── test_validators.py
    └── test_consolidation.py
```

**Interface:**
```python
from services.core_compiler import ResultsCompiler

compiler = ResultsCompiler()
results = compiler.consolidate(
    files=[file1, file2],
    rules={...}
)
```

---

### **2. API Server** (`services/api_server/`)
**Responsibility:** HTTP API, session management, orchestration

- ✅ Stateless (all state in database)
- ✅ Calls core compiler, AI service, bot adapter
- ✅ Handles authentication, rate limiting
- ✅ Manages database connections

**Endpoints:**
```
POST   /api/upload              - Upload Excel files
POST   /api/consolidate         - Process consolidation
POST   /api/transform           - Apply data transformation
GET    /api/download/:id        - Download result
POST   /api/chat                - Chat with AI
GET    /api/status              - System health check
```

---

### **3. Telegram Bot Adapter** (`services/telegram_bot/`)
**Responsibility:** Bot message handling, user interface

- ✅ Calls API server endpoints
- ✅ No core business logic
- ✅ Message formatting/parsing only
- ✅ Can be stopped/restarted without losing data

**Flow:**
```
User → Telegram API → Bot Adapter → API Server → Core Services
```

---

### **4. AI Assistant Service** (`services/ai_assistant/`)
**Responsibility:** Natural language processing, data action generation

- ✅ Isolated from other services
- ✅ Calls to Groq API
- ✅ Cost tracking and monitoring
- ✅ Fallback responses if API fails

---

### **5. Web UI** (`web/`)
**Responsibility:** Frontend interface

- ✅ React/Next.js frontend
- ✅ Calls API endpoints
- ✅ No server-side state (stateless)
- ✅ Can be deployed independently

---

## 💾 **Data Storage**

### **Database Schema** (SQLite / PostgreSQL)

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    user_id TEXT,
    created_at TIMESTAMP,
    expires_at TIMESTAMP,
    status TEXT (uploading/processing/completed/failed),
    metadata JSON
);

CREATE TABLE uploads (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions,
    filename TEXT,
    size INTEGER,
    uploaded_at TIMESTAMP,
    status TEXT
);

CREATE TABLE results (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions,
    consolidation_id UUID,
    result_type TEXT (consolidation/transformation/report),
    file_path TEXT,
    created_at TIMESTAMP,
    metadata JSON
);

CREATE TABLE transformations (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions,
    action_type TEXT (collate/grade/rank/filter),
    parameters JSON,
    result_id UUID REFERENCES results,
    created_at TIMESTAMP
);
```

---

## 🔄 **Request Flow Example**

### **User uploads files and asks for collation**

```
1. Frontend sends POST /api/upload
   ├─ API Server receives file
   ├─ Saves to database + filesystem
   ├─ Returns session_id
   └─ Response to user

2. User sends POST /api/consolidate
   ├─ API Server validates session
   ├─ Calls Core Compiler Service
   │  ├─ Reads files
   │  ├─ Validates data
   │  ├─ Consolidates scores
   │  └─ Returns compiled data
   ├─ Saves result to database
   ├─ Returns result_id
   └─ Response to user

3. User sends POST /api/chat with "collate scores"
   ├─ API Server receives message
   ├─ Calls AI Service → parse_data_request()
   ├─ AI Service detects action type
   ├─ Calls Core Compiler with parsed actions
   ├─ Saves transformation to database
   ├─ Returns success + download_url
   └─ Response to user

4. User requests GET /api/download/{result_id}
   ├─ API Server validates access
   ├─ Reads file from storage
   ├─ Returns file to user
   └─ Logs download event
```

---

## 🚨 **Critical Design Decisions**

### **1. Stateless API Server**
- ✅ Can run multiple instances (horizontal scaling)
- ✅ Load balancer distributes requests
- ✅ Instance failure doesn't lose data
- ✅ Easy to deploy updates (rolling deployment)

### **2. Persistent Database**
- ✅ All sessions persisted (no daily data loss)
- ✅ Audit trail of all operations
- ✅ Enables recovery from failures
- ✅ Supports multi-instance deployments

### **3. Service Isolation**
- ✅ Core compiler has zero external dependencies
- ✅ AI service can fail without breaking uploads
- ✅ Bot can be down without affecting web
- ✅ Each service can be tested independently

### **4. Message Queuing (Future)**
```
Bot → Queue → API → Processor → Database
                ↓
           Retry on failure
```

---

## 📊 **Deployment Topology**

### **Development**
```
Single machine:
  API Server (port 8000)
  SQLite database (local)
  Bot token (env var)
```

### **Production (Recommended)**
```
Kubernetes Cluster:
  ├─ API Service (3 replicas)
  ├─ Bot Service (1 instance)
  ├─ AI Service (2 replicas)
  ├─ PostgreSQL (managed)
  ├─ Redis Cache (managed)
  └─ Monitoring/Logging
```

### **Production (Simple)**
```
Render/Heroku:
  ├─ Web Service (API + Web UI)
  ├─ Worker Service (Bot)
  ├─ PostgreSQL Database
  └─ Scheduled cleanup job
```

---

## 🔐 **Security Architecture**

```
┌──────────────────────────────────────────┐
│  Internet                                │
├──────────────────────────────────────────┤
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  WAF (Web Application Firewall)    │ │
│  └────────┬─────────────────────────┬─┘ │
│           │                         │    │
│   ┌───────▼─────┐          ┌───────▼──┐ │
│   │ HTTPS Only  │          │ Rate     │ │
│   │ TLS 1.3     │          │ Limiting │ │
│   └───────┬─────┘          └───────┬──┘ │
│           │                         │    │
└───────────┼─────────────────────────┼────┘
            │                         │
    ┌───────▼─────┐          ┌───────▼──┐
    │  API Auth   │          │ Input    │
    │  JWT/API    │          │ Validation
    │  Key        │          │ Sanitize │
    └───────┬─────┘          └───────┬──┘
            │                         │
    ┌───────▼─────────────────────────▼──┐
    │  Application Layer Security         │
    ├──────────────────────────────────────┤
    │  • CORS Configuration                │
    │  • Session Token Rotation            │
    │  • Audit Logging                     │
    │  • Data Encryption at Rest           │
    └───────┬──────────────────────────────┘
            │
    ┌───────▼──────────────┐
    │  Database            │
    │  • Encrypted fields  │
    │  • Access control    │
    │  • Backup encrypted  │
    └──────────────────────┘
```

---

## 🧪 **Testing Strategy**

### **Layer 1: Unit Tests** (Fast, isolated)
```python
# tests/unit/test_compiler.py
def test_consolidation_basic():
    compiler = ResultsCompiler()
    result = compiler.consolidate(...)
    assert result.total_score == expected
```

### **Layer 2: Integration Tests** (API + Database)
```python
# tests/integration/test_api.py
async def test_upload_and_consolidate():
    response = client.post("/api/upload", files=...)
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    
    response = client.post(f"/api/consolidate/{session_id}")
    assert response.status_code == 200
```

### **Layer 3: E2E Tests** (Full workflow)
```python
# tests/e2e/test_full_workflow.py
async def test_complete_user_journey():
    # Upload files
    # Consolidate
    # Ask AI to transform
    # Download results
    # Verify file contents
```

### **CI/CD Pipeline** (GitHub Actions)
```
On push/PR:
  ├─ Lint (flake8, black)
  ├─ Type check (mypy)
  ├─ Unit tests (pytest)
  ├─ Integration tests
  ├─ Security scan (bandit, safety)
  └─ Build artifact
```

---

## 🎯 **Migration Path**

### **Phase 1: Add Persistence** (Week 1)
- [ ] Add SQLite + migrations
- [ ] Refactor session storage
- [ ] Tests for database layer

### **Phase 2: Service Split** (Weeks 2-3)
- [ ] Extract core compiler
- [ ] Create API server wrapper
- [ ] Create service boundaries
- [ ] Add service-to-service communication

### **Phase 3: CI/CD** (Week 1-ongoing)
- [ ] GitHub Actions workflows
- [ ] Automated testing
- [ ] Linting/formatting
- [ ] Security scanning

### **Phase 4: Monitoring** (Weeks 3-4)
- [ ] Structured logging
- [ ] Error tracking
- [ ] Performance metrics
- [ ] Dashboards

---

## 📈 **Scalability Plan**

| Load Level | Current | After Refactor |
|-----------|---------|-----------------|
| 10 users | ✅ OK | ✅ OK |
| 100 users | 🚩 Risky | ✅ OK |
| 1,000 users | ❌ Will fail | 🚩 Needs tuning |
| 10K users | ❌ Will fail | ✅ OK (with caching) |

**Bottlenecks to address:**
1. File upload handling (move to S3)
2. Database queries (add indexing)
3. AI service cost (rate limiting + caching)
4. Memory usage (streaming large files)

---

## 🔄 **Version History**

- **v0.1.x** - Monolithic architecture (current prod)
- **v0.2.x** - Service-oriented refactor (in progress)
- **v0.3.x** - Full CI/CD pipeline
- **v1.0.0** - Production-ready enterprise version

---

## ✅ **Definition of "Production Ready"**

- [x] Automated tests passing
- [x] Security audit completed
- [x] Performance tested
- [ ] Monitoring in place
- [ ] Runbooks written
- [ ] Team trained
- [ ] Incident response plan
- [ ] Backup/recovery tested

---

**Next Steps:**
1. Review this architecture
2. Create service directories
3. Implement persistent storage
4. Add integration tests
5. Deploy to staging environment

---

*This document represents the ACTUAL system design, not marketing claims. It identifies real weaknesses and concrete solutions.*
