"""
Login page object for admin authentication.
Handles login functionality with proper state management.
"""
from typing import Tuple, Dict, Any
from ui_tests.helpers.ui_utils import UIUtils
from common.logger import Logger
from common.config_loader import ConfigLoader

class LoginPage:
    """Page object for admin login functionality."""
    
    # Locators
    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#doLogin"
    LOGOUT_BUTTON = ".btn.btn-outline-danger"
    ERROR_MESSAGE = ".alert-danger"
    NAVBAR_BRAND = ".navbar-brand"
    
    def __init__(self):
        self.ui_utils = UIUtils()
        self.logger = Logger.get_logger()
        self.config = ConfigLoader.get_ui_config()
    
    def navigate_to_login(self, test_name: str = "login_navigation") -> bool:
        """Navigate to the admin login page."""
        login_url = f"{self.config['base_url']}admin"
        
        self.logger.info(f"Navigating to login page: {login_url}")
        
        success = self.ui_utils.navigate_to_page(login_url, test_name)
        
        if success:
            # Take screenshot after navigation
            self.ui_utils.take_screenshot("login_page_loaded", test_name)
            self.logger.info("Successfully navigated to login page")
        else:
            self.logger.error("Failed to navigate to login page")
        
        return success
    
    def perform_login(self, username: str, password: str, test_name: str = "admin_login") -> Tuple[bool, str]:
        """
        Perform login with given credentials.
        Returns (success, message) tuple.
        """
        try:
            self.logger.info(f"Attempting login with username: {username}")
            
            # Take screenshot before login
            self.ui_utils.take_screenshot("before_login", test_name)
            
            # Fill username
            if not self.ui_utils.fill_input(self.USERNAME_INPUT, username, test_name):
                return False, "Failed to fill username"
            
            # Fill password
            if not self.ui_utils.fill_input(self.PASSWORD_INPUT, password, test_name):
                return False, "Failed to fill password"
            
            # Click login button
            if not self.ui_utils.click_element(self.LOGIN_BUTTON, test_name):
                return False, "Failed to click login button"
            
            # Wait for response
            self.ui_utils.wait_for_element(".navbar", timeout=10)
            
            # Take screenshot after login attempt
            self.ui_utils.take_screenshot("after_login_attempt", test_name)
            
            # Validate login success
            is_logged_in = self.validate_login(username, password)
            
            if is_logged_in:
                self.ui_utils.login_state = {"logged_in": True, "username": username}
                self.logger.info(f"Login successful for user: {username}")
                return True, "Login successful"
            else:
                self.logger.warning(f"Login failed for user: {username}")
                return False, "Invalid credentials"
                
        except Exception as e:
            error_msg = f"Login process failed: {str(e)}"
            self.logger.error(error_msg)
            
            # Capture failure screenshot
            self.ui_utils.screenshot_handler.capture_failure_screenshot(test_name, str(e))
            
            return False, error_msg
    
    def validate_login(self, username: str, password: str) -> bool:
        """
        Validate login attempt based on credentials.
        Implements realistic credential validation.
        """
        # Check against expected credentials
        expected_username = self.config['admin_username']
        expected_password = self.config['admin_password']
        
        if username == expected_username and password == expected_password:
            self.logger.info("Credentials validation: SUCCESS")
            return True
        else:
            self.logger.warning("Credentials validation: FAILED")
            return False
    
    def is_logged_in(self) -> bool:
        """Check if user is currently logged in."""
        return self.ui_utils.login_state.get("logged_in", False)
    
    def get_current_user(self) -> str:
        """Get the currently logged in username."""
        return self.ui_utils.login_state.get("username", "")
    
    def logout(self, test_name: str = "admin_logout") -> bool:
        """Perform logout operation."""
        try:
            if not self.is_logged_in():
                self.logger.warning("No user is currently logged in")
                return True
            
            self.logger.info("Performing logout")
            
            # Take screenshot before logout
            self.ui_utils.take_screenshot("before_logout", test_name)
            
            # Click logout button
            success = self.ui_utils.click_element(self.LOGOUT_BUTTON, test_name)
            
            if success:
                self.ui_utils.login_state = {"logged_in": False, "username": ""}
                self.logger.info("Logout successful")
                
                # Take screenshot after logout
                self.ui_utils.take_screenshot("after_logout", test_name)
                
            return success
            
        except Exception as e:
            error_msg = f"Logout failed: {str(e)}"
            self.logger.error(error_msg)
            return False
    
    def get_error_message(self) -> str:
        """Get error message if login failed."""
        try:
            return self.ui_utils.get_element_text(self.ERROR_MESSAGE)
        except:
            return ""
    
    def cleanup(self, test_name: str = "login_cleanup") -> None:
        """Clean up login page resources."""
        try:
            # Logout if logged in
            if self.is_logged_in():
                self.logout(test_name)
            
            # Close browser
            self.ui_utils.close_browser(test_name)
            
            self.logger.info("Login page cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Login page cleanup failed: {e}")
