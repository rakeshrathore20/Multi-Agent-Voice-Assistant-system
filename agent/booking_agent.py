"""
Booking Agent - Manages test drive scheduling and calendar integration
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)


class BookingAgent:
    """Agent responsible for managing test drive bookings."""
    
    def __init__(self, database_path: str):
        """Initialize the booking agent.
        
        Args:
            database_path: Path to the booking database file
        """
        self.database_path = Path(database_path)
        self.bookings = []
        self.business_hours = {
            'start': '09:00',
            'end': '18:00'
        }
        self._load_database()
        
        logger.info(f"Booking Agent initialized with {len(self.bookings)} existing bookings")
    
    def _load_database(self):
        """Load booking data from JSON file."""
        try:
            if not self.database_path.exists():
                self._create_default_database()
            
            with open(self.database_path, 'r') as f:
                data = json.load(f)
                self.bookings = data.get('bookings', [])
                
            logger.info(f"Loaded {len(self.bookings)} bookings from database")
            
        except Exception as e:
            logger.error(f"Error loading booking database: {str(e)}")
            self.bookings = []
    
    def _create_default_database(self):
        """Create a default booking database if none exists."""
        default_data = {
            "bookings": [],
            "settings": {
                "business_hours": {
                    "start": "09:00",
                    "end": "18:00"
                },
                "booking_duration_minutes": 30,
                "max_daily_bookings": 20
            }
        }
        
        # Create directory if it doesn't exist
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.database_path, 'w') as f:
            json.dump(default_data, f, indent=2)
        
        logger.info("Created default booking database")
    
    def create_booking(
        self,
        vehicle: Dict[str, Any],
        date: str,
        time: str,
        customer_name: str,
        customer_phone: str,
        customer_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new test drive booking.
        
        Args:
            vehicle: Vehicle information dictionary
            date: Booking date (YYYY-MM-DD format)
            time: Booking time (HH:MM format)
            customer_name: Customer's name
            customer_phone: Customer's phone number
            customer_email: Customer's email (optional)
            
        Returns:
            dict: Booking result with success status and booking ID
        """
        try:
            # Validate date and time
            validation_result = self._validate_booking_time(date, time)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # Check for conflicts
            if self._has_conflict(date, time, vehicle['id']):
                return {
                    'success': False,
                    'error': 'This time slot is already booked. Please choose a different time.'
                }
            
            # Generate booking ID
            booking_id = str(uuid.uuid4())[:8].upper()
            
            # Create booking record
            booking = {
                'booking_id': booking_id,
                'vehicle': {
                    'id': vehicle['id'],
                    'make': vehicle['make'],
                    'model': vehicle['model'],
                    'year': vehicle['year']
                },
                'date': date,
                'time': time,
                'customer': {
                    'name': customer_name,
                    'phone': customer_phone,
                    'email': customer_email
                },
                'status': 'confirmed',
                'created_at': datetime.now().isoformat(),
                'duration_minutes': 30
            }
            
            self.bookings.append(booking)
            self._save_database()
            
            logger.info(f"Created booking {booking_id} for {customer_name}")
            
            return {
                'success': True,
                'booking_id': booking_id,
                'booking': booking
            }
            
        except Exception as e:
            logger.error(f"Error creating booking: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to create booking: {str(e)}'
            }
    
    def _validate_booking_time(
        self,
        date: str,
        time: str
    ) -> Dict[str, Any]:
        """Validate booking date and time.
        
        Args:
            date: Booking date
            time: Booking time
            
        Returns:
            dict: Validation result
        """
        try:
            # Parse date
            booking_date = datetime.strptime(date, '%Y-%m-%d')
            
            # Check if date is in the past
            if booking_date.date() < datetime.now().date():
                return {
                    'valid': False,
                    'error': 'Cannot book test drives for past dates.'
                }
            
            # Parse time
            booking_time = datetime.strptime(time, '%H:%M').time()
            business_start = datetime.strptime(
                self.business_hours['start'],
                '%H:%M'
            ).time()
            business_end = datetime.strptime(
                self.business_hours['end'],
                '%H:%M'
            ).time()
            
            # Check if time is within business hours
            if not (business_start <= booking_time <= business_end):
                return {
                    'valid': False,
                    'error': f'Bookings are only available between {self.business_hours["start"]} and {self.business_hours["end"]}.'
                }
            
            return {'valid': True}
            
        except ValueError as e:
            return {
                'valid': False,
                'error': f'Invalid date or time format: {str(e)}'
            }
    
    def _has_conflict(
        self,
        date: str,
        time: str,
        vehicle_id: str
    ) -> bool:
        """Check if booking conflicts with existing bookings.
        
        Args:
            date: Booking date
            time: Booking time
            vehicle_id: Vehicle identifier
            
        Returns:
            bool: True if conflict exists, False otherwise
        """
        for booking in self.bookings:
            if (booking['date'] == date and
                booking['time'] == time and
                booking['vehicle']['id'] == vehicle_id and
                booking['status'] != 'cancelled'):
                return True
        return False
    
    def get_available_slots(
        self,
        date: str,
        vehicle_id: Optional[str] = None
    ) -> List[str]:
        """Get available time slots for a given date.
        
        Args:
            date: Date to check availability (YYYY-MM-DD format)
            vehicle_id: Optional vehicle ID to check specific vehicle availability
            
        Returns:
            List of available time slots
        """
        # Generate all possible slots
        start_hour = int(self.business_hours['start'].split(':')[0])
        end_hour = int(self.business_hours['end'].split(':')[0])
        
        all_slots = []
        for hour in range(start_hour, end_hour):
            all_slots.append(f"{hour:02d}:00")
            all_slots.append(f"{hour:02d}:30")
        
        # Filter out booked slots
        booked_slots = set()
        for booking in self.bookings:
            if (booking['date'] == date and
                booking['status'] != 'cancelled'):
                if vehicle_id is None or booking['vehicle']['id'] == vehicle_id:
                    booked_slots.add(booking['time'])
        
        available_slots = [slot for slot in all_slots if slot not in booked_slots]
        
        return available_slots
    
    def get_booking_by_id(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve booking by ID.
        
        Args:
            booking_id: Booking identifier
            
        Returns:
            Booking dictionary or None if not found
        """
        for booking in self.bookings:
            if booking['booking_id'] == booking_id:
                return booking
        return None
    
    def cancel_booking(self, booking_id: str) -> Dict[str, Any]:
        """Cancel a booking.
        
        Args:
            booking_id: Booking identifier
            
        Returns:
            dict: Cancellation result
        """
        booking = self.get_booking_by_id(booking_id)
        
        if not booking:
            return {
                'success': False,
                'error': 'Booking not found'
            }
        
        if booking['status'] == 'cancelled':
            return {
                'success': False,
                'error': 'Booking is already cancelled'
            }
        
        booking['status'] = 'cancelled'
        booking['cancelled_at'] = datetime.now().isoformat()
        
        self._save_database()
        
        logger.info(f"Cancelled booking {booking_id}")
        
        return {
            'success': True,
            'message': 'Booking cancelled successfully'
        }
    
    def reschedule_booking(
        self,
        booking_id: str,
        new_date: str,
        new_time: str
    ) -> Dict[str, Any]:
        """Reschedule an existing booking.
        
        Args:
            booking_id: Booking identifier
            new_date: New date
            new_time: New time
            
        Returns:
            dict: Rescheduling result
        """
        booking = self.get_booking_by_id(booking_id)
        
        if not booking:
            return {
                'success': False,
                'error': 'Booking not found'
            }
        
        # Validate new time
        validation_result = self._validate_booking_time(new_date, new_time)
        if not validation_result['valid']:
            return {
                'success': False,
                'error': validation_result['error']
            }
        
        # Check for conflicts
        if self._has_conflict(new_date, new_time, booking['vehicle']['id']):
            return {
                'success': False,
                'error': 'The new time slot is already booked.'
            }
        
        # Update booking
        booking['date'] = new_date
        booking['time'] = new_time
        booking['rescheduled_at'] = datetime.now().isoformat()
        
        self._save_database()
        
        logger.info(f"Rescheduled booking {booking_id}")
        
        return {
            'success': True,
            'message': 'Booking rescheduled successfully',
            'booking': booking
        }
    
    def get_bookings_by_date(self, date: str) -> List[Dict[str, Any]]:
        """Get all bookings for a specific date.
        
        Args:
            date: Date to query (YYYY-MM-DD format)
            
        Returns:
            List of bookings for the date
        """
        return [
            booking for booking in self.bookings
            if booking['date'] == date and booking['status'] != 'cancelled'
        ]
    
    def get_customer_bookings(
        self,
        customer_phone: str
    ) -> List[Dict[str, Any]]:
        """Get all bookings for a customer.
        
        Args:
            customer_phone: Customer's phone number
            
        Returns:
            List of customer's bookings
        """
        return [
            booking for booking in self.bookings
            if booking['customer']['phone'] == customer_phone
        ]
    
    def _save_database(self):
        """Save current booking data to JSON file."""
        try:
            data = {
                'bookings': self.bookings,
                'settings': {
                    'business_hours': self.business_hours,
                    'booking_duration_minutes': 30,
                    'max_daily_bookings': 20
                }
            }
            
            with open(self.database_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info("Booking database saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving booking database: {str(e)}")
