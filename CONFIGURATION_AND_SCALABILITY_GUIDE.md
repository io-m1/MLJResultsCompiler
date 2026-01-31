# MLJResultsCompiler - Configuration & Scalability Guide

## System Overview

Your bot now has **3 operational modes**:

### 1. **Legacy Mode** (v1.0)
- Fixed 5 test files (TEST_1 through TEST_5)
- Original functionality preserved
- Used when exactly 5 files detected

### 2. **Scalable Mode** (v2.0) ← NEW
- Works with **ANY number of files** (1, 10, 50, 1000+)
- Dynamic file detection
- Agentic decision-making
- Automatic optimization

### 3. **Hybrid Mode** (v2.0)
- Auto-selects best bot based on file count
- Uses legacy if exactly 5 files
- Uses scalable otherwise
- Recommended for production

---

## Architecture

### Core Components

```
ConfigSystem (config.py)
    ├── BotConfig - Main configuration
    ├── ProcessingStrategy - How to handle files
    ├── MergeStrategy - How to combine data
    ├── ValidationLevel - Data quality checks
    └── ColorConfig - Output formatting

Agents (agents.py)
    ├── ValidationAgent - Data quality checks
    ├── OptimizationAgent - Performance suggestions
    ├── QualityAgent - Statistical analysis
    ├── RemediationAgent - Auto-fix issues
    └── AgentOrchestrator - Coordinates all agents

Bots
    ├── ResultsCompiler (v1.0) - Legacy
    ├── ScalableResultsCompiler (v2.0) - New
    └── EnhancedIntegratedCompiler - Unified interface
```

---

## Quick Start

### Option 1: Default Configuration (Recommended)

```python
from results_compiler_bot_v2 import ScalableResultsCompiler

# Works with ANY number of files automatically
compiler = ScalableResultsCompiler()
compiler.run()
```

### Option 2: Custom Configuration

```python
from config import BotConfig, ProcessingStrategy
from results_compiler_bot_v2 import ScalableResultsCompiler

# Create custom config
config = BotConfig(
    input_folder='my_tests',
    output_folder='results',
    file_pattern='TEST_*.xlsx',
    min_files_required=1,  # Can work with just 1 file
    processing_strategy=ProcessingStrategy.ADAPTIVE,
    enable_agents=True,
)

compiler = ScalableResultsCompiler(config=config)
compiler.run()
```

### Option 3: Auto-Selection (Most Intelligent)

```python
from integration_v2 import EnhancedIntegratedCompiler

# Automatically selects legacy or scalable bot
compiler = EnhancedIntegratedCompiler()
result = compiler.compile_with_validation()

print(f"Status: {result['status']}")
print(f"Participants: {result['participants']}")
```

---

## Configuration Options

### Basic Settings

```python
BotConfig(
    # Folders
    input_folder='input',           # Where test files are
    output_folder='output',         # Where results go
    
    # File detection
    file_pattern='TEST_*.xlsx',     # Pattern to find files
    case_sensitive_pattern=False,   # Case-insensitive matching
    min_files_required=1,           # Minimum files needed (default was 5)
    max_files_allowed=1000,         # Maximum files to process
)
```

### Processing Strategy

```python
ProcessingStrategy.STRICT    # All files must exist and match
ProcessingStrategy.LENIENT   # Skip missing files, process available ones
ProcessingStrategy.ADAPTIVE  # Auto-adjust based on file characteristics
```

### Merge Strategy

```python
MergeStrategy.EMAIL          # Primary key (recommended)
MergeStrategy.NAME_EMAIL     # Combination of name + email
MergeStrategy.SEQUENCE       # Row-by-row (assume same order)
MergeStrategy.FUZZY          # Fuzzy name/email matching
```

### Validation Levels

```python
DataValidationLevel.NONE     # No validation (fastest)
DataValidationLevel.MINIMAL  # Just check for NaN
DataValidationLevel.STANDARD # Type checks, ranges (recommended)
DataValidationLevel.STRICT   # Comprehensive + rules (slowest)
```

### Column Detection

```python
BotConfig(
    auto_detect_columns=True,       # Auto-find name/email/score columns
    case_insensitive_columns=True,  # Match ignoring case
)

# Customize column variations
from config import ColumnMapping

config = BotConfig(
    column_mapping=ColumnMapping(
        name_variations=['full name', 'name', 'participant', 'student'],
        email_variations=['email', 'e-mail', 'contact email'],
        score_variations=['score', 'result', 'percentage', 'points'],
    )
)
```

---

## Agentic Capabilities

### 1. Validation Agent

Automatically checks:
- Empty dataframes
- Missing required columns
- Duplicate emails
- Invalid score values
- Email format validation

```python
config = BotConfig(
    validation_agent_enabled=True,
    validation_level=DataValidationLevel.STANDARD,
)
```

### 2. Optimization Agent

Provides suggestions for:
- Large file sets (>100 files) → batch processing
- Very large sets (>1000) → parallel processing
- Optimal merge strategy based on data structure
- Color scheme generation for any number of files

### 3. Quality Agent

Generates insights:
- Data completeness percentage
- Duplicate email detection
- Invalid email identification
- Score statistics (mean, median, min, max, std)

```python
config = BotConfig(
    quality_agent_enabled=True,
    include_statistics=True,  # Include in output
)
```

### 4. Remediation Agent

Attempts automatic fixes:
- Column name normalization
- Invalid email repair
- Data type conversion
- Whitespace cleanup

```python
config = BotConfig(
    auto_remediation_enabled=True,
)
```

---

## Examples

### Example 1: Process 5 Files (Like Before)

```python
from results_compiler_bot_v2 import ScalableResultsCompiler

compiler = ScalableResultsCompiler()
compiler.run()

# Automatically finds TEST_1.xlsx through TEST_5.xlsx
# Consolidates to Consolidated_Results.xlsx
```

### Example 2: Process 50 Test Files

```python
from config import BotConfig, ProcessingStrategy
from results_compiler_bot_v2 import ScalableResultsCompiler

config = BotConfig(
    file_pattern='BATCH_*.xlsx',
    min_files_required=1,
    max_files_allowed=1000,
    processing_strategy=ProcessingStrategy.ADAPTIVE,
)

compiler = ScalableResultsCompiler(config=config)
compiler.run()

# Automatically finds all BATCH_*.xlsx files
# Intelligently processes all 50 files
# Generates color scheme for all 50 tests
```

### Example 3: Auto-Selection (Recommended)

```python
from integration_v2 import EnhancedIntegratedCompiler

compiler = EnhancedIntegratedCompiler()

# Automatically selects:
# - Legacy bot if exactly 5 TEST_*.xlsx files
# - Scalable bot for any other count

success, message, output_path = compiler.compile_from_input_folder()
print(message)  # "✓ Compilation complete! 98 participants"
```

### Example 4: Session-Based (Telegram)

```python
from integration_v2 import EnhancedIntegratedCompiler
from src.session_manager import SessionManager

compiler = EnhancedIntegratedCompiler()
session_mgr = SessionManager()

# When user uploads files via Telegram
success, message, output_path = compiler.compile_from_session(user_id, session_mgr)

if success:
    print(message)  # "✓ Compilation complete! 98 participants"
    # Return output_path to user for download
```

### Example 5: Full Validation Report

```python
from integration_v2 import EnhancedIntegratedCompiler

compiler = EnhancedIntegratedCompiler()
report = compiler.compile_with_validation()

print(f"Status: {report['status']}")           # completed
print(f"Files: {report['files_processed']}")   # 5
print(f"Participants: {report['participants']}")  # 98
print(f"Validation: {report['validation_passed']}")  # True

for msg in report['messages']:
    print(f"  ✓ {msg}")

for err in report['errors']:
    print(f"  ✗ {err}")
```

---

## Configuration File Usage

### Save Configuration

```python
from config import BotConfig

config = BotConfig(
    input_folder='tests',
    min_files_required=1,
    enable_agents=True,
)

config.save_to_json('bot_config.json')
```

### Load Configuration

```python
from config import BotConfig

config = BotConfig.from_json('bot_config.json')
print(f"Input folder: {config.input_folder}")
```

### Create Example Config

```python
from config import create_example_config

create_example_config('config_example.json')
# Creates a file with all available options
```

---

## Comparison: v1.0 vs v2.0

| Feature | v1.0 | v2.0 |
|---------|------|------|
| **Files** | Fixed 5 | Any count |
| **Auto-detect** | TEST_1-5 | Any pattern |
| **Agents** | ✗ | ✓ |
| **Configuration** | Hardcoded | Flexible |
| **Scalability** | No | Yes |
| **Remediation** | Manual | Auto |
| **Insights** | Basic | Comprehensive |
| **Backwards Compatible** | - | ✓ Yes |

---

## Migration Guide

### If You Were Using v1.0

Your code still works! No changes needed:

```python
# This still works
from results_compiler_bot import ResultsCompiler

compiler = ResultsCompiler()
compiler.run()
```

### If You Want to Use v2.0

Just change the import:

```python
# Use v2.0
from results_compiler_bot_v2 import ScalableResultsCompiler

compiler = ScalableResultsCompiler()
compiler.run()  # Works with ANY number of files
```

### If You Want Full Intelligence

Use the integrated compiler:

```python
# Use intelligent auto-selection
from integration_v2 import EnhancedIntegratedCompiler

compiler = EnhancedIntegratedCompiler()
compiler.compile_with_validation()
```

---

## Best Practices

### 1. Use Scalable Bot for Production

```python
from results_compiler_bot_v2 import ScalableResultsCompiler

compiler = ScalableResultsCompiler()
compiler.run()
```

### 2. Enable Agents for Better Results

```python
from config import BotConfig
from results_compiler_bot_v2 import ScalableResultsCompiler

config = BotConfig(
    enable_agents=True,
    validation_agent_enabled=True,
    quality_agent_enabled=True,
    auto_remediation_enabled=True,
)

compiler = ScalableResultsCompiler(config=config)
compiler.run()
```

### 3. Use Adaptive Strategy for Unknown Inputs

```python
from config import BotConfig, ProcessingStrategy

config = BotConfig(
    processing_strategy=ProcessingStrategy.ADAPTIVE,
)
```

### 4. Generate Insights

```python
compiler = ScalableResultsCompiler(config=config)
compiler.run()

insights = compiler.generate_insights()
print(f"Data quality: {insights['completeness_percent']}%")
```

---

## Troubleshooting

### No Files Found

```python
# Check your file pattern
config = BotConfig(file_pattern='MY_TEST_*.xlsx')

# Make sure files exist
import os
print(os.listdir('input'))
```

### Column Names Not Detected

```python
# Add custom column variations
from config import ColumnMapping

config = BotConfig(
    column_mapping=ColumnMapping(
        name_variations=['full name', 'your_custom_name_col'],
        email_variations=['email', 'your_custom_email_col'],
        score_variations=['score', 'your_custom_score_col'],
    )
)
```

### Many Files Processing Slowly

```python
# For 1000+ files, use optimization suggestions
from results_compiler_bot_v2 import ScalableResultsCompiler

compiler = ScalableResultsCompiler()
compiler.run()

# Check orchestrator suggestions
if compiler.orchestrator:
    print(compiler.orchestrator.reports)
```

---

## What Changed

### New Files Created
- `config.py` - Configuration system
- `agents.py` - Agentic capabilities
- `results_compiler_bot_v2.py` - Scalable bot
- `integration_v2.py` - Enhanced integration

### Files Preserved
- `results_compiler_bot.py` - Still works (legacy)
- `integration.py` - Still works (legacy)
- `telegram_bot.py` - Enhanced with v2.0 support
- All existing code backwards compatible

---

## Summary

Your bot now:

✅ Works with **ANY number of files** (not just 5)  
✅ Has **agentic capabilities** (autonomous decision-making)  
✅ **Auto-selects** best processing strategy  
✅ **Validates** data automatically  
✅ **Fixes** issues automatically  
✅ **Generates** insights and statistics  
✅ **Remains backwards compatible** with v1.0  
✅ **Scales** to thousands of files  

---

**Next Steps:**
1. Run: `python results_compiler_bot_v2.py`
2. Check output: `output/Consolidated_Results.xlsx`
3. Review insights in logs
4. Deploy to Render (same as before)

**Questions?** Check the agent reports in `compiler_execution.log` for detailed analysis.
