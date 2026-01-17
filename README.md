# Auto Dealership Voice Assistant

A production-grade Multi-Agent Voice Assistant system for auto dealership test drive booking using Python, LangChain, and advanced speech services.

## 🎯 Features

### Multi-Agent Architecture
- **Conversational Agent**: Natural language understanding, intent detection, dialogue management
- **Knowledge Agent**: Vehicle inventory management with intelligent search and filtering
- **Booking Agent**: Test drive scheduling with conflict detection and calendar management

### Speech Integration
- **Speech-to-Text (STT)**: OpenAI Whisper, Google Cloud, Azure, Simulated
- **Text-to-Speech (TTS)**: OpenAI, Google Cloud, Azure, ElevenLabs, Simulated

### Natural Language Processing
- Intent detection using LLMs
- Entity extraction (vehicle types, dates, times, customer details)
- Date/time normalization ("tomorrow at 11 AM" → 2026-01-18 11:00)
- Context-aware conversation flow

### Production-Grade Features
- Modular, extensible architecture following SOLID principles
- Comprehensive error handling and logging
- Environment-based configuration
- PEP 8 compliant code
- Unit tests included
- Scalable design

## 📁 Project Structure

```
auto-dealership-voice-assistant/
├── main.py                          # Application entry point
├── agents/                          # Multi-agent system
│   ├── conversational_agent.py      # Dialogue & intent detection
│   ├── knowledge_agent.py           # Vehicle knowledge base
│   └── booking_agent.py             # Scheduling & booking
├── services/                        # External services
│   └── speech_service.py            # STT & TTS integration
├── config/                          # Configuration
│   └── settings.py                  # Settings management
├── tests/                           # Unit tests
├── data/                            # Data storage (auto-generated)
├── output/                          # Generated audio files
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager
- OpenAI API key (for LLM and optional STT/TTS)

### Installation

**1. Download the project**
```bash
cd auto-dealership-voice-assistant
```

**2. Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment**
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

**5. Run the application**
```bash
python main.py
```

## 💬 Sample Conversation

```
Assistant: Hello! Welcome to our dealership. How can I assist you today?

You: I want to book a test drive for an SUV tomorrow at 11 AM
