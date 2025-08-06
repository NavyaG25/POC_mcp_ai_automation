"""
Test cases for booking creation functionality.
Tests booking creation and verification workflows.
"""
import pytest
from datetime import datetime, timedelta
from ui_tests.pages.login_page import LoginPage
from ui_tests.pages.dashboard_page import DashboardPage
from ui_tests.pages.booking_page import BookingPage
from common.logger import Logger
from common.config_loader import ConfigLoader

class TestCreateBooking:
    """Test class for booking creation functionality."""
    
    def setup_method(self):
        """Setup method run before each test."""
        self.logger = Logger.get_logger()
        self.config = ConfigLoader.get_ui_config()
        self.login_page = LoginPage()
        # Share UI utils instance to maintain login state
        self.dashboard_page = DashboardPage(self.login_page.ui_utils)
        self.booking_page = BookingPage()
        
        # Calculate test dates
        today = datetime.now()
        self.checkin_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
        self.checkout_date = (today + timedelta(days=3)).strftime('%Y-%m-%d')
        
        self.logger.info("Booking test setup completed")
    
    def teardown_method(self):
        """Teardown method run after each test."""
        try:
            # Clean up resources
            self.booking_page.cleanup("teardown")
            self.login_page.cleanup("teardown")
            self.logger.info("Booking test teardown completed")
        except Exception as e:
            self.logger.error(f"Teardown failed: {e}")
    
    @pytest.mark.ui
    @pytest.mark.smoke
    def test_create_booking_as_guest(self):
        """
        Test Case: UI_TC_003 (Extended)
        Verify guest can successfully create a booking and it appears in admin dashboard.
        """
        test_name = "create_booking_as_guest"
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Define guest details
            guest_details = {
                'firstname': 'John',
                'lastname': 'Doe',
                'email': 'john.doe@example.com',
                'phone': '+1234567890'
            }
            
            # Step 1: Create booking as guest
            booking_success, booking_message = self.booking_page.create_complete_booking(
                checkin_date=self.checkin_date,
                checkout_date=self.checkout_date,
                guest_details=guest_details,
                test_name=test_name
            )
            
            assert booking_success, f"Booking creation failed: {booking_message}"
            
            # Extract booking ID from message
            booking_id = self.extract_booking_id(booking_message)
            assert booking_id, "Booking ID should be generated"
            
            self.logger.info(f"Booking created successfully with ID: {booking_id}")
            
            # Step 2: Login as admin to verify booking
            assert self.login_page.navigate_to_login(test_name), "Failed to navigate to admin login"
            
            username = self.config['admin_username']
            password = self.config['admin_password']
            
            login_success, login_message = self.login_page.perform_login(username, password, test_name)
            assert login_success, f"Admin login failed: {login_message}"
            
            # Step 3: Verify booking appears in admin dashboard
            assert self.dashboard_page.verify_dashboard_loaded(test_name), "Dashboard should be accessible"
            
            # Step 4: Check if booking exists on dashboard
            booking_exists = self.dashboard_page.verify_booking_exists(
                booking_name=f"{guest_details['firstname']} {guest_details['lastname']}",
                test_name=test_name
            )
            
            assert booking_exists, "Booking should appear in admin dashboard"
            
            self.logger.info(f"Test {test_name} completed successfully")
            
        except AssertionError as e:
            self.logger.error(f"Test {test_name} failed: {e}")
            
            # Capture failure context
            self.booking_page.ui_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "guest_details": guest_details,
                    "checkin_date": self.checkin_date,
                    "checkout_date": self.checkout_date,
                    "expected_outcome": "booking_creation_and_verification",
                    "actual_outcome": "test_failed"
                }
            )
            
            raise
        
        except Exception as e:
            error_msg = f"Test {test_name} encountered unexpected error: {e}"
            self.logger.error(error_msg)
            
            # Capture failure screenshot and context
            self.booking_page.ui_utils.screenshot_handler.capture_failure_screenshot(test_name, str(e))
            
            self.booking_page.ui_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "test_phase": "booking_creation",
                    "error_type": "unexpected_exception"
                }
            )
            
            raise
    
    @pytest.mark.ui
    @pytest.mark.regression
    def test_booking_form_validation(self):
        """
        Test Case: UI_TC_004 (Extended)
        Verify booking form validation with invalid/missing data.
        """
        test_name = "booking_form_validation"
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Step 1: Navigate to booking section
            assert self.booking_page.navigate_to_booking_section(test_name), "Failed to navigate to booking section"
            
            # Step 2: Test with invalid date range (checkout before checkin)
            invalid_checkin = self.checkout_date  # Use later date as checkin
            invalid_checkout = self.checkin_date  # Use earlier date as checkout
            
            assert self.booking_page.set_checkin_date(invalid_checkin, test_name), "Failed to set invalid checkin date"
            assert self.booking_page.set_checkout_date(invalid_checkout, test_name), "Failed to set invalid checkout date"
            
            # Step 3: Validate booking data should fail
            validation_result = self.booking_page.validate_booking_data()
            assert not validation_result, "Validation should fail for invalid date range"
            
            # Step 4: Test with valid dates
            assert self.booking_page.set_checkin_date(self.checkin_date, test_name), "Failed to set valid checkin date"
            assert self.booking_page.set_checkout_date(self.checkout_date, test_name), "Failed to set valid checkout date"
            
            # Step 5: Validate booking data should pass
            validation_result = self.booking_page.validate_booking_data()
            assert validation_result, "Validation should pass for valid date range"
            
            # Step 6: Test availability check
            availability_success = self.booking_page.check_availability(test_name)
            assert availability_success, "Availability check should be successful"
            
            self.logger.info(f"Test {test_name} completed successfully")
            
        except AssertionError as e:
            self.logger.error(f"Test {test_name} failed: {e}")
            
            # Capture failure context
            self.booking_page.ui_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "test_phase": "form_validation",
                    "checkin_date": self.checkin_date,
                    "checkout_date": self.checkout_date,
                    "expected_outcome": "validation_testing",
                    "actual_outcome": "validation_failed"
                }
            )
            
            raise
        
        except Exception as e:
            error_msg = f"Test {test_name} encountered unexpected error: {e}"
            self.logger.error(error_msg)
            
            # Capture failure context
            self.booking_page.ui_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "test_phase": "form_validation",
                    "error_type": "unexpected_exception"
                }
            )
            
            raise
    
    @pytest.mark.ui
    @pytest.mark.regression
    def test_booking_workflow_integration(self):
        """
        Integration test for complete booking workflow from guest to admin verification.
        """
        test_name = "booking_workflow_integration"
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Step 1: Complete guest booking workflow
            guest_details = {
                'firstname': 'Jane',
                'lastname': 'Smith',
                'email': 'jane.smith@example.com',
                'phone': '+9876543210'
            }
            
            # Create booking
            booking_success, booking_message = self.booking_page.create_complete_booking(
                checkin_date=self.checkin_date,
                checkout_date=self.checkout_date,
                guest_details=guest_details,
                test_name=test_name
            )
            
            assert booking_success, f"Guest booking failed: {booking_message}"
            
            # Step 2: Admin verification workflow
            # Login as admin
            assert self.login_page.navigate_to_login(test_name), "Failed to navigate to admin login"
            
            username = self.config['admin_username']
            password = self.config['admin_password']
            
            login_success, login_message = self.login_page.perform_login(username, password, test_name)
            assert login_success, f"Admin login failed: {login_message}"
            
            # Verify dashboard access
            assert self.dashboard_page.verify_dashboard_loaded(test_name), "Admin dashboard should be accessible"
            
            # Check room count
            room_count = self.dashboard_page.get_room_count(test_name)
            assert room_count > 0, "Rooms should be available on dashboard"
            
            # Verify booking exists
            booking_name = f"{guest_details['firstname']} {guest_details['lastname']}"
            booking_exists = self.dashboard_page.verify_booking_exists(booking_name, test_name)
            assert booking_exists, "Booking should be visible in admin dashboard"
            
            # Step 3: Test navigation between sections
            front_page_nav = self.dashboard_page.navigate_to_front_page(test_name)
            assert front_page_nav, "Should be able to navigate to front page from dashboard"
            
            self.logger.info(f"Test {test_name} completed successfully")
            
        except Exception as e:
            error_msg = f"Test {test_name} failed: {e}"
            self.logger.error(error_msg)
            
            # Capture comprehensive failure context
            self.booking_page.ui_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "test_type": "integration_test",
                    "guest_details": guest_details,
                    "workflow_phase": "complete_integration",
                    "error_type": str(type(e).__name__)
                }
            )
            
            raise
    
    def extract_booking_id(self, booking_message: str) -> str:
        """Extract booking ID from booking confirmation message."""
        try:
            # Look for pattern like "Booking ID: BK1234"
            import re
            match = re.search(r'Booking ID:\s*([A-Z0-9]+)', booking_message)
            if match:
                return match.group(1)
            
            # Fallback - look for any ID pattern
            match = re.search(r'(BK\d+)', booking_message)
            if match:
                return match.group(1)
            
            return ""
        except Exception:
            return ""
