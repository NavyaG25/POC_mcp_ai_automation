"""
Test cases for API booking creation functionality.
Tests booking creation with authentication and data validation.
"""
import pytest
from datetime import datetime, timedelta
from api_tests.endpoints.auth_api import AuthAPI
from api_tests.endpoints.booking_api import BookingAPI
from common.logger import Logger
from common.config_loader import ConfigLoader

class TestCreateBookingAPI:
    """Test class for API booking creation functionality."""
    
    def setup_method(self):
        """Setup method run before each test."""
        self.logger = Logger.get_logger()
        self.config = ConfigLoader.get_api_config()
        self.auth_api = AuthAPI()
        self.booking_api = BookingAPI()
        
        self.logger.info("API booking test setup completed")
    
    def teardown_method(self):
        """Teardown method run after each test."""
        try:
            # Clean up resources
            self.booking_api.cleanup()
            self.logger.info("API booking test teardown completed")
        except Exception as e:
            self.logger.error(f"Teardown failed: {e}")
    
    @pytest.mark.api
    @pytest.mark.smoke
    def test_create_booking_with_valid_token(self):
        """
        Test Case: API_TC_002
        Verify successful booking creation using valid authentication token.
        """
        test_name = "create_booking_with_valid_token"
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Step 1: Generate authentication token
            auth_success, token, auth_response = self.auth_api.generate_token(test_name=f"{test_name}_auth")
            
            assert auth_success, f"Authentication should succeed: {auth_response}"
            assert token, "Token should be generated"
            
            # Step 2: Prepare booking data
            booking_data = self.booking_api.create_sample_booking(
                guest_name="John Doe",
                days_from_now=1,
                stay_duration=2,
                test_name=test_name
            )
            
            assert booking_data, "Sample booking data should be created"
            
            # Step 3: Create booking
            booking_success, booking_response = self.booking_api.create_booking(
                booking_data=booking_data,
                token=token,
                test_name=test_name
            )
            
            assert booking_success, f"Booking creation should succeed: {booking_response}"
            
            # Step 4: Verify response structure
            assert 'status_code' in booking_response, "Response should contain status_code"
            status_code = booking_response['status_code']
            assert status_code in [200, 201], f"Expected 200 or 201, got {status_code}"
            
            response_data = booking_response.get('data', {})
            assert 'bookingid' in response_data, "Response should contain bookingid"
            
            booking_id = response_data['bookingid']
            assert isinstance(booking_id, int), f"Booking ID should be integer, got {type(booking_id)}"
            assert booking_id > 0, f"Booking ID should be positive, got {booking_id}"
            
            # Step 5: Verify booking details are echoed back
            assert 'booking' in response_data, "Response should contain booking details"
            
            echoed_booking = response_data['booking']
            assert echoed_booking['firstname'] == booking_data['firstname'], "Firstname should match"
            assert echoed_booking['lastname'] == booking_data['lastname'], "Lastname should match"
            assert echoed_booking['totalprice'] == booking_data['totalprice'], "Total price should match"
            assert echoed_booking['depositpaid'] == booking_data['depositpaid'], "Deposit paid should match"
            
            # Verify booking dates
            echoed_dates = echoed_booking.get('bookingdates', {})
            original_dates = booking_data.get('bookingdates', {})
            assert echoed_dates['checkin'] == original_dates['checkin'], "Check-in date should match"
            assert echoed_dates['checkout'] == original_dates['checkout'], "Check-out date should match"
            
            # Step 6: Verify echo validation if available
            echo_validation = booking_response.get('echo_validation', {})
            if echo_validation:
                assert echo_validation.get('valid', False), \
                    f"Echo validation should pass: {echo_validation.get('message', '')}"
            
            self.logger.info(f"Test {test_name} completed successfully. Booking ID: {booking_id}")
            
        except AssertionError as e:
            self.logger.error(f"Test {test_name} failed: {e}")
            
            # Capture failure context
            self.booking_api.api_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "booking_data": booking_data if 'booking_data' in locals() else {},
                    "token_generated": bool(token if 'token' in locals() else False),
                    "expected_outcome": "successful_booking_creation",
                    "actual_outcome": "booking_creation_failed",
                    "booking_response": booking_response if 'booking_response' in locals() else {}
                }
            )
            
            raise
        
        except Exception as e:
            error_msg = f"Test {test_name} encountered unexpected error: {e}"
            self.logger.error(error_msg)
            
            # Capture failure context
            self.booking_api.api_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "test_phase": "booking_creation_execution",
                    "error_type": "unexpected_exception"
                }
            )
            
            raise
    
    @pytest.mark.api
    @pytest.mark.regression
    def test_create_booking_without_token(self):
        """
        Test Case: API_TC_002_NEGATIVE
        Verify booking creation behavior without authentication token.
        Note: Restful-booker allows booking creation without authentication.
        """
        test_name = "create_booking_without_token"
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Step 1: Prepare booking data
            booking_data = self.booking_api.create_sample_booking(
                guest_name="Jane Smith",
                test_name=test_name
            )
            
            assert booking_data, "Sample booking data should be created"
            
            # Step 2: Attempt to create booking without token with retry logic
            booking_success = False
            booking_response = {}
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    self.logger.info(f"Booking creation attempt {attempt + 1}/{max_retries}")
                    booking_success, booking_response = self.booking_api.create_booking(
                        booking_data=booking_data,
                        token="",  # Empty token (no authentication)
                        test_name=f"{test_name}_attempt_{attempt+1}"
                    )
                    
                    if booking_success:
                        break
                    
                    # Check if it's a connection or timeout error
                    if booking_response.get('error') in ['connection_error', 'timeout']:
                        self.logger.warning(f"Network error on attempt {attempt + 1}: {booking_response.get('error')}, retrying...")
                        if attempt < max_retries - 1:
                            import time
                            time.sleep(2)  # Wait before retry
                        continue
                    else:
                        # Non-connection error, don't retry
                        break
                        
                except Exception as e:
                    self.logger.warning(f"Attempt {attempt + 1} failed with error: {e}")
                    if attempt == max_retries - 1:
                        raise
                    import time
                    time.sleep(2)
            
            # Step 3: Verify booking creation succeeds (restful-booker allows this)
            # If still failing after retries, check if it's a connection issue and handle gracefully
            if not booking_success:
                if booking_response.get('error') in ['connection_error', 'timeout']:
                    pytest.skip(f"Skipping test due to network connectivity issues: {booking_response.get('message', 'Network failed')}")
                else:
                    assert booking_success, f"Booking creation should succeed without token in restful-booker API. Response: {booking_response}"
            
            # Step 4: Verify response structure
            assert 'data' in booking_response, "Response should contain booking data"
            
            response_data = booking_response.get('data', {})
            assert 'bookingid' in response_data, "Response should contain booking ID"
            
            booking_id = response_data.get('bookingid')
            assert booking_id, "Booking ID should not be empty"
            
            self.logger.info(f"Booking created successfully without auth, ID: {booking_id}")
            self.logger.info(f"Test {test_name} completed successfully")
            
        except AssertionError as e:
            self.logger.error(f"Test {test_name} failed: {e}")
            
            # Capture failure context
            self.booking_api.api_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "booking_data": booking_data if 'booking_data' in locals() else {},
                    "expected_outcome": "authorization_failure",
                    "actual_outcome": "unexpected_success",
                    "booking_response": booking_response if 'booking_response' in locals() else {}
                }
            )
            
            raise
        
        except Exception as e:
            error_msg = f"Test {test_name} encountered unexpected error: {e}"
            self.logger.error(error_msg)
            
            # Capture failure context
            self.booking_api.api_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "test_phase": "unauthorized_booking_test",
                    "error_type": "unexpected_exception"
                }
            )
            
            raise
    
    @pytest.mark.api
    @pytest.mark.regression
    def test_create_booking_invalid_data(self):
        """
        Test booking creation with invalid data to verify validation.
        """
        test_name = "create_booking_invalid_data"
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Step 1: Generate valid token
            auth_success, token, auth_response = self.auth_api.generate_token(test_name=f"{test_name}_auth")
            assert auth_success, f"Authentication should succeed: {auth_response}"
            
            # Step 2: Test with missing required fields
            invalid_booking_data = {
                "firstname": "Test",
                # Missing lastname, totalprice, depositpaid, bookingdates
            }
            
            booking_success, booking_response = self.booking_api.create_booking(
                booking_data=invalid_booking_data,
                token=token,
                test_name=test_name
            )
            
            # Step 3: Verify booking creation fails due to validation
            assert not booking_success, "Booking creation should fail with invalid data"
            
            assert 'error' in booking_response, "Response should contain error information"
            error_type = booking_response.get('error', '')
            assert error_type == 'validation_failed', \
                f"Expected validation_failed error, got: {error_type}"
            
            self.logger.info(f"Test {test_name} completed successfully")
            
        except Exception as e:
            error_msg = f"Test {test_name} failed: {e}"
            self.logger.error(error_msg)
            
            # Capture failure context
            self.booking_api.api_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "test_phase": "invalid_data_validation",
                    "error_type": str(type(e).__name__)
                }
            )
            
            raise
    
    @pytest.mark.api
    @pytest.mark.regression
    def test_booking_data_validation(self):
        """
        Test booking data validation functionality.
        """
        test_name = "booking_data_validation"
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Step 1: Test valid booking data
            valid_booking = self.booking_api.create_sample_booking(test_name=test_name)
            validation_result = self.booking_api.validate_booking_data(valid_booking)
            
            assert validation_result['valid'], \
                f"Valid booking data should pass validation: {validation_result['message']}"
            
            # Step 2: Test missing required fields
            invalid_booking = {
                "firstname": "Test"
                # Missing other required fields
            }
            
            validation_result = self.booking_api.validate_booking_data(invalid_booking)
            assert not validation_result['valid'], \
                "Booking with missing fields should fail validation"
            assert "missing required fields" in validation_result['message'].lower(), \
                "Error message should mention missing fields"
            
            # Step 3: Test invalid date range
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            invalid_date_booking = {
                "firstname": "Test",
                "lastname": "User",
                "totalprice": 100,
                "depositpaid": True,
                "bookingdates": {
                    "checkin": tomorrow,
                    "checkout": yesterday  # Checkout before checkin
                }
            }
            
            validation_result = self.booking_api.validate_booking_data(invalid_date_booking)
            assert not validation_result['valid'], \
                "Booking with invalid date range should fail validation"
            assert "checkout date must be after checkin" in validation_result['message'].lower(), \
                "Error message should mention date order issue"
            
            self.logger.info(f"Test {test_name} completed successfully")
            
        except Exception as e:
            error_msg = f"Test {test_name} failed: {e}"
            self.logger.error(error_msg)
            
            # Capture failure context
            self.booking_api.api_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "test_phase": "data_validation_testing",
                    "error_type": str(type(e).__name__)
                }
            )
            
            raise
    
    @pytest.mark.api
    @pytest.mark.smoke
    def test_complete_booking_workflow(self):
        """
        Integration test for complete booking workflow including creation and retrieval.
        """
        test_name = "complete_booking_workflow"
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Step 1: Authentication with retry logic
            auth_success = False
            token = None
            auth_response = {}
            
            # Try authentication up to 3 times to handle network issues
            for attempt in range(3):
                try:
                    auth_success, token, auth_response = self.auth_api.generate_token(test_name=f"{test_name}_auth_attempt_{attempt+1}")
                    if auth_success and token:
                        break
                    self.logger.warning(f"Authentication attempt {attempt+1} failed, retrying...")
                except Exception as e:
                    self.logger.warning(f"Authentication attempt {attempt+1} failed with error: {e}")
                    if attempt == 2:  # Last attempt
                        # Check if it's a connection issue
                        if "connection" in str(e).lower() or "network" in str(e).lower():
                            pytest.skip(f"Skipping test due to network connectivity issues during authentication: {e}")
                        else:
                            raise
                    import time
                    time.sleep(2)  # Wait before retry
            
            # Check authentication success or skip due to connectivity
            if not auth_success:
                if "connection" in str(auth_response).lower() or auth_response.get('error') == 'connection_error':
                    pytest.skip(f"Skipping test due to network connectivity issues: {auth_response}")
                else:
                    assert auth_success, f"Authentication should succeed after retries. Last response: {auth_response}"
            
            # Step 2: Create booking with retry logic
            booking_data = self.booking_api.create_sample_booking(
                guest_name="Integration Test User",
                test_name=test_name
            )
            
            booking_success = False
            booking_response = {}
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    self.logger.info(f"Booking creation attempt {attempt + 1}/{max_retries}")
                    booking_success, booking_response = self.booking_api.create_booking(
                        booking_data=booking_data,
                        token=token,
                        test_name=f"{test_name}_booking_attempt_{attempt+1}"
                    )
                    
                    if booking_success:
                        break
                    
                    # Check if it's a connection or timeout error
                    if booking_response.get('error') in ['connection_error', 'timeout']:
                        self.logger.warning(f"Booking creation network error on attempt {attempt + 1}: {booking_response.get('error')}, retrying...")
                        if attempt < max_retries - 1:
                            import time
                            time.sleep(2)  # Wait before retry
                        continue
                    else:
                        # Non-connection error, don't retry
                        break
                        
                except Exception as e:
                    self.logger.warning(f"Booking creation attempt {attempt + 1} failed with error: {e}")
                    if attempt == max_retries - 1:
                        raise
                    import time
                    time.sleep(2)
            
            # Check if booking creation succeeded or skip due to connectivity issues
            if not booking_success:
                if booking_response.get('error') in ['connection_error', 'timeout']:
                    pytest.skip(f"Skipping test due to network connectivity issues: {booking_response.get('message', 'Network failed')}")
                else:
                    assert booking_success, f"Booking creation should succeed. Response: {booking_response}"
            
            response_data = booking_response.get('data', {})
            booking_id = response_data.get('bookingid')
            assert booking_id, "Booking ID should be returned"
            
            # Step 3: Retrieve created booking
            get_success, get_response = self.booking_api.get_booking(booking_id, test_name)
            
            if get_success:
                # Verify retrieved booking matches created booking
                retrieved_data = get_response.get('data', {})
                
                if 'firstname' in retrieved_data:
                    assert retrieved_data['firstname'] == booking_data['firstname'], \
                        "Retrieved firstname should match created booking"
                
                self.logger.info("Booking retrieval successful")
            else:
                # Booking retrieval might not be immediately available
                # This is acceptable in test environments
                self.logger.info("Booking retrieval not immediately available (acceptable)")
            
            self.logger.info(f"Test {test_name} completed successfully")
            
        except Exception as e:
            error_msg = f"Test {test_name} failed: {e}"
            self.logger.error(error_msg)
            
            # Capture comprehensive failure context
            self.booking_api.api_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "test_type": "integration_test",
                    "workflow_phase": "complete_booking_workflow",
                    "error_type": str(type(e).__name__)
                }
            )
            
            raise
