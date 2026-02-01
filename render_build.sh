#!/usr/bin/env bash
set -euo pipefail

echo "🔧 Render Build Helper - ensure modern pip/setuptools/wheel before PEP 517 build"

# Use python -m pip to avoid system pip ambiguity
echo "🛠 Upgrading pip, setuptools, wheel..."
python -m pip install --upgrade pip setuptools wheel

echo "📥 Installing runtime dependencies from requirements.txt..."
python -m pip install -r requirements.txt

echo "🔎 Verifying critical imports..."
python -c "import fastapi; print('✓ fastapi')"
python -c "import pandas; print('✓ pandas')"
python -c "import src.main; print('✓ src.main')"

echo "✅ render_build.sh finished successfully"
