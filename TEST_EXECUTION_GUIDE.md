# MLJResultsCompiler - Test Execution Guide
**Date:** January 31, 2026  
**Purpose:** Step-by-step instructions for executing the comprehensive test plan

---

## QUICK START (5 minutes)

### Run Automated Tests
```bash
python mlj_test_automation_suite.py
```

Expected output:
- 18 automated tests executed
- JSON report: `test_results.json`
- Pass rate should be 100% for basic functionality

---

## FULL TEST EXECUTION (2-3 hours)

### Phase 1: Setup (10 minutes)

**Step 1: Prepare Test Data Directory**
```bash
mkdir test_data
cd test_data
```

**Step 2: Create 5 Sample Test Files**
Use your actual SurveyHeart exports or create samples:

**Test 1.xlsx** (Base file - no color):
```
Full Name          | Email              | Score
Alice Johnson      | alice@company.com  | 85
Bob Smith          | bob@company.com    | 92
Charlie Brown      | charlie@company.com| 78
David Wilson       | david@company.com  | 88
Emily Davis        | emily@company.com  | 91
```

**Test 2.xlsx** (Sky Blue #87CEEB):
```
Full Name          | Email              | Score
Alice Johnson      | alice@company.com  | 88
Bob Smith          | bob@company.com    | 85
Charlie Brown      | charlie@company.com| 82
Frank Thomas       | frank@company.com  | 94
Emily Davis        | emily@company.com  | 89
```

**Test 3.xlsx** (Yellow #FFFF00):
```
Full Name          | Email              | Score
Alice Johnson      | alice@company.com  | 91
Bob Smith          | bob@company.com    | 93
Charlie Brown      | charlie@company.com| 75
Grace Lee          | grace@company.com  | 87
Emily Davis        | emily@company.com  | 92
```

**Test 4.xlsx** (Army Green #556B2F):
```
Full Name          | Email              | Score
Alice Johnson      | alice@company.com  | 79
Bob Smith          | bob@company.com    | 88
Charlie Brown      | charlie@company.com| 80
Henry Martin       | henry@company.com  | 85
Emily Davis        | emily@company.com  | 86
```

**Test 5.xlsx** (Red #FF0000):
```
Full Name          | Email              | Score
Alice Johnson      | alice@company.com  | 84
Bob Smith          | bob@company.com    | 90
Charlie Brown      | charlie@company.com| 81
Iris Chen          | iris@company.com   | 88
Emily Davis        | emily@company.com  | 93
```

---

### Phase 2: Manual Validation Tests A-D (30 minutes)

#### Test A: File Format Validation (5 minutes)

**Objective:** Verify all files are valid XLSX format

**Steps:**
1. Open Test 1.xlsx in Excel/LibreOffice
2. Open Test 2.xlsx in Excel/LibreOffice
3. Verify all files open without errors
4. Check each file has columns: Full Name, Email, Score
5. Verify no read-lock errors

**Pass Criteria:**
- [ ] All 5 files open without errors
- [ ] All files readable and not corrupted
- [ ] Required columns present in all files

**Notes:**
```
If any file fails to open:
1. Try opening in different application
2. Check file permissions
3. Verify file not currently locked by another process
```

---

#### Test B: Color Formatting Verification (10 minutes)

**Objective:** Verify color coding applied correctly to each test

**Steps:**
1. Open Test 1.xlsx - verify WHITE background (or no color)
2. Open Test 2.xlsx - verify SKY BLUE background (#87CEEB)
3. Open Test 3.xlsx - verify YELLOW background (#FFFF00)
4. Open Test 4.xlsx - verify ARMY GREEN background (#556B2F)
5. Open Test 5.xlsx - verify RED background (#FF0000)

**For each test file:**
- Check ALL data rows have color applied
- Verify header row is clear (usually no color)
- Confirm color is consistent across all rows
- Verify color doesn't obscure text (readable)

**Pass Criteria:**
- [ ] Test 1: White/No color
- [ ] Test 2: Sky Blue (#87CEEB)
- [ ] Test 3: Yellow (#FFFF00)
- [ ] Test 4: Army Green (#556B2F)
- [ ] Test 5: Red (#FF0000)
- [ ] All data rows colored consistently
- [ ] Text remains readable

**Notes:**
```
Color hex codes:
- Test 1: None or #FFFFFF
- Test 2: #87CEEB (Sky Blue)
- Test 3: #FFFF00 (Yellow)
- Test 4: #556B2F (Army Green)
- Test 5: #FF0000 (Red)
```

---

#### Test C: Column Extraction & Alphabetical Sorting (10 minutes)

**Objective:** Verify columns extracted and sorted correctly

**Manual Steps:**
1. Open Test 1.xlsx
2. Sort by "Full Name" (A → Z)
3. Verify order is:
   ```
   1. Alice Johnson
   2. Bob Smith
   3. Charlie Brown
   4. David Wilson
   5. Emily Davis
   ```
4. Repeat for Tests 2-5
5. Note any duplicates or unusual entries

**Pass Criteria:**
- [ ] All participants present (5 in each test)
- [ ] Alphabetical order correct (A-Z)
- [ ] No names missing
- [ ] No data corruption

**Notes:**
```
If sorting fails:
- Check for leading/trailing spaces
- Verify no special characters breaking sort
- Ensure no merged cells in data area
```

---

#### Test D: Email Format & Matching (5 minutes)

**Objective:** Verify email format valid and matching-ready

**Manual Steps:**
1. Open Test 1.xlsx
2. Check all emails in column B are valid format: user@domain.com
3. Note exact email for each participant
4. Open Test 2.xlsx
5. Compare emails in Test 2 to Test 1
6. Document any variations:
   - Case differences (ALICE@test.com vs alice@test.com)
   - Whitespace issues (leading/trailing spaces)
   - Format changes (@company.com vs @company.us)

**Pass Criteria:**
- [ ] All emails valid format (user@domain.com)
- [ ] No blank email cells
- [ ] No invalid characters
- [ ] Case variations noted for later matching

**Sample Email Validation:**
```
Valid emails:
- alice@company.com ✓
- bob.smith@company.com ✓
- emily_davis@company.co.uk ✓

Invalid emails:
- alice@company (no TLD) ✗
- @company.com (no user) ✗
- alice@.com (no domain) ✗
- alice company.com (no @) ✗
```

---

### Phase 3: Automated Test Execution (10 minutes)

**Step 1: Run Full Automation Suite**
```bash
python mlj_test_automation_suite.py
```

**Expected Output:**
```
MLJResultsCompiler - Test Automation Suite
==================================================

Section 2: Success Path Tests
[PASS] 2.1: Happy Path - All Participants
[PASS] 2.2: Missing Data - One Participant Missing
[PASS] 2.3: New Participant in Test 2-5
[PASS] 2.4: Email Case Insensitivity
[PASS] 2.5: Alphabetical Sorting

Section 3: Failure Scenario Tests
[PASS] 3.1: Corrupted File Handling
[PASS] 3.2: Missing Required Columns
[PASS] 3.3: Invalid Score Validation
[PASS] 3.4: Invalid Email Format
[PASS] 3.5: Duplicate Names - Different Emails
[PASS] 3.6: Duplicate Email - Different Names

Section 4: Edge Case Tests
[PASS] 4.1: Special Characters in Names
[PASS] 4.2: Very Long Names/Emails
[PASS] 4.3: No Overlap - All Different Participants
[PASS] 4.4: Blank Rows Handling
[PASS] 4.5: Score Zero Handling
[PASS] 4.6: Whitespace in Emails

Section 5: Attack Vector Tests
[PASS] 5.1: Path Traversal Prevention
[PASS] 5.2: Formula Injection Prevention
[PASS] 5.3: XLSM Macro File Handling
[PASS] 5.4: Non-UTF8 Encoding Handling
[PASS] 5.5: Large Cell Values Handling
[PASS] 5.6: Concurrent Access Safety

==================================================
Total Tests: 21
Passed: 21
Failed: 0
Pass Rate: 100.0%
==================================================

Report saved to: test_results.json
```

**Step 2: Review Test Report**
```bash
cat test_results.json
```

**Step 3: Verify Results**
- [ ] All 21 tests PASS
- [ ] Pass rate = 100%
- [ ] No failures detected

---

### Phase 4: Edge Case Testing (20 minutes)

#### Test 4A: Whitespace Handling
```
Create Test X.xlsx with:
- Emails with leading spaces: " alice@test.com"
- Emails with trailing spaces: "bob@test.com "
- Names with double spaces: "John  Smith"

Expected: Should match " alice@test.com" with "alice@test.com"
```

#### Test 4B: Special Characters
```
Create Test X.xlsx with:
- José García
- François Müller
- Mary-Jane Watson
- O'Connor
- 中文 Name (Chinese)
- Иван (Russian)

Expected: All names preserved exactly in output
```

#### Test 4C: Large Dataset
```
Create Test X.xlsx with 1,000+ rows:
- 1,000 participants
- Varying overlap (50%, 25%, 75%)
- Random order

Run compilation:
- Should complete in <30 seconds
- All participants in output
- No data loss
- Memory usage reasonable
```

#### Test 4D: Score Edge Cases
```
Test values:
- 0% (valid, minimum)
- 100% (valid, maximum)
- -5% (invalid, below minimum)
- 105% (invalid, above maximum)
- 99.5% (valid, decimal)
- "N/A" (invalid, text)
- "" (blank, missing)

Expected handling: Validate and report invalid values
```

---

### Phase 5: Failure Scenario Testing (15 minutes)

#### Test 3A: Corrupted File
```
1. Create dummy file named "Test_Corrupted.xlsx"
2. Open in text editor, replace content with: "CORRUPTED"
3. Save file
4. Try to run compilation with this file
5. Verify: Clear error message, process halts gracefully
```

**Expected Error Message:**
```
ERROR: Test_Corrupted.xlsx is corrupted or invalid
Cannot read XLSX file. Please verify file is not corrupted.
Try downloading file again from SurveyHeart.
```

#### Test 3B: Missing Required Column
```
1. Create Test X.xlsx with only Name and Score
2. Delete Email column entirely
3. Run compilation
4. Verify: Process stops, suggests "Email" as required
```

**Expected Error Message:**
```
ERROR: Required column missing
Column 'Email' not found in Test X.xlsx
Expected columns: Full Name, Email, Score
Aliases accepted: E-mail, Email Address, E_Mail
```

#### Test 3C: Invalid Email Addresses
```
Create Test X.xlsx with:
- notanemail (no @ symbol)
- @example.com (no user)
- user@ (no domain)
- user@example.c (incomplete TLD)

Run compilation:
Verify: Warning logged, process continues, invalid emails flagged
```

#### Test 3D: Invalid Score Values
```
Create Test X.xlsx with:
- Score: "N/A" (text)
- Score: "-10" (negative)
- Score: "150" (over 100)
- Score: "" (blank)

Run compilation:
Verify: Warnings logged, handled appropriately
```

---

### Phase 6: Stress Testing (10 minutes)

#### Test 6A: Large Participant Count
```bash
# Create 5 test files with 10,000 participants each
# Random emails (some overlap, some unique)

# Measure:
- Start time: [TIME]
- End time: [TIME]
- Total duration: [SECONDS]
- Memory usage: [MB]
- Output file size: [MB]

Expected:
- Complete in < 30 seconds
- Output opens without lag
- All participants in output
```

#### Test 6B: Large File Size
```bash
# Create test files with:
- Very long names (255+ characters)
- Very long emails (100+ characters)
- Long descriptions/notes in score cells
- Total file size > 10MB

Expected:
- Files open without lag
- Content preserved completely
- No truncation
- No memory overflow
```

#### Test 6C: Complex Character Sets
```bash
# Create test with:
- Latin (English, French, Spanish): José, François, Müller
- Cyrillic (Russian, Bulgarian): Иван, Борис, Марья
- Greek: Αλέξανδρος, Σοφία
- CJK (Chinese, Japanese, Korean): 中文, 日本語, 한글
- Arabic: العربية, فارسی
- Emoji: 😀, 🎯, ✓

Expected:
- All characters preserved
- No encoding issues
- Sorting works (stable)
```

---

## TROUBLESHOOTING

### Issue: Test Files Not Opening
**Solution:**
1. Verify file format is .xlsx (not .xls or .csv)
2. Check file permissions (not read-only)
3. Verify file not locked by another process
4. Try opening in different application (Excel, LibreOffice, Google Sheets)
5. Re-download from SurveyHeart if persistently corrupted

### Issue: Color Not Applied or Lost
**Solution:**
1. Verify color applied to DATA rows (not just header)
2. Check that entire row colored (not just score column)
3. Verify color format is RGB hex (#87CEEB) not HSL
4. Check export format (XLSX preserves colors, CSV/PDF may not)

### Issue: Email Matching Fails
**Solution:**
1. Check for leading/trailing whitespace in emails
2. Verify case consistency (should be case-insensitive)
3. Look for special characters (+ signs, underscores)
4. Check domain variations (company.com vs company.us)
5. Consider email aliases (john+filter@gmail.com)

### Issue: Performance Degradation
**Solution:**
1. Check available disk space
2. Close other applications
3. Verify RAM available (recommend 4GB+)
4. Check system CPU usage
5. Consider splitting large files into batches

### Issue: Data Loss or Corruption
**Solution:**
1. STOP processing immediately
2. Do NOT overwrite output files
3. Check source files are still intact
4. Review error logs for what went wrong
5. Contact support with test_consolidation.log

---

## SUCCESS CRITERIA SUMMARY

### All Tests Must Pass For Production Release

**Manual Tests (Phase 2):**
- [ ] Test A: All 5 files valid XLSX format
- [ ] Test B: Color formatting correct for all 5 tests
- [ ] Test C: Alphabetical sorting correct
- [ ] Test D: Email format valid and matching-ready

**Automated Tests (Phase 3):**
- [ ] All 21 automated tests PASS
- [ ] Pass rate = 100%
- [ ] No critical failures

**Edge Cases (Phase 4):**
- [ ] Whitespace handled correctly
- [ ] Special characters preserved
- [ ] Large datasets process correctly
- [ ] Score edge cases handled

**Failure Scenarios (Phase 5):**
- [ ] Corrupted files detected gracefully
- [ ] Missing columns identified
- [ ] Invalid data reported clearly
- [ ] Process doesn't crash

**Stress Testing (Phase 6):**
- [ ] Large datasets complete in < 30 seconds
- [ ] Memory usage reasonable
- [ ] Complex characters handled
- [ ] No data loss

---

## TEST EXECUTION LOG TEMPLATE

```
TEST EXECUTION LOG
==================

Session Date: _______________
Tester Name: ________________
Email: ______________________
Test Environment: Windows / Mac / Linux

PHASE 1: SETUP
Status: [ ] Complete
Notes: _______________________________________________________

PHASE 2: MANUAL VALIDATION
Test A (File Format):
  Status: [ ] Pass [ ] Fail
  Notes: _________________________________________________
  
Test B (Color Formatting):
  Status: [ ] Pass [ ] Fail
  Notes: _________________________________________________
  
Test C (Sorting):
  Status: [ ] Pass [ ] Fail
  Notes: _________________________________________________
  
Test D (Email Format):
  Status: [ ] Pass [ ] Fail
  Notes: _________________________________________________

PHASE 3: AUTOMATED TESTS
Command run: python mlj_test_automation_suite.py
Start time: ________________
End time: ________________
Total duration: ________________

Results:
  Total tests: _____
  Passed: _____
  Failed: _____
  Pass rate: _____% 

Status: [ ] All Pass [ ] Some Failed

PHASE 4: EDGE CASES
4A (Whitespace): [ ] Pass [ ] Fail
4B (Special chars): [ ] Pass [ ] Fail
4C (Large dataset): [ ] Pass [ ] Fail
4D (Score edge cases): [ ] Pass [ ] Fail

PHASE 5: FAILURE SCENARIOS
3A (Corrupted file): [ ] Pass [ ] Fail
3B (Missing column): [ ] Pass [ ] Fail
3C (Invalid email): [ ] Pass [ ] Fail
3D (Invalid score): [ ] Pass [ ] Fail

PHASE 6: STRESS TESTING
6A (Large participant count): [ ] Pass [ ] Fail
6B (Large file size): [ ] Pass [ ] Fail
6C (Complex characters): [ ] Pass [ ] Fail

OVERALL RESULT
==============
[ ] All Tests PASS - Ready for Production
[ ] Some Tests FAILED - See notes below

Critical Issues Found:
1. ___________________________________________________________
2. ___________________________________________________________
3. ___________________________________________________________

Recommendations:
1. ___________________________________________________________
2. ___________________________________________________________
3. ___________________________________________________________

Sign-off:
Tester: ______________________  Date: ___________
```

---

## NEXT STEPS

1. **Run Phase 1-3 (45 min total)**
   - Setup test files
   - Run manual validation tests
   - Run automated test suite

2. **Document Results**
   - Record pass/fail for each test
   - Note any anomalies
   - Save test_results.json

3. **If All Pass:**
   - Move to Phase 4-6 (optional, for robustness)
   - Document success
   - Ready for production use

4. **If Any Fail:**
   - Document which test failed
   - Record error messages
   - Review troubleshooting section
   - Retry after fixes

5. **Generate Final Report**
   - Use TEST_EXECUTION_LOG_TEMPLATE
   - Attach test_results.json
   - Send to project stakeholders

---

**Test Guide Version:** 1.0  
**Last Updated:** January 31, 2026  
**Status:** Ready to Execute
