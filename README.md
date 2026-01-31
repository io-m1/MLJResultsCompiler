# MLJ Results Compiler

Automated consolidation tool for test results from SurveyHeart Excel files.

## Overview

This tool processes 1-5 test result files and consolidates them into a single Excel spreadsheet with:
- **Color-coded columns** for each test
- **Alphabetically sorted** participants
- **Matched records** across all tests by email
- **Comprehensive validation** of data quality

## Test Color Scheme

| Test | Color | RGB |
|------|-------|-----|
| Test 1 | White | #FFFFFF |
| Test 2 | Sky Blue | #87CEEB |
| Test 3 | Yellow | #FFFF00 |
| Test 4 | Army Green | #556B2F |
| Test 5 | Red | #FF0000 |

## Project Structure

```
MLJResultsCompiler/
├── input/              # Drop your test XLSX files here
├── output/             # Consolidated results saved here
├── config/             # Configuration files
├── src/
│   ├── main.py        # Entry point
│   ├── excel_processor.py  # Core processing logic
│   ├── validators.py   # Data validation
│   └── color_config.py # Color definitions
├── requirements.txt
└── README.md
```

## Installation

1. Ensure Python 3.8+ is installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Preparing Input Files

1. Export test result files from SurveyHeart as XLSX
2. Name them clearly: `Test 1.xlsx`, `Test 2.xlsx`, etc.
3. Place them in the `input/` folder

### Running the Consolidation

```bash
python src/main.py
```

The tool will:
- Scan the `input/` folder for test files
- Extract Full Name, Email, and Score columns
- Match participants across tests by email
- Create a consolidated file with all test scores
- Apply color coding for visual verification
- Save to `output/Consolidated_Results.xlsx`

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

The process logs all operations to `test_consolidation.log` with:
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

## Troubleshooting

### No test files found
- Ensure files are in the `input/` folder
- Verify filenames contain "Test" and a number (1-5)
- Check file extension is `.xlsx`

### Column not found errors
- Verify column headers match expected names
- Check for extra spaces in headers
- Ensure headers are in the first row

### Invalid email errors
- Check email format in source files
- Look for typos or special characters
- Review `test_consolidation.log` for specific issues

## Support

For issues or questions, check the log file first:
```bash
cat test_consolidation.log
```

The log contains detailed information about the processing steps and any validation issues encountered.
