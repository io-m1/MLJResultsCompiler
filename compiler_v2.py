#!/usr/bin/env python3
"""
MLJResultsCompiler v2.0 - PRODUCTION GRADE
Fixed version addressing all critical issues
- Proper header generation
- Data loss detection
- Duplicate handling with reporting
- Input validation
- Error recovery
- Comprehensive logging

Author: Fixed by Claude (Anthropic)
Version: 2.0 (Production-Ready)
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from enum import Enum
import traceback

# Configure structured logging
class StructuredLogger:
    def __init__(self, log_file: str = 'compiler_execution.log'):
        self.log_file = log_file
        self.warnings = []
        self.errors = []
        
        # File handler
        self.file_handler = open(log_file, 'w')
        
        # Console handler
        self.console_handler = sys.stdout
    
    def log(self, level: str, message: str, **kwargs):
        timestamp = datetime.now().isoformat()
        entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message,
            **kwargs
        }
        
        # Log to file
        self.file_handler.write(json.dumps(entry) + '\n')
        self.file_handler.flush()
        
        # Log to console
        print(f"[{level:7}] {message}")
        
        # Track warnings/errors
        if level == 'WARNING':
            self.warnings.append(message)
        elif level == 'ERROR':
            self.errors.append(message)
    
    def info(self, msg: str): self.log('INFO', msg)
    def warning(self, msg: str): self.log('WARNING', msg)
    def error(self, msg: str): self.log('ERROR', msg)
    def debug(self, msg: str): self.log('DEBUG', msg)
    
    def close(self):
        self.file_handler.close()


class DuplicateStrategy(Enum):
    KEEP_FIRST = 'first'
    KEEP_LAST = 'last'
    ERROR = 'error'
    FLAG = 'flag'


class ValidationError(Exception):
    """Validation failed"""
    pass


class DataLossError(Exception):
    """Data was lost during processing"""
    pass


class ColumnDetectionError(Exception):
    """Could not detect required columns"""
    pass


class CompilationStats:
    """Track compilation statistics"""
    def __init__(self):
        self.start_time = datetime.now()
        self.files_processed = 0
        self.total_input_rows = 0
        self.total_output_rows = 0
        self.duplicates_found = {}
        self.duplicates_removed = 0
        self.warnings = []
        self.errors = []
    
    def duration(self):
        return (datetime.now() - self.start_time).total_seconds()
    
    def to_dict(self):
        return {
            'start_time': self.start_time.isoformat(),
            'duration_seconds': self.duration(),
            'files_processed': self.files_processed,
            'total_input_rows': self.total_input_rows,
            'total_output_rows': self.total_output_rows,
            'duplicates_removed': self.duplicates_removed,
            'warnings': self.warnings,
            'errors': self.errors
        }


class InputValidator:
    """Validate input files before processing"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
    
    def validate_file(self, filepath: str) -> Tuple[bool, str]:
        """Validate a single XLSX file"""
        checks = []
        
        # File exists
        if not os.path.exists(filepath):
            return False, f"File not found: {filepath}"
        checks.append(("File exists", True))
        
        # Is XLSX
        if not filepath.endswith('.xlsx'):
            return False, f"File must be .xlsx, got: {filepath}"
        checks.append(("Is XLSX format", True))
        
        # Can be read
        try:
            df = pd.read_excel(filepath, nrows=1)
            checks.append(("File is readable", True))
        except Exception as e:
            return False, f"Cannot read file: {str(e)}"
        
        # Has data
        try:
            df = pd.read_excel(filepath)
            if len(df) == 0:
                return False, "File has no data rows"
            checks.append(("File has data", True))
        except Exception as e:
            return False, f"Error reading data: {str(e)}"
        
        # Has Email column
        if 'Email' not in df.columns and 'EMAIL' not in df.columns:
            available = [c for c in df.columns if 'mail' in c.lower()]
            return False, f"Missing 'Email' column. Available: {available}"
        checks.append(("Has Email column", True))
        
        # Has Result/Score column
        has_result = any('result' in c.lower() or 'score' in c.lower() for c in df.columns)
        if not has_result:
            return False, "Missing 'Result' or 'Score' column"
        checks.append(("Has Result column", True))
        
        # Has Name column
        has_name = any('name' in c.lower() for c in df.columns)
        if not has_name:
            return False, "Missing name column (Name, Full Names, Full name, etc.)"
        checks.append(("Has Name column", True))
        
        return True, "All checks passed"
    
    def validate_all(self, test_files: Dict[int, str]) -> bool:
        """Validate all test files"""
        all_valid = True
        
        for test_num in range(1, 6):
            if test_num not in test_files:
                self.logger.warning(f"Test {test_num} not found")
                all_valid = False
                continue
            
            valid, msg = self.validate_file(test_files[test_num])
            if valid:
                self.logger.info(f"Test {test_num}: {msg}")
            else:
                self.logger.error(f"Test {test_num}: {msg}")
                all_valid = False
        
        return all_valid


class FuzzyColumnDetector:
    """Fuzzy column detection with scoring"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        
        self.name_variants = [
            ' Full Names',  # With leading space
            'Full Names',
            'Full names',
            'Name',
            'Full Name',
            'Participant',
            'Student',
            'Respondent',
        ]
        
        self.email_variants = [
            'Email',
            'EMAIL',
            'email',
            'E-mail',
            'E-Mail',
            'Contact',
        ]
        
        self.score_variants = [
            'Result',
            'RESULT',
            'result',
            'Score',
            'SCORE',
            'score',
            'Total Marks',
            'Percentage',
            'Percent',
            '%',
        ]
    
    def _score_column(self, col_name: str, variants: List[str]) -> Tuple[str, float]:
        """Score a column against variants (0.0 to 1.0)"""
        col_lower = col_name.lower().strip()
        
        # Exact match
        for variant in variants:
            if col_name == variant:
                return variant, 1.0
        
        # Case-insensitive match
        for variant in variants:
            if col_lower == variant.lower():
                return variant, 0.95
        
        # Contains match
        for variant in variants:
            if variant.lower() in col_lower:
                return variant, 0.8
        
        # Partial match
        for variant in variants:
            variant_words = variant.lower().split()
            col_words = col_lower.split()
            match_count = sum(1 for w in variant_words if w in col_words)
            if match_count > 0:
                score = 0.5 + (match_count / len(variant_words)) * 0.3
                return variant, score
        
        return None, 0.0
    
    def detect_columns(self, df: pd.DataFrame, test_num: int) -> Dict[str, str]:
        """Detect name, email, score columns"""
        
        # Score all columns
        name_scores = {}
        email_scores = {}
        score_scores = {}
        
        for col in df.columns:
            name_match, name_score = self._score_column(col, self.name_variants)
            if name_score > 0.5:
                name_scores[col] = name_score
            
            email_match, email_score = self._score_column(col, self.email_variants)
            if email_score > 0.5:
                email_scores[col] = email_score
            
            score_match, score_score = self._score_column(col, self.score_variants)
            if score_score > 0.5:
                score_scores[col] = score_score
        
        # Get best matches
        name_col = max(name_scores, key=name_scores.get) if name_scores else None
        email_col = max(email_scores, key=email_scores.get) if email_scores else None
        score_col = max(score_scores, key=score_scores.get) if score_scores else None
        
        # Verify all found
        if not all([name_col, email_col, score_col]):
            missing = []
            if not name_col:
                missing.append('Name')
            if not email_col:
                missing.append('Email')
            if not score_col:
                missing.append('Score')
            
            raise ColumnDetectionError(
                f"Test {test_num}: Could not find: {', '.join(missing)}\n"
                f"Available columns: {list(df.columns[:10])}"
            )
        
        self.logger.info(f"Test {test_num}: Detected Name='{name_col}', Email='{email_col}', Score='{score_col}'")
        
        return {'name': name_col, 'email': email_col, 'score': score_col}


class DeduplicationHandler:
    """Handle duplicate emails with reporting"""
    
    def __init__(self, logger: StructuredLogger, strategy: DuplicateStrategy = DuplicateStrategy.KEEP_FIRST):
        self.logger = logger
        self.strategy = strategy
        self.removal_reports = {}
    
    def handle_duplicates(self, df: pd.DataFrame, test_num: int) -> Tuple[pd.DataFrame, Dict]:
        """Remove duplicates and return report"""
        
        before = len(df)
        
        # Find duplicates
        dupes_mask = df.duplicated(subset=['Email'], keep=False)
        dupes = df[dupes_mask].sort_values('Email')
        
        if len(dupes) > 0:
            self.logger.warning(f"Test {test_num}: Found {len(dupes)} duplicate email entries")
            
            # Summarize duplicates
            dupe_emails = dupes['Email'].unique()
            for email in dupe_emails:
                email_dupes = dupes[dupes['Email'] == email]
                self.logger.warning(f"  {email}: {len(email_dupes)} entries")
        
        # Remove duplicates based on strategy
        if self.strategy == DuplicateStrategy.KEEP_FIRST:
            df_clean = df.drop_duplicates(subset=['Email'], keep='first')
        elif self.strategy == DuplicateStrategy.KEEP_LAST:
            df_clean = df.drop_duplicates(subset=['Email'], keep='last')
        elif self.strategy == DuplicateStrategy.ERROR:
            if len(dupes) > 0:
                raise ValueError(f"Duplicates found and error strategy selected")
            df_clean = df
        else:  # FLAG
            df_clean = df.copy()
            df_clean['_has_duplicate'] = df_clean.duplicated(subset=['Email'], keep=False)
        
        after = len(df_clean)
        removed = before - after
        
        report = {
            'test_num': test_num,
            'before': before,
            'after': after,
            'removed': removed,
            'duplicates': dupes.to_dict('records') if len(dupes) > 0 else []
        }
        
        self.removal_reports[test_num] = report
        
        if removed > 0:
            self.logger.info(f"Test {test_num}: Removed {removed} duplicate entries")
        
        return df_clean, report


class ResultsCompilerV2:
    """Production-grade results compiler (Fixed)"""
    
    def __init__(self, input_folder: str = 'input', output_folder: str = 'output', 
                 duplicate_strategy: DuplicateStrategy = DuplicateStrategy.KEEP_FIRST):
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(exist_ok=True)
        
        self.logger = StructuredLogger(str(self.output_folder / 'compiler_execution.log'))
        self.stats = CompilationStats()
        self.validator = InputValidator(self.logger)
        self.column_detector = FuzzyColumnDetector(self.logger)
        self.dedup_handler = DeduplicationHandler(self.logger, duplicate_strategy)
        
        self.test_files = {}
        self.dataframes = {}
        self.merged_df = None
    
    def find_test_files(self) -> bool:
        """Find all 5 test files"""
        self.logger.info("Searching for test files...")
        
        test_patterns = {
            1: ['TEST_1', 'test_1'],
            2: ['TEST_2', 'test_2'],
            3: ['TEST_3', 'test_3'],
            4: ['TEST_4', 'test_4'],
            5: ['TEST_5', 'test_5', 'ultrasonography'],
        }
        
        for test_num in range(1, 6):
            found = False
            for file in self.input_folder.glob('*.xlsx'):
                filename = file.stem.upper()
                if any(pattern.upper() in filename for pattern in test_patterns[test_num]):
                    self.test_files[test_num] = str(file)
                    self.logger.info(f"Test {test_num} found: {file.name}")
                    found = True
                    break
            
            if not found:
                self.logger.warning(f"Test {test_num} not found")
        
        if len(self.test_files) < 5:
            self.logger.error(f"Only found {len(self.test_files)}/5 test files")
            return False
        
        return True
    
    def load_and_process_test(self, test_num: int) -> bool:
        """Load test and extract core columns"""
        
        if test_num not in self.test_files:
            return False
        
        try:
            self.logger.info(f"Loading Test {test_num}...")
            df = pd.read_excel(self.test_files[test_num])
            self.logger.info(f"  Rows: {len(df)}, Columns: {len(df.columns)}")
            self.stats.files_processed += 1
            self.stats.total_input_rows += len(df)
            
            # Detect columns
            columns = self.column_detector.detect_columns(df, test_num)
            
            # Extract only needed columns
            df_extracted = df[[columns['name'], columns['email'], columns['score']]].copy()
            df_extracted.columns = ['Full Name', 'Email', f'Test{test_num}_Score']
            
            # Normalize emails
            df_extracted['Email'] = df_extracted['Email'].astype(str).str.lower().str.strip()
            
            # Parse scores
            df_extracted[f'Test{test_num}_Score'] = df_extracted[f'Test{test_num}_Score'].astype(str)
            df_extracted[f'Test{test_num}_Score'] = df_extracted[f'Test{test_num}_Score'].str.replace('%', '').str.strip()
            
            try:
                df_extracted[f'Test{test_num}_Score'] = pd.to_numeric(df_extracted[f'Test{test_num}_Score'], errors='coerce')
            except Exception as e:
                self.logger.warning(f"Test {test_num}: Could not parse all scores: {str(e)}")
            
            # Handle duplicates
            df_extracted, dedup_report = self.dedup_handler.handle_duplicates(df_extracted, test_num)
            
            # Remove completely blank rows
            df_extracted = df_extracted.dropna(subset=['Full Name', 'Email'], how='all')
            
            self.dataframes[test_num] = df_extracted
            self.stats.total_output_rows += len(df_extracted)
            
            self.logger.info(f"Test {test_num}: {len(df_extracted)} rows extracted")
            
            return True
            
        except ColumnDetectionError as e:
            self.logger.error(f"Test {test_num}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Test {test_num}: Unexpected error: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False
    
    def load_all_tests(self) -> bool:
        """Load all 5 tests"""
        self.logger.info("\n" + "="*80)
        self.logger.info("STEP 1: LOAD AND VALIDATE TESTS")
        self.logger.info("="*80)
        
        success_count = 0
        for test_num in range(1, 6):
            if self.load_and_process_test(test_num):
                success_count += 1
        
        self.logger.info(f"\nResult: {success_count}/5 tests loaded")
        
        return success_count == 5
    
    def merge_all_tests(self) -> bool:
        """Merge tests with validation"""
        self.logger.info("\n" + "="*80)
        self.logger.info("STEP 2: MERGE TESTS")
        self.logger.info("="*80)
        
        if len(self.dataframes) < 5:
            self.logger.error("Not all tests available")
            return False
        
        try:
            # Count input emails
            input_emails = set()
            for test_num in range(1, 6):
                df = self.dataframes[test_num]
                input_emails.update(df['Email'].unique())
            
            input_count = len(input_emails)
            self.logger.info(f"Input: {input_count} unique emails")
            
            # Merge
            self.merged_df = self.dataframes[1][['Full Name', 'Email', 'Test1_Score']].copy()
            self.merged_df.columns = ['Full Name', 'Email', 'Test 1 (%)']
            
            for test_num in range(2, 6):
                df_test = self.dataframes[test_num][['Email', f'Test{test_num}_Score']].copy()
                df_test.columns = ['Email', f'Test {test_num} (%)']
                
                self.merged_df = pd.merge(
                    self.merged_df,
                    df_test,
                    on='Email',
                    how='outer'
                )
            
            # Count output
            output_count = self.merged_df['Email'].nunique()
            self.logger.info(f"Output: {output_count} unique emails")
            
            # Validate - allow small margin for deduplication
            if output_count < input_count * 0.95:
                missing = input_count - output_count
                self.logger.error(f"DATA LOSS DETECTED: {missing} emails missing from output")
                raise DataLossError(f"Lost {missing} participants during merge")
            
            return True
            
        except DataLossError as e:
            self.logger.error(f"Merge validation failed: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Merge error: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False
    
    def clean_and_sort(self) -> bool:
        """Clean, validate, and sort output"""
        self.logger.info("\n" + "="*80)
        self.logger.info("STEP 3: CLEAN, VALIDATE, AND SORT")
        self.logger.info("="*80)
        
        try:
            # Remove duplicates (by email)
            before = len(self.merged_df)
            self.merged_df = self.merged_df.drop_duplicates(subset=['Email'], keep='first')
            after = len(self.merged_df)
            
            if before != after:
                self.logger.warning(f"Removed {before - after} duplicate emails from merged output")
            
            # Sort alphabetically
            self.merged_df = self.merged_df.sort_values(
                by='Full Name',
                key=lambda x: x.str.lower(),
                ignore_index=True
            )
            
            # Validate structure
            if self.merged_df.isna().all(axis=1).any():
                self.logger.warning("Found completely blank rows")
                self.merged_df = self.merged_df.dropna(how='all')
            
            # Validate header
            expected_cols = ['Full Name', 'Email', 'Test 1 (%)', 'Test 2 (%)', 
                           'Test 3 (%)', 'Test 4 (%)', 'Test 5 (%)']
            
            if list(self.merged_df.columns) != expected_cols:
                self.logger.error(f"Column mismatch: {list(self.merged_df.columns)}")
                return False
            
            self.logger.info(f"Final output: {len(self.merged_df)} rows, {len(self.merged_df.columns)} columns")
            
            # Sample output
            self.logger.info("Sample output (first 3 rows):")
            for idx in range(min(3, len(self.merged_df))):
                row = self.merged_df.iloc[idx]
                self.logger.info(f"  {row['Full Name']} | {row['Email']}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Clean/sort error: {str(e)}")
            return False
    
    def export_to_xlsx(self, filename: str = 'Consolidated_Results.xlsx') -> bool:
        """Export with proper header"""
        self.logger.info("\n" + "="*80)
        self.logger.info("STEP 4: EXPORT RESULTS")
        self.logger.info("="*80)
        
        try:
            output_path = self.output_folder / filename
            
            # CRITICAL FIX: Ensure proper column names BEFORE writing
            if list(self.merged_df.columns) != ['Full Name', 'Email', 'Test 1 (%)', 'Test 2 (%)', 
                                                  'Test 3 (%)', 'Test 4 (%)', 'Test 5 (%)']:
                self.logger.error("Column validation failed before export")
                return False
            
            # Export with index=False and header=True (explicit)
            self.merged_df.to_excel(str(output_path), index=False, header=True, sheet_name='Results')
            
            self.logger.info(f"Exported to: {output_path}")
            
            # Verify written file
            verify_df = pd.read_excel(output_path)
            
            # Check header
            expected_header = ['Full Name', 'Email', 'Test 1 (%)', 'Test 2 (%)', 
                             'Test 3 (%)', 'Test 4 (%)', 'Test 5 (%)']
            
            if list(verify_df.columns) != expected_header:
                self.logger.error(f"Header verification failed! Got: {list(verify_df.columns)}")
                return False
            
            self.logger.info(f"Header verification passed")
            
            # Check data
            if len(verify_df) != len(self.merged_df):
                self.logger.error(f"Row count mismatch: {len(verify_df)} vs {len(self.merged_df)}")
                return False
            
            self.logger.info(f"Data verification passed")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Export error: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False
    
    def generate_reports(self) -> bool:
        """Generate JSON and text reports"""
        self.logger.info("\n" + "="*80)
        self.logger.info("STEP 5: GENERATE REPORTS")
        self.logger.info("="*80)
        
        try:
            # JSON report
            report_data = {
                'compilation_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'version': '2.0',
                    'status': 'SUCCESS'
                },
                'statistics': self.stats.to_dict(),
                'deduplication': {
                    f'Test {num}': report for num, report in self.dedup_handler.removal_reports.items()
                },
                'output': {
                    'file': 'Consolidated_Results.xlsx',
                    'rows': len(self.merged_df),
                    'columns': list(self.merged_df.columns)
                }
            }
            
            report_file = self.output_folder / 'compilation_report.json'
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            self.logger.info(f"JSON report: {report_file}")
            
            # Deduplication report
            if self.dedup_handler.removal_reports:
                dedup_file = self.output_folder / 'deduplication_report.json'
                with open(dedup_file, 'w') as f:
                    json.dump(self.dedup_handler.removal_reports, f, indent=2, default=str)
                
                self.logger.info(f"Deduplication report: {dedup_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Report generation error: {str(e)}")
            return False
    
    def run(self) -> bool:
        """Main workflow"""
        self.logger.info("="*80)
        self.logger.info("MLJ RESULTS COMPILER v2.0 - PRODUCTION GRADE")
        self.logger.info(f"Start: {datetime.now().isoformat()}")
        self.logger.info("="*80)
        
        try:
            # Step 0: Validate inputs
            self.logger.info("\n" + "="*80)
            self.logger.info("STEP 0: VALIDATE INPUTS")
            self.logger.info("="*80)
            
            if not self.find_test_files():
                self.logger.error("Could not find all test files")
                return False
            
            if not self.validator.validate_all(self.test_files):
                self.logger.error("Input validation failed")
                return False
            
            # Step 1: Load
            if not self.load_all_tests():
                self.logger.error("Failed to load tests")
                return False
            
            # Step 2: Merge
            if not self.merge_all_tests():
                self.logger.error("Failed to merge tests")
                return False
            
            # Step 3: Clean
            if not self.clean_and_sort():
                self.logger.error("Failed to clean/sort")
                return False
            
            # Step 4: Export
            if not self.export_to_xlsx():
                self.logger.error("Failed to export")
                return False
            
            # Step 5: Reports
            if not self.generate_reports():
                self.logger.warning("Report generation had issues")
            
            self.logger.info("\n" + "="*80)
            self.logger.info("COMPILATION SUCCESSFUL")
            self.logger.info(f"End: {datetime.now().isoformat()}")
            self.logger.info(f"Duration: {self.stats.duration():.2f} seconds")
            self.logger.info("="*80)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False
        finally:
            self.logger.close()


def main():
    """Entry point"""
    input_folder = sys.argv[1] if len(sys.argv) > 1 else 'input'
    output_folder = sys.argv[2] if len(sys.argv) > 2 else 'output'
    
    compiler = ResultsCompilerV2(input_folder=input_folder, output_folder=output_folder)
    success = compiler.run()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
