# Pre-deployment verification script for MLJ Results Compiler
# Simulates "npm run build" for Python/Telegram bot
# Runs all checks before allowing deployment to Render

param(
    [switch]$Deploy = $false  # Use -Deploy flag to auto-deploy after success
)

$ErrorActionPreference = "Stop"
$script:failures = @()
$script:warnings = @()

function Write-Header($msg) {
    Write-Host ""
    Write-Host "=================================================================" -ForegroundColor Cyan
    Write-Host "  $msg" -ForegroundColor Cyan
    Write-Host "=================================================================" -ForegroundColor Cyan
}

function Write-Step($msg) {
    Write-Host ">> $msg" -ForegroundColor Yellow
}

function Write-Success($msg) {
    Write-Host "[OK] $msg" -ForegroundColor Green
}

function Write-Error-Custom($msg) {
    Write-Host "[FAIL] $msg" -ForegroundColor Red
    $script:failures += $msg
}

function Write-Warning-Custom($msg) {
    Write-Host "[WARN] $msg" -ForegroundColor Yellow
    $script:warnings += $msg
}

# Start build process
Write-Header "MLJ Results Compiler - Pre-Deployment Build Verification"

# 1. Check Python environment
Write-Step "Checking Python environment..."
try {
    $python_version = python --version 2>&1
    Write-Success "Python found: $python_version"
} catch {
    Write-Error-Custom "Python not found in PATH"
    exit 1
}

# 2. Check .env file
Write-Step "Checking .env configuration..."
if (Test-Path ".env") {
    Write-Success ".env file exists"
    $token_check = Select-String -Path ".env" -Pattern "TELEGRAM_BOT_TOKEN" -ErrorAction SilentlyContinue
    if ($token_check) {
        Write-Success "TELEGRAM_BOT_TOKEN configured"
    } else {
        Write-Warning-Custom "TELEGRAM_BOT_TOKEN not found in .env (needed for bot)"
    }
} else {
    Write-Warning-Custom ".env file not found (optional locally, required on Render)"
}

# 3. Check requirements.txt
Write-Step "Checking requirements.txt..."
if (Test-Path "requirements.txt") {
    Write-Success "requirements.txt exists"
    $req_count = (Get-Content requirements.txt | Measure-Object -Line).Lines
    Write-Success "  $req_count dependencies defined"
} else {
    Write-Error-Custom "requirements.txt not found"
    exit 1
}

# 4. Check syntax errors
Write-Step "Scanning Python files for syntax errors..."
$python_files = Get-ChildItem -Path . -Recurse -Include "*.py" -Exclude "__pycache__*", ".venv", "venv"
$syntax_errors = 0
foreach ($file in $python_files) {
    $check = python -m py_compile $file.FullName 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Syntax error in $($file.Name)"
        $syntax_errors++
    }
}
if ($syntax_errors -eq 0) {
    Write-Success "All Python files have valid syntax"
}

# 5. Test imports
Write-Step "Testing critical imports..."
$imports_ok = $true

# Test server import
$import_test = python -c "from server import app; print('OK')" 2>&1
if ($LASTEXITCODE -eq 0 -and $import_test -like "*OK*") {
    Write-Success "server.app imports successfully"
} else {
    Write-Error-Custom "Failed to import server.app"
    Write-Host "  Error: $import_test" -ForegroundColor Red
    $imports_ok = $false
}

# Test telegram_bot import
$import_test = python -c "from telegram_bot import build_application; print('OK')" 2>&1
if ($LASTEXITCODE -eq 0 -and $import_test -like "*OK*") {
    Write-Success "telegram_bot.build_application imports successfully"
} else {
    Write-Error-Custom "Failed to import telegram_bot.build_application"
    Write-Host "  Error: $import_test" -ForegroundColor Red
    $imports_ok = $false
}

# Test excel_processor import
$import_test = python -c "from src.excel_processor import ExcelProcessor; print('OK')" 2>&1
if ($LASTEXITCODE -eq 0 -and $import_test -like "*OK*") {
    Write-Success "ExcelProcessor imports successfully"
} else {
    Write-Error-Custom "Failed to import ExcelProcessor"
    Write-Host "  Error: $import_test" -ForegroundColor Red
    $imports_ok = $false
}

# 6. Run existing tests
Write-Step "Running existing test suites..."
$test_files = @(
    "test_core_functionality.py",
    "test_bonus_system.py",
    "test_6_tests_percentages.py"
)

foreach ($test_file in $test_files) {
    if (Test-Path $test_file) {
        Write-Step "  Running $test_file..."
        $output = python $test_file 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "    Tests passed"
        } else {
            Write-Error-Custom "Tests failed in $test_file"
        }
    }
}

# 7. Check git status
Write-Step "Checking git status..."
$git_status = git status --porcelain
if ([string]::IsNullOrWhiteSpace($git_status)) {
    Write-Success "Working tree is clean"
} else {
    Write-Warning-Custom "Working tree has uncommitted changes"
}

# 8. Summary
Write-Header "Build Verification Summary"

if ($script:failures.Count -gt 0) {
    Write-Host ""
    Write-Host "[FAIL] BUILD FAILED - $($script:failures.Count) errors found" -ForegroundColor Red
    foreach ($failure in $script:failures) {
        Write-Host "  - $failure" -ForegroundColor Red
    }
    exit 1
}

if ($script:warnings.Count -gt 0) {
    Write-Host ""
    Write-Host "[WARN] Warnings ($($script:warnings.Count)):" -ForegroundColor Yellow
    foreach ($warning in $script:warnings) {
        Write-Host "  - $warning" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Success "[OK] BUILD VERIFICATION PASSED - Ready for deployment!"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Verify changes: git status" -ForegroundColor Cyan
Write-Host "  2. Deploy: ./verify-build.ps1 -Deploy" -ForegroundColor Cyan
Write-Host ""

# Auto-deploy if requested
if ($Deploy) {
    Write-Header "Deploying to Render"
    
    if (-not [string]::IsNullOrWhiteSpace($git_status)) {
        Write-Error-Custom "Cannot deploy - uncommitted changes exist"
        exit 1
    }
    
    Write-Step "Triggering Render deployment..."
    $webhook_url = "https://api.render.com/deploy/srv-d5v2bviqcgvc7398shog?key=JXiRdSFkZO8"
    
    try {
        $response = Invoke-WebRequest -Uri $webhook_url -Method POST -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 202) {
            Write-Success "Deployment triggered successfully!"
            Write-Host "  Monitor: https://dashboard.render.com" -ForegroundColor Cyan
            Write-Host "  Service: https://mljresultscompiler.onrender.com" -ForegroundColor Cyan
        } else {
            Write-Error-Custom "Unexpected response: $($response.StatusCode)"
            exit 1
        }
    } catch {
        Write-Error-Custom "Failed to trigger deployment: $_"
        exit 1
    }
} else {
    Write-Host "Use -Deploy flag to auto-deploy: ./verify-build.ps1 -Deploy" -ForegroundColor Cyan
    Write-Host ""
}
