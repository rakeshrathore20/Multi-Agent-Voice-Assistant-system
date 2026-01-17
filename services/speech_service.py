"""
Speech Service - Handles Speech-to-Text and Text-to-Speech
"""

import logging
from typing import Optional
import asyncio
from pathlib import Path

# For production, you would use actual STT/TTS services
# This demonstrates the interface with simulated implementations

logger = logging.getLogger(__name__)


class SpeechService:
    """Service for handling speech recognition and synthesis."""
    
    def __init__(self, config):
        """Initialize the speech service.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.stt_provider = config.STT_PROVIDER
        self.tts_provider = config.TTS_PROVIDER
        
        logger.info(f"Speech Service initialized (STT: {self.stt_provider}, TTS: {self.tts_provider})")
    
    async def speech_to_text(self, audio_file_path: str) -> str:
        """Convert speech audio to text.
        
        In production, this would use services like:
        - Google Cloud Speech-to-Text
        - AWS Transcribe
        - Azure Speech Services
        - OpenAI Whisper API
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            str: Transcribed text
        """
        try:
            if self.stt_provider == 'whisper':
                return await self._whisper_stt(audio_file_path)
            elif self.stt_provider == 'google':
                return await self._google_stt(audio_file_path)
            elif self.stt_provider == 'azure':
                return await self._azure_stt(audio_file_path)
            else:
                return await self._simulated_stt(audio_file_path)
                
        except Exception as e:
            logger.error(f"STT error: {str(e)}")
            raise
    
    async def _whisper_stt(self, audio_file_path: str) -> str:
        """Use OpenAI Whisper for speech recognition.
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            str: Transcribed text
        """
        try:
            import openai
            
            openai.api_key = self.config.OPENAI_API_KEY
            
            with open(audio_file_path, 'rb') as audio_file:
                transcript = await asyncio.to_thread(
                    openai.Audio.transcribe,
                    "whisper-1",
                    audio_file
                )
            
            logger.info("Whisper STT completed")
            return transcript['text']
            
        except ImportError:
            logger.warning("OpenAI library not available, using simulation")
            return await self._simulated_stt(audio_file_path)
        except Exception as e:
            logger.error(f"Whisper STT error: {str(e)}")
            raise
    
    async def _google_stt(self, audio_file_path: str) -> str:
        """Use Google Cloud Speech-to-Text.
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            str: Transcribed text
        """
        try:
            from google.cloud import speech
            
            client = speech.SpeechClient()
            
            with open(audio_file_path, 'rb') as audio_file:
                content = audio_file.read()
            
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
            )
            
            response = await asyncio.to_thread(
                client.recognize,
                config=config,
                audio=audio
            )
            
            transcript = ' '.join([
                result.alternatives[0].transcript
                for result in response.results
            ])
            
            logger.info("Google STT completed")
            return transcript
            
        except ImportError:
            logger.warning("Google Cloud library not available, using simulation")
            return await self._simulated_stt(audio_file_path)
        except Exception as e:
            logger.error(f"Google STT error: {str(e)}")
            raise
    
    async def _azure_stt(self, audio_file_path: str) -> str:
        """Use Azure Speech Services for speech recognition.
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            str: Transcribed text
        """
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            speech_config = speechsdk.SpeechConfig(
                subscription=self.config.AZURE_SPEECH_KEY,
                region=self.config.AZURE_SPEECH_REGION
            )
            audio_config = speechsdk.AudioConfig(filename=audio_file_path)
            
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            
            result = await asyncio.to_thread(
                speech_recognizer.recognize_once
            )
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                logger.info("Azure STT completed")
                return result.text
            else:
                raise Exception(f"Speech recognition failed: {result.reason}")
                
        except ImportError:
            logger.warning("Azure SDK not available, using simulation")
            return await self._simulated_stt(audio_file_path)
        except Exception as e:
            logger.error(f"Azure STT error: {str(e)}")
            raise
    
    async def _simulated_stt(self, audio_file_path: str) -> str:
        """Simulated STT for testing without API keys.
        
        Args:
            audio_file_path: Path to audio file (ignored in simulation)
            
        Returns:
            str: Simulated transcript
        """
        logger.info("Using simulated STT (for testing)")
        await asyncio.sleep(0.5)  # Simulate processing time
        
        # Return empty string to indicate user should type their message
        return ""
    
    async def text_to_speech(
        self,
        text: str,
        output_path: Optional[str] = None
    ) -> str:
        """Convert text to speech audio.
        
        In production, this would use services like:
        - Google Cloud Text-to-Speech
        - AWS Polly
        - Azure Speech Services
        - OpenAI TTS
        - ElevenLabs
        
        Args:
            text: Text to convert to speech
            output_path: Optional path to save audio file
            
        Returns:
            str: Path to generated audio file
        """
        try:
            if self.tts_provider == 'openai':
                return await self._openai_tts(text, output_path)
            elif self.tts_provider == 'google':
                return await self._google_tts(text, output_path)
            elif self.tts_provider == 'azure':
                return await self._azure_tts(text, output_path)
            elif self.tts_provider == 'elevenlabs':
                return await self._elevenlabs_tts(text, output_path)
            else:
                return await self._simulated_tts(text, output_path)
                
        except Exception as e:
            logger.error(f"TTS error: {str(e)}")
            raise
    
    async def _openai_tts(
        self,
        text: str,
        output_path: Optional[str] = None
    ) -> str:
        """Use OpenAI TTS for speech synthesis.
        
        Args:
            text: Text to convert
            output_path: Optional output path
            
        Returns:
            str: Path to audio file
        """
        try:
            import openai
            from pathlib import Path
            
            openai.api_key = self.config.OPENAI_API_KEY
            
            if not output_path:
                output_path = f"output/tts_{hash(text)}.mp3"
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            response = await asyncio.to_thread(
                openai.Audio.create_speech,
                model="tts-1",
                voice="alloy",
                input=text
            )
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"OpenAI TTS completed: {output_path}")
            return output_path
            
        except ImportError:
            logger.warning("OpenAI library not available, using simulation")
            return await self._simulated_tts(text, output_path)
        except Exception as e:
            logger.error(f"OpenAI TTS error: {str(e)}")
            raise
    
    async def _google_tts(
        self,
        text: str,
        output_path: Optional[str] = None
    ) -> str:
        """Use Google Cloud Text-to-Speech.
        
        Args:
            text: Text to convert
            output_path: Optional output path
            
        Returns:
            str: Path to audio file
        """
        try:
            from google.cloud import texttospeech
            from pathlib import Path
            
            client = texttospeech.TextToSpeechClient()
            
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            response = await asyncio.to_thread(
                client.synthesize_speech,
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            if not output_path:
                output_path = f"output/tts_{hash(text)}.mp3"
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as out:
                out.write(response.audio_content)
            
            logger.info(f"Google TTS completed: {output_path}")
            return output_path
            
        except ImportError:
            logger.warning("Google Cloud library not available, using simulation")
            return await self._simulated_tts(text, output_path)
        except Exception as e:
            logger.error(f"Google TTS error: {str(e)}")
            raise
    
    async def _azure_tts(
        self,
        text: str,
        output_path: Optional[str] = None
    ) -> str:
        """Use Azure Speech Services for TTS.
        
        Args:
            text: Text to convert
            output_path: Optional output path
            
        Returns:
            str: Path to audio file
        """
        try:
            import azure.cognitiveservices.speech as speechsdk
            from pathlib import Path
            
            if not output_path:
                output_path = f"output/tts_{hash(text)}.wav"
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            speech_config = speechsdk.SpeechConfig(
                subscription=self.config.AZURE_SPEECH_KEY,
                region=self.config.AZURE_SPEECH_REGION
            )
            audio_config = speechsdk.AudioConfig(filename=output_path)
            
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            
            result = await asyncio.to_thread(
                synthesizer.speak_text_async(text).get
            )
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.info(f"Azure TTS completed: {output_path}")
                return output_path
            else:
                raise Exception(f"Speech synthesis failed: {result.reason}")
                
        except ImportError:
            logger.warning("Azure SDK not available, using simulation")
            return await self._simulated_tts(text, output_path)
        except Exception as e:
            logger.error(f"Azure TTS error: {str(e)}")
            raise
    
    async def _elevenlabs_tts(
        self,
        text: str,
        output_path: Optional[str] = None
    ) -> str:
        """Use ElevenLabs for high-quality TTS.
        
        Args:
            text: Text to convert
            output_path: Optional output path
            
        Returns:
            str: Path to audio file
        """
        try:
            from elevenlabs import generate, save
            from pathlib import Path
            
            if not output_path:
                output_path = f"output/tts_{hash(text)}.mp3"
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            audio = await asyncio.to_thread(
                generate,
                text=text,
                voice="Adam",
                api_key=self.config.ELEVENLABS_API_KEY
            )
            
            save(audio, output_path)
            
            logger.info(f"ElevenLabs TTS completed: {output_path}")
            return output_path
            
        except ImportError:
            logger.warning("ElevenLabs library not available, using simulation")
            return await self._simulated_tts(text, output_path)
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {str(e)}")
            raise
    
    async def _simulated_tts(
        self,
        text: str,
        output_path: Optional[str] = None
    ) -> str:
        """Simulated TTS for testing without API keys.
        
        Args:
            text: Text to convert (logged but not converted)
            output_path: Optional output path (not used)
            
        Returns:
            str: Simulated audio file path
        """
        logger.info(f"Simulated TTS: {text[:50]}...")
        await asyncio.sleep(0.3)  # Simulate processing time
        
        # In simulation mode, we just log the text
        return "simulated_audio.mp3"
