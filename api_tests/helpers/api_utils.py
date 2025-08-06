"""
API utilities for HTTP request handling and response processing.
Provides standardized API interaction methods with error handling.
"""
import requests
import json
import time
from typing import Dict, Any, Optional, Tuple
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from common.logger import Logger
from common.config_loader import ConfigLoader
from common.ai_debugger import AIDebugger

class APIUtils:
    """Utility class for API interactions with comprehensive error handling."""
    
    def __init__(self):
        self.logger = Logger.get_logger()
        self.config = ConfigLoader.get_api_config()
        self.ai_debugger = AIDebugger()
        self.session = self._create_session()
        self.base_url = self.config['base_url']
        
        # Initialize configuration
        ConfigLoader.load_config()
        self.logger.info("API Utils initialized with base URL: " + self.base_url)
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()
        
        # Define retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def make_request(self, method: str, endpoint: str, 
                    data: Optional[Dict[str, Any]] = None,
                    headers: Optional[Dict[str, str]] = None,
                    params: Optional[Dict[str, Any]] = None,
                    timeout: int = 10,
                    test_name: str = "api_request") -> Tuple[bool, Dict[str, Any]]:
        """
        Make HTTP request with comprehensive error handling and logging.
        
        Returns:
            Tuple[bool, Dict]: (success, response_data)
        """
        url = f"{self.base_url}{endpoint}"
        correlation_id = f"api_{int(time.time() * 1000)}"
        
        # Prepare headers
        default_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Automation-Framework/1.0'
        }
        
        if headers:
            default_headers.update(headers)
        
        # Prepare request data
        json_data = json.dumps(data) if data else None
        
        try:
            self.logger.info(f"Making {method} request to {url}")
            
            # Make the request
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                headers=default_headers,
                params=params,
                timeout=timeout
            )
            
            # Parse response
            try:
                response_data = response.json() if response.text else {}
            except json.JSONDecodeError:
                response_data = {'raw_response': response.text}
            
            # Prepare response info
            response_info = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'data': response_data,
                'url': url,
                'method': method,
                'success': response.status_code < 400
            }
            
            # Log API interaction
            Logger.log_api_response(
                method=method,
                url=url,
                status_code=response.status_code,
                request_data=data,
                response_data=response_data,
                correlation_id=correlation_id
            )
            
            # Capture AI debug context
            self.ai_debugger.capture_api_interaction(
                test_name=test_name,
                endpoint=endpoint,
                method=method,
                request_data=data or {},
                response_data=response_info
            )
            
            if response.status_code < 400:
                self.logger.info(f"Request successful: {method} {url} - Status: {response.status_code}")
                return True, response_info
            else:
                self.logger.warning(f"Request failed: {method} {url} - Status: {response.status_code}")
                return False, response_info
                
        except requests.exceptions.Timeout:
            error_info = {
                'error': 'timeout',
                'message': f'Request timed out after {timeout} seconds',
                'url': url,
                'method': method
            }
            self.logger.error(f"Request timeout: {method} {url}")
            return False, error_info
            
        except requests.exceptions.ConnectionError:
            error_info = {
                'error': 'connection_error',
                'message': 'Failed to establish connection',
                'url': url,
                'method': method
            }
            self.logger.error(f"Connection error: {method} {url}")
            return False, error_info
            
        except Exception as e:
            error_info = {
                'error': 'unexpected_error',
                'message': str(e),
                'url': url,
                'method': method
            }
            self.logger.error(f"Unexpected error in API request: {e}")
            return False, error_info
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            test_name: str = "api_get") -> Tuple[bool, Dict[str, Any]]:
        """Make GET request."""
        return self.make_request('GET', endpoint, params=params, headers=headers, test_name=test_name)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None,
             test_name: str = "api_post") -> Tuple[bool, Dict[str, Any]]:
        """Make POST request."""
        return self.make_request('POST', endpoint, data=data, headers=headers, test_name=test_name)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            test_name: str = "api_put") -> Tuple[bool, Dict[str, Any]]:
        """Make PUT request."""
        return self.make_request('PUT', endpoint, data=data, headers=headers, test_name=test_name)
    
    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None,
               test_name: str = "api_delete") -> Tuple[bool, Dict[str, Any]]:
        """Make DELETE request."""
        return self.make_request('DELETE', endpoint, headers=headers, test_name=test_name)
    
    def validate_response_structure(self, response_data: Dict[str, Any], 
                                  required_fields: list,
                                  test_name: str = "response_validation") -> Tuple[bool, str]:
        """
        Validate response structure contains required fields.
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            if not isinstance(response_data, dict):
                return False, "Response is not a JSON object"
            
            missing_fields = []
            
            for field in required_fields:
                if field not in response_data:
                    missing_fields.append(field)
            
            if missing_fields:
                error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                self.logger.warning(f"Response validation failed: {error_msg}")
                
                # Capture validation context
                self.ai_debugger.capture_context(
                    test_name=test_name,
                    context_type="response_validation",
                    context_data={
                        "validation_result": "failed",
                        "missing_fields": missing_fields,
                        "required_fields": required_fields,
                        "response_keys": list(response_data.keys())
                    }
                )
                
                return False, error_msg
            
            self.logger.info("Response validation successful")
            return True, "Validation successful"
            
        except Exception as e:
            error_msg = f"Response validation error: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def validate_status_code(self, actual_status: int, expected_status: int,
                           test_name: str = "status_validation") -> Tuple[bool, str]:
        """Validate HTTP status code."""
        if actual_status == expected_status:
            self.logger.info(f"Status code validation successful: {actual_status}")
            return True, f"Status code {actual_status} as expected"
        else:
            error_msg = f"Expected status {expected_status}, got {actual_status}"
            self.logger.warning(error_msg)
            
            # Capture validation context
            self.ai_debugger.capture_context(
                test_name=test_name,
                context_type="status_validation",
                context_data={
                    "expected_status": expected_status,
                    "actual_status": actual_status,
                    "validation_result": "failed"
                }
            )
            
            return False, error_msg
    
    def extract_field_from_response(self, response_data: Dict[str, Any], 
                                  field_path: str) -> Optional[Any]:
        """
        Extract field from response using dot notation (e.g., 'booking.bookingid').
        """
        try:
            current_data = response_data
            
            for field in field_path.split('.'):
                if isinstance(current_data, dict) and field in current_data:
                    current_data = current_data[field]
                else:
                    return None
            
            return current_data
            
        except Exception as e:
            self.logger.error(f"Error extracting field '{field_path}': {e}")
            return None
    
    def cleanup(self) -> None:
        """Clean up API session resources."""
        try:
            if self.session:
                self.session.close()
                self.logger.info("API session closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing API session: {e}")
