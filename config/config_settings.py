"""
Configuration Settings - Application configuration and environment variables
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application configuration settings."""
    
    def __init__(self):
        """Initialize settings from environment variables."""
        
        # Base paths
        self.BASE_DIR = Path(__file__).parent.parent
        self.DATA_DIR = self.BASE_DIR / "data"
        self.OUTPUT_DIR = self.BASE_DIR / "output"
        
        # Create directories if they don't exist
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Knowledge base
        self.KNOWLEDGE_BASE_PATH = str(
            self.DATA_DIR / "vehicle_knowledge_base.json"
        )
        
        # Booking database
        self.BOOKING_DB_PATH = str(
            self.DATA_DIR / "bookings.json"
        )
        
        # LLM Configuration
        self.OPENAI_API_KEY = os.getenv(
            "OPENAI_API_KEY",
            "your-openai-api-key-here"
        )
        self.LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        
        # Speech-to-Text Configuration
        self.STT_PROVIDER = os.getenv("STT_PROVIDER", "simulated")
        # Options: whisper, google, azure, simulated
        
        # Text-to-Speech Configuration
        self.TTS_PROVIDER = os.getenv("TTS_PROVIDER", "simulated")
        # Options: openai, google, azure, elevenlabs, simulated
        
        # Google Cloud Configuration
        self.GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.GOOGLE_APPLICATION_CREDENTIALS = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS"
        )
        
        # Azure Configuration
        self.AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
        self.AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "eastus")
        
        # ElevenLabs Configuration
        self.ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
        
        # Application Settings
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
        # Business Configuration
        self.BUSINESS_NAME = os.getenv(
            "BUSINESS_NAME",
            "Premium Auto Dealership"
        )
        self.BUSINESS_PHONE = os.getenv("BUSINESS_PHONE", "1-800-AUTO-DEAL")
        self.BUSINESS_EMAIL = os.getenv(
            "BUSINESS_EMAIL",
            "info@autodealership.com"
        )
        
    def validate(self) -> bool:
        """Validate that required settings are configured.
        
        Returns:
            bool: True if valid, raises exception otherwise
        """
        errors = []
        
        # Check if using real services but missing API keys
        if self.STT_PROVIDER == "whisper" and self.OPENAI_API_KEY == "your-openai-api-key-here":
            errors.append("OpenAI API key required for Whisper STT")
        
        if self.STT_PROVIDER == "google" and not self.GOOGLE_APPLICATION_CREDENTIALS:
            errors.append("Google Cloud credentials required for Google STT")
        
        if self.STT_PROVIDER == "azure" and not self.AZURE_SPEECH_KEY:
            errors.append("Azure Speech key required for Azure STT")
        
        if self.TTS_PROVIDER == "openai" and self.OPENAI_API_KEY == "your-openai-api-key-here":
            errors.append("OpenAI API key required for OpenAI TTS")
        
        if self.TTS_PROVIDER == "elevenlabs" and not self.ELEVENLABS_API_KEY:
            errors.append("ElevenLabs API key required for ElevenLabs TTS")
        
        if errors:
            error_msg = "Configuration errors:\n" + "\n".join(f"- {e}" for e in errors)
            raise ValueError(error_msg)
        
        return True
    
    def get_summary(self) -> str:
        """Get configuration summary.
        
        Returns:
            str: Configuration summary
        """
        summary = f"""
Configuration Summary:
---------------------
Business: {self.BUSINESS_NAME}
Data Directory: {self.DATA_DIR}
Knowledge Base: {self.KNOWLEDGE_BASE_PATH}
Booking Database: {self.BOOKING_DB_PATH}

LLM Configuration:
- Provider: OpenAI
- Model: {self.LLM_MODEL}
- Temperature: {self.LLM_TEMPERATURE}

Speech Services:
- STT Provider: {self.STT_PROVIDER}
- TTS Provider: {self.TTS_PROVIDER}

Debug Mode: {self.DEBUG}
Log Level: {self.LOG_LEVEL}
"""
        return summary


# Create global settings instance
settings = Settings()
