import os
import tempfile
import logging
from io import BytesIO
from gtts import gTTS
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceHandler:
    def __init__(self, groq_api_key: str = None):
        """Initialize voice handler"""
        # Voice handler now only uses gTTS for text-to-speech
        # Speech-to-text will be disabled without API key
        self.groq_api_key = groq_api_key
    
    def speech_to_text(self, audio_file) -> str:
        """Convert speech to text - currently disabled without Whisper API"""
        try:
            logger.warning("Speech-to-text is currently disabled without OpenAI Whisper API")
            return ""
                    
        except Exception as e:
            logger.error(f"Error in speech to text: {e}")
            return ""
    
    def text_to_speech(self, text: str, language: str = 'en') -> BytesIO:
        """Convert text to speech using gTTS"""
        try:
            # Language mapping for gTTS
            lang_map = {
                'hi': 'hi',
                'en': 'en',
                'te': 'te',
                'ta': 'ta',
                'bn': 'bn',
                'mr': 'mr',
                'gu': 'gu'
            }
            
            tts_lang = lang_map.get(language, 'en')
            
            # Generate speech
            tts = gTTS(text=text, lang=tts_lang, slow=False)
            
            # Save to BytesIO
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return audio_buffer
            
        except Exception as e:
            logger.error(f"Error in text to speech: {e}")
            # Return empty buffer on error
            return BytesIO()
    
    def create_audio_player(self, audio_buffer: BytesIO, autoplay: bool = True):
        """Create audio player in Streamlit"""
        try:
            if audio_buffer.getvalue():
                st.audio(audio_buffer, format='audio/mp3', autoplay=autoplay)
            else:
                st.warning("Could not generate audio response")
                
        except Exception as e:
            logger.error(f"Error creating audio player: {e}")
            st.error("Error playing audio response")
    
    def process_voice_query(self, audio_file) -> str:
        """Process voice input and return transcribed text"""
        if audio_file is not None:
            try:
                # Transcribe audio
                transcription = self.speech_to_text(audio_file)
                
                if transcription:
                    logger.info(f"Transcription successful: {transcription[:50]}...")
                    return transcription
                else:
                    logger.warning("Empty transcription received")
                    return ""
                    
            except Exception as e:
                logger.error(f"Error processing voice query: {e}")
                return ""
        
        return ""
    
    def create_voice_response(self, text: str, language: str = 'en'):
        """Create voice response and play it"""
        try:
            if text and text.strip():
                audio_buffer = self.text_to_speech(text, language)
                if audio_buffer.getvalue():
                    self.create_audio_player(audio_buffer)
                    return True
                else:
                    st.warning("Could not generate voice response")
                    return False
            else:
                logger.warning("Empty text provided for voice response")
                return False
                
        except Exception as e:
            logger.error(f"Error creating voice response: {e}")
            st.error("Error generating voice response")
            return False
