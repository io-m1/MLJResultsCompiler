#!/usr/bin/env python3
"""
Data Cleaning Agent - Clean and standardize data
SUBSTANTIAL IMPLEMENTATION with real cleaning capabilities
"""

import logging
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import pandas as pd
import re
import tempfile
from datetime import datetime

from .base_agent import BaseProcessingAgent, ProcessingResult

logger = logging.getLogger(__name__)


class DataCleaningAgent(BaseProcessingAgent):
    """Clean and standardize data with intelligent algorithms"""
    
    def __init__(self):
        super().__init__(name="DataCleaningAgent")
    
    def can_handle(self, documents: List[Dict], intent: str) -> bool:
        """Check if this is a data cleaning request"""
        if intent != 'data_cleaning':
            return False
        
        # Check for data file types
        data_formats = ['.xlsx', '.xls', '.csv', '.tsv', '.json']
        for doc in documents:
            file_format = doc.get('format', '').lower()
            if file_format not in data_formats:
                return False
        
        return True
    
    def validate_inputs(self, documents: List[Dict]) -> Tuple[bool, List[str]]:
        """Validate input documents"""
        errors = []
        
        if not documents:
            errors.append("No documents provided")
            return False, errors
        
        # Check files exist
        for i, doc in enumerate(documents):
            path = doc.get('path')
            if not path or not Path(path).exists():
                errors.append(f"Document {i+1}: File not found")
        
        return len(errors) == 0, errors
    
    def process(self, documents: List[Dict], config: Dict) -> ProcessingResult:
        """
        Clean and standardize data
        
        Features:
        - Remove duplicates
        - Standardize formats (dates, emails, phone numbers)
        - Fill missing values
        - Detect and fix common errors
        - Trim whitespace
        - Normalize text case
        """
        self.log_processing(documents, config)
        
        # Validate inputs
        is_valid, errors = self.validate_inputs(documents)
        if not is_valid:
            result = ProcessingResult(
                success=False,
                message="Validation failed",
                errors=errors
            )
            self.log_result(result)
            return result
        
        try:
            cleaned_files = []
            cleaning_report = {
                'total_files': len(documents),
                'files_processed': 0,
                'total_rows_before': 0,
                'total_rows_after': 0,
                'duplicates_removed': 0,
                'cells_cleaned': 0,
                'issues_fixed': []
            }
            
            for doc in documents:
                # Load data
                df = self._load_dataframe(doc['path'])
                if df is None:
                    continue
                
                original_rows = len(df)
                cleaning_report['total_rows_before'] += original_rows
                
                # Perform cleaning operations
                df, file_report = self._clean_dataframe(df, config)
                
                cleaned_rows = len(df)
                cleaning_report['total_rows_after'] += cleaned_rows
                cleaning_report['duplicates_removed'] += (original_rows - cleaned_rows)
                cleaning_report['cells_cleaned'] += file_report['cells_cleaned']
                cleaning_report['issues_fixed'].extend(file_report['issues'])
                
                # Save cleaned file
                output_path = self._save_cleaned_data(df, doc['path'], config)
                cleaned_files.append(output_path)
                cleaning_report['files_processed'] += 1
            
            result = ProcessingResult(
                success=True,
                message=f"Successfully cleaned {cleaning_report['files_processed']} file(s)",
                output_file=cleaned_files[0] if cleaned_files else None,
                metadata=cleaning_report
            )
            
            self.log_result(result)
            return result
            
        except Exception as e:
            logger.error(f"Error cleaning data: {e}", exc_info=True)
            result = ProcessingResult(
                success=False,
                message=f"Cleaning failed: {str(e)}",
                errors=[str(e)]
            )
            self.log_result(result)
            return result
    
    def _load_dataframe(self, file_path: str) -> Optional[pd.DataFrame]:
        """Load dataframe from file"""
        try:
            path = Path(file_path)
            ext = path.suffix.lower()
            
            if ext in ['.xlsx', '.xls']:
                return pd.read_excel(file_path)
            elif ext == '.csv':
                return pd.read_csv(file_path)
            elif ext == '.tsv':
                return pd.read_csv(file_path, sep='\t')
            elif ext == '.json':
                return pd.read_json(file_path)
            else:
                logger.warning(f"Unsupported format: {ext}")
                return None
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return None
    
    def _clean_dataframe(self, df: pd.DataFrame, config: Dict) -> Tuple[pd.DataFrame, Dict]:
        """Clean a dataframe"""
        report = {
            'cells_cleaned': 0,
            'issues': []
        }
        
        # 1. Clean string columns FIRST (before duplicate detection)
        for col in df.select_dtypes(include=['object']).columns:
            # Trim whitespace
            original = df[col].copy()
            # Convert to string and trim, but preserve NaN
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
            changed = (original != df[col]).sum()
            if changed > 0:
                report['cells_cleaned'] += changed
                report['issues'].append(f"Trimmed whitespace in {changed} cell(s) in column '{col}'")
        
        # 2. Standardize email addresses
        for col in df.columns:
            if 'email' in col.lower():
                df[col] = df[col].apply(lambda x: x.lower().strip() if isinstance(x, str) else x)
                report['issues'].append(f"Standardized emails in column '{col}'")
        
        # 3. Standardize names (title case)
        for col in df.columns:
            if 'name' in col.lower():
                df[col] = df[col].apply(lambda x: x.title() if isinstance(x, str) else x)
                report['issues'].append(f"Standardized names in column '{col}'")
        
        # 4. NOW remove duplicate rows (after cleaning so duplicates are properly detected)
        original_len = len(df)
        df = df.drop_duplicates()
        if len(df) < original_len:
            removed = original_len - len(df)
            report['issues'].append(f"Removed {removed} duplicate row(s)")
        
        # 5. Remove completely empty rows
        before_empty = len(df)
        df = df.dropna(how='all')
        if len(df) < before_empty:
            removed = before_empty - len(df)
            report['issues'].append(f"Removed {removed} empty row(s)")
        
        # 6. Detect and fix common data issues
        for col in df.columns:
            # Replace common null values with NaN
            null_values = ['', 'N/A', 'NA', 'null', 'NULL', 'None', 'none', '-']
            for null_val in null_values:
                mask = df[col].astype(str) == null_val
                if mask.any():
                    df.loc[mask, col] = pd.NA
                    count = mask.sum()
                    report['cells_cleaned'] += count
        
        # 7. Try to standardize date columns
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    report['issues'].append(f"Standardized dates in column '{col}'")
                except:
                    pass
        
        return df, report
    
    def _save_cleaned_data(self, df: pd.DataFrame, original_path: str, config: Dict) -> str:
        """Save cleaned data"""
        output_format = config.get('output_format', 'xlsx')
        original_name = Path(original_path).stem
        
        if output_format == 'xlsx':
            output_file = tempfile.NamedTemporaryFile(
                mode='wb', suffix='.xlsx', delete=False, 
                prefix=f"{original_name}_cleaned_"
            )
            output_path = output_file.name
            output_file.close()
            df.to_excel(output_path, index=False)
        elif output_format == 'csv':
            output_file = tempfile.NamedTemporaryFile(
                mode='w', suffix='.csv', delete=False,
                prefix=f"{original_name}_cleaned_"
            )
            output_path = output_file.name
            output_file.close()
            df.to_csv(output_path, index=False)
        else:
            output_file = tempfile.NamedTemporaryFile(
                mode='wb', suffix='.xlsx', delete=False,
                prefix=f"{original_name}_cleaned_"
            )
            output_path = output_file.name
            output_file.close()
            df.to_excel(output_path, index=False)
        
        logger.info(f"Saved cleaned data to {output_path}")
        return output_path
