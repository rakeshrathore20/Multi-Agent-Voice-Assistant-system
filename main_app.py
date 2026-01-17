"""
Auto Dealership Voice Assistant - Main Application
Production-grade multi-agent system for test drive booking
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

from agents.conversational_agent import ConversationalAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.booking_agent import BookingAgent
from services.speech_service import SpeechService
from config.settings import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dealership_assistant.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class VoiceAssistant:
    """Main orchestrator for the multi-agent voice assistant."""
    
    def __init__(self, config: Settings):
        """Initialize the voice assistant with all agents and services.
        
        Args:
            config: Application configuration settings
        """
        self.config = config
        self.speech_service = SpeechService(config)
        
        # Initialize agents
        self.knowledge_agent = KnowledgeAgent(
            knowledge_base_path=config.KNOWLEDGE_BASE_PATH
        )
        self.booking_agent = BookingAgent(
            database_path=config.BOOKING_DB_PATH
        )
        self.conversational_agent = ConversationalAgent(
            knowledge_agent=self.knowledge_agent,
            booking_agent=self.booking_agent,
            llm_api_key=config.OPENAI_API_KEY
        )
        
        logger.info("Voice Assistant initialized successfully")
    
    async def process_voice_input(self, audio_file_path: str) -> dict:
        """Process voice input through the complete pipeline.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            dict: Processing result with transcript, response, and audio
        """
        try:
            # Step 1: Speech to Text
            logger.info("Converting speech to text...")
            transcript = await self.speech_service.speech_to_text(
                audio_file_path
            )
            logger.info(f"Transcript: {transcript}")
            
            # Step 2: Process through conversational agent
            logger.info("Processing through conversational agent...")
            response_text = await self.conversational_agent.process_message(
                transcript
            )
            logger.info(f"Response: {response_text}")
            
            # Step 3: Text to Speech
            logger.info("Converting response to speech...")
            audio_response = await self.speech_service.text_to_speech(
                response_text
            )
            
            return {
                'success': True,
                'transcript': transcript,
                'response_text': response_text,
                'audio_response': audio_response,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing voice input: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def run_interactive_session(self):
        """Run an interactive voice session with the customer."""
        logger.info("Starting interactive session...")
        
        print("\n" + "="*60)
        print("Auto Dealership Voice Assistant")
        print("="*60)
        print("\nWelcome! I can help you book a test drive.")
        print("Type your message or 'quit' to exit.\n")
        
        # Initial greeting
        greeting = await self.conversational_agent.generate_greeting()
        print(f"Assistant: {greeting}\n")
        
        # Convert greeting to speech
        await self.speech_service.text_to_speech(greeting)
        
        while True:
            try:
                # Get user input (simulating voice input with text)
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    farewell = "Thank you for contacting our dealership. Have a great day!"
                    print(f"Assistant: {farewell}")
                    await self.speech_service.text_to_speech(farewell)
                    break
                
                if not user_input:
                    continue
                
                # Process through conversational agent
                response = await self.conversational_agent.process_message(
                    user_input
                )
                print(f"Assistant: {response}\n")
                
                # Convert to speech
                await self.speech_service.text_to_speech(response)
                
            except KeyboardInterrupt:
                print("\n\nSession ended by user.")
                break
            except Exception as e:
                logger.error(f"Error in interactive session: {str(e)}")
                print(f"Error: {str(e)}\n")


async def main():
    """Main entry point for the application."""
    try:
        # Load configuration
        config = Settings()
        
        # Initialize voice assistant
        assistant = VoiceAssistant(config)
        
        # Run interactive session
        await assistant.run_interactive_session()
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
