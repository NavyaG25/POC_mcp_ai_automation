"""
Booking API endpoint handler.
Manages booking creation, retrieval, and management operations.
"""
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
from api_tests.helpers.api_utils import APIUtils
from api_tests.endpoints.auth_api import AuthAPI
from common.logger import Logger
from common.config_loader import ConfigLoader

class BookingAPI:
    """Handles booking API operations."""
    
    def __init__(self):
        # Load configuration first
        ConfigLoader.load_config()
        
        self.logger = Logger.get_logger()
        self.api_utils = APIUtils()
        self.auth_api = AuthAPI()
        self.config = ConfigLoader.get_api_config()
        
        # API endpoints
        self.booking_endpoint = "/booking"
        self.booking_by_id_endpoint = "/booking/{booking_id}"
        
        self.logger.info("BookingAPI initialized")
    
    def create_booking(self, booking_data: Dict[str, Any], 
                      token: Optional[str] = None,
                      test_name: str = "create_booking") -> Tuple[bool, Dict[str, Any]]:
        """
        Create a new booking with authentication.
        
        Args:
            booking_data: Booking details dictionary
            token: Authentication token (if None, will generate new token)
            test_name: Test name for logging
            
        Returns:
            Tuple[bool, Dict]: (success, response_data)
        """
        try:
            self.logger.info("Creating new booking")
            
            # Get authentication token if not provided (None means auto-generate, empty string means no token)
            if token is None:
                auth_success, token, auth_response = self.auth_api.generate_token(test_name=f"{test_name}_auth")
                
                if not auth_success or not token:
                    error_msg = f"Failed to obtain authentication token: {auth_response}"
                    self.logger.error(error_msg)
                    return False, {'error': 'authentication_failed', 'details': auth_response}
            
            # Prepare headers with authentication (if token provided)
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            # Add authentication header only if token is provided and not empty
            if token and token.strip():
                headers['Cookie'] = f'token={token}'
            
            # Validate booking data
            validation_result = self.validate_booking_data(booking_data)
            if not validation_result['valid']:
                error_msg = f"Booking data validation failed: {validation_result['message']}"
                self.logger.error(error_msg)
                return False, {'error': 'validation_failed', 'details': validation_result}
            
            # Make booking creation request
            success, response = self.api_utils.post(
                endpoint=self.booking_endpoint,
                data=booking_data,
                headers=headers,
                test_name=test_name
            )
            
            if not success:
                error_msg = f"Booking creation request failed: {response}"
                self.logger.error(error_msg)
                return False, response
            
            # Validate response status (accept both 200 and 201)
            status_code = response.get('status_code', 0)
            if status_code not in [200, 201]:
                error_msg = f"Unexpected status code: {status_code}"
                self.logger.warning(error_msg)
            
            # Extract booking details from response
            response_data = response.get('data', {})
            
            # Validate response structure
            required_fields = ['bookingid']
            structure_valid, structure_msg = self.api_utils.validate_response_structure(
                response_data, required_fields, test_name
            )
            
            if structure_valid:
                booking_id = response_data.get('bookingid')
                self.logger.info(f"Booking created successfully with ID: {booking_id}")
                
                # Validate that booking details are echoed back
                booking_details = response_data.get('booking', {})
                echo_validation = self.validate_booking_echo(booking_data, booking_details)
                
                response['echo_validation'] = echo_validation
                
                return True, response
            else:
                # Check if this is an authorization error
                if status_code in [401, 403]:
                    error_msg = f"Authorization failed: {structure_msg}"
                    self.logger.error(error_msg)
                    return False, {'error': 'authorization_failed', 'status_code': status_code}
                else:
                    error_msg = f"Response structure validation failed: {structure_msg}"
                    self.logger.error(error_msg)
                    return False, {'error': 'invalid_response_structure', 'details': structure_msg}
                    
        except Exception as e:
            error_msg = f"Booking creation encountered error: {str(e)}"
            self.logger.error(error_msg)
            
            return False, {
                'error': 'booking_creation_exception',
                'message': str(e)
            }
    
    def get_booking(self, booking_id: int, test_name: str = "get_booking") -> Tuple[bool, Dict[str, Any]]:
        """
        Retrieve booking by ID.
        
        Returns:
            Tuple[bool, Dict]: (success, booking_data)
        """
        try:
            self.logger.info(f"Retrieving booking with ID: {booking_id}")
            
            endpoint = self.booking_by_id_endpoint.format(booking_id=booking_id)
            
            success, response = self.api_utils.get(
                endpoint=endpoint,
                test_name=test_name
            )
            
            if success:
                status_code = response.get('status_code', 0)
                if status_code == 200:
                    self.logger.info(f"Booking {booking_id} retrieved successfully")
                    return True, response
                elif status_code == 404:
                    self.logger.warning(f"Booking {booking_id} not found")
                    return False, {'error': 'booking_not_found', 'booking_id': booking_id}
                else:
                    self.logger.warning(f"Unexpected status code: {status_code}")
                    return False, response
            else:
                return False, response
                
        except Exception as e:
            error_msg = f"Error retrieving booking {booking_id}: {str(e)}"
            self.logger.error(error_msg)
            
            return False, {
                'error': 'get_booking_exception',
                'booking_id': booking_id,
                'message': str(e)
            }
    
    def validate_booking_data(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate booking data structure and content.
        
        Returns:
            Dict: Validation result with 'valid' boolean and 'message'
        """
        try:
            required_fields = ['firstname', 'lastname', 'totalprice', 'depositpaid', 'bookingdates']
            
            # Check required fields
            missing_fields = []
            for field in required_fields:
                if field not in booking_data:
                    missing_fields.append(field)
            
            if missing_fields:
                return {
                    'valid': False,
                    'message': f"Missing required fields: {', '.join(missing_fields)}"
                }
            
            # Validate booking dates structure
            booking_dates = booking_data.get('bookingdates', {})
            if not isinstance(booking_dates, dict):
                return {
                    'valid': False,
                    'message': "bookingdates must be an object"
                }
            
            date_fields = ['checkin', 'checkout']
            missing_date_fields = []
            for field in date_fields:
                if field not in booking_dates:
                    missing_date_fields.append(field)
            
            if missing_date_fields:
                return {
                    'valid': False,
                    'message': f"Missing date fields: {', '.join(missing_date_fields)}"
                }
            
            # Validate date format and logic
            try:
                checkin_date = datetime.strptime(booking_dates['checkin'], '%Y-%m-%d')
                checkout_date = datetime.strptime(booking_dates['checkout'], '%Y-%m-%d')
                
                if checkout_date <= checkin_date:
                    return {
                        'valid': False,
                        'message': "Checkout date must be after checkin date"
                    }
                    
            except ValueError as e:
                return {
                    'valid': False,
                    'message': f"Invalid date format: {str(e)}"
                }
            
            # Validate data types
            if not isinstance(booking_data.get('totalprice'), (int, float)):
                return {
                    'valid': False,
                    'message': "totalprice must be a number"
                }
            
            if not isinstance(booking_data.get('depositpaid'), bool):
                return {
                    'valid': False,
                    'message': "depositpaid must be a boolean"
                }
            
            return {
                'valid': True,
                'message': "Booking data validation successful"
            }
            
        except Exception as e:
            return {
                'valid': False,
                'message': f"Validation error: {str(e)}"
            }
    
    def validate_booking_echo(self, original_data: Dict[str, Any], 
                            echoed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that the API correctly echoes back the booking data.
        
        Returns:
            Dict: Validation result
        """
        try:
            validation_result = {
                'valid': True,
                'mismatches': [],
                'message': 'Booking data echoed correctly'
            }
            
            # Compare key fields
            fields_to_check = ['firstname', 'lastname', 'totalprice', 'depositpaid', 'additionalneeds']
            
            for field in fields_to_check:
                if field in original_data and field in echoed_data:
                    if original_data[field] != echoed_data[field]:
                        validation_result['valid'] = False
                        validation_result['mismatches'].append({
                            'field': field,
                            'original': original_data[field],
                            'echoed': echoed_data[field]
                        })
            
            # Check booking dates
            if 'bookingdates' in original_data and 'bookingdates' in echoed_data:
                orig_dates = original_data['bookingdates']
                echo_dates = echoed_data['bookingdates']
                
                for date_field in ['checkin', 'checkout']:
                    if orig_dates.get(date_field) != echo_dates.get(date_field):
                        validation_result['valid'] = False
                        validation_result['mismatches'].append({
                            'field': f'bookingdates.{date_field}',
                            'original': orig_dates.get(date_field),
                            'echoed': echo_dates.get(date_field)
                        })
            
            if not validation_result['valid']:
                validation_result['message'] = f"Data mismatch in {len(validation_result['mismatches'])} fields"
            
            return validation_result
            
        except Exception as e:
            return {
                'valid': False,
                'message': f"Echo validation error: {str(e)}",
                'mismatches': []
            }
    
    def create_sample_booking(self, guest_name: str = "John Doe", 
                            days_from_now: int = 1,
                            stay_duration: int = 2,
                            test_name: str = "sample_booking") -> Dict[str, Any]:
        """
        Create a sample booking with reasonable default values.
        
        Returns:
            Dict: Sample booking data
        """
        try:
            # Calculate dates
            checkin_date = (datetime.now() + timedelta(days=days_from_now)).strftime('%Y-%m-%d')
            checkout_date = (datetime.now() + timedelta(days=days_from_now + stay_duration)).strftime('%Y-%m-%d')
            
            # Split name
            name_parts = guest_name.split()
            firstname = name_parts[0] if name_parts else "John"
            lastname = name_parts[1] if len(name_parts) > 1 else "Doe"
            
            booking_data = {
                "firstname": firstname,
                "lastname": lastname,
                "totalprice": 150,
                "depositpaid": True,
                "bookingdates": {
                    "checkin": checkin_date,
                    "checkout": checkout_date
                },
                "additionalneeds": "Breakfast"
            }
            
            self.logger.info(f"Generated sample booking for {guest_name}")
            
            return booking_data
            
        except Exception as e:
            self.logger.error(f"Error creating sample booking: {e}")
            return {}
    
    def cleanup(self) -> None:
        """Clean up booking API resources."""
        try:
            self.auth_api.cleanup()
            self.api_utils.cleanup()
            self.logger.info("BookingAPI cleanup completed")
        except Exception as e:
            self.logger.error(f"BookingAPI cleanup failed: {e}")
