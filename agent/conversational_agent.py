"""
Conversational Agent - Handles dialogue, intent detection, and orchestration
"""

import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import re

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


class ConversationalAgent:
    """Agent responsible for managing conversation flow and intent detection."""
    
    def __init__(
        self,
        knowledge_agent,
        booking_agent,
        llm_api_key: str,
        model_name: str = "gpt-3.5-turbo"
    ):
        """Initialize the conversational agent.
        
        Args:
            knowledge_agent: Agent for car knowledge queries
            booking_agent: Agent for booking management
            llm_api_key: API key for LLM service
            model_name: Name of the LLM model to use
        """
        self.knowledge_agent = knowledge_agent
        self.booking_agent = booking_agent
        self.llm = ChatOpenAI(
            model_name=model_name,
            openai_api_key=llm_api_key,
            temperature=0.7
        )
        
        # Conversation state
        self.conversation_state = {
            'intent': None,
            'vehicle_type': None,
            'selected_vehicle': None,
            'date': None,
            'time': None,
            'awaiting_confirmation': False,
            'customer_name': None,
            'customer_phone': None
        }
        
        logger.info("Conversational Agent initialized")
    
    async def generate_greeting(self) -> str:
        """Generate a natural greeting for the customer.
        
        Returns:
            str: Greeting message
        """
        greetings = [
            "Hello! Welcome to our dealership. How can I assist you today?",
            "Good day! Thank you for calling. Are you interested in scheduling a test drive?",
            "Hi there! I'm here to help you book a test drive. What vehicle are you interested in?"
        ]
        return greetings[0]
    
    async def process_message(self, message: str) -> str:
        """Process customer message and generate appropriate response.
        
        Args:
            message: Customer's message
            
        Returns:
            str: Assistant's response
        """
        try:
            # Detect intent using LLM
            intent_info = await self._detect_intent(message)
            
            logger.info(f"Detected intent: {intent_info}")
            
            # Handle based on intent
            if intent_info['intent'] == 'test_drive_booking':
                return await self._handle_test_drive_booking(
                    message,
                    intent_info
                )
            elif intent_info['intent'] == 'information_request':
                return await self._handle_information_request(intent_info)
            elif intent_info['intent'] == 'confirmation':
                return await self._handle_confirmation(message)
            elif intent_info['intent'] == 'cancellation':
                return await self._handle_cancellation()
            else:
                return await self._handle_general_inquiry(message)
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return "I apologize, but I'm having trouble processing your request. Could you please rephrase that?"
    
    async def _detect_intent(self, message: str) -> Dict[str, Any]:
        """Detect customer intent using LLM.
        
        Args:
            message: Customer's message
            
        Returns:
            dict: Intent information including type and entities
        """
        system_prompt = """You are an intent detection system for an auto dealership.
        Analyze the customer's message and extract:
        1. Intent: test_drive_booking, information_request, confirmation, cancellation, general_inquiry
        2. Vehicle type: SUV, sedan, truck, coupe, etc. (if mentioned)
        3. Specific model: exact model name (if mentioned)
        4. Date/time: any temporal references
        5. Customer details: name, phone (if mentioned)
        
        Return a JSON object with these fields.
        """
        
        user_prompt = f"Customer message: {message}"
        
        response = self.llm.predict_messages([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        try:
            # Parse LLM response
            intent_data = json.loads(response.content)
            return intent_data
        except json.JSONDecodeError:
            # Fallback parsing
            return self._fallback_intent_detection(message)
    
    def _fallback_intent_detection(self, message: str) -> Dict[str, Any]:
        """Fallback intent detection using regex patterns.
        
        Args:
            message: Customer's message
            
        Returns:
            dict: Basic intent information
        """
        message_lower = message.lower()
        
        intent_data = {
            'intent': 'general_inquiry',
            'vehicle_type': None,
            'model': None,
            'date': None,
            'time': None
        }
        
        # Check for booking intent
        if any(word in message_lower for word in ['book', 'schedule', 'test drive', 'appointment']):
            intent_data['intent'] = 'test_drive_booking'
        
        # Check for confirmation
        if any(word in message_lower for word in ['yes', 'confirm', 'sure', 'okay', 'proceed']):
            intent_data['intent'] = 'confirmation'
        
        # Check for cancellation
        if any(word in message_lower for word in ['cancel', 'no thanks', 'never mind']):
            intent_data['intent'] = 'cancellation'
        
        # Extract vehicle type
        vehicle_types = ['suv', 'sedan', 'truck', 'coupe', 'hatchback']
        for vtype in vehicle_types:
            if vtype in message_lower:
                intent_data['vehicle_type'] = vtype.upper()
                break
        
        # Extract temporal references
        if 'tomorrow' in message_lower:
            intent_data['date'] = 'tomorrow'
        elif 'today' in message_lower:
            intent_data['date'] = 'today'
        
        # Extract time
        time_pattern = r'\b(\d{1,2})\s*(am|pm|AM|PM)\b'
        time_match = re.search(time_pattern, message)
        if time_match:
            intent_data['time'] = time_match.group(0)
        
        return intent_data
    
    async def _handle_test_drive_booking(
        self,
        message: str,
        intent_info: Dict[str, Any]
    ) -> str:
        """Handle test drive booking request.
        
        Args:
            message: Customer's message
            intent_info: Extracted intent information
            
        Returns:
            str: Response message
        """
        # Update conversation state
        self.conversation_state['intent'] = 'test_drive_booking'
        
        if intent_info.get('vehicle_type'):
            self.conversation_state['vehicle_type'] = intent_info['vehicle_type']
        
        if intent_info.get('date'):
            self.conversation_state['date'] = self._normalize_date(
                intent_info['date']
            )
        
        if intent_info.get('time'):
            self.conversation_state['time'] = self._normalize_time(
                intent_info['time']
            )
        
        # Query available vehicles
        if self.conversation_state['vehicle_type']:
            vehicles = self.knowledge_agent.search_vehicles(
                vehicle_type=self.conversation_state['vehicle_type']
            )
            
            if not vehicles:
                return f"I apologize, but we don't have any {self.conversation_state['vehicle_type']}s available at the moment. Would you like to explore other vehicle types?"
            
            # Present available vehicles
            response = f"Great! We have several {self.conversation_state['vehicle_type']}s available:\n\n"
            
            for i, vehicle in enumerate(vehicles[:3], 1):
                response += f"{i}. {vehicle['make']} {vehicle['model']} - {vehicle['year']}\n"
                response += f"   Features: {', '.join(vehicle['features'][:3])}\n"
                response += f"   Price: ${vehicle['price']:,}\n\n"
            
            response += "Which model would you like to test drive?"
            
            self.conversation_state['awaiting_confirmation'] = True
            
            return response
        else:
            return "I'd be happy to help you book a test drive! What type of vehicle are you interested in? We have SUVs, sedans, trucks, and more."
    
    async def _handle_information_request(
        self,
        intent_info: Dict[str, Any]
    ) -> str:
        """Handle information request about vehicles.
        
        Args:
            intent_info: Extracted intent information
            
        Returns:
            str: Response with vehicle information
        """
        if intent_info.get('model'):
            vehicle = self.knowledge_agent.get_vehicle_by_model(
                intent_info['model']
            )
            if vehicle:
                return self._format_vehicle_details(vehicle)
        
        return "I can provide information about our vehicles. What would you like to know?"
    
    async def _handle_confirmation(self, message: str) -> str:
        """Handle customer confirmation.
        
        Args:
            message: Customer's message
            
        Returns:
            str: Confirmation response
        """
        if not self.conversation_state['awaiting_confirmation']:
            return "I'm not sure what you're confirming. Could you please clarify?"
        
        # Extract model selection
        if self.conversation_state['vehicle_type']:
            vehicles = self.knowledge_agent.search_vehicles(
                vehicle_type=self.conversation_state['vehicle_type']
            )
            
            # Simple selection logic (can be enhanced)
            selected_vehicle = vehicles[0] if vehicles else None
            
            if selected_vehicle:
                self.conversation_state['selected_vehicle'] = selected_vehicle
                
                # Check if we have date and time
                if not self.conversation_state['date'] or not self.conversation_state['time']:
                    return "Great choice! When would you like to schedule your test drive? Please provide a date and time."
                
                # Create booking
                booking_result = self.booking_agent.create_booking(
                    vehicle=selected_vehicle,
                    date=self.conversation_state['date'],
                    time=self.conversation_state['time'],
                    customer_name=self.conversation_state.get('customer_name', 'Customer'),
                    customer_phone=self.conversation_state.get('customer_phone', 'N/A')
                )
                
                if booking_result['success']:
                    response = f"Perfect! Your test drive for the {selected_vehicle['make']} {selected_vehicle['model']} is confirmed for {self.conversation_state['date']} at {self.conversation_state['time']}. "
                    response += f"Booking ID: {booking_result['booking_id']}. We look forward to seeing you!"
                    
                    # Reset state
                    self._reset_conversation_state()
                    
                    return response
                else:
                    return f"I apologize, but there was an issue with the booking: {booking_result.get('error', 'Unknown error')}. Would you like to try a different time?"
        
        return "Thank you for confirming! How else can I help you today?"
    
    async def _handle_cancellation(self) -> str:
        """Handle cancellation request.
        
        Returns:
            str: Cancellation response
        """
        self._reset_conversation_state()
        return "No problem! If you change your mind or need any information about our vehicles, feel free to ask."
    
    async def _handle_general_inquiry(self, message: str) -> str:
        """Handle general inquiries.
        
        Args:
            message: Customer's message
            
        Returns:
            str: Response to general inquiry
        """
        return "I'm here to help you book a test drive or answer questions about our vehicles. What would you like to know?"
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to actual date.
        
        Args:
            date_str: Date string (e.g., 'tomorrow', 'today')
            
        Returns:
            str: Normalized date in YYYY-MM-DD format
        """
        today = datetime.now()
        
        if date_str.lower() == 'today':
            return today.strftime('%Y-%m-%d')
        elif date_str.lower() == 'tomorrow':
            return (today + timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            return date_str
    
    def _normalize_time(self, time_str: str) -> str:
        """Normalize time string.
        
        Args:
            time_str: Time string (e.g., '11 AM', '2:30 PM')
            
        Returns:
            str: Normalized time in HH:MM format
        """
        time_str = time_str.upper().strip()
        
        # Handle formats like "11 AM" or "11AM"
        pattern = r'(\d{1,2})(?::(\d{2}))?\s*(AM|PM)'
        match = re.match(pattern, time_str)
        
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            period = match.group(3)
            
            if period == 'PM' and hour != 12:
                hour += 12
            elif period == 'AM' and hour == 12:
                hour = 0
            
            return f"{hour:02d}:{minute:02d}"
        
        return time_str
    
    def _format_vehicle_details(self, vehicle: Dict[str, Any]) -> str:
        """Format vehicle details for presentation.
        
        Args:
            vehicle: Vehicle information dictionary
            
        Returns:
            str: Formatted vehicle details
        """
        details = f"{vehicle['make']} {vehicle['model']} ({vehicle['year']})\n"
        details += f"Type: {vehicle['type']}\n"
        details += f"Price: ${vehicle['price']:,}\n"
        details += f"Features: {', '.join(vehicle['features'])}\n"
        
        if 'specs' in vehicle:
            details += f"Specifications: {vehicle['specs']}"
        
        return details
    
    def _reset_conversation_state(self):
        """Reset conversation state for new interaction."""
        self.conversation_state = {
            'intent': None,
            'vehicle_type': None,
            'selected_vehicle': None,
            'date': None,
            'time': None,
            'awaiting_confirmation': False,
            'customer_name': None,
            'customer_phone': None
        }
