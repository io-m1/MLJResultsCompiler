#!/usr/bin/env python3
"""
Base Agent Classes for MLJ Results Compiler
Abstract interfaces for specialized processing agents
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result from agent processing"""
    success: bool
    message: str
    output_file: str = None
    data: Any = None
    metadata: Dict[str, Any] = None
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class BaseProcessingAgent(ABC):
    """Abstract base class for all processing agents"""
    
    def __init__(self, name: str = "BaseAgent"):
        """
        Initialize base agent
        
        Args:
            name: Agent name for logging
        """
        self.name = name
        logger.info(f"{self.name} initialized")
    
    @abstractmethod
    def can_handle(self, documents: List[Dict], intent: str) -> bool:
        """
        Check if agent can process given documents
        
        Args:
            documents: List of document metadata
            intent: User intent
            
        Returns:
            True if agent can handle this request
        """
        pass
    
    @abstractmethod
    def process(self, documents: List[Dict], config: Dict) -> ProcessingResult:
        """
        Execute processing logic
        
        Args:
            documents: List of documents to process
            config: Processing configuration
            
        Returns:
            ProcessingResult with outcome
        """
        pass
    
    @abstractmethod
    def validate_inputs(self, documents: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Validate input documents
        
        Args:
            documents: Documents to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        pass
    
    def generate_preview(self, result: ProcessingResult, max_lines: int = 10) -> str:
        """
        Generate text preview of results
        
        Args:
            result: ProcessingResult to preview
            max_lines: Maximum lines to include
            
        Returns:
            Text preview
        """
        if not result.success:
            return f"❌ Processing failed: {result.message}"
        
        preview = f"✅ {result.message}\n\n"
        
        if result.metadata:
            preview += "📊 **Summary:**\n"
            for key, value in list(result.metadata.items())[:5]:
                preview += f"  • {key}: {value}\n"
        
        if result.warnings:
            preview += f"\n⚠️ {len(result.warnings)} warning(s)\n"
        
        return preview
    
    def log_processing(self, documents: List[Dict], config: Dict):
        """Log processing start"""
        logger.info(f"{self.name}: Processing {len(documents)} documents")
        logger.debug(f"{self.name}: Config: {config}")
    
    def log_result(self, result: ProcessingResult):
        """Log processing result"""
        if result.success:
            logger.info(f"{self.name}: Processing completed successfully")
        else:
            logger.error(f"{self.name}: Processing failed - {result.message}")
        
        if result.errors:
            for error in result.errors:
                logger.error(f"{self.name}: {error}")
        
        if result.warnings:
            for warning in result.warnings:
                logger.warning(f"{self.name}: {warning}")
