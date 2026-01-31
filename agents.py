#!/usr/bin/env python3
"""
Agentic Capabilities for MLJResultsCompiler
Autonomous agents for validation, optimization, and quality assurance
Enables self-healing and intelligent decision-making
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

# Make pandas/numpy imports lazy - only import when needed
# This allows the bot to run even if pandas isn't immediately available
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None
    np = None
    logger.warning("pandas/numpy not available - agent optimization features will be limited")


class AgentStatus(Enum):
    """Status of an agent's work"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REMEDIATED = "remediated"


@dataclass
class AgentReport:
    """Report from an agent's analysis"""
    agent_name: str
    status: AgentStatus
    issues_found: int
    issues_fixed: int
    timestamp: str
    message: str
    details: Dict[str, Any]
    
    def __str__(self) -> str:
        icon = {
            AgentStatus.COMPLETED: "✓",
            AgentStatus.REMEDIATED: "✓",
            AgentStatus.FAILED: "✗",
            AgentStatus.IDLE: "-",
            AgentStatus.RUNNING: "⟳",
        }[self.status]
        return f"{icon} {self.agent_name}: {self.message} (Issues: {self.issues_found}, Fixed: {self.issues_fixed})"


class ValidationAgent:
    """Validates data quality and structure"""
    
    def __init__(self):
        self.name = "ValidationAgent"
        self.issues = []
        self.fixes = []
    
    def validate_dataframe(self, df: pd.DataFrame, file_name: str = "Unknown") -> AgentReport:
        """
        Comprehensive validation of a dataframe
        Returns AgentReport with findings
        """
        self.issues = []
        self.fixes = []
        
        logger.info(f"ValidationAgent: Analyzing {file_name}")
        
        # Check for empty dataframe
        if df.empty:
            self.issues.append(f"{file_name}: DataFrame is empty")
            return self._create_report(AgentStatus.FAILED)
        
        # Check for all-NaN columns
        for col in df.columns:
            if df[col].isna().all():
                self.issues.append(f"Column '{col}' is entirely NaN")
        
        # Check for required columns
        required_indicators = ['name', 'email', 'score']
        found_indicators = [col.lower() for col in df.columns]
        for indicator in required_indicators:
            if not any(indicator in col.lower() for col in df.columns):
                self.issues.append(f"Missing column matching '{indicator}'")
        
        # Check for duplicate emails
        if 'email' in [col.lower() for col in df.columns]:
            email_col = next(col for col in df.columns if col.lower() == 'email')
            duplicates = df[email_col].duplicated().sum()
            if duplicates > 0:
                self.issues.append(f"Found {duplicates} duplicate email addresses")
        
        # Check for invalid score values
        score_cols = [col for col in df.columns if 'score' in col.lower()]
        for score_col in score_cols:
            invalid_scores = df[~df[score_col].isna()][~df[score_col].apply(self._is_valid_score)].shape[0]
            if invalid_scores > 0:
                self.issues.append(f"Column '{score_col}' has {invalid_scores} invalid score values")
        
        status = AgentStatus.COMPLETED if not self.issues else AgentStatus.FAILED
        return self._create_report(status, f"Validated {file_name}")
    
    def validate_merged_data(self, df: pd.DataFrame) -> AgentReport:
        """Validate consolidated/merged data"""
        self.issues = []
        self.fixes = []
        
        logger.info("ValidationAgent: Analyzing merged dataset")
        
        # Check for sufficient data
        if df.shape[0] < 1:
            self.issues.append("Merged dataset is empty")
        
        # Check for consistency across test columns
        test_cols = [col for col in df.columns if 'test' in col.lower()]
        if test_cols:
            for idx, row in df.iterrows():
                non_nan_count = row[test_cols].notna().sum()
                if non_nan_count == 0:
                    self.issues.append(f"Row {idx}: No test scores present")
        
        # Check email/name consistency
        if 'email' in [col.lower() for col in df.columns]:
            email_col = next(col for col in df.columns if col.lower() == 'email')
            invalid_emails = df[~df[email_col].isna()][~df[email_col].apply(self._is_valid_email)].shape[0]
            if invalid_emails > 0:
                self.issues.append(f"Found {invalid_emails} invalid email addresses")
        
        status = AgentStatus.COMPLETED if not self.issues else AgentStatus.FAILED
        return self._create_report(status, f"Validated {df.shape[0]} consolidated records")
    
    @staticmethod
    def _is_valid_score(value) -> bool:
        """Check if a score is valid"""
        if pd.isna(value):
            return True
        try:
            num = float(value)
            return 0 <= num <= 100
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def _is_valid_email(email) -> bool:
        """Check if email is valid"""
        if pd.isna(email):
            return True
        email_str = str(email).strip()
        return '@' in email_str and '.' in email_str
    
    def _create_report(self, status: AgentStatus, message: str = "") -> AgentReport:
        """Create an agent report"""
        return AgentReport(
            agent_name=self.name,
            status=status,
            issues_found=len(self.issues),
            issues_fixed=len(self.fixes),
            timestamp=datetime.now().isoformat(),
            message=message or f"Found {len(self.issues)} issues",
            details={
                'issues': self.issues,
                'fixes': self.fixes,
            }
        )


class OptimizationAgent:
    """Optimizes data processing and performance"""
    
    def __init__(self):
        self.name = "OptimizationAgent"
        self.suggestions = []
    
    def analyze_file_structure(self, file_list: List[str]) -> AgentReport:
        """Analyze file structure and suggest optimal processing strategy"""
        self.suggestions = []
        
        logger.info(f"OptimizationAgent: Analyzing {len(file_list)} files")
        
        if len(file_list) > 100:
            self.suggestions.append("Large number of files detected. Consider batch processing.")
        
        if len(file_list) > 1000:
            self.suggestions.append("Very large file set. Consider parallel processing to improve performance.")
        
        if len(file_list) == 0:
            self.suggestions.append("No files found. Check input folder path.")
        
        return AgentReport(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            issues_found=0,
            issues_fixed=0,
            timestamp=datetime.now().isoformat(),
            message=f"Analyzed {len(file_list)} files",
            details={'suggestions': self.suggestions}
        )
    
    def suggest_merge_strategy(self, dataframes: Dict[str, pd.DataFrame]) -> AgentReport:
        """Suggest optimal merge strategy based on data characteristics"""
        self.suggestions = []
        
        logger.info(f"OptimizationAgent: Analyzing merge strategy for {len(dataframes)} datasets")
        
        # Check if email is consistent key
        all_have_email = all('email' in [col.lower() for col in df.columns] for df in dataframes.values())
        if all_have_email:
            self.suggestions.append("Email column found in all files. Email merge strategy recommended.")
        
        # Check if data is consistently ordered
        first_df = next(iter(dataframes.values())) if dataframes else None
        if first_df is not None and len(dataframes) > 1:
            # Check if row order matches
            dfs = list(dataframes.values())
            if len(dfs) > 1:
                self.suggestions.append(f"Detected {len(dataframes)} datasets. Using email-based outer join for comprehensive merge.")
        
        return AgentReport(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            issues_found=0,
            issues_fixed=0,
            timestamp=datetime.now().isoformat(),
            message="Generated optimization suggestions",
            details={'suggestions': self.suggestions}
        )
    
    def suggest_color_scheme(self, file_count: int) -> Dict[str, str]:
        """Suggest appropriate color scheme based on file count"""
        # Generate contrasting colors for any number of files
        colors = {}
        base_colors = [
            'FFFFFF',  # White
            '87CEEB',  # Sky Blue
            'FFFF00',  # Yellow
            '556B2F',  # Army Green
            'FF0000',  # Red
            '800080',  # Purple
            '00FFFF',  # Cyan
            'FFA500',  # Orange
            '90EE90',  # Light Green
            'FFB6C1',  # Light Pink
            '00008B',  # Dark Blue
            'FF1493',  # Deep Pink
        ]
        
        for i in range(file_count):
            colors[f'Test_{i+1}'] = base_colors[i % len(base_colors)]
        
        logger.info(f"OptimizationAgent: Generated color scheme for {file_count} tests")
        return colors


class QualityAgent:
    """Monitors data quality and provides insights"""
    
    def __init__(self):
        self.name = "QualityAgent"
        self.metrics = {}
    
    def assess_data_quality(self, df: pd.DataFrame) -> AgentReport:
        """Assess overall data quality"""
        self.metrics = {}
        
        logger.info("QualityAgent: Assessing data quality")
        
        # Calculate completeness
        total_cells = df.shape[0] * df.shape[1]
        non_null_cells = df.notna().sum().sum()
        completeness = (non_null_cells / total_cells * 100) if total_cells > 0 else 0
        
        self.metrics['completeness_percent'] = round(completeness, 2)
        self.metrics['total_records'] = df.shape[0]
        self.metrics['total_fields'] = df.shape[1]
        self.metrics['null_records'] = df.isna().sum().sum()
        
        # Quality score (0-100)
        quality_score = min(100, completeness)
        
        status = AgentStatus.COMPLETED
        message = f"Data quality: {quality_score:.1f}% complete"
        if quality_score < 70:
            message += " (Warning: Quality below 70%)"
            status = AgentStatus.FAILED
        
        return AgentReport(
            agent_name=self.name,
            status=status,
            issues_found=int(self.metrics['null_records']),
            issues_fixed=0,
            timestamp=datetime.now().isoformat(),
            message=message,
            details=self.metrics
        )
    
    def generate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive statistics"""
        stats = {
            'record_count': df.shape[0],
            'field_count': df.shape[1],
            'completeness_percent': round(df.notna().sum().sum() / (df.shape[0] * df.shape[1]) * 100, 2),
            'duplicate_emails': 0,
            'invalid_emails': 0,
            'score_columns': [],
            'score_statistics': {},
        }
        
        # Email analysis
        email_cols = [col for col in df.columns if 'email' in col.lower()]
        if email_cols:
            email_col = email_cols[0]
            stats['duplicate_emails'] = df[email_col].duplicated().sum()
            stats['invalid_emails'] = df[~df[email_col].isna()][~df[email_col].apply(lambda x: '@' in str(x))].shape[0]
        
        # Score analysis
        score_cols = [col for col in df.columns if 'test' in col.lower() or 'score' in col.lower()]
        for score_col in score_cols:
            numeric_col = pd.to_numeric(df[score_col], errors='coerce')
            stats['score_columns'].append(score_col)
            stats['score_statistics'][score_col] = {
                'mean': round(numeric_col.mean(), 2),
                'median': round(numeric_col.median(), 2),
                'min': round(numeric_col.min(), 2),
                'max': round(numeric_col.max(), 2),
                'std': round(numeric_col.std(), 2),
            }
        
        return stats


class RemediationAgent:
    """Attempts to fix identified issues"""
    
    def __init__(self):
        self.name = "RemediationAgent"
        self.fixes_applied = []
    
    def fix_column_naming(self, df: pd.DataFrame, column_mapping) -> Tuple[pd.DataFrame, List[str]]:
        """Attempt to fix column naming issues"""
        self.fixes_applied = []
        
        logger.info("RemediationAgent: Attempting column name normalization")
        
        # Normalize column names
        new_columns = {}
        for col in df.columns:
            col_lower = col.lower().strip()
            
            # Check against name variations
            for variation in column_mapping.name_variations:
                if variation == col_lower:
                    new_columns[col] = 'Full Name'
                    self.fixes_applied.append(f"Renamed '{col}' → 'Full Name'")
                    break
            
            # Check against email variations
            for variation in column_mapping.email_variations:
                if variation == col_lower:
                    new_columns[col] = 'Email'
                    self.fixes_applied.append(f"Renamed '{col}' → 'Email'")
                    break
            
            # Check against score variations
            for variation in column_mapping.score_variations:
                if variation == col_lower:
                    new_columns[col] = 'Score'
                    self.fixes_applied.append(f"Renamed '{col}' → 'Score'")
                    break
        
        if new_columns:
            df = df.rename(columns=new_columns)
            logger.info(f"RemediationAgent: Applied {len(self.fixes_applied)} column fixes")
        
        return df, self.fixes_applied
    
    def fix_invalid_emails(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        """Attempt to fix invalid emails"""
        fixes = 0
        
        email_cols = [col for col in df.columns if col.lower() == 'email']
        if not email_cols:
            return df, fixes
        
        email_col = email_cols[0]
        
        for idx, val in df[email_col].items():
            if pd.isna(val):
                continue
            
            email_str = str(val).strip()
            
            # Fix common issues
            if email_str and '@' not in email_str and '.' in email_str:
                # Might be missing @
                parts = email_str.split('.')
                if len(parts) >= 2:
                    # Try to reconstruct
                    potential_email = email_str.replace('.', '@', 1)
                    if '@' in potential_email:
                        df.at[idx, email_col] = potential_email
                        self.fixes_applied.append(f"Fixed email at row {idx}: {email_str} → {potential_email}")
                        fixes += 1
        
        return df, fixes


class AgentOrchestrator:
    """Coordinates all agents in the system"""
    
    def __init__(self, config=None):
        self.config = config
        self.validation_agent = ValidationAgent()
        self.optimization_agent = OptimizationAgent()
        self.quality_agent = QualityAgent()
        self.remediation_agent = RemediationAgent()
        self.reports = []
        
        logger.info("AgentOrchestrator: Initialized with 4 agents")
    
    def validate_files(self, dataframes: Dict[str, pd.DataFrame]) -> List[AgentReport]:
        """Run validation on all dataframes"""
        reports = []
        for file_name, df in dataframes.items():
            report = self.validation_agent.validate_dataframe(df, file_name)
            reports.append(report)
            logger.info(str(report))
        return reports
    
    def validate_merged(self, df: pd.DataFrame) -> AgentReport:
        """Run validation on merged data"""
        report = self.validation_agent.validate_merged_data(df)
        logger.info(str(report))
        return report
    
    def optimize(self, files: List[str], dataframes: Dict[str, pd.DataFrame]) -> List[AgentReport]:
        """Run optimization analysis"""
        reports = []
        
        file_report = self.optimization_agent.analyze_file_structure(files)
        reports.append(file_report)
        logger.info(str(file_report))
        
        merge_report = self.optimization_agent.suggest_merge_strategy(dataframes)
        reports.append(merge_report)
        logger.info(str(merge_report))
        
        return reports
    
    def assess_quality(self, df: pd.DataFrame) -> AgentReport:
        """Assess data quality"""
        report = self.quality_agent.assess_data_quality(df)
        logger.info(str(report))
        return report
    
    def generate_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive insights"""
        return self.quality_agent.generate_statistics(df)
    
    def remediate(self, df: pd.DataFrame, column_mapping) -> Tuple[pd.DataFrame, List[str]]:
        """Attempt remediation of issues"""
        df, fixes = self.remediation_agent.fix_column_naming(df, column_mapping)
        df, email_fixes = self.remediation_agent.fix_invalid_emails(df)
        
        all_fixes = fixes + [f"Email fix: {i}" for i in range(email_fixes)]
        return df, all_fixes
    
    def generate_report(self) -> str:
        """Generate comprehensive orchestration report"""
        report = "=" * 60 + "\n"
        report += "AGENT ORCHESTRATOR REPORT\n"
        report += "=" * 60 + "\n"
        
        for r in self.reports:
            report += f"\n{str(r)}\n"
        
        report += "\n" + "=" * 60 + "\n"
        return report
