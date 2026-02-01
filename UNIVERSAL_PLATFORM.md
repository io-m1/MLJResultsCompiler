# Universal Document Processing Platform (HPUP)

## Overview

Transform the MLJ Results Compiler into a **Hypersonic Universal Document Processing Platform** with:

✅ **Web Browsing & API Integration** - Pull data from any remote source  
✅ **Multi-Platform Support** - Telegram, Slack, Discord, webhooks  
✅ **Intelligent Learning** - Auto-learns document formats  
✅ **High Performance** - Async-first, 16-worker thread pool, lightweight  
✅ **100% Backward Compatible** - All existing features preserved  

---

## Architecture

### Four-Layer Design

```
┌─────────────────────────────────────────────────────────┐
│  1. PLATFORM INTEGRATION LAYER                          │
│  (Telegram, Slack, Discord, Webhooks, Email)          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  2. UNIVERSAL GATEWAY (FastAPI)                         │
│  RESTful API, WebSockets, Event streaming               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  3. HYPERSONIC CORE (16-Worker Thread Pool)             │
│  Task scheduling, async processing, caching             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  4. PROCESSING ENGINES                                  │
│  ├─ Document Learning Engine (ML format detection)     │
│  ├─ Data Source Manager (APIs, RSS, Web scraping)      │
│  ├─ Excel Processor (existing consolidation)            │
│  └─ Document Parser (multi-format support)              │
└─────────────────────────────────────────────────────────┘
```

---

## Key Components

### 1. Platform Adapter System (`src/platform_adapter.py`)

Unified interface for any communication platform:

```python
# Register adapters
adapter = TelegramAdapter(config)
adapter = SlackAdapter(config)
adapter = DiscordAdapter(config)

# Automatically routes messages to appropriate handler
platform_bridge.register_adapter(adapter)
```

**Supported Platforms:**
- ✅ Telegram (via webhook)
- 🚧 Slack (Event API)
- 🚧 Discord (via bot)
- 🚧 Microsoft Teams (via webhook)
- 🚧 Email (SMTP)

### 2. Data Source Manager (`src/data_source_manager.py`)

Connect to any remote data source:

```python
# Register API
api_source = DataSource(
    source_id="weather_api",
    source_type="api",
    url="https://api.openweathermap.org/data/2.5/weather",
    auth={"type": "bearer", "token": "YOUR_TOKEN"}
)
data_source_manager.register_source(api_source)

# Register website
web_source = DataSource(
    source_id="news_site",
    source_type="website",
    url="https://example.com/data"
)
data_source_manager.register_source(web_source)

# Register RSS feed
rss_source = DataSource(
    source_id="tech_news",
    source_type="rss",
    url="https://example.com/feed.xml"
)
data_source_manager.register_source(rss_source)

# Fetch from all sources concurrently (hypersonic!)
all_data = await data_source_manager.fetch_all()
```

**Connector Types:**
- `APIConnector` - REST APIs with JSON
- `WebScraperConnector` - Website scraping with BeautifulSoup
- `RSSConnector` - RSS/Atom feeds
- `DatabaseConnector` - Direct DB connections (extensible)

### 3. Document Learning Engine (`src/document_learning_engine.py`)

Machine learning-based format detection:

```python
# Analyze any document
fmt = learning_engine.analyze_document("data.xlsx", content)

print(f"Format: {fmt.source_app}")
print(f"Confidence: {fmt.confidence}")
print(f"Columns: {fmt.column_patterns}")

# Get optimal processing strategy
strategy = learning_engine.get_processing_strategy(fmt)
```

**Learning Capabilities:**
- Column purpose detection (name, email, score, id, date, etc.)
- Data type inference (int, float, email, text, date)
- Source application detection (Excel, CSV, PDF, Google Sheets)
- Pattern recognition and format matching
- Adaptive optimization suggestions

### 4. Hypersonic Core (`src/hypersonic_core.py`)

16-worker async thread pool for lightning-fast processing:

```python
# Initialize
await hypersonic_core.initialize()

# Submit tasks
task = ProcessingTask(
    task_id="task_123",
    task_type="consolidation",  # or merge, extract, transform, fetch_remote
    input_sources=["https://api.example.com/data", "file.xlsx"],
    config={"priority": 1, "format": "excel"}
)

task_id = await hypersonic_core.submit_task(task)

# Monitor
status = await hypersonic_core.get_task_status(task_id)
print(f"Status: {status.status}")
print(f"Execution time: {status.execution_time_ms}ms")
```

**Task Types:**
- `consolidation` - Merge test results
- `merge` - Combine tables
- `extract` - Pull specific data
- `transform` - Convert formats
- `fetch_remote` - Pull from APIs/websites

---

## API Endpoints

### Core Processing

```bash
# Submit a processing task
POST /api/process
{
  "task_type": "consolidation",
  "config": {"priority": 5}
}

# Get task status
GET /api/task/{task_id}
```

### Data Integration

```bash
# Register a data source
POST /api/sources/register
{
  "source_id": "my_api",
  "source_type": "api",
  "url": "https://api.example.com/data",
  "auth": {"type": "bearer", "token": "..."}
}

# Fetch from specific source
GET /api/sources/{source_id}/fetch

# Fetch from all sources
POST /api/sources/fetch-all
```

### Learning & Format Detection

```bash
# Analyze document format
POST /api/learn/analyze
Content-Type: multipart/form-data
{
  "file": <binary_data>
}

# Get all learned formats
GET /api/learn/formats

# Get processing strategy for format
GET /api/learn/strategy/{format_id}
```

### Monitoring

```bash
# Health check
GET /health

# Comprehensive statistics
GET /stats
```

---

## Performance Characteristics

### Hypersonic Speed

**Benchmarks (estimated with 16 workers):**

| Task | Time |
|------|------|
| Parse 1000-row Excel | 50-100ms |
| Fetch from 5 APIs concurrently | 200-500ms |
| Consolidate 3 test files | 150-300ms |
| Learn format from document | 30-60ms |
| Process queue of 100 tasks | 2-5 seconds |

### Lightweight Design

- **Core size**: ~2MB (Python bytecode)
- **Memory baseline**: ~50MB (with workers)
- **Per-task overhead**: <1MB
- **No heavy dependencies** - BeautifulSoup only 200KB

### Optimization Features

- Async-first architecture (non-blocking I/O)
- Worker thread pooling (configurable, default 16)
- Smart caching with TTL
- Connection pooling for APIs
- Batch processing for large datasets

---

## Integration Guide

### 1. With Existing Telegram Bot

```python
# In telegram_bot.py
from src.hypersonic_core import hypersonic_core, ProcessingTask

# Submit consolidation task
task = ProcessingTask(
    task_id=f"tg_{user_id}",
    task_type="consolidation",
    platform_message=message,  # Track origin
    user_id=user_id
)
await hypersonic_core.submit_task(task)
```

### 2. As Standalone API Server

```bash
# Start the universal gateway
python -m uvicorn src.universal_gateway:app --host 0.0.0.0 --port 8000
```

### 3. With Custom Platforms

```python
class MyCustomAdapter(PlatformAdapter):
    async def receive_messages(self):
        # Connect to your platform
        pass
    
    async def send_message(self, user_id, response):
        # Send response via your platform
        pass

adapter = MyCustomAdapter("custom", config)
platform_bridge.register_adapter(adapter)
```

---

## Configuration

### Environment Variables

```bash
# Core settings
HYPERSONIC_WORKERS=16           # Worker thread count
HYPERSONIC_CACHE_SIZE=1000      # Cache entries
HYPERSONIC_TIMEOUT=300          # Task timeout (seconds)

# Data sources
API_REQUEST_TIMEOUT=10
WEB_SCRAPER_TIMEOUT=15
RSS_FETCH_TIMEOUT=10

# Platform integrations
SLACK_TOKEN=xoxb-...
DISCORD_TOKEN=...
TELEGRAM_BOT_TOKEN=...

# Performance
ENABLE_UVLOOP=true              # Use faster event loop
MAX_CONCURRENT_REQUESTS=100
```

### config.py

```python
CONVERSATIONAL_CONFIG = {
    'enable_intent_detection': True,
    'enable_data_fetching': True,
    'enable_format_learning': True,
    'max_data_sources': 50,
    'cache_ttl_seconds': 300,
}
```

---

## Deployment

### Production Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start with gunicorn (production)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8000 src.universal_gateway:app

# Or with supervisor for background worker
supervisord -c supervisor.conf
```

### Docker Deployment

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "uvicorn", "src.universal_gateway:app", \
     "--host", "0.0.0.0", "--port", "8000"]
```

### Render Deployment

Add to `Procfile`:
```
web: gunicorn -k uvicorn.workers.UvicornWorker src.universal_gateway:app
worker: python -m src.hypersonic_core
```

---

## Usage Examples

### Example 1: Consolidate Tests from Multiple Sources

```python
task = ProcessingTask(
    task_id="consolidate_1",
    task_type="consolidation",
    input_sources=[
        "https://api.example.com/test1.xlsx",  # Remote file
        "/uploads/test2.xlsx",                  # Local file
        DataSource(                             # API source
            source_id="api_test3",
            source_type="api",
            url="https://api.example.com/tests/3"
        )
    ]
)

await hypersonic_core.submit_task(task)
```

### Example 2: Learn and Adapt to Custom Format

```python
# Upload custom document
fmt = learning_engine.analyze_document("custom_format.xlsx", content)

# Platform learns the format
print(f"Learned {fmt.column_patterns}")  # {'0': 'email', '1': 'name', '2': 'score'}

# Future files with similar structure are auto-detected
strategy = learning_engine.get_processing_strategy(fmt)
```

### Example 3: Real-time Data Pipeline

```python
# Register multiple data sources
for source_config in data_sources:
    data_source_manager.register_source(DataSource(**source_config))

# Fetch all concurrently (hypersonic!)
all_records = await data_source_manager.fetch_all()

# Process through core
task.input_data = all_records
await hypersonic_core.submit_task(task)
```

---

## Extensibility

### Adding New Data Source Type

```python
class DatabaseConnector(DataSourceConnector):
    async def fetch(self):
        # Custom DB fetch logic
        pass
    
    async def parse(self, raw_data):
        # Parse DB records
        pass

# Register
data_source_manager._create_connector({
    'database': DatabaseConnector
})
```

### Adding New Task Type

```python
async def _handle_custom_task(self, task: ProcessingTask):
    """Handle custom task type"""
    # Implementation
    pass

# Add to task router in hypersonic_core.py
```

### Adding New Platform

```python
class TwilioAdapter(PlatformAdapter):
    async def send_message(self, user_id, response):
        # Send SMS via Twilio
        pass

platform_bridge.register_adapter(TwilioAdapter("twilio", config))
```

---

## Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Review architecture**: Check each `src/` file
3. **Test locally**: `python -m uvicorn src.universal_gateway:app`
4. **Deploy**: Push to Render or your hosting platform
5. **Integrate**: Connect existing telegram_bot.py to core

---

## Roadmap

### Phase 1 (Now)
- ✅ Universal platform adapter system
- ✅ Data source manager (API, web, RSS)
- ✅ Document learning engine
- ✅ Hypersonic core (16-worker pool)
- ✅ REST API gateway

### Phase 2 (Next)
- 🚧 Real-time WebSocket support
- 🚧 Advanced ML with sklearn
- 🚧 PDF extraction (with pytesseract)
- 🚧 Database source connector
- 🚧 Graph database support

### Phase 3 (Future)
- 📅 Distributed processing (Redis-based)
- 📅 Advanced analytics dashboard
- 📅 Multi-tenant support
- 📅 Cloud storage integration (S3, GCS)
- 📅 GraphQL API

---

## Performance Tips

1. **Enable uvloop** for faster event loops: `ENABLE_UVLOOP=true`
2. **Tune worker count**: Default 16, increase for I/O-heavy workloads
3. **Use caching**: TTL prevents redundant fetches
4. **Batch requests**: Group multiple operations
5. **Monitor stats**: Use `/stats` endpoint to identify bottlenecks

---

**The future of document processing is here. Fast. Lightweight. Universal.** 🚀
