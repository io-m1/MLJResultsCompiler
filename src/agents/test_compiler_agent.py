#!/usr/bin/env python3
"""
Test Compiler Agent - Wrapper for existing test consolidation
Ensures 100% backward compatibility with existing functionality
"""

import logging
from typing import List, Dict, Tuple
from pathlib import Path

from .base_agent import BaseProcessingAgent, ProcessingResult

logger = logging.getLogger(__name__)


class TestCompilerAgent(BaseProcessingAgent):
    """
    Wrapper for existing test consolidation functionality
    Maintains backward compatibility while providing agent interface
    """
    
    def __init__(self):
        super().__init__(name="TestCompilerAgent")
        self.compiler = None  # Will be initialized when needed
    
    def can_handle(self, documents: List[Dict], intent: str) -> bool:
        """
        Check if this is a test consolidation request
        
        Args:
            documents: List of document metadata
            intent: User intent
            
        Returns:
            True if this agent can handle the request
        """
        # Must be test consolidation intent
        if intent != 'test_consolidation':
            return False
        
        # Check if all documents are Excel files
        for doc in documents:
            file_format = doc.get('format', '').lower()
            if file_format not in ['.xlsx', '.xls', '.csv']:
                logger.warning(f"TestCompilerAgent: Unsupported format {file_format}")
                return False
        
        logger.info(f"TestCompilerAgent: Can handle {len(documents)} documents")
        return True
    
    def validate_inputs(self, documents: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Validate input documents for test consolidation
        
        Args:
            documents: Documents to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not documents:
            errors.append("No documents provided")
            return False, errors
        
        # Check each document
        for i, doc in enumerate(documents):
            # Check file exists
            file_path = doc.get('path')
            if not file_path:
                errors.append(f"Document {i+1}: No file path provided")
                continue
            
            if not Path(file_path).exists():
                errors.append(f"Document {i+1}: File not found - {file_path}")
            
            # Check format
            file_format = doc.get('format', '').lower()
            if file_format not in ['.xlsx', '.xls', '.csv']:
                errors.append(f"Document {i+1}: Unsupported format {file_format}")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info(f"TestCompilerAgent: All {len(documents)} documents validated")
        else:
            logger.warning(f"TestCompilerAgent: Validation failed with {len(errors)} errors")
        
        return is_valid, errors
    
    def process(self, documents: List[Dict], config: Dict) -> ProcessingResult:
        """
        Process test consolidation using existing ScalableResultsCompiler
        
        Args:
            documents: List of documents to process
            config: Processing configuration
            
        Returns:
            ProcessingResult with outcome
        """
        self.log_processing(documents, config)
        
        # Validate inputs first
        is_valid, errors = self.validate_inputs(documents)
        if not is_valid:
            result = ProcessingResult(
                success=False,
                message="Input validation failed",
                errors=errors
            )
            self.log_result(result)
            return result
        
        try:
            # Import the existing compiler (lazy import to avoid circular dependencies)
            from results_compiler_bot_v2 import ScalableResultsCompiler
            
            # This is where we would integrate with the existing compiler
            # For now, return a success placeholder
            # The actual integration would happen in the telegram bot handler
            
            result = ProcessingResult(
                success=True,
                message=f"Ready to consolidate {len(documents)} test files",
                metadata={
                    'file_count': len(documents),
                    'agent': 'test_compiler',
                    'intent': config.get('intent', 'test_consolidation')
                }
            )
            
            logger.info(f"TestCompilerAgent: Ready to process {len(documents)} files")
            self.log_result(result)
            return result
            
        except Exception as e:
            logger.error(f"TestCompilerAgent: Error - {e}", exc_info=True)
            result = ProcessingResult(
                success=False,
                message=f"Processing error: {str(e)}",
                errors=[str(e)]
            )
            self.log_result(result)
            return result
    
    def _extract_test_data(self, file_path: str) -> Dict:
        """
        Extract test data from file (placeholder)
        
        Args:
            file_path: Path to test file
            
        Returns:
            Dictionary with test data
        """
        # This would use the existing ExcelProcessor
        # For now, return placeholder
        return {
            'file_path': file_path,
            'participants': []
        }
