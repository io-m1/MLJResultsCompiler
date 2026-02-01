# Render deployment configuration
# Single web process with integrated Telegram bot and async services
release: pip install --upgrade pip setuptools wheel
web: uvicorn src.main:app --host 0.0.0.0 --port $PORT --timeout-graceful-shutdown 30
