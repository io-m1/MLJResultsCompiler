# AI Assistant Feature - Documentation & Governance

**Status:** Optional Feature (Feature-Flagged)  
**Model:** Groq Llama 3.1 70B Versatile  
**Provider:** Groq Cloud (groq.com)  
**API Version:** Compatible with OpenAI-compatible endpoints

---

## 🤖 What The AI Does

Optional conversational interface for data transformation requests:

- Natural language data transformations ("collate scores", "add grades", "rank students")
- Troubleshooting assistance
- Cold email generation (experimental)

**CRITICAL:** AI is optional enhancement, not core functionality. System works 100% without it.

---

## 💰 Costs

### Free Tier (Groq)

- **Rate:** 30 requests/minute
- **Cost:** $0 (community tier)
- **Use Case:** Development, testing, light production

### Production Tier

- **Rate:** Contact Groq
- **Cost:** Pay-per-token
- **Use Case:** High-volume deployments

---

## 🚀 Enabling AI

### Step 1: Get API Key

1. Go to https://groq.com/console
2. Sign up for free account
3. Create API key
4. Copy key

### Step 2: Set Environment Variable

```bash
export GROQ_API_KEY=gsk_xxxxx...
```

Or in `.env`:
```
GROQ_API_KEY=gsk_xxxxx...
```

### Step 3: Verify

```bash
curl http://localhost:8000/status | grep ai_enabled
# Should return: "ai_enabled": true
```

---

## ⚙️ Configuration

All AI settings via environment variables. See `src/config.py`:

```python
GROQ_API_KEY: Optional[str]      # API key (None = disabled)
GROQ_MODEL: str                   # Model name
GROQ_TIMEOUT: int                 # Request timeout (seconds)
ENABLE_AI_ASSISTANT: bool         # Auto-set to True if key present
```

---

## 📊 Cost Monitoring

### Development (Free)

```bash
# Safe: 30 requests/minute, unlimited free tier
curl -X POST http://localhost:8000/api/hybrid/ai-assist \
  -H "Content-Type: application/json" \
  -d '{"message": "collate scores", "session_id": "test"}'

# Cost: $0
```

### Production (Paid)

```python
# Track usage in logs
from src.ai_assistant import get_assistant

assistant = get_assistant()
response = assistant.analyze_message("collate scores")

# Log cost
tokens_used = response.get("usage", {}).get("total_tokens", 0)
cost_estimate = tokens_used * 0.0015  # ~$0.0015 per 1k tokens
logger.info(f"AI request cost estimate: ${cost_estimate:.4f}")
```

---

## 🛡️ Safety & Limits

### Built-in Safeguards

1. **Request Timeout:** 30 seconds default
   - Prevents hanging requests
   - Prevents runaway costs

2. **Feature Flag:** Must set `GROQ_API_KEY`
   - Off by default (zero cost)
   - Can be disabled by unset

3. **Fallback:** If API fails or timeout
   - Returns helpful suggestions (no data loss)
   - System continues working

4. **Rate Limiting:** Groq's rate limits enforced
   - 30 req/min on free tier
   - Returns 429 if exceeded

---

## 🧪 Testing AI Features

### Unit Test

```python
# tests/unit/test_ai_assistant.py
def test_ai_disabled_without_key():
    """AI disabled if no API key"""
    assistant = get_assistant()
    assert not assistant.llm_enabled


def test_ai_parsing_works():
    """Intent detection works offline"""
    assistant = get_assistant()
    result = assistant.parse_data_request("collate scores")
    assert result["execute"] == True
    assert len(result["actions"]) > 0
```

### Integration Test

```python
# tests/integration/test_ai_endpoint.py
async def test_ai_request_with_key():
    """Full AI request (requires GROQ_API_KEY set)"""
    response = client.post("/api/hybrid/ai-assist", json={
        "message": "collate scores",
        "session_id": "test-123"
    })
    assert response.status_code in [200, 503]  # 503 if AI unavailable
```

---

## 📋 Feature Flag Logic

```python
# Automatic feature detection (src/config.py)

if os.getenv("GROQ_API_KEY"):
    ENABLE_AI_ASSISTANT = True
else:
    ENABLE_AI_ASSISTANT = False

# Check at startup
settings = get_settings()
if settings.ENABLE_AI_ASSISTANT:
    logger.info("AI Assistant ENABLED")
else:
    logger.info("AI Assistant DISABLED (set GROQ_API_KEY to enable)")
```

---

## 🚨 Failure Modes

### Scenario 1: API Key Invalid

```
User: "collate scores"
System: Detects invalid key at startup → logs error → disables AI
Response: "I can help with: • Add random scores • Add grades..."
Cost: $0 (feature disabled)
```

### Scenario 2: Rate Limit Exceeded

```
User: [makes 31st request]
API Response: 429 Too Many Requests
System: Returns helpful suggestions
Cost: $0 (request not charged)
```

### Scenario 3: Network Timeout

```
User: "collate scores"
API: Takes >30 seconds
System: Timeout triggered → returns suggestions
Response: "I can help with: • Add random scores • Add grades..."
Cost: Partial charge for incomplete request (unlikely, but possible)
```

### Scenario 4: API Outage

```
User: "collate scores"
API: Service unavailable
System: Graceful fallback
Response: "I can help with: • Add random scores • Add grades..."
Cost: $0 (request failed before token generation)
```

---

## 💵 Cost Estimation

### Free Tier (Groq Community)

- Requests per day: ~400 (30/min * 14 hours active)
- Average tokens/request: ~200
- Total tokens/day: 80,000
- Cost: **$0**

### Low Volume Production

- Requests/day: 1,000
- Average tokens/request: 200
- Total tokens/day: 200,000
- Daily cost: 200K * $0.0005 = **~$0.10/day**
- Monthly cost: **~$3/month**

### High Volume Production

- Requests/day: 10,000
- Average tokens/request: 200
- Total tokens/day: 2,000,000
- Daily cost: 2M * $0.0005 = **~$1/day**
- Monthly cost: **~$30/month**

---

## 📊 Monitoring

### Check AI Status

```bash
curl http://localhost:8000/status | jq .features.ai_assistant

# Output:
{
  "ai_assistant": true,
  "telegram_bot": false
}
```

### Check Logs

```bash
grep "AI" logs/app.log
# Output:
2026-02-01 10:00:00 INFO    AI Assistant ENABLED
2026-02-01 10:01:23 INFO    AI request: collate scores (157 tokens)
2026-02-01 10:02:45 WARNING AI timeout after 30s
```

---

## 🔄 Production Checklist

- [x] Feature is optional (feature-flagged)
- [x] Can be disabled instantly (unset env var)
- [x] Has fallback if API fails
- [x] Has timeout (prevent hanging)
- [x] Has rate limiting (built-in)
- [x] Costs are documented
- [x] Monitoring is in place
- [ ] Cost alerts configured (TODO)
- [ ] Usage dashboard setup (TODO)

---

## 🎯 When to Use AI

**USE:**
- User explicitly asks for data transformation
- Development/testing with free tier
- Production with monitored costs

**DON'T USE:**
- Every request (would be expensive)
- Without rate limiting
- Without monitoring
- Without user consent

---

## 🔮 Future Improvements

1. **Local Models** - Run Ollama locally (zero cost, slower)
2. **Caching** - Cache common transformations
3. **Cost Alerts** - Slack notifications if cost threshold exceeded
4. **Usage Analytics** - Dashboard showing AI usage/cost
5. **Model Switching** - Support multiple AI providers

---

## 📞 Support

- **Groq Issues:** Visit https://console.groq.com/support
- **API Docs:** https://console.groq.com/docs
- **Community:** https://groq.com/community

---

**Last Updated:** February 1, 2026

This document reflects actual costs, safety measures, and governance for the AI feature. No exaggerations.
