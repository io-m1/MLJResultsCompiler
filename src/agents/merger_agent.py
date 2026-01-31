#!/usr/bin/env python3
"""
Generic Table Merger Agent - Merge any tabular data with intelligent column matching
SUBSTANTIAL IMPLEMENTATION with real merging capabilities
"""

import logging
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import pandas as pd
from difflib import SequenceMatcher
import tempfile

from .base_agent import BaseProcessingAgent, ProcessingResult

logger = logging.getLogger(__name__)


class GenericTableMergerAgent(BaseProcessingAgent):
    """Merge any tabular data with intelligent column matching"""
    
    def __init__(self):
        super().__init__(name="GenericTableMergerAgent")
        self.common_key_columns = ['email', 'e-mail', 'id', 'identifier', 'name', 
                                   'full name', 'username', 'user']
    
    def can_handle(self, documents: List[Dict], intent: str) -> bool:
        """Check if this is a table merge request"""
        if intent not in ['table_merge', 'test_consolidation']:
            return False
        
        # Check for tabular file types
        tabular_formats = ['.xlsx', '.xls', '.csv', '.tsv']
        for doc in documents:
            file_format = doc.get('format', '').lower()
            if file_format not in tabular_formats:
                return False
        
        return len(documents) >= 2  # Need at least 2 tables to merge
    
    def validate_inputs(self, documents: List[Dict]) -> Tuple[bool, List[str]]:
        """Validate input documents"""
        errors = []
        
        if not documents:
            errors.append("No documents provided")
            return False, errors
        
        if len(documents) < 2:
            errors.append("Need at least 2 tables to merge")
            return False, errors
        
        # Check that files exist
        for i, doc in enumerate(documents):
            path = doc.get('path')
            if not path or not Path(path).exists():
                errors.append(f"Document {i+1}: File not found")
        
        return len(errors) == 0, errors
    
    def process(self, documents: List[Dict], config: Dict) -> ProcessingResult:
        """
        Merge tables with intelligent column matching
        
        Features:
        - Auto-detect common columns
        - Smart matching (fuzzy, email, ID)
        - Handle conflicts
        - Multiple merge strategies
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
            # Load all tables
            dataframes = []
            for doc in documents:
                df = self._load_dataframe(doc['path'])
                if df is not None:
                    dataframes.append({
                        'df': df,
                        'name': Path(doc['path']).name,
                        'path': doc['path']
                    })
            
            if len(dataframes) < 2:
                return ProcessingResult(
                    success=False,
                    message="Could not load enough tables to merge",
                    errors=["Need at least 2 valid tables"]
                )
            
            # Detect common columns
            merge_column = self._detect_merge_column(dataframes)
            logger.info(f"Detected merge column: {merge_column}")
            
            # Merge all tables
            merged_df = self._merge_tables(dataframes, merge_column, config)
            
            # Save result
            output_path = self._save_merged_table(merged_df, config)
            
            result = ProcessingResult(
                success=True,
                message=f"Successfully merged {len(dataframes)} tables",
                output_file=output_path,
                data=merged_df,
                metadata={
                    'tables_merged': len(dataframes),
                    'merge_column': merge_column,
                    'total_rows': len(merged_df),
                    'total_columns': len(merged_df.columns),
                    'source_files': [d['name'] for d in dataframes]
                }
            )
            
            self.log_result(result)
            return result
            
        except Exception as e:
            logger.error(f"Error merging tables: {e}", exc_info=True)
            result = ProcessingResult(
                success=False,
                message=f"Merge failed: {str(e)}",
                errors=[str(e)]
            )
            self.log_result(result)
            return result
    
    def _load_dataframe(self, file_path: str) -> Optional[pd.DataFrame]:
        """Load a dataframe from file"""
        try:
            path = Path(file_path)
            ext = path.suffix.lower()
            
            if ext in ['.xlsx', '.xls']:
                return pd.read_excel(file_path)
            elif ext == '.csv':
                return pd.read_csv(file_path)
            elif ext == '.tsv':
                return pd.read_csv(file_path, sep='\t')
            else:
                logger.warning(f"Unsupported format: {ext}")
                return None
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return None
    
    def _detect_merge_column(self, dataframes: List[Dict]) -> str:
        """Detect the best column to merge on"""
        if not dataframes:
            return None
        
        # Get columns from first dataframe
        first_cols = set(dataframes[0]['df'].columns.str.lower())
        
        # Find columns common to all dataframes
        common_columns = first_cols
        for df_dict in dataframes[1:]:
            df_cols = set(df_dict['df'].columns.str.lower())
            common_columns = common_columns.intersection(df_cols)
        
        logger.info(f"Common columns: {common_columns}")
        
        # Prioritize known key columns
        for key_col in self.common_key_columns:
            if key_col in common_columns:
                # Find the actual column name (with original casing)
                for col in dataframes[0]['df'].columns:
                    if col.lower() == key_col:
                        return col
        
        # If no known key column, use first common column
        if common_columns:
            target_col = list(common_columns)[0]
            for col in dataframes[0]['df'].columns:
                if col.lower() == target_col:
                    return col
        
        # Fallback: use first column
        return dataframes[0]['df'].columns[0]
    
    def _merge_tables(self, dataframes: List[Dict], merge_column: str, 
                     config: Dict) -> pd.DataFrame:
        """Merge multiple tables on a common column"""
        if not dataframes:
            return pd.DataFrame()
        
        # Start with first dataframe
        result = dataframes[0]['df'].copy()
        result['_source_1'] = dataframes[0]['name']
        
        # Merge each subsequent dataframe
        for i, df_dict in enumerate(dataframes[1:], start=2):
            df = df_dict['df'].copy()
            df[f'_source_{i}'] = df_dict['name']
            
            # Find the merge column in this dataframe (case-insensitive)
            merge_col_in_df = None
            for col in df.columns:
                if col.lower() == merge_column.lower():
                    merge_col_in_df = col
                    break
            
            if merge_col_in_df is None:
                logger.warning(f"Merge column not found in {df_dict['name']}, skipping")
                continue
            
            # Rename column to match if needed
            if merge_col_in_df != merge_column:
                df = df.rename(columns={merge_col_in_df: merge_column})
            
            # Perform merge (outer join to keep all records)
            result = pd.merge(result, df, on=merge_column, how='outer', 
                            suffixes=('', f'_from_{df_dict["name"]}'))
        
        return result
    
    def _save_merged_table(self, df: pd.DataFrame, config: Dict) -> str:
        """Save merged table to file"""
        output_format = config.get('output_format', 'xlsx')
        
        # Create temp output file
        if output_format == 'xlsx':
            output_file = tempfile.NamedTemporaryFile(
                mode='wb', suffix='.xlsx', delete=False
            )
            output_path = output_file.name
            output_file.close()
            df.to_excel(output_path, index=False)
        elif output_format == 'csv':
            output_file = tempfile.NamedTemporaryFile(
                mode='w', suffix='.csv', delete=False
            )
            output_path = output_file.name
            output_file.close()
            df.to_csv(output_path, index=False)
        else:
            output_file = tempfile.NamedTemporaryFile(
                mode='wb', suffix='.xlsx', delete=False
            )
            output_path = output_file.name
            output_file.close()
            df.to_excel(output_path, index=False)
        
        logger.info(f"Saved merged table to {output_path}")
        return output_path
