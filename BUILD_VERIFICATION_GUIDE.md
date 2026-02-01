# Build Verification Guide

Just like web dev has `npm run build`, this project now has a pre-deployment verification script.

## Quick Start

```powershell
# Check build (runs all verification checks)
.\verify-build.ps1

# If all checks pass, deploy to Render
.\verify-build.ps1 -Deploy
```

## What It Checks

✅ **Python Environment**
- Python version and availability
- Installation integrity

✅ **Configuration**
- .env file exists
- TELEGRAM_BOT_TOKEN configured

✅ **Dependencies**
- requirements.txt exists
- All dependencies listed

✅ **Code Quality**
- Python syntax errors across all files
- No import errors
- Critical imports work:
  - `server.app`
  - `telegram_bot.build_application`
  - `src.excel_processor.ExcelProcessor`

✅ **Test Suite**
- `test_core_functionality.py` passes
- `test_bonus_system.py` passes
- `test_6_tests_percentages.py` passes

✅ **Git Status**
- Working tree clean (no uncommitted changes)
- Ready for deployment

## Workflow

### Before Deployment

```powershell
# Make your changes
# ... edit files ...

# Verify the build is good
.\verify-build.ps1

# If all checks pass (green [OK] indicators):
#   ✅ BUILD VERIFICATION PASSED - Ready for deployment!

# If any checks fail (red [FAIL] indicators):
#   Fix the errors and try again
```

### Deploy When Ready

```powershell
# Automatic deployment after verification
.\verify-build.ps1 -Deploy

# This will:
# 1. Run all verification checks
# 2. If all pass, trigger Render deployment via webhook
# 3. Show deployment status (HTTP 202 Accepted)
```

## Exit Codes

- `0` = Success (ready to deploy)
- `1` = Failure (do not deploy)

## Example Output

```
=================================================================
  MLJ Results Compiler - Pre-Deployment Build Verification
=================================================================
>> Checking Python environment...
[OK] Python found: Python 3.12.7
>> Checking .env configuration...
[OK] .env file exists
[OK] TELEGRAM_BOT_TOKEN configured
>> Checking requirements.txt...
[OK] requirements.txt exists
[OK]   10 dependencies defined
>> Scanning Python files for syntax errors...
[OK] All Python files have valid syntax
>> Testing critical imports...
[OK] server.app imports successfully
[OK] telegram_bot.build_application imports successfully
[OK] ExcelProcessor imports successfully
>> Running existing test suites...
>> Running test_core_functionality.py...
[OK]     Tests passed
>> Running test_bonus_system.py...
[OK]     Tests passed
>> Running test_6_tests_percentages.py...
[OK]     Tests passed
>> Checking git status...
[OK] Working tree is clean

=================================================================
Build Verification Summary
=================================================================

[OK] [OK] BUILD VERIFICATION PASSED - Ready for deployment!

Next steps:
  1. Verify changes: git status
  2. Deploy: ./verify-build.ps1 -Deploy
```

## If Something Fails

The script shows red `[FAIL]` indicators. Common issues:

### Syntax Errors
```
[FAIL] Syntax error in server.py
```
→ Fix the Python syntax error and try again

### Import Errors
```
[FAIL] Failed to import server.app
```
→ Check dependencies: `pip install -r requirements.txt`

### Test Failures
```
[FAIL] Tests failed in test_bonus_system.py
```
→ Run the test directly to debug: `python test_bonus_system.py`

### Uncommitted Changes
```
[WARN] Working tree has uncommitted changes
```
→ Commit or stash changes before deploying: `git commit -am "message"`

## Tips

- Run this **before every deployment** to catch issues early
- Takes ~30-45 seconds to run all checks
- Saves hours of debugging Render deployment errors
- Keeps the deployment process confident and reliable

---

*Verification script: `./verify-build.ps1`*
