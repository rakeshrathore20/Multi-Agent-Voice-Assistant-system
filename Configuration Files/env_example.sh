# ====================================
# Auto Dealership Voice Assistant
# Environment Configuration
# ====================================

# ====================================
# LLM Configuration
# ====================================
OPENAI_API_KEY=your-openai-api-key-here
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.7

# ====================================
# Speech-to-Text Configuration
# ====================================
# Options: whisper, google, azure, simulated
STT_PROVIDER=simulated

# ====================================
# Text-to-Speech Configuration
# ====================================
# Options: openai, google, azure, elevenlabs, simulated
TTS_PROVIDER=simulated

# ====================================
# Google Cloud Configuration
# ====================================
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# ====================================
# Azure Configuration
# ====================================
AZURE_SPEECH_KEY=your-azure-speech-key
AZURE_SPEECH_REGION=eastus

# ====================================
# ElevenLabs Configuration
# ====================================
ELEVENLABS_API_KEY=your-elevenlabs-api-key

# ====================================
# Application Settings
# ====================================
DEBUG=False
LOG_LEVEL=INFO

# ====================================
# Business Configuration
# ====================================
BUSINESS_NAME=Premium Auto Dealership
BUSINESS_PHONE=1-800-AUTO-DEAL
BUSINESS_EMAIL=info@autodealership.com
