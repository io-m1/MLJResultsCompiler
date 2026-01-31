#!/bin/bash
# MLJ Results Compiler Bot - Setup & Validation Script
# Fixes common errors and validates deployment readiness

set -e

echo "========================================"
echo "MLJ Bot Setup Validator"
echo "========================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check Python version
echo -e "\n${YELLOW}[1/8] Checking Python version...${NC}"
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo -e "Python version: ${GREEN}$PYTHON_VERSION${NC}"
if [[ $PYTHON_VERSION == 3.* ]]; then
    echo -e "${GREEN}✓ Python 3.x detected${NC}"
else
    echo -e "${RED}✗ Python 3.x required${NC}"
    exit 1
fi

# 2. Check .env file
echo -e "\n${YELLOW}[2/8] Checking .env file...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file exists${NC}"
    # Check for required keys
    if grep -q "TELEGRAM_BOT_TOKEN=" .env; then
        echo -e "${GREEN}✓ TELEGRAM_BOT_TOKEN set${NC}"
    else
        echo -e "${RED}✗ TELEGRAM_BOT_TOKEN missing in .env${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ .env file not found, creating from .env.example${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}Please fill in .env with your actual values${NC}"
        exit 1
    fi
fi

# 3. Check .gitignore
echo -e "\n${YELLOW}[3/8] Checking .gitignore...${NC}"
if grep -q "\.env" .gitignore 2>/dev/null; then
    echo -e "${GREEN}✓ .env is ignored in git${NC}"
else
    echo -e "${YELLOW}⚠ .env not in .gitignore, adding...${NC}"
    echo ".env" >> .gitignore
    echo -e "${GREEN}✓ Added .env to .gitignore${NC}"
fi

# 4. Check virtual environment
echo -e "\n${YELLOW}[4/8] Checking virtual environment...${NC}"
if [ -d ".venv" ] || [ -d "venv" ] || [ -d "env" ]; then
    echo -e "${GREEN}✓ Virtual environment detected${NC}"
else
    echo -e "${YELLOW}⚠ No virtual environment found${NC}"
    echo "Creating venv..."
    python -m venv .venv
    source .venv/bin/activate || . .venv/Scripts/activate
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# 5. Check requirements.txt
echo -e "\n${YELLOW}[5/8] Checking requirements.txt...${NC}"
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✓ requirements.txt exists${NC}"
    # Check key packages
    if grep -q "fastapi" requirements.txt; then
        echo -e "${GREEN}✓ fastapi present${NC}"
    else
        echo -e "${RED}✗ fastapi missing${NC}"
        exit 1
    fi
    if grep -q "uvicorn" requirements.txt; then
        echo -e "${GREEN}✓ uvicorn present${NC}"
    else
        echo -e "${RED}✗ uvicorn missing${NC}"
        exit 1
    fi
    if grep -q "pandas==2.2" requirements.txt; then
        echo -e "${GREEN}✓ pandas 2.2.x (pre-built wheels)${NC}"
    else
        echo -e "${YELLOW}⚠ Consider pandas 2.2.x for wheel availability${NC}"
    fi
else
    echo -e "${RED}✗ requirements.txt missing${NC}"
    exit 1
fi

# 6. Check core files
echo -e "\n${YELLOW}[6/8] Checking core files...${NC}"
REQUIRED_FILES=("server.py" "telegram_bot.py" "src/excel_processor.py" ".env.example")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file exists${NC}"
    else
        echo -e "${RED}✗ $file missing${NC}"
        exit 1
    fi
done

# 7. Check Python imports (dry run)
echo -e "\n${YELLOW}[7/8] Checking Python imports...${NC}"
python -c "
try:
    from telegram import Update
    print('✓ python-telegram-bot OK')
except ImportError as e:
    print('✗ Import error:', e)
    exit(1)
try:
    from fastapi import FastAPI
    print('✓ fastapi OK')
except ImportError as e:
    print('✗ Import error:', e)
    exit(1)
try:
    import openpyxl
    print('✓ openpyxl OK')
except ImportError as e:
    print('✗ Import error:', e)
    exit(1)
" 2>&1 || echo -e "${YELLOW}⚠ Some imports missing, run: pip install -r requirements.txt${NC}"

# 8. Render deployment check
echo -e "\n${YELLOW}[8/8] Render deployment checklist...${NC}"
echo -e "${GREEN}Required Render env vars:${NC}"
echo "  TELEGRAM_BOT_TOKEN=<your-token>"
echo "  WEBHOOK_SECRET=<long-random-string>"
echo "  WEBHOOK_BASE_URL=https://mljresultscompiler.onrender.com"
echo ""
echo -e "${GREEN}Render service info:${NC}"
echo "  Service URL: https://mljresultscompiler.onrender.com"
echo "  Service ID: srv-d5v21o4oud1c73873kbg"
echo "  Build Command: pip install -r requirements.txt"
echo "  Start Command: uvicorn server:app --host 0.0.0.0 --port \$PORT"

# Summary
echo ""
echo "========================================"
echo -e "${GREEN}✓ Setup validation complete!${NC}"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Ensure all Render env vars are set (see above)"
echo "2. Trigger redeploy on Render dashboard"
echo "3. Check logs: Dashboard → Logs tab"
echo "4. Test: https://mljresultscompiler.onrender.com/"
echo "5. Telegram: send /start to @mlj_results_compiler_bot"
echo ""
