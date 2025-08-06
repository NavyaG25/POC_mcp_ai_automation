"""
Screenshot handler for the automation framework.
Manages screenshot capture and organization.
"""
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
from common.logger import Logger

class ScreenshotHandler:
    """Handles screenshot capture and management for UI tests."""
    
    def __init__(self):
        self.logger = Logger.get_logger()
        self.screenshots_dir = os.path.join(os.path.dirname(__file__), '..', 'screenshots')
        os.makedirs(self.screenshots_dir, exist_ok=True)
    
    def capture_screenshot(self, test_name: str, step_description: str, 
                          screenshot_data: Optional[str] = None, 
                          file_path: Optional[str] = None) -> str:
        """Capture and save screenshot with metadata."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_test_name = "".join(c for c in test_name if c.isalnum() or c in ('-', '_'))
            safe_step = "".join(c for c in step_description if c.isalnum() or c in ('-', '_'))
            
            filename = f"{safe_test_name}_{safe_step}_{timestamp}.png"
            screenshot_path = os.path.join(self.screenshots_dir, filename)
            
            if file_path and os.path.exists(file_path):
                # Copy existing screenshot file
                import shutil
                shutil.copy2(file_path, screenshot_path)
            elif screenshot_data:
                # Save base64 screenshot data
                import base64
                with open(screenshot_path, 'wb') as f:
                    f.write(base64.b64decode(screenshot_data))
            else:
                self.logger.warning(f"No screenshot data provided for {test_name}")
                return ""
            
            # Save metadata
            metadata = {
                'test_name': test_name,
                'step_description': step_description,
                'timestamp': timestamp,
                'filename': filename,
                'path': screenshot_path
            }
            
            metadata_path = screenshot_path.replace('.png', '_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Screenshot captured: {filename}")
            return screenshot_path
            
        except Exception as e:
            self.logger.error(f"Failed to capture screenshot: {e}")
            return ""
    
    def capture_failure_screenshot(self, test_name: str, error_msg: str) -> str:
        """Capture screenshot specifically for test failures."""
        return self.capture_screenshot(
            test_name=test_name,
            step_description=f"FAILURE_{error_msg[:50]}"
        )
    
    def get_screenshot_path(self, test_name: str, step_description: str = "default") -> str:
        """Get the expected path for a screenshot."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_test_name = "".join(c for c in test_name if c.isalnum() or c in ('-', '_'))
        safe_step = "".join(c for c in step_description if c.isalnum() or c in ('-', '_'))
        
        filename = f"{safe_test_name}_{safe_step}_{timestamp}.png"
        return os.path.join(self.screenshots_dir, filename)
