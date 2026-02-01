#!/usr/bin/env python3
"""
Production Readiness Test
Tests: No debug code, hardcoded paths, logging quality, bot stability
Date: February 1, 2026
"""

import os
import sys
import logging
from pathlib import Path

# Force UTF-8 output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductionReadinessTester:
    """Test production readiness"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.issues = []
    
    def check_no_hardcoded_paths(self):
        """Test 1: No hardcoded paths"""
        logger.info("\n📋 Test 1: Hardcoded Paths Check")
        try:
            issues = []
            
            # Check main files
            files_to_check = [
                'telegram_bot.py',
                'config.py',
                'integration_v2.py',
                'data_validator.py'
            ]
            
            root = Path(__file__).parent
            suspicious_patterns = [
                r'C:\\',
                r'/home/',
                r'/Users/',
                r'D:\\',
                r'E:\\',
            ]
            
            for file_name in files_to_check:
                file_path = root / file_name
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Check for hardcoded absolute paths
                        lines = content.split('\n')
                        for i, line in enumerate(lines, 1):
                            if '/tmp/' in line or 'C:\\Users' in line or '/home/' in line:
                                if not ('Path' in line or 'input' in line or 'output' in line):
                                    issues.append(f"{file_name}:{i} - {line.strip()[:60]}")
            
            if issues:
                logger.warning(f"  Found {len(issues)} potential hardcoded paths:")
                for issue in issues[:5]:
                    logger.warning(f"    - {issue}")
                self.failed += 1
                self.issues.append(f"Hardcoded Paths: {len(issues)} found")
            else:
                logger.info("  ✅ No hardcoded paths detected")
                self.passed += 1
            
            return len(issues) == 0
        except Exception as e:
            logger.error(f"  ❌ Check failed: {e}")
            self.failed += 1
            self.issues.append(f"Hardcoded Paths Check: {e}")
            return False
    
    def check_no_debug_code(self):
        """Test 2: No debug/print statements"""
        logger.info("\n📋 Test 2: Debug Code Check")
        try:
            debug_issues = []
            
            files_to_check = [
                'telegram_bot.py',
                'integration_v2.py',
                'data_validator.py'
            ]
            
            root = Path(__file__).parent
            debug_patterns = [
                'print(',
                'pdb.set_trace',
                'breakpoint(',
                'import pdb',
                '# DEBUG',
                '# TODO:',
                'DEBUG = True',
            ]
            
            for file_name in files_to_check:
                file_path = root / file_name
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines, 1):
                            for pattern in debug_patterns:
                                if pattern in line and not line.strip().startswith('#'):
                                    debug_issues.append(f"{file_name}:{i}")
                                    break
            
            if debug_issues:
                logger.warning(f"  Found {len(debug_issues)} debug statements:")
                for issue in debug_issues[:5]:
                    logger.warning(f"    - {issue}")
                self.failed += 1
                self.issues.append(f"Debug Code: {len(debug_issues)} found")
            else:
                logger.info("  ✅ No debug code detected")
                self.passed += 1
            
            return len(debug_issues) == 0
        except Exception as e:
            logger.error(f"  ❌ Check failed: {e}")
            self.failed += 1
            self.issues.append(f"Debug Code Check: {e}")
            return False
    
    def check_logging_quality(self):
        """Test 3: Logging is properly configured"""
        logger.info("\n📋 Test 3: Logging Quality Check")
        try:
            # Check if logging is imported in main files
            telegram_bot_path = Path(__file__).parent / 'telegram_bot.py'
            
            if telegram_bot_path.exists():
                with open(telegram_bot_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    has_logging_import = 'import logging' in content
                    has_logger = 'logger = logging.getLogger' in content
                    has_handlers = 'handlers=[' in content or 'logging.basicConfig' in content
                    
                    if has_logging_import and has_logger:
                        logger.info("  ✅ Logging properly configured")
                        self.passed += 1
                        return True
                    else:
                        logger.warning("  ⚠️  Logging not fully configured")
                        logger.warning(f"    - Import: {has_logging_import}")
                        logger.warning(f"    - Logger: {has_logger}")
                        self.failed += 1
                        self.issues.append("Logging not fully configured")
                        return False
            else:
                logger.warning("  ⚠️  telegram_bot.py not found")
                self.failed += 1
                return False
        except Exception as e:
            logger.error(f"  ❌ Check failed: {e}")
            self.failed += 1
            self.issues.append(f"Logging Check: {e}")
            return False
    
    def check_error_handling(self):
        """Test 4: Error handling is comprehensive"""
        logger.info("\n📋 Test 4: Error Handling Check")
        try:
            telegram_bot_path = Path(__file__).parent / 'telegram_bot.py'
            
            if telegram_bot_path.exists():
                with open(telegram_bot_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    has_try_except = 'try:' in content and 'except' in content
                    has_error_logging = 'logger.error' in content
                    has_exception_info = 'exc_info=True' in content or 'traceback' in content
                    
                    checks = {
                        'Try/Except blocks': has_try_except,
                        'Error logging': has_error_logging,
                        'Exception info': has_exception_info
                    }
                    
                    passed = sum(1 for v in checks.values() if v)
                    
                    for check, status in checks.items():
                        logger.info(f"    - {check}: {'YES' if status else 'NO'}")
                    
                    if passed >= 2:
                        logger.info("  ✅ Error handling appears comprehensive")
                        self.passed += 1
                        return True
                    else:
                        logger.warning("  ⚠️  Error handling may need improvement")
                        self.failed += 1
                        self.issues.append("Error handling incomplete")
                        return False
            else:
                logger.warning("  ⚠️  telegram_bot.py not found")
                self.failed += 1
                return False
        except Exception as e:
            logger.error(f"  ❌ Check failed: {e}")
            self.failed += 1
            self.issues.append(f"Error Handling Check: {e}")
            return False
    
    def check_config_completeness(self):
        """Test 5: Configuration is complete"""
        logger.info("\n📋 Test 5: Configuration Completeness Check")
        try:
            config_path = Path(__file__).parent / 'config.py'
            env_example_path = Path(__file__).parent / '.env.example'
            
            issues = []
            
            # Check .env.example exists
            if not env_example_path.exists():
                issues.append(".env.example not found")
            
            # Check config.py has required sections
            if config_path.exists():
                with open(config_path, 'r') as f:
                    content = f.read()
                    
                    required_configs = [
                        'input_folder',
                        'output_folder',
                        'merge_strategy',
                        'processing_strategy'
                    ]
                    
                    for req_config in required_configs:
                        if req_config not in content:
                            issues.append(f"Missing config: {req_config}")
            
            if issues:
                logger.warning(f"  Found {len(issues)} config issues:")
                for issue in issues:
                    logger.warning(f"    - {issue}")
                self.failed += 1
                self.issues.append(f"Config Issues: {len(issues)}")
                return False
            else:
                logger.info("  ✅ Configuration is complete")
                self.passed += 1
                return True
        except Exception as e:
            logger.error(f"  ❌ Check failed: {e}")
            self.failed += 1
            self.issues.append(f"Config Check: {e}")
            return False
    
    def check_environment_setup(self):
        """Test 6: Environment is properly set up"""
        logger.info("\n📋 Test 6: Environment Setup Check")
        try:
            root = Path(__file__).parent
            required_files = [
                'requirements.txt',
                'config.py',
                'telegram_bot.py',
                '.env.example',
                'Procfile',
                'runtime.txt'
            ]
            
            missing = []
            for file_name in required_files:
                file_path = root / file_name
                if not file_path.exists():
                    missing.append(file_name)
            
            if missing:
                logger.warning(f"  Missing files: {', '.join(missing)}")
                self.failed += 1
                self.issues.append(f"Missing files: {', '.join(missing)}")
                return False
            else:
                logger.info("  ✅ All required files present")
                self.passed += 1
                return True
        except Exception as e:
            logger.error(f"  ❌ Check failed: {e}")
            self.failed += 1
            self.issues.append(f"Environment Check: {e}")
            return False
    
    def run_all_checks(self):
        """Run all production readiness checks"""
        logger.info("=" * 60)
        logger.info("PRODUCTION READINESS TEST SUITE")
        logger.info("=" * 60)
        logger.info(f"\n🚀 RUNNING PRODUCTION CHECKS\n")
        
        self.check_no_hardcoded_paths()
        self.check_no_debug_code()
        self.check_logging_quality()
        self.check_error_handling()
        self.check_config_completeness()
        self.check_environment_setup()
        
        # Print summary
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        logger.info("\n" + "=" * 60)
        logger.info("PRODUCTION READINESS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Checks Passed: {self.passed}")
        logger.info(f"Checks Failed: {self.failed}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info("=" * 60)
        
        if self.issues:
            logger.warning(f"\nIssues Found ({len(self.issues)}):")
            for issue in self.issues:
                logger.warning(f"  - {issue}")
            logger.warning("\n⚠️  Fix issues before deploying to production")
        else:
            logger.info("\n✅ All checks passed! System is production-ready")
        
        return self.passed, self.failed


def main():
    tester = ProductionReadinessTester()
    passed, failed = tester.run_all_checks()
    
    if failed > 0:
        logger.warning(f"\nProduction readiness check incomplete. {failed} issues found.")
        sys.exit(1)
    else:
        logger.info(f"\n✅ System is PRODUCTION READY")
        sys.exit(0)


if __name__ == "__main__":
    main()
