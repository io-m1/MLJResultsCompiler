#!/usr/bin/env python3
"""
MLJResultsCompiler Integration Module
Bridges the new results_compiler_bot with the existing src/excel_processor infrastructure
Enables seamless operation on Render with Telegram webhooks
"""

import os
import sys
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict
from datetime import datetime
import traceback

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from results_compiler_bot import ResultsCompiler
from src.excel_processor import ExcelProcessor
from src.session_manager import SessionManager

logger = logging.getLogger(__name__)

class IntegratedCompiler:
    """
    Unified compilation interface that works with both the new bot and existing infrastructure
    Handles both file-based (input/output folders) and session-based (Telegram) workflows
    """
    
    def __init__(self, input_folder: str = 'input', output_folder: str = 'output'):
        """Initialize integrated compiler"""
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.new_bot = ResultsCompiler(
            input_folder=str(self.input_folder),
            output_folder=str(self.output_folder)
        )
        self.legacy_processor = ExcelProcessor(
            input_dir=str(self.input_folder),
            output_dir=str(self.output_folder)
        )
        logger.info(f"IntegratedCompiler initialized with input={self.input_folder}, output={self.output_folder}")
    
    def compile_from_session(self, user_id: int, session_manager: SessionManager) -> Tuple[bool, str, Optional[Path]]:
        """
        Compile results from a Telegram session
        
        Args:
            user_id: Telegram user ID
            session_manager: SessionManager instance with active session
            
        Returns:
            Tuple of (success: bool, message: str, output_path: Optional[Path])
        """
        try:
            session = session_manager.get_session(user_id)
            if not session or 'files' not in session:
                return False, "❌ No files in session", None
            
            # Get temp directory with test files
            temp_dir = Path(session['temp_dir'])
            
            # Create temporary compiler with session temp directory
            temp_compiler = ResultsCompiler(
                input_folder=str(temp_dir),
                output_folder=str(temp_dir)
            )
            
            # Run compilation pipeline
            if not temp_compiler.find_test_files():
                return False, "❌ Could not find test files in session", None
            
            if not temp_compiler.load_all_test_files():
                return False, "❌ Could not load test files", None
            
            if not temp_compiler.merge_tests():
                return False, "❌ Could not merge test results", None
            
            if not temp_compiler.clean_and_sort():
                return False, "❌ Could not clean and sort results", None
            
            if not temp_compiler.format_scores():
                return False, "❌ Could not format scores", None
            
            if not temp_compiler.export_to_xlsx(filename='Consolidated_Results.xlsx'):
                return False, "❌ Could not export results", None
            
            output_path = temp_dir / 'Consolidated_Results.xlsx'
            
            # Update session
            session_manager.set_compilation_status(user_id, 'ready', str(output_path))
            
            return True, f"✅ Compiled {len(temp_compiler.merged_df)} participants", output_path
            
        except Exception as e:
            logger.error(f"Error in compile_from_session: {str(e)}")
            logger.error(traceback.format_exc())
            return False, f"❌ Compilation error: {str(e)}", None
    
    def compile_from_input_folder(self, format: str = 'xlsx') -> Tuple[bool, str, Optional[Path]]:
        """
        Compile results from files in input/ folder (standard workflow)
        
        Args:
            format: Output format ('xlsx', 'pdf', 'docx')
            
        Returns:
            Tuple of (success: bool, message: str, output_path: Optional[Path])
        """
        try:
            # Use new bot for compilation
            if not self.new_bot.find_test_files():
                return False, "❌ Could not find test files (expected TEST_1 through TEST_5)", None
            
            if not self.new_bot.load_all_test_files():
                return False, "❌ Could not load test files", None
            
            if not self.new_bot.merge_tests():
                return False, "❌ Could not merge test results", None
            
            if not self.new_bot.clean_and_sort():
                return False, "❌ Could not clean and sort results", None
            
            if not self.new_bot.format_scores():
                return False, "❌ Could not format scores", None
            
            # Export in requested format
            if format.lower() == 'xlsx':
                if not self.new_bot.export_to_xlsx():
                    return False, "❌ Could not export to XLSX", None
                output_path = self.output_folder / 'Consolidated_Results.xlsx'
            
            elif format.lower() == 'pdf':
                # Use legacy processor for PDF/DOCX (has those capabilities)
                if not self.legacy_processor.load_all_tests(max_tests=5):
                    return False, "❌ Could not load test files for PDF export", None
                
                consolidated = self.legacy_processor.consolidate_results()
                if not consolidated:
                    return False, "❌ Could not consolidate results for PDF", None
                
                if not self.legacy_processor.save_as_pdf(consolidated, "Consolidated_Results.pdf"):
                    return False, "❌ Could not save as PDF", None
                
                output_path = self.output_folder / 'Consolidated_Results.pdf'
            
            elif format.lower() == 'docx':
                # Use legacy processor for DOCX
                if not self.legacy_processor.load_all_tests(max_tests=5):
                    return False, "❌ Could not load test files for DOCX export", None
                
                consolidated = self.legacy_processor.consolidate_results()
                if not consolidated:
                    return False, "❌ Could not consolidate results for DOCX", None
                
                if not self.legacy_processor.save_as_docx(consolidated, "Consolidated_Results.docx"):
                    return False, "❌ Could not save as DOCX", None
                
                output_path = self.output_folder / 'Consolidated_Results.docx'
            
            else:
                return False, f"❌ Unsupported format: {format}", None
            
            # Generate summary
            participant_count = len(self.new_bot.merged_df) if self.new_bot.merged_df is not None else 0
            message = f"✅ Compiled {participant_count} participants to {format.upper()}"
            
            return True, message, output_path
            
        except Exception as e:
            logger.error(f"Error in compile_from_input_folder: {str(e)}")
            logger.error(traceback.format_exc())
            return False, f"❌ Compilation error: {str(e)}", None
    
    def compile_with_validation(self) -> Dict:
        """
        Run full compilation with validation checks
        Returns detailed report
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'status': 'STARTED',
            'steps': {}
        }
        
        try:
            # Step 1: Find files
            step1_success = self.new_bot.find_test_files()
            report['steps']['find_files'] = {
                'status': 'PASS' if step1_success else 'FAIL',
                'files_found': len(self.new_bot.test_files)
            }
            if not step1_success:
                report['status'] = 'FAILED'
                return report
            
            # Step 2: Load files
            step2_success = self.new_bot.load_all_test_files()
            report['steps']['load_files'] = {
                'status': 'PASS' if step2_success else 'FAIL',
                'dataframes_loaded': len(self.new_bot.dataframes)
            }
            if not step2_success:
                report['status'] = 'FAILED'
                return report
            
            # Step 3: Merge
            step3_success = self.new_bot.merge_tests()
            report['steps']['merge'] = {
                'status': 'PASS' if step3_success else 'FAIL',
                'participants': len(self.new_bot.merged_df) if self.new_bot.merged_df is not None else 0
            }
            if not step3_success:
                report['status'] = 'FAILED'
                return report
            
            # Step 4: Clean & Sort
            step4_success = self.new_bot.clean_and_sort()
            report['steps']['clean_sort'] = {
                'status': 'PASS' if step4_success else 'FAIL'
            }
            if not step4_success:
                report['status'] = 'FAILED'
                return report
            
            # Step 5: Format
            step5_success = self.new_bot.format_scores()
            report['steps']['format'] = {
                'status': 'PASS' if step5_success else 'FAIL'
            }
            if not step5_success:
                report['status'] = 'FAILED'
                return report
            
            # Step 6: Export
            step6_success = self.new_bot.export_to_xlsx()
            report['steps']['export'] = {
                'status': 'PASS' if step6_success else 'FAIL'
            }
            
            report['status'] = 'COMPLETE' if step6_success else 'FAILED'
            report['output_file'] = str(self.output_folder / 'Consolidated_Results.xlsx')
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            report['status'] = 'ERROR'
            report['error'] = str(e)
        
        return report


def main():
    """CLI entry point for testing integrated compiler"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MLJ Results Compiler - Integrated')
    parser.add_argument('--format', '-f', choices=['xlsx', 'pdf', 'docx'], default='xlsx')
    parser.add_argument('--input', '-i', default='input')
    parser.add_argument('--output', '-o', default='output')
    parser.add_argument('--validate', action='store_true', help='Run with full validation report')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create compiler
    compiler = IntegratedCompiler(input_folder=args.input, output_folder=args.output)
    
    # Run compilation
    if args.validate:
        report = compiler.compile_with_validation()
        print("\n" + "="*60)
        print("VALIDATION REPORT")
        print("="*60)
        for key, value in report.items():
            print(f"{key}: {value}")
    else:
        success, message, output_path = compiler.compile_from_input_folder(format=args.format)
        print(message)
        if success:
            print(f"Output: {output_path}")
            return 0
        else:
            return 1


if __name__ == '__main__':
    sys.exit(main())
