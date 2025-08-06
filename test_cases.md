# Formal Test Cases Document

## UI Test Cases

### Test Case 1: Admin Login with Valid Credentials (Positive Scenario)
- **TCID**: UI_TC_001
- **Summary**: Verify admin can successfully login with valid credentials and access dashboard
- **Preconditions**: 
  - Browser is launched and navigated to https://automationintesting.online/
  - Admin login page is accessible
- **Test Steps**:
  1. Navigate to the admin login section
  2. Enter username: "admin"
  3. Enter password: "password"
  4. Click on login button
  5. Wait for dashboard to load
- **Expected Result**: 
  - Admin should be successfully logged in
  - Dashboard should be displayed with calendar view
  - Admin session should persist during browser session

### Test Case 2: Admin Login with Invalid Credentials (Negative Scenario)
- **TCID**: UI_TC_002
- **Summary**: Verify admin login fails with invalid credentials and appropriate error message is displayed
- **Preconditions**: 
  - Browser is launched and navigated to https://automationintesting.online/
  - Admin login page is accessible
- **Test Steps**:
  1. Navigate to the admin login section
  2. Enter username: "invaliduser"
  3. Enter password: "wrongpassword"
  4. Click on login button
  5. Observe the response
- **Expected Result**: 
  - Login should fail
  - Appropriate error message should be displayed
  - User should remain on login page
  - Dashboard should not be accessible

## API Test Cases

### Test Case 3: Generate Authentication Token with Valid Credentials (Positive Scenario)
- **TCID**: API_TC_001
- **Summary**: Verify successful token generation with valid admin credentials
- **Preconditions**: 
  - API endpoint https://restful-booker.herokuapp.com/auth is accessible
  - Valid admin credentials are available
- **Test Steps**:
  1. Send POST request to /auth endpoint
  2. Set Content-Type header to "application/json"
  3. Set Accept header to "application/json"
  4. Include valid credentials in request body: {"username": "admin", "password": "password123"}
  5. Execute the request
- **Expected Result**: 
  - Response status code should be 200 OK
  - Response body should contain JSON with "token" field
  - Token value should be a non-empty string

### Test Case 4: Create Booking with Authentication Token (Data Operation)
- **TCID**: API_TC_002
- **Summary**: Verify successful booking creation using valid authentication token
- **Preconditions**: 
  - Valid authentication token is available from /auth endpoint
  - API endpoint https://restful-booker.herokuapp.com/booking is accessible
- **Test Steps**:
  1. Obtain valid token from /auth endpoint
  2. Send POST request to /booking endpoint
  3. Set Content-Type header to "application/json"
  4. Set Accept header to "application/json"
  5. Include token in Cookie header: "token=<token_value>"
  6. Include booking details in request body with valid data
  7. Execute the request
- **Expected Result**: 
  - Response status code should be 200 OK or 201 Created
  - Response should contain "bookingid" (integer)
  - Response should echo back all booking details correctly
  - Booking should be created successfully in the system
