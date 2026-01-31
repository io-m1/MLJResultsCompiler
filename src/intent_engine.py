#!/usr/bin/env python3
"""
Intent Detection Engine for MLJ Results Compiler
Understands user requests and routes to appropriate processing agents
"""

import re
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Intent:
    """Represents a detected user intent"""
    name: str
    confidence: float
    extracted_params: Dict[str, Any]
    suggestions: List[str]


class IntentEngine:
    """Natural language intent detection for document processing"""
    
    INTENTS = {
        'test_consolidation': {
            'keywords': ['merge tests', 'combine results', 'consolidate scores', 'test results', 
                        'combine tests', 'merge scores', 'consolidate test', 'test consolidation',
                        'consolidate', 'merge', 'combine', 'test', 'tests'],
            'patterns': [r'test\s+\d+', r'consolidate.*test', r'merge.*xlsx', r'combine.*excel',
                        r'test.*result', r'merge.*test'],
            'confidence_threshold': 0.5
        },
        'invoice_processing': {
            'keywords': ['invoice', 'billing', 'payment', 'total cost', 'invoice total',
                        'sum invoices', 'billing summary', 'invoices'],
            'patterns': [r'invoice.*total', r'sum.*invoices?', r'billing.*summary', r'process.*invoice'],
            'confidence_threshold': 0.5
        },
        'image_extraction': {
            'keywords': ['extract', 'ocr', 'read image', 'scan', 'photo', 'extract text',
                        'read photo', 'scan document', 'image', 'picture'],
            'patterns': [r'extract.*image', r'read.*photo', r'ocr', r'scan.*text', r'text.*image'],
            'confidence_threshold': 0.5
        },
        'table_merge': {
            'keywords': ['combine tables', 'merge data', 'join', 'consolidate data',
                        'merge tables', 'combine data', 'join columns', 'table'],
            'patterns': [r'merge.*table', r'combine.*data', r'join.*column', r'table.*merge'],
            'confidence_threshold': 0.5
        },
        'report_generation': {
            'keywords': ['create report', 'generate summary', 'make document', 'generate report',
                        'create summary', 'make report', 'report', 'summary'],
            'patterns': [r'create.*report', r'generate.*summary', r'make.*document', r'report.*generate'],
            'confidence_threshold': 0.5
        },
        'data_cleaning': {
            'keywords': ['clean', 'fix', 'standardize', 'normalize', 'clean data',
                        'fix format', 'standardize data', 'cleaning'],
            'patterns': [r'clean.*data', r'fix.*format', r'standardize', r'normalize', r'data.*clean'],
            'confidence_threshold': 0.5
        }
    }
    
    def __init__(self):
        """Initialize the intent engine"""
        logger.info("Intent Engine initialized")
    
    def detect_intent(self, message: str) -> Dict[str, Any]:
        """
        Detect user intent from natural language message
        
        Args:
            message: User's natural language message
            
        Returns:
            Dictionary with:
                - intent: str (detected intent name)
                - confidence: float (0-1)
                - extracted_params: dict (extracted parameters)
                - suggestions: list (helpful suggestions)
        """
        if not message or not message.strip():
            return self._create_result('unknown', 0.0, {}, [])
        
        message_lower = message.lower().strip()
        
        # Calculate scores for each intent
        intent_scores = {}
        for intent_name, intent_config in self.INTENTS.items():
            score = self._calculate_intent_score(message_lower, intent_config)
            intent_scores[intent_name] = score
        
        # Get the best matching intent
        if not intent_scores:
            return self._create_result('unknown', 0.0, {}, [])
        
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent_name, confidence = best_intent
        
        # Check if confidence meets threshold
        threshold = self.INTENTS[intent_name]['confidence_threshold']
        if confidence < threshold:
            # Not confident enough, return unknown
            return self._create_result('unknown', confidence, {}, 
                                      self._get_suggestions_for_unclear_intent())
        
        # Extract parameters based on detected intent
        extracted_params = self.extract_parameters(message, intent_name)
        
        # Get suggestions for this intent
        suggestions = self.get_clarification_questions(intent_name, [])
        
        logger.info(f"Intent detected: {intent_name} (confidence: {confidence:.2%})")
        
        return self._create_result(intent_name, confidence, extracted_params, suggestions)
    
    def _calculate_intent_score(self, message: str, intent_config: Dict) -> float:
        """Calculate score for a specific intent"""
        score = 0.0
        
        # Keyword matching (50% weight)
        keywords = intent_config['keywords']
        keyword_matches = 0
        for keyword in keywords:
            if keyword.lower() in message:
                keyword_matches += 1
        
        if keywords:
            score += 0.5 * (keyword_matches / len(keywords))
        
        # Pattern matching (50% weight)
        patterns = intent_config['patterns']
        pattern_matches = 0
        for pattern in patterns:
            if re.search(pattern, message, re.IGNORECASE):
                pattern_matches += 1
        
        if patterns:
            score += 0.5 * (pattern_matches / len(patterns))
        
        # Boost score if we have any matches
        if keyword_matches > 0 or pattern_matches > 0:
            # Give bonus for multiple matches
            total_matches = keyword_matches + pattern_matches
            bonus = min(0.3, total_matches * 0.1)
            score += bonus
        
        return min(score, 1.0)
    
    def extract_parameters(self, message: str, intent: str) -> Dict[str, Any]:
        """
        Extract processing parameters from user message
        
        Args:
            message: User message
            intent: Detected intent
            
        Returns:
            Dictionary of extracted parameters
        """
        params = {}
        message_lower = message.lower()
        
        # Extract file types mentioned
        file_types = []
        if 'pdf' in message_lower:
            file_types.append('pdf')
        if 'excel' in message_lower or 'xlsx' in message_lower:
            file_types.append('xlsx')
        if 'image' in message_lower or 'jpg' in message_lower or 'png' in message_lower:
            file_types.append('image')
        if 'csv' in message_lower:
            file_types.append('csv')
        
        if file_types:
            params['file_types'] = file_types
        
        # Extract numbers (test numbers, counts, etc.)
        numbers = re.findall(r'\d+', message)
        if numbers:
            params['numbers'] = [int(n) for n in numbers]
        
        # Extract output format preferences
        if 'pdf' in message_lower and intent != 'invoice_processing':
            params['output_format'] = 'pdf'
        elif 'excel' in message_lower or 'xlsx' in message_lower:
            params['output_format'] = 'xlsx'
        elif 'word' in message_lower or 'docx' in message_lower:
            params['output_format'] = 'docx'
        
        return params
    
    def get_clarification_questions(self, intent: str, uploaded_files: List[Dict]) -> List[str]:
        """
        Generate intelligent follow-up questions based on context
        
        Args:
            intent: Detected intent
            uploaded_files: List of uploaded file metadata
            
        Returns:
            List of clarification questions
        """
        questions = []
        
        if intent == 'test_consolidation':
            if not uploaded_files:
                questions.append("Please upload your test Excel files (Test 1.xlsx, Test 2.xlsx, etc.)")
            else:
                questions.append("Upload more test files or use /consolidate to process")
        
        elif intent == 'invoice_processing':
            if not uploaded_files:
                questions.append("Please upload invoice files (PDF or images)")
            questions.append("What output format would you like? (Excel summary, PDF report)")
        
        elif intent == 'image_extraction':
            if not uploaded_files:
                questions.append("Please upload images containing text or tables")
            questions.append("Should I extract text, tables, or both?")
        
        elif intent == 'table_merge':
            if not uploaded_files:
                questions.append("Please upload the tables you want to merge (Excel, CSV)")
            questions.append("Which column should I use to match rows?")
        
        elif intent == 'report_generation':
            questions.append("What type of report would you like? (Summary, detailed analysis)")
            questions.append("Which format? (PDF, Word, Excel)")
        
        elif intent == 'data_cleaning':
            if not uploaded_files:
                questions.append("Please upload the data file you want to clean")
            questions.append("What specific cleaning operations do you need?")
        
        return questions
    
    def _create_result(self, intent: str, confidence: float, 
                      extracted_params: Dict[str, Any], 
                      suggestions: List[str]) -> Dict[str, Any]:
        """Create a standardized result dictionary"""
        return {
            'intent': intent,
            'confidence': confidence,
            'extracted_params': extracted_params,
            'suggestions': suggestions
        }
    
    def _get_suggestions_for_unclear_intent(self) -> List[str]:
        """Get suggestions when intent is unclear"""
        return [
            "I can help with:",
            "• Test result consolidation",
            "• Invoice processing",
            "• Text extraction from images",
            "• Merging tables",
            "• Generating reports",
            "• Data cleaning",
            "What would you like to do?"
        ]
