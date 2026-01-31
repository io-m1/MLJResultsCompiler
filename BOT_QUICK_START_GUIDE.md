# MLJResultsCompiler Bot - Quick Start Guide
**Date:** January 31, 2026  
**Version:** 1.0 - Production Ready  
**Based on:** Analysis of real Obstetrics & Gynaecology test data

---

## WHAT YOU HAVE NOW

You have a **fully automated bot** that consolidates 5 test result files from SurveyHeart into one professional report.

```
BEFORE (Manual - 45+ minutes):
1. Download tests 1-5 from SurveyHeart
2. Open each test, apply color formatting
3. Extract Name, Email, Score columns
4. Sort alphabetically
5. Email-match across tests (create merged table)
6. Transpose to one row per person
7. Verify and fix errors
8. Save final consolidated report

AFTER (Automated - 30 seconds):
python results_compiler_bot.py
✓ Done! Check output/Consolidated_Results.xlsx
```

---

## QUICK START (5 MINUTES)

### Step 1: Install Requirements
```bash
pip install pandas openpyxl numpy
```

### Step 2: Setup Folder Structure
```
your_project/
├── input/                          ← Place TEST_1 to TEST_5 files here
├── output/                         ← Bot creates consolidated results here
├── results_compiler_bot.py         ← The automation bot
└── compiler_execution.log          ← Bot creates this log file
```

### Step 3: Place Test Files
Copy your 5 test files to the `input/` folder:
```
input/
├── TEST_1_Obstetrics___Gynecology_JANUARY_2026.xlsx
├── TEST_2_Obstetrics___Gynae_JANUARY_2026.xlsx
├── TEST_3_Obstetrics___Gynaecology_JANUARY_15.xlsx
├── TEST_4_Obstetrics___Gynecology_JANUARY_17.xlsx
└── TEST_5_Obstetrics_and_Gynaecology_Ultrasonography.xlsx
```

### Step 4: Run the Bot
```bash
# Option A: Default (looks for ./input/, creates ./output/)
python results_compiler_bot.py

# Option B: Custom paths
python results_compiler_bot.py /path/to/tests /path/to/output

# Option C: Run from within Python
from results_compiler_bot import ResultsCompiler
compiler = ResultsCompiler(input_folder='input', output_folder='output')
compiler.run()
```

### Step 5: Check Results
```
✓ Output file: output/Consolidated_Results.xlsx
✓ Log file: compiler_execution.log
✓ Time taken: ~30 seconds
```

---

## WHAT THE BOT DOES

### Processing Pipeline
```
STEP 1: FIND & LOAD FILES
├─ Searches for TEST_1 to TEST_5 in input/
├─ Handles different file naming patterns
└─ Reports which files found

STEP 2: EXTRACT CORE DATA
├─ Detects column names (handles variations):
│  ├─ Name: " Full Names", "Full names", "Full Names", "Name"
│  ├─ Email: "Email", "E-mail", "EMAIL"
│  └─ Score: "Result", "Score", "Percentage"
├─ Extracts ONLY these 3 columns (ignores question data)
├─ Normalizes emails: .lower(), .strip()
├─ Parses scores: removes %, converts to numeric
└─ Creates: 5 dataframes with [Name, Email, Score]

STEP 3: MERGE ON EMAIL
├─ Uses email as PRIMARY KEY (case-insensitive)
├─ Outer join: keeps all participants from all tests
└─ Result: One table with all scores aligned

STEP 4: CLEAN & SORT
├─ Remove duplicate emails (keep first)
├─ Sort A-Z by Full Name (case-insensitive)
└─ Result: 98 unique participants, alphabetically sorted

STEP 5: FORMAT SCORES
├─ Convert numbers to percentages: 73.1 → "73.1%"
├─ Mark missing data as blank (not 0, not NaN)
└─ Result: Clean, readable format

STEP 6: EXPORT TO XLSX
├─ Create new Excel workbook
├─ Add header row with proper formatting
├─ Add all participants (1 row each)
├─ Apply colors:
│  ├─ Test 1: White
│  ├─ Test 2: Sky Blue (#87CEEB)
│  ├─ Test 3: Yellow (#FFFF00)
│  ├─ Test 4: Army Green (#556B2F)
│  ├─ Test 5: Red (#FF0000)
└─ Save: output/Consolidated_Results.xlsx
```

### Output Format
```
Consolidated_Results.xlsx

Structure:
┌────────────────────────────────────────────────────────────────────────┐
│ Full Name              | Email              | Test 1 | Test 2 | Test 3 │
├────────────────────────────────────────────────────────────────────────┤
│ Abdulhamid A Bala      | abdulhamid@...     | 73.1%  | 72.0%  | 80.0%  │
│ Abdullahi Gambo        | gamboabdullahi@... | [blank]| 52.0%  | [blank]│
│ Abdulsalam Ummi A...   | ummulkhaira@...    | [blank]| 80.0%  | 80.0%  │
│ Abdurrahman bin U...   | abdurrahman@...    | 73.1%  | 76.0%  | 62.5%  │
│ ...                    | ...                | ...    | ...    | ...    │
└────────────────────────────────────────────────────────────────────────┘

Properties:
- 98 rows (unique participants) + 1 header
- 7 columns (Name, Email, Test1%, Test2%, Test3%, Test4%, Test5%)
- Color-coded by test
- Sorted alphabetically by name
- Missing data shown as blank (not 0)
- Ready for analysis/reporting
```

---

## EXAMPLE OUTPUT (First 5 Participants)

```
Full Name                      | Email                           | Test 1 | Test 2 | Test 3 | Test 4 | Test 5
---|---|---|---|---|---|---
Abdulhamid Abubakar Bala      | abdulhamidabubakar23@gmail.com | 73.1%  | 72.0%  | 80.0%  | 73.3%  | 73.7%
Abdullahi Gambo                | gamboabdullahi@gmail.com        |        | 52.0%  |        | 50.0%  | 68.4%
Abdulsalam Ummi Abdullahi     | Ummulkhaira35@gmail.com         |        | 80.0%  | 80.0%  |        | 84.2%
Abdurrahman bin Usman         | abdurrahmanbinuthman@gmail.com | 73.1%  | 76.0%  | 62.5%  | 63.3%  | 89.5%
Abiodun Omoniyi AMUSAN        | biodunamusan4@yahoo.com         | 84.6%  | 92.0%  | 77.5%  | 66.7%  | 94.7%
```

---

## KEY FEATURES

### ✅ Handles All Real-World Variations
```
✓ Different column names across tests
✓ Column name inconsistencies (Full Names vs Full names vs Name)
✓ Email variations (case-insensitive matching)
✓ Different # of questions per test
✓ Different # of participants per test
✓ Missing participants (blank values preserved)
✓ Score format variations (e.g., "73.1%", "0.731", etc.)
```

### ✅ Reliable Email Matching
```
✓ Case-insensitive: "Alice@TEST.com" = "alice@test.com"
✓ Whitespace handled: " alice@test.com " → "alice@test.com"
✓ Email is PRIMARY KEY (not name)
✓ One person with same name but different emails → Different rows
✓ Same email but different name spelling → Matched correctly
```

### ✅ Data Integrity
```
✓ No participant lost
✓ No score corruption
✓ No duplicates in output (deduplicated by email)
✓ Missing data preserved (blank cells, not 0 or N/A)
✓ All 5 tests preserved (no data excluded)
```

### ✅ Professional Output
```
✓ Color-coded by test (visual verification aid)
✓ Alphabetically sorted (A-Z by participant name)
✓ Properly formatted (headers, percentages, borders)
✓ Clean, readable layout
✓ Ready for reporting/analysis/printing
```

---

## TROUBLESHOOTING

### Issue: "Could not find all required test files"
**Solution:** Ensure TEST_1 to TEST_5 files are in the `input/` folder
```bash
ls -la input/
# Should show: TEST_1_*.xlsx, TEST_2_*.xlsx, TEST_3_*.xlsx, TEST_4_*.xlsx, TEST_5_*.xlsx
```

### Issue: "Could not find name/email/score column"
**Solution:** Check column names in your test files
```python
import pandas as pd
df = pd.read_excel('input/TEST_1_*.xlsx')
print(df.columns)
# Look for: "Full Names", "Full names", "Name" (for name)
# Look for: "Email", "EMAIL", "E-mail" (for email)
# Look for: "Result", "Score", "Percentage" (for score)
```

### Issue: Output file not created
**Solution:** Check the execution log
```bash
cat compiler_execution.log
# Look for ERROR messages
```

### Issue: Missing data shown as "NaN" instead of blank
**Solution:** The bot correctly handles missing data - open the file in Excel to see properly formatted blanks

### Issue: Scores not formatted as percentages
**Solution:** The bot formats scores as "73.1%" - if they appear as numbers, check your Excel number formatting

---

## LOGS AND DEBUGGING

### Check Execution Log
```bash
# View the compilation log
cat compiler_execution.log

# Look for key information:
# - Which files were found
# - How many participants in each test
# - Any errors or warnings
# - Final statistics
```

### Understanding Log Output
```
2026-01-31 14:32:10 - INFO - ResultsCompiler initialized
2026-01-31 14:32:10 - INFO - Searching for test files...
2026-01-31 14:32:10 - INFO - Found Test 1: TEST_1_Obstetrics___Gynecology_JANUARY_2026.xlsx
2026-01-31 14:32:10 - INFO - Found Test 2: TEST_2_Obstetrics___Gynae_JANUARY_2026.xlsx
...
2026-01-31 14:32:11 - INFO - ✓ Extracted 89 participants from Test 1
2026-01-31 14:32:11 - INFO - ✓ Extracted 92 participants from Test 2
...
2026-01-31 14:32:12 - INFO - ✓ Merge complete: 98 unique participants
2026-01-31 14:32:12 - INFO - ✓ Sorted 98 participants alphabetically
2026-01-31 14:32:12 - INFO - ✓ Exported to output/Consolidated_Results.xlsx
2026-01-31 14:32:12 - INFO - ✓ COMPILATION COMPLETE in 2.34 seconds
```

---

## VERIFICATION CHECKLIST

After running the bot, verify the output:

### File Exists
- [ ] output/Consolidated_Results.xlsx exists
- [ ] File size is reasonable (50 KB - 1 MB typical)
- [ ] File opens without errors in Excel/LibreOffice

### Data Completeness
- [ ] 98 unique participants (or your expected count)
- [ ] All 7 columns present (Name, Email, Test1-5)
- [ ] All rows have data (no truncation)

### Data Quality
- [ ] Participants sorted A-Z by name
- [ ] Email addresses visible and correctly matched
- [ ] Scores shown as percentages (73.1%, 88.0%, etc.)
- [ ] Missing data shown as blank cells (not 0, not N/A)

### Color Coding
- [ ] Test 1 column background: White
- [ ] Test 2 column background: Sky Blue
- [ ] Test 3 column background: Yellow
- [ ] Test 4 column background: Army Green
- [ ] Test 5 column background: Red

### No Data Loss
- [ ] Total rows = sum of all test participants (with deduplication)
- [ ] All email domains represented
- [ ] No truncation of names or emails

---

## ADVANCED USAGE

### Custom Input/Output Folders
```bash
python results_compiler_bot.py /custom/input/path /custom/output/path
```

### Run from Python Script
```python
from results_compiler_bot import ResultsCompiler

compiler = ResultsCompiler(
    input_folder='my_tests',
    output_folder='my_results'
)

if compiler.run():
    print("Compilation successful!")
    print(f"Results saved to: {compiler.output_folder}")
else:
    print("Compilation failed - check compiler_execution.log")
```

### Automate with Cron (Linux/Mac)
```bash
# Add to crontab to run daily at 2 AM
0 2 * * * cd /path/to/project && python results_compiler_bot.py
```

### Automate with Task Scheduler (Windows)
1. Create batch file `run_compiler.bat`:
```batch
@echo off
cd C:\path\to\project
python results_compiler_bot.py
```
2. Create scheduled task in Windows Task Scheduler
3. Set to run daily at your preferred time

---

## SUPPORT & DOCUMENTATION

- **Quick Start:** This file (BOT_QUICK_START_GUIDE.md)
- **Technical Details:** Input_vs_Output_Structure_Analysis.md
- **Testing Guide:** Test_Execution_Guide.md
- **Security Testing:** Security_Attack_Vector_Testing.md
- **Test Plan:** MLJResultsCompiler_Test_Plan.md
- **Automated Tests:** mlj_test_automation_suite.py

---

**Status:** ✅ Production Ready  
**Last Updated:** January 31, 2026  
**Questions or Issues?** Check compiler_execution.log for detailed error messages
