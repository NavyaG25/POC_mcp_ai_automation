"""
AI debugger for capturing context and responses for debugging.
Stores AI interactions and test context for analysis.
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from common.logger import Logger

class AIDebugger:
    """Captures AI context and responses for debugging purposes."""
    
    def __init__(self):
        self.logger = Logger.get_logger()
        self.debug_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(self.debug_dir, exist_ok=True)
        self.debug_file = os.path.join(self.debug_dir, 'ai_debug_responses.json')
        self.debug_data = []
    
    def capture_context(self, test_name: str, context_type: str, 
                       context_data: Dict[str, Any], 
                       ai_response: Optional[str] = None) -> None:
        """Capture test context and AI responses for debugging."""
        try:
            debug_entry = {
                'timestamp': datetime.now().isoformat(),
                'test_name': test_name,
                'context_type': context_type,
                'context_data': context_data,
                'ai_response': ai_response,
                'correlation_id': f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            }
            
            self.debug_data.append(debug_entry)
            
            # Save to file
            self._save_debug_data()
            
            self.logger.debug(f"AI context captured for {test_name}: {context_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to capture AI context: {e}")
    
    def capture_test_failure(self, test_name: str, error_message: str, 
                           stack_trace: str, test_data: Dict[str, Any]) -> None:
        """Capture test failure context for AI analysis."""
        failure_context = {
            'error_message': error_message,
            'stack_trace': stack_trace,
            'test_data': test_data,
            'failure_type': 'test_execution'
        }
        
        self.capture_context(
            test_name=test_name,
            context_type='test_failure',
            context_data=failure_context
        )
    
    def capture_mcp_interaction(self, test_name: str, mcp_function: str, 
                               parameters: Dict[str, Any], 
                               response: Dict[str, Any]) -> None:
        """Capture MCP function interactions for analysis."""
        mcp_context = {
            'mcp_function': mcp_function,
            'parameters': parameters,
            'response': response,
            'interaction_type': 'mcp_call'
        }
        
        self.capture_context(
            test_name=test_name,
            context_type='mcp_interaction',
            context_data=mcp_context
        )
    
    def capture_api_interaction(self, test_name: str, endpoint: str, 
                               method: str, request_data: Dict[str, Any],
                               response_data: Dict[str, Any]) -> None:
        """Capture API interactions for analysis."""
        api_context = {
            'endpoint': endpoint,
            'method': method,
            'request_data': request_data,
            'response_data': response_data,
            'interaction_type': 'api_call'
        }
        
        self.capture_context(
            test_name=test_name,
            context_type='api_interaction',
            context_data=api_context
        )
    
    def _save_debug_data(self) -> None:
        """Save debug data to JSON file."""
        try:
            with open(self.debug_file, 'w', encoding='utf-8') as f:
                json.dump(self.debug_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save debug data: {e}")
    
    def get_debug_summary(self, test_name: Optional[str] = None) -> Dict[str, Any]:
        """Get summary of debug information."""
        filtered_data = self.debug_data
        
        if test_name:
            filtered_data = [entry for entry in self.debug_data 
                           if entry.get('test_name') == test_name]
        
        summary = {
            'total_entries': len(filtered_data),
            'context_types': {},
            'test_names': set(),
            'latest_timestamp': None
        }
        
        for entry in filtered_data:
            context_type = entry.get('context_type', 'unknown')
            summary['context_types'][context_type] = summary['context_types'].get(context_type, 0) + 1
            summary['test_names'].add(entry.get('test_name'))
            
            if not summary['latest_timestamp'] or entry.get('timestamp', '') > summary['latest_timestamp']:
                summary['latest_timestamp'] = entry.get('timestamp')
        
        summary['test_names'] = list(summary['test_names'])
        
        return summary
