release: pip install --upgrade pip setuptools wheel
web: python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT --timeout-graceful-shutdown 30 --loop asyncio
