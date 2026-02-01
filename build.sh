#!/bin/bash
# Render Build Script
# Ensures proper dependency installation and app startup

set -e

echo "🔨 MLJ Results Compiler - Render Build Script"
echo "=============================================="

# Step 1: Install build tools
echo "📦 Installing build tools..."
pip install --upgrade pip setuptools wheel

# Step 2: Install dependencies from requirements.txt
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Step 3: Verify key imports
echo "✅ Verifying imports..."
python -c "import fastapi; print('✓ FastAPI OK')"
python -c "import pandas; print('✓ Pandas OK')"
python -c "import src.main; print('✓ Main module OK')"
python -c "import src.async_ai_service; print('✓ Async AI service OK')"
python -c "import src.async_data_agent; print('✓ Async data agent OK')"
python -c "import src.async_file_io; print('✓ Async file I/O OK')"

echo ""
echo "✅ Build completed successfully!"
echo "Ready for deployment."
