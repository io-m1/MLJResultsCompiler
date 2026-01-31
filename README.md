# MLJ Results Compiler

Automated consolidation tool for test results from SurveyHeart Excel files.

## Features

- 🤖 **Telegram Bot** - Upload files directly from Telegram (24/7 available)
- 📊 **Multi-Format Export** - XLSX (with colors), PDF, DOCX
- 📧 **Email Matching** - Automatically matches participants across tests
- 🎨 **Color Coded** - Visual verification with test-specific colors
- ✨ **Auto-Sorting** - Alphabetically organized results
- ✅ **Data Validation** - Comprehensive validation and error reporting

## Test Color Scheme

| Test | Color | RGB |
|------|-------|-----|
| Test 1 | White | #FFFFFF |
| Test 2 | Sky Blue | #87CEEB |
| Test 3 | Yellow | #FFFF00 |
| Test 4 | Army Green | #556B2F |
| Test 5 | Red | #FF0000 |

## Quick Start

### Option 1: Telegram Bot (Easiest) 🤖

1. Find your bot on Telegram (search by username)
2. Send `/start`
3. Upload your test XLSX files
4. Select output format
5. Download results instantly!

**Deploy bot:** See [TELEGRAM_BOT_SETUP.md](TELEGRAM_BOT_SETUP.md)

### Option 2: Command Line

```bash
# Install dependencies
pip install -r requirements.txt

# Run with default XLSX output
python src/main.py

# Or choose format
python src/main.py --format pdf
python src/main.py --format docx
```

Results go to `output/` folder

## Expected Input Format

Each test file should contain columns:
- **Full Name** (or Name, Participant)
- **Email** (or E-mail, Email Address)
- **Score** (or Result, %, Percentage)

## Output Format

The consolidated file contains:
- Column A: Full Name
- Column B: Email
- Columns C-G: Test 1-5 Scores (color-coded)

Missing scores for a participant in a specific test are left blank.

## Logging

All operations are logged to `test_consolidation.log` with:
- Timestamp of each operation
- Number of records loaded per test
- Validation warnings and errors
- Final summary and output location

## Data Validation

The tool validates:
- ✓ Email format (RFC 5322 simplified)
- ✓ Score range (0-100%)
- ✓ Required fields present
- ✓ Duplicate handling by email
- ✓ Case normalization (names and emails)

## Project Structure

```
MLJResultsCompiler/
├── input/                    # Drop test XLSX files here
├── output/                   # Results saved here
├── src/
│   ├── main.py              # CLI entry point
│   ├── excel_processor.py    # Core processing
│   ├── validators.py         # Data validation
│   └── color_config.py       # Color definitions
├── telegram_bot.py          # Telegram bot (for deployment)
├── generate_sample_data.py   # Create test files
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── TELEGRAM_BOT_SETUP.md   # Bot deployment guide
├── Procfile                # Heroku deployment
├── runtime.txt             # Python version for Heroku
└── README.md               # This file
```
