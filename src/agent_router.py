#!/usr/bin/env python3
"""
Agent Router for MLJ Results Compiler
Routes requests to specialized processing agents
"""

import logging
from typing import Dict, Any, Tuple, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProcessingConfig:
    """Configuration for agent processing"""
    intent: str
    files: List[Dict[str, Any]]
    output_format: str = 'xlsx'
    merge_strategy: str = 'email'
    custom_options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_options is None:
            self.custom_options = {}


class BaseProcessingAgent:
    """Base class for processing agents (placeholder)"""
    
    def can_handle(self, documents: List[Dict], intent: str) -> bool:
        """Check if agent can process given documents"""
        return False
    
    def process(self, documents: List[Dict], config: ProcessingConfig) -> Dict[str, Any]:
        """Execute processing logic"""
        return {
            'success': False,
            'message': 'Base agent cannot process - use specialized agent'
        }


class TestCompilerAgent(BaseProcessingAgent):
    """Agent for test consolidation (wraps existing functionality)"""
    
    def can_handle(self, documents: List[Dict], intent: str) -> bool:
        """Check if this is a test consolidation request"""
        if intent != 'test_consolidation':
            return False
        
        # Check if all documents are spreadsheets
        for doc in documents:
            file_format = doc.get('format', '')
            if file_format not in ['.xlsx', '.xls', '.csv']:
                return False
        
        return True
    
    def process(self, documents: List[Dict], config: ProcessingConfig) -> Dict[str, Any]:
        """Process test consolidation using existing compiler"""
        logger.info(f"Test Compiler Agent processing {len(documents)} files")
        
        # This will be integrated with existing ScalableResultsCompiler
        return {
            'success': True,
            'message': f'Ready to consolidate {len(documents)} test files',
            'agent': 'test_compiler',
            'files_count': len(documents)
        }


class GenericProcessorAgent(BaseProcessingAgent):
    """Fallback agent for generic processing"""
    
    def can_handle(self, documents: List[Dict], intent: str) -> bool:
        """Can handle any request as fallback"""
        return True
    
    def process(self, documents: List[Dict], config: ProcessingConfig) -> Dict[str, Any]:
        """Generic processing"""
        logger.info(f"Generic Processor Agent handling {len(documents)} files")
        
        return {
            'success': True,
            'message': f'Processing {len(documents)} files with generic handler',
            'agent': 'generic',
            'files_count': len(documents)
        }


class AgentRouter:
    """Routes requests to specialized processing agents"""
    
    def __init__(self):
        """Initialize agent router with available agents"""
        self.agents = {
            'test_compiler': TestCompilerAgent(),
            'generic': GenericProcessorAgent(),
        }
        logger.info("Agent Router initialized with agents: " + ", ".join(self.agents.keys()))
    
    def route(self, intent: str, documents: List[Dict]) -> Tuple[BaseProcessingAgent, ProcessingConfig]:
        """
        Select best agent for the job
        
        Args:
            intent: Detected user intent
            documents: List of document metadata
            
        Returns:
            Tuple of (selected_agent, processing_config)
        """
        # Routing map - defines which agent handles which intent
        routing_map = {
            'test_consolidation': 'test_compiler',
            'invoice_processing': 'generic',  # Placeholder
            'image_extraction': 'generic',     # Placeholder
            'table_merge': 'generic',          # Placeholder
            'report_generation': 'generic',    # Placeholder
            'data_cleaning': 'generic',        # Placeholder
        }
        
        # Get agent name from routing map
        agent_name = routing_map.get(intent, 'generic')
        
        # Get the agent instance
        agent = self.agents.get(agent_name, self.agents['generic'])
        
        # Verify agent can handle this request
        if not agent.can_handle(documents, intent):
            logger.warning(f"Agent {agent_name} cannot handle intent {intent}, using fallback")
            agent = self.agents['generic']
        
        # Build processing configuration
        config = self._build_config(intent, documents)
        
        logger.info(f"Routed intent '{intent}' to agent '{agent_name}'")
        
        return agent, config
    
    def can_chain_agents(self, intent: str, documents: List[Dict]) -> List[str]:
        """
        Determine if multiple agents needed (e.g., OCR → Merge → Report)
        
        Args:
            intent: User intent
            documents: Document list
            
        Returns:
            List of agent names to chain (empty if single agent sufficient)
        """
        # For now, single agent processing
        # Future enhancement: support agent chaining
        return []
    
    def _build_config(self, intent: str, documents: List[Dict]) -> ProcessingConfig:
        """
        Build agent-specific configuration
        
        Args:
            intent: User intent
            documents: Document list
            
        Returns:
            ProcessingConfig object
        """
        # Extract file formats
        file_formats = [doc.get('format', '') for doc in documents]
        
        # Determine output format based on intent
        output_format = 'xlsx'  # Default
        if intent == 'report_generation':
            output_format = 'pdf'
        
        # Determine merge strategy
        merge_strategy = 'email'
        if intent == 'test_consolidation':
            merge_strategy = 'email'
        elif intent == 'table_merge':
            merge_strategy = 'auto'
        
        config = ProcessingConfig(
            intent=intent,
            files=documents,
            output_format=output_format,
            merge_strategy=merge_strategy,
            custom_options={
                'file_formats': file_formats,
                'file_count': len(documents)
            }
        )
        
        return config
    
    def get_agent_info(self, agent_name: str) -> Dict[str, Any]:
        """Get information about a specific agent"""
        agent = self.agents.get(agent_name)
        if not agent:
            return {'exists': False}
        
        return {
            'exists': True,
            'name': agent_name,
            'type': type(agent).__name__,
            'description': agent.__class__.__doc__ or 'No description'
        }
    
    def list_agents(self) -> List[str]:
        """List all available agents"""
        return list(self.agents.keys())
