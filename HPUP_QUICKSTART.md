# HPUP Quick Start Guide

## What You Now Have

You've transformed your MLJ Results Compiler into a **Hypersonic Universal Processing Platform (HPUP)** with these capabilities:

### 🌐 Web Browsing & API Integration
- **REST APIs** - Connect to any API with automatic JSON parsing
- **Web Scraping** - Extract data from websites with BeautifulSoup
- **RSS Feeds** - Monitor and aggregate RSS/Atom feeds
- **Webhooks** - Receive push data from any service

### 🤖 Multi-Platform Support
- **Telegram** (✅ Active) - Existing bot enhanced
- **Slack** (🚧 Coming) - Full event API support
- **Discord** (🚧 Coming) - Bot integration
- **Teams, Email, etc.** (Extensible)

### 🧠 Intelligent Learning
- **Auto-detects** document formats
- **Learns** column purposes and data types
- **Adapts** processing based on patterns
- **Optimizes** strategies over time

### ⚡ Hypersonic Performance
- **16 concurrent workers** (configurable)
- **Non-blocking async I/O**
- **Smart caching** with TTL
- **Batch processing** for speed

---

## 5-Minute Setup

### Step 1: Install New Dependencies

```bash
pip install -r requirements.txt
```

New packages added:
- `aiohttp` - Async HTTP client for APIs
- `beautifulsoup4` - Web scraping
- `feedparser` - RSS/Atom feeds
- `requests` - HTTP utilities

### Step 2: Start the Server

```bash
# Development
python -m uvicorn src.universal_gateway:app --reload

# Production
gunicorn -k uvicorn.workers.UvicornWorker src.universal_gateway:app
```

Visit: `http://localhost:8000`

### Step 3: Test with Examples

```bash
# Health check
curl http://localhost:8000/health

# Stats
curl http://localhost:8000/stats

# API docs
open http://localhost:8000/docs  # Swagger UI
```

---

## Common Tasks

### Task 1: Register an API Data Source

```bash
curl -X POST http://localhost:8000/api/sources/register \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "weather_api",
    "source_type": "api",
    "url": "https://api.openweathermap.org/data/2.5/weather",
    "params": {
      "lat": "40.7128",
      "lon": "-74.0060"
    },
    "auth": {
      "type": "bearer",
      "token": "YOUR_API_KEY"
    }
  }'
```

### Task 2: Fetch Data from API

```bash
curl http://localhost:8000/api/sources/weather_api/fetch
```

Response:
```json
{
  "source_id": "weather_api",
  "records_fetched": 1,
  "data": [
    {
      "record_id": "weather_api:0",
      "data": {"temp": 72, "humidity": 65},
      "timestamp": "2026-02-01T10:30:00"
    }
  ]
}
```

### Task 3: Scrape a Website

```bash
curl -X POST http://localhost:8000/api/sources/register \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "my_website",
    "source_type": "website",
    "url": "https://example.com/data-table"
  }'

# Fetch
curl http://localhost:8000/api/sources/my_website/fetch
```

### Task 4: Subscribe to RSS Feed

```bash
curl -X POST http://localhost:8000/api/sources/register \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "hacker_news",
    "source_type": "rss",
    "url": "https://news.ycombinator.com/rss",
    "refresh_interval": 3600
  }'

# Fetch latest items
curl http://localhost:8000/api/sources/hacker_news/fetch
```

### Task 5: Process Test Consolidation

```bash
# Submit task
curl -X POST http://localhost:8000/api/process \
  -F "task_type=consolidation" \
  -F "files=@test1.xlsx" \
  -F "files=@test2.xlsx" \
  -F "config={\"priority\":5}"

# Response
{
  "task_id": "task_1738401000.123",
  "status": "submitted",
  "task_type": "consolidation"
}

# Check status
curl http://localhost:8000/api/task/task_1738401000.123
```

### Task 6: Learn Document Format

```bash
curl -X POST http://localhost:8000/api/learn/analyze \
  -F "file=@my_custom_format.xlsx"

# Response
{
  "format_id": "fmt_0",
  "confidence": 0.95,
  "source_app": "excel",
  "column_patterns": {
    "0": "name",
    "1": "email",
    "2": "score"
  }
}

# Get processing strategy
curl http://localhost:8000/api/learn/strategy/fmt_0
```

---

## Python Integration

### In Your Existing Code

```python
from src.hypersonic_core import hypersonic_core, ProcessingTask
from src.data_source_manager import DataSource, data_source_manager

# Initialize
await hypersonic_core.initialize()

# Register data source
api_source = DataSource(
    source_id="my_api",
    source_type="api",
    url="https://api.example.com/data",
    auth={"type": "bearer", "token": "YOUR_TOKEN"}
)
data_source_manager.register_source(api_source)

# Submit task
task = ProcessingTask(
    task_id="my_task",
    task_type="consolidation",
    input_sources=["https://api.example.com/test.xlsx", "local_file.xlsx"]
)
task_id = await hypersonic_core.submit_task(task)

# Monitor
status = await hypersonic_core.get_task_status(task_id)
print(f"Status: {status.status}")
print(f"Results: {status.results}")
print(f"Time: {status.execution_time_ms}ms")
```

---

## Platform Integration

### Slack Integration (Optional)

```bash
# Install slack-bolt
pip install slack-bolt

# Set token
export SLACK_TOKEN=xoxb-your-token-here

# Register adapter
from src.platform_adapter import SlackAdapter, platform_bridge

slack = SlackAdapter("slack", {"token": os.getenv("SLACK_TOKEN")})
platform_bridge.register_adapter(slack)
```

### Discord Integration (Optional)

```bash
# Install discord.py
pip install discord.py

# Register adapter
from src.platform_adapter import DiscordAdapter, platform_bridge

discord = DiscordAdapter("discord", {"token": os.getenv("DISCORD_TOKEN")})
platform_bridge.register_adapter(discord)
```

---

## Configuration

### Environment Variables

Create `.env` file:

```bash
# Core
HYPERSONIC_WORKERS=16
HYPERSONIC_CACHE_SIZE=1000
HYPERSONIC_TIMEOUT=300

# APIs
API_REQUEST_TIMEOUT=10
WEB_SCRAPER_TIMEOUT=15

# Platforms (optional)
SLACK_TOKEN=xoxb-...
DISCORD_TOKEN=...
TELEGRAM_BOT_TOKEN=...

# Performance
ENABLE_UVLOOP=true
```

Load in your code:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Monitoring & Debugging

### Check Health

```bash
curl http://localhost:8000/health
```

Output:
```json
{
  "status": "healthy",
  "workers": 16,
  "queue_size": 0,
  "performance": {
    "tasks_completed": 42,
    "total_processing_ms": 1234.56,
    "avg_processing_ms": 29.39
  },
  "cache": {
    "cache_size": 12,
    "hits": 234,
    "misses": 56
  }
}
```

### Get Statistics

```bash
curl http://localhost:8000/stats
```

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Advanced: Custom Data Source

Create a custom connector:

```python
from src.data_source_manager import DataSourceConnector, DataRecord

class CustomConnector(DataSourceConnector):
    async def fetch(self):
        # Your custom logic
        raw_data = await self._your_fetch_method()
        return await self.parse(raw_data)
    
    async def parse(self, raw_data):
        records = []
        for item in raw_data:
            records.append(DataRecord(
                source_id=self.source.source_id,
                record_id=f"{self.source.source_id}:{id(item)}",
                data=item,
                timestamp=datetime.now()
            ))
        return records

# Register
data_source_manager.connectors['custom'] = CustomConnector
```

---

## Performance Tuning

### Increase Worker Count (for I/O-heavy)

```python
from src.hypersonic_core import hypersonic_core
hypersonic_core.max_workers = 32  # Before initialize()
```

### Enable uvloop (faster event loop)

```python
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
```

### Batch Operations

```python
# Instead of:
for url in urls:
    await fetch(url)  # Sequential, slow

# Do this:
tasks = [fetch(url) for url in urls]
results = await asyncio.gather(*tasks)  # Parallel, fast!
```

---

## Deployment

### Render Deployment

Update `Procfile`:

```
web: gunicorn -k uvicorn.workers.UvicornWorker src.universal_gateway:app
```

Push to GitHub:

```bash
git add -A
git commit -m "Deploy HPUP with universal platform"
git push
```

Render auto-deploys! 🚀

### Docker

```dockerfile
FROM python:3.13

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "-m", "uvicorn", "src.universal_gateway:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Troubleshooting

### "Module not found" errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check versions
pip list | grep -E "aiohttp|beautifulsoup"
```

### API requests timing out

- Increase `API_REQUEST_TIMEOUT` in `.env`
- Check your internet connection
- Verify API URL is accessible

### Memory issues

- Reduce `HYPERSONIC_CACHE_SIZE`
- Lower `HYPERSONIC_WORKERS`
- Monitor with `GET /stats`

---

## What's Next?

1. ✅ **You have**: Universal platform with API integration
2. **Next step**: [Review UNIVERSAL_PLATFORM.md](UNIVERSAL_PLATFORM.md) for detailed architecture
3. **Then**: Integrate with existing telegram_bot.py
4. **Finally**: Deploy to production

---

## Support

- 📚 **Docs**: [UNIVERSAL_PLATFORM.md](UNIVERSAL_PLATFORM.md)
- 🔧 **API Docs**: `http://localhost:8000/docs` (Swagger)
- 📊 **Stats**: `http://localhost:8000/stats`
- ❤️ **Health**: `http://localhost:8000/health`

**Welcome to the future of document processing! 🚀**
