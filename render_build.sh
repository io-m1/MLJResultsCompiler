#!/usr/bin/env bash
set -euo pipefail

echo "[BUILD] Render Build Helper - ensure modern pip/setuptools/wheel before PEP 517 build"

# Use python -m pip to avoid system pip ambiguity
echo "[BUILD] Upgrading pip, setuptools, wheel..."
python -m pip install --upgrade pip setuptools wheel

echo "[BUILD] Installing runtime dependencies from requirements.txt..."
python -m pip install -r requirements.txt

echo "[BUILD] Verifying critical imports..."
python -c "import fastapi; print('[OK] fastapi')"
python -c "import pandas; print('[OK] pandas')"
python -c "import src.main; print('[OK] src.main')"

echo "[SUCCESS] render_build.sh finished successfully"
