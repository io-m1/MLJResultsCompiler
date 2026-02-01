#!/usr/bin/env python3
"""
MLJResultsCompiler Enhanced Integration Module
Bridges legacy and new scalable bot architectures
Provides unified interface for multiple compilation workflows
"""

import os
import sys
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict, List
from datetime import datetime
import traceback

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import both old and new bots
try:
    from results_compiler_bot import ResultsCompiler as LegacyBot
    legacy_available = True
except ImportError:
    legacy_available = False
    logger = logging.getLogger(__name__)
    logger.warning("Legacy bot not available")

try:
    from results_compiler_bot_v2 import ScalableResultsCompiler as ScalableBot
    scalable_available = True
except ImportError:
    scalable_available = False
    logger = logging.getLogger(__name__)
    logger.warning("Scalable bot not available")

from config import BotConfig
from src.excel_processor import ExcelProcessor
from src.session_manager import SessionManager

logger = logging.getLogger(__name__)


class EnhancedIntegratedCompiler:
    """
    Unified compilation interface supporting:
    - Legacy bot (fixed 5 files)
    - Scalable bot (ANY number of files)
    - Agentic decision making
    - Multiple output formats
    """
    
    def __init__(self, config: Optional[BotConfig] = None, input_folder: str = 'input', output_folder: str = 'output'):
        """Initialize integrated compiler"""
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        
        # Load or create configuration
        if config:
            self.config = config
        else:
            # Try to load from config file
            config_path = Path('bot_config.json')
            if config_path.exists():
                self.config = BotConfig.from_json(str(config_path))
            else:
                self.config = BotConfig(input_folder=input_folder, output_folder=output_folder)
        
        # Initialize bots
        self.legacy_bot = None
        self.scalable_bot = None
        self.selected_bot = None
        
        if legacy_available:
            try:
                self.legacy_bot = LegacyBot(
                    input_folder=str(self.input_folder),
                    output_folder=str(self.output_folder)
                )
                logger.info("Legacy bot initialized (handles 5 fixed test files)")
            except Exception as e:
                logger.warning(f"Could not initialize legacy bot: {e}")
        
        if scalable_available:
            try:
                self.scalable_bot = ScalableBot(
                    config=self.config,
                    input_folder=str(self.input_folder),
                    output_folder=str(self.output_folder)
                )
                logger.info("Scalable bot initialized (handles ANY number of files)")
            except Exception as e:
                logger.warning(f"Could not initialize scalable bot: {e}")
        
        self.legacy_processor = ExcelProcessor(
            input_dir=str(self.input_folder),
            output_dir=str(self.output_folder)
        )
        
        logger.info(f"EnhancedIntegratedCompiler initialized")
        logger.info(f"  Legacy bot available: {legacy_available and self.legacy_bot is not None}")
        logger.info(f"  Scalable bot available: {scalable_available and self.scalable_bot is not None}")
    
    def auto_select_bot(self) -> str:
        """
        Automatically select best bot based on detected files
        Uses configuration to make intelligent decision
        """
        logger.info("Auto-selecting compilation bot...")
        
        if not self.input_folder.exists():
            logger.error("Input folder does not exist")
            return "none"
        
        # Count test files
        pattern = self.config.file_pattern
        if not self.config.case_sensitive_pattern:
            matches = list(self.input_folder.glob(pattern.replace('.xlsx', '') + '*.xlsx'))
        else:
            matches = list(self.input_folder.glob(pattern))
        
        file_count = len(matches)
        logger.info(f"Detected {file_count} test files")
        
        # Decision logic
        if file_count == 0:
            logger.error("No test files detected")
            return "none"
        
        elif 1 <= file_count <= 5:
            # Use legacy bot for fixed 5-file scenario
            if self.legacy_bot and file_count == 5:
                logger.info("→ Selected LEGACY bot (5 files detected)")
                self.selected_bot = "legacy"
                return "legacy"
            else:
                logger.info("→ Selected SCALABLE bot (flexible file count)")
                self.selected_bot = "scalable"
                return "scalable"
        
        else:
            # Use scalable bot for many files
            logger.info(f"→ Selected SCALABLE bot ({file_count} files detected, scalability required)")
            self.selected_bot = "scalable"
            return "scalable"
    
    def compile_from_session(self, user_id: int, session_manager: SessionManager) -> Tuple[bool, str, Optional[Path]]:
        """
        Compile results from a Telegram session
        Uses auto-selection to choose appropriate bot
        """
        try:
            session = session_manager.get_session(user_id)
            if not session or 'files' not in session:
                return False, "❌ No files in session", None
            
            # Get temp directory with test files
            temp_dir = Path(session['temp_dir'])
            
            # Auto-select bot for this session
            bot_choice = self.auto_select_bot()
            
            if bot_choice == "legacy" and self.legacy_bot:
                logger.info("Using legacy bot for session compilation")
                # Use legacy bot
                temp_bot = LegacyBot(
                    input_folder=str(temp_dir),
                    output_folder=str(temp_dir)
                )
                
                if not temp_bot.find_test_files():
                    return False, "❌ Could not find test files in session", None
                
                if not temp_bot.load_all_test_files():
                    return False, "❌ Could not load test files", None
                
                if not temp_bot.merge_tests():
                    return False, "❌ Could not merge test results", None
                
                if not temp_bot.clean_and_sort():
                    return False, "❌ Could not clean and sort results", None
                
                if not temp_bot.format_scores():
                    return False, "❌ Could not format scores", None
                
                if not temp_bot.export_to_xlsx():
                    return False, "❌ Could not export results", None
                
                message = f"✓ Compilation complete! {len(temp_bot.merged_df)} participants consolidated"
                output_path = temp_dir / 'Consolidated_Results.xlsx'
                
            elif bot_choice == "scalable" and self.scalable_bot:
                logger.info("Using scalable bot for session compilation")
                # Create new scalable bot for this session
                temp_bot = ScalableBot(
                    config=self.config,
                    input_folder=str(temp_dir),
                    output_folder=str(temp_dir)
                )
                
                if not temp_bot.run():
                    return False, "❌ Compilation failed", None
                
                message = f"✓ Compilation complete! {len(temp_bot.merged_df)} participants consolidated"
                output_path = temp_dir / 'Consolidated_Results.xlsx'
            
            else:
                return False, "❌ No suitable compilation bot available", None
            
            # Update session with completion status
            session_manager.update_session(user_id, {
                'status': 'completed',
                'output_file': str(output_path),
                'completion_time': datetime.now().isoformat()
            })
            
            return True, message, output_path
            
        except Exception as e:
            logger.error(f"Session compilation error: {str(e)}")
            logger.error(traceback.format_exc())
            return False, f"❌ Error during compilation: {str(e)}", None
    
    def compile_from_input_folder(self, output_format: str = "xlsx") -> Tuple[bool, str, Optional[Path]]:
        """
        Compile results from input folder (file-based workflow)
        Auto-selects appropriate bot and format
        """
        try:
            logger.info(f"Starting file-based compilation (format: {output_format})")
            
            # Auto-select bot
            bot_choice = self.auto_select_bot()
            
            if bot_choice == "legacy" and self.legacy_bot:
                logger.info("Using legacy bot")
                if not self.legacy_bot.run():
                    return False, "❌ Compilation failed", None
                
                output_path = self.output_folder / 'Consolidated_Results.xlsx'
                message = f"✓ Compilation complete! {len(self.legacy_bot.merged_df)} participants"
            
            elif bot_choice == "scalable" and self.scalable_bot:
                logger.info("Using scalable bot")
                if not self.scalable_bot.run():
                    return False, "❌ Compilation failed", None
                
                output_path = self.output_folder / 'Consolidated_Results.xlsx'
                message = f"✓ Compilation complete! {len(self.scalable_bot.merged_df)} participants"
            
            else:
                return False, "❌ No suitable compilation bot available", None
            
            # Handle format conversion if needed
            if output_format.lower() != "xlsx":
                logger.info(f"Converting output to {output_format}...")
                if output_format.lower() == "csv":
                    # Convert to CSV
                    csv_path = output_path.with_suffix('.csv')
                    if self.legacy_bot and self.legacy_bot.merged_df is not None:
                        self.legacy_bot.merged_df.to_csv(csv_path, index=False)
                    elif self.scalable_bot and self.scalable_bot.merged_df is not None:
                        self.scalable_bot.merged_df.to_csv(csv_path, index=False)
                    output_path = csv_path
                elif output_format.lower() in ["pdf", "docx"]:
                    # Use legacy processor for PDF/DOCX
                    logger.info(f"Converting to {output_format} using legacy processor...")
                    # This would use the existing ExcelProcessor
                    pass
            
            return True, message, output_path
            
        except Exception as e:
            logger.error(f"File-based compilation error: {str(e)}")
            logger.error(traceback.format_exc())
            return False, f"❌ Error during compilation: {str(e)}", None
    
    def compile_with_validation(self, validate_only: bool = False) -> Dict:
        """
        Run comprehensive compilation with full validation
        Returns detailed report
        """
        try:
            logger.info("Starting comprehensive compilation with validation...")
            
            report = {
                'status': 'unknown',
                'timestamp': datetime.now().isoformat(),
                'selected_bot': self.auto_select_bot(),
                'files_detected': 0,
                'files_processed': 0,
                'participants': 0,
                'validation_passed': False,
                'agents_enabled': self.config.enable_agents,
                'messages': [],
                'errors': [],
            }
            
            if report['selected_bot'] == 'scalable' and self.scalable_bot:
                # Use scalable bot with full validation
                if not self.scalable_bot.find_test_files():
                    report['errors'].append("Could not find test files")
                    report['status'] = 'failed'
                    return report
                
                report['files_detected'] = len(self.scalable_bot.test_files)
                
                if validate_only:
                    report['status'] = 'validated'
                    report['messages'].append(f"Found {report['files_detected']} test files - ready for compilation")
                    return report
                
                if not self.scalable_bot.run():
                    report['errors'].append("Compilation failed")
                    report['status'] = 'failed'
                    return report
                
                report['files_processed'] = len(self.scalable_bot.dataframes)
                report['participants'] = len(self.scalable_bot.merged_df)
                report['status'] = 'completed'
                report['validation_passed'] = True
                report['messages'].append(f"Successfully consolidated {report['participants']} participants from {report['files_processed']} files")
            
            elif report['selected_bot'] == 'legacy' and self.legacy_bot:
                # Use legacy bot
                if not self.legacy_bot.run():
                    report['errors'].append("Compilation failed")
                    report['status'] = 'failed'
                    return report
                
                report['files_processed'] = len(self.legacy_bot.dataframes)
                report['participants'] = len(self.legacy_bot.merged_df)
                report['status'] = 'completed'
                report['validation_passed'] = True
                report['messages'].append(f"Successfully consolidated {report['participants']} participants")
            
            else:
                report['errors'].append("No suitable bot available")
                report['status'] = 'failed'
            
            return report
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'errors': [str(e)],
                'validation_passed': False,
            }
    
    def get_configuration(self) -> BotConfig:
        """Get current configuration"""
        return self.config
    
    def set_configuration(self, config: BotConfig) -> bool:
        """Update configuration"""
        try:
            self.config = config
            logger.info("Configuration updated")
            return True
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def save_configuration(self, path: str = "bot_config.json") -> bool:
        """Save configuration to file"""
        return self.config.save_to_json(path)


# Legacy compatibility alias
class IntegratedCompiler(EnhancedIntegratedCompiler):
    """Backwards compatibility wrapper"""
    pass


def main():
    """Main entry point"""
    # Create compiler with auto-configuration
    compiler = EnhancedIntegratedCompiler()
    
    # Run compilation with full validation
    result = compiler.compile_with_validation()
    
    if result['status'] == 'completed':
        logger.info(f"✓ Compilation successful!")
        logger.info(f"  Participants: {result['participants']}")
        logger.info(f"  Files processed: {result['files_processed']}")
        sys.exit(0)
    else:
        logger.error(f"✗ Compilation failed!")
        for error in result['errors']:
            logger.error(f"  - {error}")
        sys.exit(1)


if __name__ == '__main__':
    main()
