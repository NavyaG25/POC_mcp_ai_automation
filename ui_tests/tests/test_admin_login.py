"""
Test cases for admin login functionality.
Tests both positive and negative login scenarios.
"""
import pytest
from ui_tests.pages.login_page import LoginPage
from ui_tests.pages.dashboard_page import DashboardPage
from common.logger import Logger
from common.config_loader import ConfigLoader

class TestAdminLogin:
    """Test class for admin login functionality."""
    
    def setup_method(self):
        """Setup method run before each test."""
        self.logger = Logger.get_logger()
        self.config = ConfigLoader.get_ui_config()
        self.login_page = LoginPage()
        # Share UI utils instance to maintain login state
        self.dashboard_page = DashboardPage(self.login_page.ui_utils)
        
        self.logger.info("Test setup completed")
    
    def teardown_method(self):
        """Teardown method run after each test."""
        try:
            # Clean up resources
            self.login_page.cleanup("teardown")
            self.logger.info("Test teardown completed")
        except Exception as e:
            self.logger.error(f"Teardown failed: {e}")
    
    @pytest.mark.ui
    @pytest.mark.smoke
    def test_admin_login_valid_credentials(self):
        """
        Test Case: UI_TC_001
        Verify admin can successfully login with valid credentials and access dashboard.
        """
        test_name = "admin_login_valid_credentials"
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Step 1: Navigate to login page
            assert self.login_page.navigate_to_login(test_name), "Failed to navigate to login page"
            
            # Step 2: Perform login with valid credentials
            username = self.config['admin_username']
            password = self.config['admin_password']
            
            success, message = self.login_page.perform_login(username, password, test_name)
            
            assert success, f"Login failed: {message}"
            
            # Step 3: Verify login state
            assert self.login_page.is_logged_in(), "User should be logged in"
            assert self.login_page.get_current_user() == username, f"Current user should be {username}"
            
            # Step 4: Verify dashboard access
            assert self.dashboard_page.verify_dashboard_loaded(test_name), "Dashboard should be accessible"
            
            # Step 5: Verify dashboard content
            room_count = self.dashboard_page.get_room_count(test_name)
            assert room_count > 0, "Dashboard should show available rooms"
            
            room_details = self.dashboard_page.get_room_details(test_name)
            assert len(room_details) > 0, "Dashboard should show room details"
            
            self.logger.info(f"Test {test_name} completed successfully")
            
        except AssertionError as e:
            self.logger.error(f"Test {test_name} failed: {e}")
            
            # Capture failure context
            self.login_page.ui_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "username": username,
                    "expected_outcome": "successful_login",
                    "actual_outcome": "login_failed"
                }
            )
            
            raise
        
        except Exception as e:
            error_msg = f"Test {test_name} encountered unexpected error: {e}"
            self.logger.error(error_msg)
            
            # Capture failure screenshot and context
            self.login_page.ui_utils.screenshot_handler.capture_failure_screenshot(test_name, str(e))
            
            self.login_page.ui_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "test_phase": "execution",
                    "error_type": "unexpected_exception"
                }
            )
            
            raise
    
    @pytest.mark.ui
    @pytest.mark.regression
    def test_admin_login_invalid_credentials(self):
        """
        Test Case: UI_TC_002
        Verify admin login fails with invalid credentials and appropriate error handling.
        """
        test_name = "admin_login_invalid_credentials"
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Step 1: Navigate to login page
            assert self.login_page.navigate_to_login(test_name), "Failed to navigate to login page"
            
            # Step 2: Attempt login with invalid credentials
            invalid_username = "invaliduser"
            invalid_password = "wrongpassword"
            
            success, message = self.login_page.perform_login(invalid_username, invalid_password, test_name)
            
            # Step 3: Verify login failure
            assert not success, "Login should fail with invalid credentials"
            assert "invalid" in message.lower() or "failed" in message.lower(), "Error message should indicate invalid credentials"
            
            # Step 4: Verify user is not logged in
            assert not self.login_page.is_logged_in(), "User should not be logged in"
            assert self.login_page.get_current_user() == "", "No user should be logged in"
            
            # Step 5: Verify dashboard is not accessible
            # User should remain on login page, not reach dashboard
            dashboard_accessible = self.dashboard_page.verify_dashboard_loaded(test_name)
            assert not dashboard_accessible, "Dashboard should not be accessible with invalid credentials"
            
            self.logger.info(f"Test {test_name} completed successfully")
            
        except AssertionError as e:
            self.logger.error(f"Test {test_name} failed: {e}")
            
            # Capture failure context
            self.login_page.ui_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "username": invalid_username,
                    "password": invalid_password,
                    "expected_outcome": "login_failure",
                    "actual_outcome": "unexpected_success"
                }
            )
            
            raise
        
        except Exception as e:
            error_msg = f"Test {test_name} encountered unexpected error: {e}"
            self.logger.error(error_msg)
            
            # Capture failure screenshot and context
            self.login_page.ui_utils.screenshot_handler.capture_failure_screenshot(test_name, str(e))
            
            self.login_page.ui_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "test_phase": "execution",
                    "error_type": "unexpected_exception"
                }
            )
            
            raise
    
    @pytest.mark.ui
    @pytest.mark.smoke
    def test_login_logout_cycle(self):
        """
        Additional test for login/logout cycle to verify session management.
        """
        test_name = "login_logout_cycle"
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Step 1: Navigate and login
            assert self.login_page.navigate_to_login(test_name), "Failed to navigate to login page"
            
            username = self.config['admin_username']
            password = self.config['admin_password']
            
            success, message = self.login_page.perform_login(username, password, test_name)
            assert success, f"Login failed: {message}"
            
            # Step 2: Verify login
            assert self.login_page.is_logged_in(), "User should be logged in"
            
            # Step 3: Perform logout
            logout_success = self.login_page.logout(test_name)
            assert logout_success, "Logout should be successful"
            
            # Step 4: Verify logout
            assert not self.login_page.is_logged_in(), "User should be logged out"
            assert self.login_page.get_current_user() == "", "No user should be logged in after logout"
            
            self.logger.info(f"Test {test_name} completed successfully")
            
        except Exception as e:
            error_msg = f"Test {test_name} failed: {e}"
            self.logger.error(error_msg)
            
            # Capture failure context
            self.login_page.ui_utils.ai_debugger.capture_test_failure(
                test_name=test_name,
                error_message=str(e),
                stack_trace="",
                test_data={
                    "test_phase": "login_logout_cycle",
                    "error_type": str(type(e).__name__)
                }
            )
            
            raise
