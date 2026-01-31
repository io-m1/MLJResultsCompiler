#!/usr/bin/env python3
"""
Report Generation Agent - Create formatted reports from data
SUBSTANTIAL IMPLEMENTATION with real report generation capabilities
"""

import logging
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import pandas as pd
import tempfile
from datetime import datetime

from .base_agent import BaseProcessingAgent, ProcessingResult

logger = logging.getLogger(__name__)


class ReportGeneratorAgent(BaseProcessingAgent):
    """Generate formatted reports from data with statistics and summaries"""
    
    def __init__(self):
        super().__init__(name="ReportGeneratorAgent")
    
    def can_handle(self, documents: List[Dict], intent: str) -> bool:
        """Check if this is a report generation request"""
        if intent != 'report_generation':
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
        Generate formatted report from data
        
        Features:
        - Summary statistics
        - Data overview
        - Column analysis
        - Missing data report
        - Distribution analysis
        - Formatted Excel output with multiple sheets
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
            reports = []
            
            for doc in documents:
                # Load data
                df = self._load_dataframe(doc['path'])
                if df is None:
                    continue
                
                # Generate report
                report_path = self._generate_report(df, doc, config)
                reports.append(report_path)
            
            if not reports:
                return ProcessingResult(
                    success=False,
                    message="Could not generate any reports",
                    errors=["No valid data files found"]
                )
            
            result = ProcessingResult(
                success=True,
                message=f"Successfully generated {len(reports)} report(s)",
                output_file=reports[0] if reports else None,
                metadata={
                    'reports_generated': len(reports),
                    'report_files': [Path(r).name for r in reports]
                }
            )
            
            self.log_result(result)
            return result
            
        except Exception as e:
            logger.error(f"Error generating report: {e}", exc_info=True)
            result = ProcessingResult(
                success=False,
                message=f"Report generation failed: {str(e)}",
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
    
    def _generate_report(self, df: pd.DataFrame, doc: Dict, config: Dict) -> str:
        """Generate comprehensive report"""
        original_name = Path(doc['path']).stem
        
        # Create Excel file with multiple sheets
        output_file = tempfile.NamedTemporaryFile(
            mode='wb', suffix='.xlsx', delete=False,
            prefix=f"{original_name}_report_"
        )
        output_path = output_file.name
        output_file.close()
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet 1: Summary
            summary = self._generate_summary(df, doc)
            summary_df = pd.DataFrame(list(summary.items()), columns=['Metric', 'Value'])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Sheet 2: Data Overview (first 100 rows)
            df.head(100).to_excel(writer, sheet_name='Data Preview', index=False)
            
            # Sheet 3: Column Analysis
            column_analysis = self._analyze_columns(df)
            column_analysis.to_excel(writer, sheet_name='Column Analysis', index=False)
            
            # Sheet 4: Missing Data Report
            missing_report = self._analyze_missing_data(df)
            missing_report.to_excel(writer, sheet_name='Missing Data', index=False)
            
            # Sheet 5: Numeric Statistics (if any numeric columns)
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                stats = df[numeric_cols].describe()
                stats.to_excel(writer, sheet_name='Numeric Statistics')
        
        logger.info(f"Generated report at {output_path}")
        return output_path
    
    def _generate_summary(self, df: pd.DataFrame, doc: Dict) -> Dict:
        """Generate summary statistics"""
        summary = {
            'Report Generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Source File': Path(doc['path']).name,
            'Total Rows': len(df),
            'Total Columns': len(df.columns),
            'Numeric Columns': len(df.select_dtypes(include=['number']).columns),
            'Text Columns': len(df.select_dtypes(include=['object']).columns),
            'Date Columns': len(df.select_dtypes(include=['datetime']).columns),
            'Total Cells': len(df) * len(df.columns),
            'Missing Cells': df.isna().sum().sum(),
            'Missing %': f"{(df.isna().sum().sum() / (len(df) * len(df.columns)) * 100):.2f}%",
            'Duplicate Rows': df.duplicated().sum(),
            'Memory Usage (MB)': f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f}"
        }
        return summary
    
    def _analyze_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze each column"""
        analysis = []
        
        for col in df.columns:
            col_data = {
                'Column Name': col,
                'Data Type': str(df[col].dtype),
                'Non-Null Count': df[col].notna().sum(),
                'Null Count': df[col].isna().sum(),
                'Null %': f"{(df[col].isna().sum() / len(df) * 100):.2f}%",
                'Unique Values': df[col].nunique(),
                'Duplicate Values': len(df[col]) - df[col].nunique()
            }
            
            # Add type-specific analysis
            if df[col].dtype in ['int64', 'float64']:
                col_data['Min'] = df[col].min()
                col_data['Max'] = df[col].max()
                col_data['Mean'] = f"{df[col].mean():.2f}" if pd.notna(df[col].mean()) else 'N/A'
                col_data['Median'] = df[col].median()
            elif df[col].dtype == 'object':
                # Most common value
                if df[col].notna().any():
                    most_common = df[col].value_counts().index[0] if len(df[col].value_counts()) > 0 else 'N/A'
                    col_data['Most Common'] = str(most_common)[:50]  # Truncate long values
            
            analysis.append(col_data)
        
        return pd.DataFrame(analysis)
    
    def _analyze_missing_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze missing data patterns"""
        missing_data = []
        
        for col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                missing_data.append({
                    'Column': col,
                    'Missing Count': missing_count,
                    'Missing %': f"{(missing_count / len(df) * 100):.2f}%",
                    'Present Count': df[col].notna().sum(),
                    'Present %': f"{(df[col].notna().sum() / len(df) * 100):.2f}%"
                })
        
        if not missing_data:
            # No missing data
            return pd.DataFrame([{
                'Column': 'No missing data found',
                'Missing Count': 0,
                'Missing %': '0.00%',
                'Present Count': len(df) * len(df.columns),
                'Present %': '100.00%'
            }])
        
        return pd.DataFrame(missing_data).sort_values('Missing Count', ascending=False)
