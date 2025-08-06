"""
Test cases for authentication token generation.
Tests both positive and negative authentication scenarios.
"""
import pytest
from api_tests.endpoints.auth_api import AuthAPI
from common.logger import Logger
from common.config_loader import ConfigLoader

class TestTokenGeneration:
    """Test class for authentication token generation."""
    
    def setup_method(self):
        """Setup method run before each test."""
        self.logger = Logger.get_logger()
        self.config = ConfigLoader.get_api_config()
        self.auth_api = AuthAPI()
        
        self.logger.info("API authentication test setup completed")
    
    def teardown_method(self):
        """Teardown method run after each test."""
        try:
            # Clean up resources
            self.auth_api.cleanup()
            self.logger.info("API authentication test teardown completed")
        except Exception as e:
            self.logger.error(f"Teardown failed: {e}")
    
    @pytest.mark.api
    @pytest.mark.smoke
    def test_generate_token_valid_credentials(self):
        """
        Test Case: API_TC_001
        Verify successful token generation with valid admin credentials.
        """
        test_name = "generate_token_valid_credentials"
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Step 1: Generate token with valid credentials
            username = self.config['username']
            password = self.config['password']
            
            success, token, response = self.auth_api.generate_token(
                username=username,
                password=password,
                test_name=test_name
            )
            
            # Step 2: Verify token generation success
            assert success, f"Token generation should succeed: {response}"
            assert token, "Token should not be empty"
            assert isinstance(token, str), "Token should be a string"
            
            # Step 3: Verify response structure
            assert 'status_code' in response, "Response should contain status_code"
            assert response['status_code'] == 200, f"Expected status 200, got {response['status_code']}"
            
            response_data = response.get('data', {})
            assert 'token' in response_data, "Response data should contain token field"
            assert response_data['token'] == token, "Response token should match returned token"
            
            # Step 4: Verify token format
            assert len(token) >= 10, f"Token should be at least 10 characters, got {len(token)}"
            
            # Step 5: Store token for potential reuse
            stored_token = self.auth_api.get_current_token()
            assert stored_token == token, "Stored token should match generated token"
            
            self.logger.info(f"Test {test_name} completed successfully")
            
        except AssertionError as e:
            self.logger.error(f"Test {test_name} failed: {e}")
            
            # Capture failure context
            self.auth_api.api_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "username": username,
                    "expected_outcome": "successful_token_generation",
                    "actual_outcome": "token_generation_failed",
                    "response": response if 'response' in locals() else {}
                }
            )
            
            raise
        
        except Exception as e:
            error_msg = f"Test {test_name} encountered unexpected error: {e}"
            self.logger.error(error_msg)
            
            # Capture failure context
            self.auth_api.api_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "test_phase": "token_generation_execution",
                    "error_type": "unexpected_exception"
                }
            )
            
            raise
    
    @pytest.mark.api
    @pytest.mark.regression
    def test_generate_token_invalid_credentials(self):
        """
        Test Case: API_TC_001_NEGATIVE
        Verify token generation fails with invalid credentials.
        """
        test_name = "generate_token_invalid_credentials"
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Step 1: Attempt token generation with invalid credentials
            invalid_username = "invalid_user"
            invalid_password = "wrong_password"
            
            success, token, response = self.auth_api.generate_token(
                username=invalid_username,
                password=invalid_password,
                test_name=test_name
            )
            
            # Step 2: Verify token generation failure
            assert not success, "Token generation should fail with invalid credentials"
            assert not token, "No token should be returned for invalid credentials"
            
            # Step 3: Verify response handling
            assert 'status_code' in response, "Response should contain status_code"
            
            # API might return 200 with error message or non-200 status
            status_code = response['status_code']
            if status_code == 200:
                # Check that no token is in the response
                response_data = response.get('data', {})
                assert 'token' not in response_data or not response_data.get('token'), \
                    "No valid token should be in response for invalid credentials"
            else:
                # Non-200 status is also acceptable for authentication failure
                assert status_code in [400, 401, 403], \
                    f"Expected authentication error status, got {status_code}"
            
            # Step 4: Verify no token is stored
            stored_token = self.auth_api.get_current_token()
            assert not stored_token, "No token should be stored after failed authentication"
            
            self.logger.info(f"Test {test_name} completed successfully")
            
        except AssertionError as e:
            self.logger.error(f"Test {test_name} failed: {e}")
            
            # Capture failure context
            self.auth_api.api_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "username": invalid_username,
                    "password": invalid_password,
                    "expected_outcome": "authentication_failure",
                    "actual_outcome": "unexpected_success",
                    "response": response if 'response' in locals() else {}
                }
            )
            
            raise
        
        except Exception as e:
            error_msg = f"Test {test_name} encountered unexpected error: {e}"
            self.logger.error(error_msg)
            
            # Capture failure context
            self.auth_api.api_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "test_phase": "invalid_credentials_test",
                    "error_type": "unexpected_exception"
                }
            )
            
            raise
    
    @pytest.mark.api
    @pytest.mark.regression
    def test_authentication_flow_comprehensive(self):
        """
        Comprehensive test for the complete authentication flow.
        Tests multiple scenarios in a single test.
        """
        test_name = "authentication_flow_comprehensive"
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Step 1: Test authentication flow
            flow_results = self.auth_api.test_authentication_flow(test_name)
            
            # Step 2: Verify overall success
            assert flow_results.get('overall_success', False), \
                f"Authentication flow should be successful: {flow_results}"
            
            # Step 3: Verify valid credentials test
            valid_creds_result = flow_results.get('valid_credentials_test', {})
            assert valid_creds_result.get('success', False), \
                "Valid credentials test should succeed"
            assert valid_creds_result.get('token_received', False), \
                "Token should be received for valid credentials"
            
            # Step 4: Verify invalid credentials test
            invalid_creds_result = flow_results.get('invalid_credentials_test', {})
            assert invalid_creds_result.get('success', False), \
                "Invalid credentials test should succeed (by failing authentication)"
            
            # Step 5: Verify token format test
            token_format_result = flow_results.get('token_format_test', {})
            if token_format_result:  # Only check if token was generated
                assert token_format_result.get('success', False), \
                    "Token format validation should succeed"
            
            self.logger.info(f"Test {test_name} completed successfully")
            
        except AssertionError as e:
            self.logger.error(f"Test {test_name} failed: {e}")
            
            # Capture comprehensive failure context
            self.auth_api.api_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "test_type": "comprehensive_auth_flow",
                    "flow_results": flow_results if 'flow_results' in locals() else {},
                    "expected_outcome": "complete_flow_success",
                    "actual_outcome": "flow_test_failed"
                }
            )
            
            raise
        
        except Exception as e:
            error_msg = f"Test {test_name} encountered unexpected error: {e}"
            self.logger.error(error_msg)
            
            # Capture failure context
            self.auth_api.api_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "test_phase": "comprehensive_flow_execution",
                    "error_type": "unexpected_exception"
                }
            )
            
            raise
    
    @pytest.mark.api
    @pytest.mark.smoke
    def test_token_validation_and_management(self):
        """
        Test token validation and management operations.
        """
        test_name = "token_validation_and_management"
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Step 1: Generate valid token
            success, token, response = self.auth_api.generate_token(test_name=test_name)
            assert success, "Token generation should succeed"
            assert token, "Token should be generated"
            
            # Step 2: Test token retrieval
            current_token = self.auth_api.get_current_token()
            assert current_token == token, "Retrieved token should match generated token"
            
            # Step 3: Test token validation
            token_valid = self.auth_api.validate_token_format(token)
            assert token_valid, f"Generated token should be valid format: {token}"
            
            # Step 4: Test token clearing
            self.auth_api.clear_token()
            cleared_token = self.auth_api.get_current_token()
            assert cleared_token is None, "Token should be cleared"
            
            # Step 5: Test credential validation helper
            username = self.config['username']
            password = self.config['password']
            
            cred_valid, cred_message = self.auth_api.validate_credentials(username, password, test_name)
            assert cred_valid, f"Credentials should be valid: {cred_message}"
            
            self.logger.info(f"Test {test_name} completed successfully")
            
        except Exception as e:
            error_msg = f"Test {test_name} failed: {e}"
            self.logger.error(error_msg)
            
            # Capture failure context
            self.auth_api.api_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "test_phase": "token_management",
                    "error_type": str(type(e).__name__)
                }
            )
            
            raise
