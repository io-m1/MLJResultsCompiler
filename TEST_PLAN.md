# MLJResultsCompiler - Comprehensive Test & Attack Plan
**Date:** January 31, 2026  
**Purpose:** Failproof testing of the results compilation workflow with systematic validation

---

## EXECUTIVE SUMMARY

Your workflow automates consolidation of 5 test result sheets from SurveyHeart, using:
- **Color coding** as visual verification markers (Test 1-5 different colors)
- **Email matching** for participant alignment (primary key)
- **Transposition** to merge test results into one row per participant
- **Alphabetical sorting** for consistency checks

This test plan covers **Success Paths**, **Failure Scenarios**, **Edge Cases**, and **Attack Vectors** to ensure 100% data integrity.

---

## SECTION 1: WORKFLOW BREAKDOWN & VALIDATION POINTS

### Step 1: Input Data (5 XLSX Files from SurveyHeart)
**Expected Format:**
- Files contain: Full Name, Email, Score (%)
- Tests 1-5 in separate files
- Column names may vary (Name, Participant, E-mail, Result, Percentage)

**Validation Points:**
- ✓ File format is valid XLSX (not CSV, XLS, or corrupted)
- ✓ Required columns exist (name + email + score)
- ✓ Score values are numeric and in valid range (0-100%)
- ✓ Email values are in valid format
- ✓ No completely blank rows in data
- ✓ File is not read-locked or corrupted

---

### Step 2: Color Formatting
**Current Manual Process:**
- Test 1: White (no color)
- Test 2: Sky Blue (#87CEEB)
- Test 3: Yellow (#FFFF00)
- Test 4: Army Green (#556B2F)
- Test 5: Red (#FF0000)

**Validation Points:**
- ✓ Colors applied consistently to ALL data rows
- ✓ Colors preserved during file operations
- ✓ Color information aids in verification

---

### Step 3: Column Extraction & Alphabetical Sorting
**Process:**
1. Extract Full Name, Email, Score from each test file
2. Sort each test's data alphabetically by Full Name
3. Maintain color coding during sorting

**Validation Points:**
- ✓ All participants from all 5 tests are extracted
- ✓ Sorting is case-insensitive and alphabetically correct
- ✓ No data loss during extraction
- ✓ Duplicate names handled (email used as tiebreaker)
- ✓ Special characters don't break sorting

---

### Step 4: Transposition & Email Matching
**Process:**
1. Test 2-5 participants matched to Test 1 by email
2. Test 2-5 scores added as new columns to matching Test 1 row
3. Participants in Tests 2-5 but not Test 1 are appended
4. Missing test scores show as blank cells
5. Color markers identify matches and missing data

**Validation Points:**
- ✓ Email matching is case-insensitive
- ✓ Whitespace in emails trimmed before matching
- ✓ All Test 2-5 participants appear in final output
- ✓ Participants missing from specific tests show blank cells (not 0)
- ✓ Color coding aids verification visually

---

### Step 5: Final Output
**Expected Format:**
```
Name | Email | Test1 | Test2 | Test3 | Test4 | Test5
```

**Validation Points:**
- ✓ Exactly one row per unique email (primary key)
- ✓ All scores retained correctly
- ✓ Missing scores shown as blank
- ✓ No participant lost or duplicated
- ✓ Report clean and ready for analysis

---

## SECTION 2: SUCCESS PATH TEST SCENARIOS

### Test 2.1: Happy Path - All Participants in All Tests
**Setup:**
```
Test 1: Alice (85), Bob (92), Charlie (78)
Tests 2-5: Same participants, same emails, different scores
```

**Expected Result:**
- 3 rows in output (one per person)
- All 5 scores present for each person
- Correct scores matched by email
- Alphabetical order: Alice, Bob, Charlie

**Pass Criteria:**
- ✓ Correct row count (3)
- ✓ All scores present
- ✓ Correct values
- ✓ Alphabetical order maintained
- ✓ No data corruption

---

### Test 2.2: Participant Missing from One Test
**Setup:**
```
Test 1: Alice (85), Bob (92), Charlie (78)
Test 2: Alice (88), Charlie (82) [Bob MISSING]
Tests 3-5: Complete data
```

**Expected Result:**
```
Alice | alice@test.com | 85 | 88 | ... (all scores)
Bob   | bob@test.com   | 92 | [BLANK] | ... (blank for Test 2)
Charlie | charlie@test.com | 78 | 82 | ...
```

**Pass Criteria:**
- ✓ Bob's Test 2 cell is BLANK (not 0, not "N/A")
- ✓ Bob still appears in output
- ✓ Color coding shows Test 2 as incomplete
- ✓ No errors thrown

---

### Test 2.3: Participant in Test 2-5 But Not Test 1
**Setup:**
```
Test 1: Alice (85), Bob (92)
Tests 2-5: Alice, Bob, and David (not in Test 1)
```

**Expected Result:**
```
Alice | alice@test.com | 85 | 88 | ... (all scores)
Bob   | bob@test.com   | 92 | 85 | ...
David | david@test.com | [BLANK] | 94 | ... (blank for Test 1)
```

**Pass Criteria:**
- ✓ David appears in output (not lost)
- ✓ David's Test 1 is BLANK
- ✓ David's Tests 2-5 have correct scores
- ✓ Alphabetical order maintained

---

### Test 2.4: Email Matching - Case Insensitivity
**Setup:**
```
Test 1: alice@TEST.com (85)
Test 2: ALICE@test.com (88)
(Same person, different email case)
```

**Expected Result:**
```
Alice | alice@test.com | 85 | 88
```

**Pass Criteria:**
- ✓ Matched correctly (1 row, not 2)
- ✓ Email normalized to consistent case
- ✓ Scores correctly aligned

---

### Test 2.5: Alphabetical Sorting Correctness
**Setup:**
```
Unordered: Zoe, Alice, Bob, Charlie, David, Emily, Frank, Grace
```

**Expected Result:**
```
Alphabetical order A-Z:
1. Alice
2. Bob
3. Charlie
4. David
5. Emily
6. Frank
7. Grace
8. Zoe
```

**Pass Criteria:**
- ✓ Names sorted case-insensitive A-Z
- ✓ Consistent throughout
- ✓ No sorting breaks

---

## SECTION 3: FAILURE SCENARIOS

### Test 3.1: Corrupted Input File
**Setup:**
- One of 5 XLSX files is corrupted/unreadable

**Expected Behavior:**
- ✓ Clear error message indicating which test file
- ✓ Process halts gracefully (doesn't crash)
- ✓ Error logged with timestamp
- ✓ User instructed to re-download

**Test This:**
- Try to process corrupted XLSX
- Verify error handling
- Check log file

---

### Test 3.2: Missing Required Columns
**Setup:**
- Test 1 XLSX missing Email column

**Expected Behavior:**
- ✓ Error: "Test 1 missing required column: Email"
- ✓ Suggests column name aliases
- ✓ Process stops before merge attempt

**Test This:**
- Create XLSX without Email column
- Run compilation
- Verify clear error message

---

### Test 3.3: Invalid Score Values
**Setup:**
```
Test 2: Score = "N/A", "-10", "150%", "" (empty)
```

**Expected Behavior:**
- ✓ Validation warning logged
- ✓ Process indicates which scores failed
- ✓ User can review and fix
- ✓ Compilation doesn't crash

**Test This:**
- Create test files with invalid scores
- Verify graceful error handling

---

### Test 3.4: Invalid Email Addresses
**Setup:**
```
Test 3: Email = "notanemail", "@example.com", "user@"
```

**Expected Behavior:**
- ✓ Validation warning logged
- ✓ Participant still processed (email flagged)
- ✓ Matching may fail but doesn't crash

---

### Test 3.5: Duplicate Names (Different Emails)
**Setup:**
```
John Smith | john.smith@test.com | 85
John Smith | john.smith.2@test.com | 92
(Same name, different emails - 2 different people)
```

**Expected Behavior:**
- ✓ Treated as 2 different participants
- ✓ Both appear in output
- ✓ Email is primary key (not name)

---

### Test 3.6: Duplicate Email (Different Names)
**Setup:**
```
Test 1: John Smith | john@test.com | 85
Test 2: Jon Smith | john@test.com | 88
(Same email, name spelling differs)
```

**Expected Behavior:**
- ✓ Matched by email (same person)
- ✓ One row in output
- ✓ Name normalized or user warned

---

## SECTION 4: EDGE CASES & BOUNDARY TESTS

### Test 4.1: Special Characters in Names
**Setup:**
```
José García, François Müller, Mary-Jane Watson, O'Connor, John3
```

**Expected Behavior:**
- ✓ All names preserved exactly
- ✓ Sorting works correctly
- ✓ No data corruption

---

### Test 4.2: Very Long Names/Emails
**Setup:**
```
Name: "Alexander Christopher Montgomery-Fitzgerald III"
Email: "alexander.christopher.montgomery@longemailprovider.com"
```

**Expected Behavior:**
- ✓ Names and emails fully preserved
- ✓ No truncation in output
- ✓ XLSX formatting works

---

### Test 4.3: All Tests Have Different Participants (No Overlap)
**Setup:**
```
Test 1: Alice, Bob, Charlie
Test 2: David, Emily, Frank
Test 3: Grace, Henry, Iris
Test 4: Jack, Kate, Leo
Test 5: Mona, Noah, Oscar
(No overlap)
```

**Expected Behavior:**
- ✓ Output has 15 rows (all participants)
- ✓ Each person has only 1 score filled
- ✓ Other cells blank
- ✓ No errors

---

### Test 4.4: Only Test 1 Has Data (Tests 2-5 Empty)
**Setup:**
```
Test 1: Normal data (10 participants)
Tests 2-5: Empty or missing
```

**Expected Behavior:**
- ✓ Output = Test 1 + 4 empty columns
- ✓ No errors
- ✓ Handles gracefully

---

### Test 4.5: Extreme Data Volumes
**Setup:**
```
Test 1: 10,000 participants
Tests 2-5: 10,000 participants
Total: ~15,000-50,000 rows after merge
```

**Expected Behavior:**
- ✓ Process completes in <30 seconds
- ✓ No memory errors
- ✓ Output opens without lag
- ✓ Sorting still correct

---

### Test 4.6: Whitespace in Emails
**Setup:**
```
Test 1: " alice@test.com" (leading space)
Test 2: "alice@test.com " (trailing space)
```

**Expected Behavior:**
- ✓ Trimmed before matching
- ✓ Recognized as same person
- ✓ One row in output
- ✓ Email stored without spaces

---

### Test 4.7: Blank Rows in Input Files
**Setup:**
```
Row 1: Alice | alice@test.com | 85
Row 2: [blank]
Row 3: Bob | bob@test.com | 92
Row 4: [blank]
```

**Expected Behavior:**
- ✓ Blank rows skipped
- ✓ Only valid data processed
- ✓ Output has 2 rows (Alice, Bob)
- ✓ No errors

---

### Test 4.8: Score = 0%
**Setup:**
```
Test 2: Alice | alice@test.com | 0
(Valid score of zero)
```

**Expected Behavior:**
- ✓ 0 is treated as valid score
- ✓ Appears in output as "0" (not blank)
- ✓ Distinct from blank cells

---

## SECTION 5: ATTACK VECTORS & MALICIOUS INPUTS

### Test 5.1: Path Traversal in File Names
**Attack:**
```
Filenames: "test ../../../etc/passwd.xlsx"
```

**Defense Expected:**
- ✓ File paths sanitized
- ✓ No path traversal possible
- ✓ Invalid characters rejected

---

### Test 5.2: Formula Injection
**Attack:**
```
Name: =cmd|'/c calc'!A1
Email: john@test.com'--
Score: =1+1 (formula)
```

**Defense Expected:**
- ✓ Values treated as data, not formulas
- ✓ Formulas exported as text
- ✓ No unintended execution

---

### Test 5.3: Extremely Large Cell Values
**Attack:**
```
Name cell: 1MB of text
```

**Defense Expected:**
- ✓ Cells read without buffer overflow
- ✓ Content preserved or truncated with warning
- ✓ Memory safe

---

### Test 5.4: Non-UTF8 Encoding
**Attack:**
```
File with Cyrillic, Arabic, Chinese characters
```

**Defense Expected:**
- ✓ Encoding auto-detected or converted
- ✓ Characters preserved
- ✓ No corruption

---

### Test 5.5: Macro-Enabled Files (.xlsm)
**Attack:**
```
XLSM file with embedded macros
```

**Defense Expected:**
- ✓ Macros not executed
- ✓ File treated as data only
- ✓ Safe handling

---

### Test 5.6: Concurrent File Access
**Attack:**
```
Try to compile while:
- User editing input file
- File locked by another process
```

**Defense Expected:**
- ✓ File locking handled gracefully
- ✓ Error message: "File in use, please close and retry"
- ✓ No data corruption

---

## SECTION 6: VALIDATION CHECKLIST

### Pre-Compilation Checks
```
☐ All 5 test XLSX files exist and readable
☐ All files have required columns
☐ Color formatting applied correctly
☐ All files UTF-8 encoded
☐ No files read-locked
☐ File names valid (no special chars)
```

### Data Validation
```
☐ Score values numeric (0-100%)
☐ Email addresses valid format
☐ Names have no unsupported characters
☐ No completely blank rows
☐ Email = primary key
```

### Compilation Validation
```
☐ All participants from all tests present
☐ Email matching case-insensitive
☐ Alphabetical sorting correct
☐ Missing scores shown as blank
☐ No duplicate rows
☐ Color preserved
```

### Output Validation
```
☐ One row per unique email
☐ Exactly 5 score columns
☐ All scores correctly aligned
☐ No data corruption/truncation
☐ File format correct (XLSX/PDF/DOCX)
☐ File opens without errors
```

### Log Validation
```
☐ Log file created
☐ All operations timestamped
☐ Summary shows correct counts
☐ All warnings/errors logged
☐ Log human-readable
```

---

## SECTION 7: KNOWN ISSUES & MITIGATIONS

### Issue 1: Color Loss in PDF/DOCX
**Problem:** Colors may not export to PDF/DOCX  
**Mitigation:** Add legend, include test number in header, add text indicators

### Issue 2: Email Matching Sensitivity
**Problem:** Email format variations break matching  
**Mitigation:** Use email as primary key, warn user before merge, manual review option

### Issue 3: Name Format Variations
**Problem:** Names vary in format ("John Smith" vs "Smith, John")  
**Mitigation:** Email is primary key, not name. Name is display only.

### Issue 4: Large File Performance
**Problem:** 50,000+ rows may slow Excel  
**Mitigation:** Split output by test, offer CSV export, implement incremental processing

---

## SECTION 8: TEST EXECUTION SUMMARY TEMPLATE

```
TEST SESSION: [Date & Time]
TESTER: [Your Name]
FOCUS: [E.g., "Email Matching", "Color Preservation"]

TESTS RUN:
[List test IDs executed]

RESULTS:
☐ Test 2.1 (Happy Path): PASS / FAIL
☐ Test 2.2 (Missing Data): PASS / FAIL
☐ Test 2.3 (New Participant): PASS / FAIL
☐ Test 2.4 (Case Insensitive): PASS / FAIL
☐ Test 2.5 (Alphabetical Order): PASS / FAIL
[... continue for all tests ...]

CRITICAL ISSUES: [Count]
MAJOR ISSUES: [Count]
MINOR ISSUES: [Count]

RECOMMENDATIONS:
1. [Fix priority 1]
2. [Fix priority 2]

SIGN-OFF: [Date & Signature]
```

---

## FINAL NOTES

This test plan covers:
✓ 30+ individual test scenarios
✓ Happy paths (success cases)
✓ Failure scenarios (graceful degradation)
✓ Edge cases (boundary conditions)
✓ Attack vectors (malicious inputs)
✓ Complete validation checklists

**Next Steps:**
1. Run Test 2.1 (Happy Path) first
2. Progress to Test 2.2-2.5 (Core Functionality)
3. Test edge cases (Section 4)
4. Perform attack/stress tests (Section 5)
5. Document all findings
6. Prioritize fixes
7. Re-test after fixes
8. Automate repeatable tests

---

**Test Plan Version:** 1.0  
**Status:** Ready for Implementation  
**Last Updated:** January 31, 2026
