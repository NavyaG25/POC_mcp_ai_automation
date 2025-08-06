# Automation Framework

A comprehensive UI and API test automation framework built with Python, Playwright MCP, and pytest. This framework provides robust testing capabilities for web applications with proper error handling, logging, and reporting.

## 🏗️ Project Structure

```
automation_project/
│
├── ui_tests/                          # UI test automation
│   ├── pages/                         # Page Object Model classes
│   │   ├── login_page.py             # Login functionality
│   │   ├── dashboard_page.py         # Dashboard operations
│   │   └── booking_page.py           # Booking form handling
│   ├── tests/                        # UI test cases
│   │   ├── test_admin_login.py       # Admin login scenarios
│   │   └── test_create_booking.py    # Booking creation tests
│   └── helpers/                      # UI utilities
│       └── ui_utils.py               # MCP browser utilities
│
├── api_tests/                        # API test automation
│   ├── endpoints/                    # API endpoint classes
│   │   ├── auth_api.py              # Authentication endpoints
│   │   └── booking_api.py           # Booking API operations
│   ├── tests/                       # API test cases
│   │   ├── test_token_generation.py # Token management tests
│   │   └── test_create_booking_api.py# API booking tests
│   └── helpers/                     # API utilities
│       └── api_utils.py             # API utilities
│
├── common/                          # Shared components
│   ├── config_loader.py            # Environment configuration
│   ├── logger.py                   # Logging setup
│   ├── screenshot_handler.py       # Screenshot management
│   └── ai_debugger.py             # AI debug context
│
├── logs/                           # Generated logs
├── screenshots/                    # Test screenshots
├── reports/                        # Test reports
├── .env                           # Environment variables
├── conftest.py                    # Pytest configuration
├── pytest.ini                    # Pytest settings
├── requirements.txt               # Dependencies
└── README.md                      # This file
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Node.js (for Playwright MCP)
- VS Code with MCP configuration

### 2. Installation

```bash
# Clone or navigate to the project directory
cd automation_project

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers (if using direct Playwright)
playwright install
```

### 3. Configuration

Create or verify the `.env` file with your test environment settings:

```env
# UI Testing
UI_BASE_URL=https://automationintesting.online/
UI_ADMIN_USERNAME=admin
UI_ADMIN_PASSWORD=password

# API Testing  
API_BASE_URL=https://restful-booker.herokuapp.com
API_USERNAME=admin
API_PASSWORD=password123

# Test Configuration
BROWSER_TYPE=chromium
HEADLESS=false
TIMEOUT=30000
SCREENSHOT_ON_FAILURE=true
```

### 4. Running Tests

```bash
# Run all tests
pytest -v

# Run only UI tests
pytest -m ui -v

# Run only API tests
pytest -m api -v

# Run smoke tests
pytest -m smoke -v

# Run with HTML report
pytest --html=reports/report.html --self-contained-html
```

## 🎯 Test Cases Covered

### UI Test Cases
- **UI_TC_001**: Admin login with valid credentials
- **UI_TC_002**: Admin login with invalid credentials
- **UI_TC_003**: Guest booking creation and verification

### API Test Cases
- **API_TC_001**: Generate authentication token with valid credentials
- **API_TC_002**: Create booking with authentication token

## 🔧 Framework Features

### UI Automation Features
- **MCP Integration**: Uses Playwright MCP for browser automation
- **Fallback Behavior**: Graceful handling when MCP functions are unavailable
- **Page Object Model**: Clean separation of test logic and page elements
- **Screenshot Capture**: Automatic screenshots on failures and key steps
- **State Management**: Proper login state tracking across page objects

### API Automation Features
- **Robust HTTP Client**: Built-in retry logic and error handling
- **Authentication Management**: Token generation and validation
- **Response Validation**: Structured validation of API responses
- **Data Validation**: Comprehensive request/response data validation

### Common Features
- **Comprehensive Logging**: Structured logging with multiple output formats
- **Configuration Management**: Environment-based configuration loading
- **Error Handling**: Detailed error context capture for debugging
- **AI Debug Context**: Captures context for AI-assisted debugging
- **CI/CD Ready**: Proper exit codes and artifact generation

## 📊 Reporting and Logging

### Log Files
- `logs/automation_YYYYMMDD.log` - Main application logs
- `logs/api_responses_YYYYMMDD.log` - API request/response logs
- `logs/ai_debug_responses.json` - AI debugging context

### Screenshots
- Automatic capture on test failures
- Step-by-step screenshots for documentation
- Organized by test name and timestamp

### HTML Reports
```bash
pytest --html=reports/report.html --self-contained-html
```

## 🛠️ Development Guidelines

### Adding New UI Tests
1. Create page objects in `ui_tests/pages/`
2. Implement test cases in `ui_tests/tests/`
3. Use appropriate pytest markers (`@pytest.mark.ui`, `@pytest.mark.smoke`)
4. Follow the existing error handling patterns

### Adding New API Tests
1. Create endpoint classes in `api_tests/endpoints/`
2. Implement test cases in `api_tests/tests/`
3. Use appropriate pytest markers (`@pytest.mark.api`, `@pytest.mark.regression`)
4. Include proper request/response validation

### Configuration
- Add new environment variables to `.env`
- Update `common/config_loader.py` for new configuration options
- Ensure default values are provided for all configuration keys

## 🔍 Troubleshooting

### Common Issues

1. **MCP Function Unavailable**
   - Framework includes fallback behavior
   - Check logs for MCP function availability
   - Verify VS Code MCP configuration

2. **Authentication Failures**
   - Verify API credentials in `.env`
   - Check API endpoint availability
   - Review authentication logs

3. **Import Errors**
   - Ensure all `__init__.py` files are present
   - Verify Python path configuration
   - Check dependency installation

### Debug Mode
```bash
# Run with verbose logging
pytest -v -s --log-cli-level=DEBUG

# Run single test with debugging
pytest -v -s ui_tests/tests/test_admin_login.py::TestAdminLogin::test_admin_login_valid_credentials
```

## 📈 Performance Considerations

- Tests include timeout configurations
- Retry logic for flaky operations
- Resource cleanup in teardown methods
- Efficient screenshot capture

## 🔐 Security Notes

- Credentials stored in `.env` file (not committed to version control)
- Token management with proper cleanup
- Secure handling of authentication data

## 🤝 Contributing

1. Follow the existing code structure
2. Add appropriate test coverage
3. Update documentation
4. Ensure all tests pass before submitting

## 📄 License

This project is for educational and testing purposes.

## 🆘 Support

For issues and questions:
1. Check the logs in `logs/` directory
2. Review AI debug context in `logs/ai_debug_responses.json`
3. Ensure environment configuration is correct
4. Verify all dependencies are installed

---

**Framework Version**: 1.0  
**Last Updated**: August 2025  
**Python Version**: 3.8+  
**Pytest Version**: 8.0+
