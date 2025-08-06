"""
Pytest configuration and fixtures for the automation framework.
Provides common test setup and teardown functionality.
"""
import pytest
import os
import sys
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from common.logger import Logger
from common.config_loader import ConfigLoader
from common.screenshot_handler import ScreenshotHandler

def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Initialize logger
    Logger.setup_logger('automation_framework')
    logger = Logger.get_logger()
    
    # Load configuration
    ConfigLoader.load_config()
    
    logger.info("Pytest configuration initialized")
    logger.info(f"Test session started at: {datetime.now().isoformat()}")

def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    logger = Logger.get_logger()
    logger.info("Starting test session")
    
    # Create necessary directories
    directories = ['logs', 'screenshots', 'reports']
    for directory in directories:
        dir_path = os.path.join(os.path.dirname(__file__), directory)
        os.makedirs(dir_path, exist_ok=True)
    
    logger.info("Test session setup completed")

def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished."""
    logger = Logger.get_logger()
    
    test_count = session.testscollected
    failed_count = session.testsfailed
    passed_count = test_count - failed_count
    
    logger.info(f"Test session finished")
    logger.info(f"Total tests: {test_count}, Passed: {passed_count}, Failed: {failed_count}")
    logger.info(f"Exit status: {exitstatus}")
    logger.info(f"Test session ended at: {datetime.now().isoformat()}")

@pytest.fixture(scope="session")
def config():
    """Provide configuration for tests."""
    return ConfigLoader.load_config()

@pytest.fixture(scope="session")
def logger():
    """Provide logger for tests."""
    return Logger.get_logger()

@pytest.fixture(scope="function")
def screenshot_handler():
    """Provide screenshot handler for tests."""
    return ScreenshotHandler()

def pytest_runtest_makereport(item, call):
    """Called to create a test report for each test item."""
    if call.when == "call":
        logger = Logger.get_logger()
        
        if call.excinfo is None:
            logger.info(f"PASSED: {item.nodeid}")
        else:
            logger.error(f"FAILED: {item.nodeid}")
            
            # Capture failure screenshot if it's a UI test
            if "ui" in item.keywords:
                try:
                    screenshot_handler = ScreenshotHandler()
                    test_name = item.nodeid.replace("::", "_").replace("/", "_")
                    screenshot_handler.capture_failure_screenshot(
                        test_name=test_name,
                        error_msg=str(call.excinfo.value)
                    )
                except Exception as e:
                    logger.error(f"Failed to capture failure screenshot: {e}")

def pytest_collection_modifyitems(config, items):
    """Modify collected test items."""
    logger = Logger.get_logger()
    logger.info(f"Collected {len(items)} test items")
    
    # Add markers based on test file location
    for item in items:
        if "ui_tests" in str(item.fspath):
            item.add_marker(pytest.mark.ui)
        elif "api_tests" in str(item.fspath):
            item.add_marker(pytest.mark.api)

# Custom markers
pytest_plugins = []
