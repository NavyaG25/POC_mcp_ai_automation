"""
Authentication API endpoint handler.
Manages token generation and authentication operations.
"""
from typing import Dict, Any, Optional, Tuple
from api_tests.helpers.api_utils import APIUtils
from common.logger import Logger
from common.config_loader import ConfigLoader

class AuthAPI:
    """Handles authentication API operations."""
    
    def __init__(self):
        # Load configuration first
        ConfigLoader.load_config()
        
        self.logger = Logger.get_logger()
        self.api_utils = APIUtils()
        self.config = ConfigLoader.get_api_config()
        self.auth_endpoint = "/auth"
        self.current_token = None
        
        self.logger.info("AuthAPI initialized")
    
    def generate_token(self, username: Optional[str] = None, password: Optional[str] = None,
                      test_name: str = "token_generation") -> Tuple[bool, str, Dict[str, Any]]:
        """
        Generate authentication token.
        
        Returns:
            Tuple[bool, str, Dict]: (success, token, full_response)
        """
        try:
            # Use provided credentials or defaults from config
            auth_username = username or self.config['username']
            auth_password = password or self.config['password']
            
            self.logger.info(f"Generating token for user: {auth_username}")
            
            # Prepare request data
            auth_data = {
                "username": auth_username,
                "password": auth_password
            }
            
            # Make authentication request
            success, response = self.api_utils.post(
                endpoint=self.auth_endpoint,
                data=auth_data,
                test_name=test_name
            )
            
            if not success:
                error_msg = f"Token generation failed: {response.get('message', 'Unknown error')}"
                self.logger.error(error_msg)
                return False, "", response
            
            # Validate response status
            status_valid, status_msg = self.api_utils.validate_status_code(
                actual_status=response.get('status_code', 0),
                expected_status=200,
                test_name=test_name
            )
            
            if not status_valid:
                self.logger.warning(f"Unexpected status code: {status_msg}")
                # Note: Some APIs might return 200 but with error in body
            
            # Extract response data
            response_data = response.get('data', {})
            
            # Check for token in response
            token = response_data.get('token', '')
            
            if token:
                self.current_token = token
                self.logger.info("Token generated successfully")
                
                # Validate token format (basic check)
                if self.validate_token_format(token):
                    return True, token, response
                else:
                    self.logger.warning("Token format validation failed, but proceeding")
                    return True, token, response
            else:
                # Check if this is an error response with valid status
                if response.get('status_code') == 200:
                    error_msg = "Authentication failed: Invalid credentials"
                    self.logger.warning(error_msg)
                    return False, "", response
                else:
                    error_msg = f"Token not found in response: {response_data}"
                    self.logger.error(error_msg)
                    return False, "", response
                    
        except Exception as e:
            error_msg = f"Token generation encountered error: {str(e)}"
            self.logger.error(error_msg)
            
            error_response = {
                'error': 'token_generation_exception',
                'message': str(e),
                'status_code': 0
            }
            
            return False, "", error_response
    
    def validate_token_format(self, token: str) -> bool:
        """Validate basic token format."""
        try:
            # Basic token validation - check if it's a non-empty string
            if not token or not isinstance(token, str):
                return False
            
            # Check minimum length
            if len(token) < 10:
                self.logger.warning(f"Token seems too short: {len(token)} characters")
                return False
            
            # Check for valid characters (basic alphanumeric check)
            if not token.replace('-', '').replace('_', '').isalnum():
                self.logger.warning("Token contains unexpected characters")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Token validation error: {e}")
            return False
    
    def validate_credentials(self, username: str, password: str,
                           test_name: str = "credential_validation") -> Tuple[bool, str]:
        """
        Validate if provided credentials are correct.
        
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        try:
            success, token, response = self.generate_token(username, password, test_name)
            
            if success and token:
                return True, "Credentials are valid"
            else:
                # Check response for specific error messages
                response_data = response.get('data', {})
                status_code = response.get('status_code', 0)
                
                if status_code == 200 and not token:
                    return False, "Invalid username or password"
                else:
                    return False, f"Authentication failed: {response.get('message', 'Unknown error')}"
                    
        except Exception as e:
            error_msg = f"Credential validation error: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def get_current_token(self) -> Optional[str]:
        """Get the currently stored token."""
        return self.current_token
    
    def clear_token(self) -> None:
        """Clear the currently stored token."""
        self.current_token = None
        self.logger.info("Token cleared")
    
    def test_authentication_flow(self, test_name: str = "auth_flow_test") -> Dict[str, Any]:
        """
        Test the complete authentication flow and return results.
        
        Returns:
            Dict: Test results with success/failure details
        """
        results = {
            'valid_credentials_test': {},
            'invalid_credentials_test': {},
            'token_format_test': {},
            'overall_success': False
        }
        
        try:
            # Test 1: Valid credentials
            self.logger.info("Testing authentication with valid credentials")
            
            valid_success, valid_token, valid_response = self.generate_token(test_name=f"{test_name}_valid")
            
            results['valid_credentials_test'] = {
                'success': valid_success,
                'token_received': bool(valid_token),
                'response_status': valid_response.get('status_code', 0),
                'message': 'Valid credentials test'
            }
            
            # Test 2: Invalid credentials
            self.logger.info("Testing authentication with invalid credentials")
            
            invalid_success, invalid_token, invalid_response = self.generate_token(
                username="invalid_user",
                password="wrong_password",
                test_name=f"{test_name}_invalid"
            )
            
            results['invalid_credentials_test'] = {
                'success': not invalid_success,  # Should fail for invalid creds
                'token_received': bool(invalid_token),
                'response_status': invalid_response.get('status_code', 0),
                'message': 'Invalid credentials test'
            }
            
            # Test 3: Token format validation
            if valid_token:
                token_format_valid = self.validate_token_format(valid_token)
                results['token_format_test'] = {
                    'success': token_format_valid,
                    'token_length': len(valid_token),
                    'message': 'Token format validation'
                }
            
            # Overall assessment
            valid_creds_ok = results['valid_credentials_test']['success']
            invalid_creds_ok = results['invalid_credentials_test']['success']
            token_format_ok = results['token_format_test'].get('success', True)
            
            results['overall_success'] = valid_creds_ok and invalid_creds_ok and token_format_ok
            
            self.logger.info(f"Authentication flow test completed. Overall success: {results['overall_success']}")
            
        except Exception as e:
            error_msg = f"Authentication flow test failed: {str(e)}"
            self.logger.error(error_msg)
            results['error'] = error_msg
            results['overall_success'] = False
        
        return results
    
    def cleanup(self) -> None:
        """Clean up authentication resources."""
        try:
            self.clear_token()
            self.api_utils.cleanup()
            self.logger.info("AuthAPI cleanup completed")
        except Exception as e:
            self.logger.error(f"AuthAPI cleanup failed: {e}")
