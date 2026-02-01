#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.data_integrity import get_validator
from src.excel_processor import ExcelProcessor

# Quick validation
processor = ExcelProcessor('input', 'output')
loaded = processor.load_all_tests()
print(f"✓ Loaded {loaded} tests")

consolidated = processor.consolidate_results()
print(f"✓ Consolidated: {len(consolidated)} emails")

validator = get_validator()
result = validator.validate_consolidation(processor.test_data, consolidated)

print(f"\nValidation Result:")
print(f"  Valid: {result['valid']}")
print(f"  Source emails: {result['stats']['source_unique_emails']}")
print(f"  Consolidated emails: {result['stats']['consolidated_emails']}")
print(f"  Data loss: {result['stats']['data_loss_percent']:.2f}%")

if result['info']:
    print(f"\nInfo:")
    for msg in result['info']:
        print(f"  {msg}")

if result['warnings']:
    print(f"\nWarnings:")
    for msg in result['warnings']:
        print(f"  {msg}")

if result['errors']:
    print(f"\nErrors:")
    for msg in result['errors']:
        print(f"  {msg}")
    sys.exit(1)
else:
    print("\n✅ VALIDATION PASSED")
    sys.exit(0)
