import logging
from typing import Dict, Any, Optional
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranslatorService:
    def __init__(self):
        """Initialize translator service"""
        # Simple translator without external dependencies
        
        # Language mappings
        self.language_codes = {
            'English': 'en',
            'Hindi': 'hi',
            'Telugu': 'te',
            'Tamil': 'ta',
            'Bengali': 'bn',
            'Marathi': 'mr',
            'Gujarati': 'gu',
            'Punjabi': 'pa',
            'Kannada': 'kn',
            'Malayalam': 'ml'
        }
        
        # Reverse mapping
        self.code_to_language = {v: k for k, v in self.language_codes.items()}
        
        # Common agricultural terms translations
        self.agricultural_terms = {
            'en': {
                'crop': 'crop',
                'seed': 'seed',
                'fertilizer': 'fertilizer',
                'irrigation': 'irrigation',
                'soil': 'soil',
                'weather': 'weather',
                'scheme': 'scheme',
                'subsidy': 'subsidy'
            },
            'hi': {
                'crop': 'फसल',
                'seed': 'बीज',
                'fertilizer': 'उर्वरक',
                'irrigation': 'सिंचाई',
                'soil': 'मिट्टी',
                'weather': 'मौसम',
                'scheme': 'योजना',
                'subsidy': 'सब्सिडी'
            }
        }
    
    def detect_language(self, text: str) -> str:
        """Detect language of the given text"""
        try:
            # Simple heuristic: check for Devanagari script for Hindi
            import re
            if re.search(r'[\u0900-\u097F]', text):
                return 'hi'  # Hindi
            else:
                return 'en'  # Default to English
                
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return 'en'  # Default to English
    
    def translate_text(self, text: str, target_language: str, source_language: str = 'auto') -> str:
        """Translate text to target language"""
        try:
            if not text or not text.strip():
                return text
            
            # If source and target are the same, no translation needed
            if source_language == target_language:
                return text
            
            # For now, return original text since we don't have translation API
            # In a real implementation, this would use a translation service
            logger.info(f"Translation requested from {source_language} to {target_language}")
            return text
            
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return text  # Return original text on error
    
    def translate_to_english(self, text: str, source_language: str = 'auto') -> str:
        """Translate text to English"""
        return self.translate_text(text, 'en', source_language)
    
    def translate_from_english(self, text: str, target_language: str) -> str:
        """Translate English text to target language"""
        return self.translate_text(text, target_language, 'en')
    
    def get_language_name(self, language_code: str) -> str:
        """Get language name from code"""
        return self.code_to_language.get(language_code, 'English')
    
    def get_language_code(self, language_name: str) -> str:
        """Get language code from name"""
        return self.language_codes.get(language_name, 'en')
    
    def create_language_selector(self, key: str = "language_selector") -> str:
        """Create language selector widget"""
        selected_language = st.selectbox(
            "Select Language / भाषा चुनें",
            options=list(self.language_codes.keys()),
            index=0,  # Default to English
            key=key
        )
        
        return self.get_language_code(selected_language)
    
    def translate_agricultural_term(self, term: str, target_language: str) -> str:
        """Translate common agricultural terms"""
        term_lower = term.lower()
        
        if target_language in self.agricultural_terms:
            return self.agricultural_terms[target_language].get(term_lower, term)
        
        # Fallback to general translation
        return self.translate_text(term, target_language)
    
    def create_multilingual_response(self, response: str, user_language: str) -> Dict[str, str]:
        """Create response in multiple languages"""
        try:
            multilingual_response = {
                'original': response,
                'user_language': user_language
            }
            
            # If response is in English and user language is different, translate
            if user_language != 'en':
                translated = self.translate_from_english(response, user_language)
                multilingual_response['translated'] = translated
            else:
                multilingual_response['translated'] = response
            
            return multilingual_response
            
        except Exception as e:
            logger.error(f"Error creating multilingual response: {e}")
            return {
                'original': response,
                'translated': response,
                'user_language': user_language
            }
    
    def process_query_translation(self, query: str, target_language: str = 'en') -> Dict[str, str]:
        """Process and translate user query"""
        try:
            detected_lang = self.detect_language(query)
            
            # Translate to English for processing if needed
            if detected_lang != 'en':
                translated_query = self.translate_to_english(query, detected_lang)
            else:
                translated_query = query
            
            return {
                'original_query': query,
                'translated_query': translated_query,
                'detected_language': detected_lang,
                'target_language': target_language
            }
            
        except Exception as e:
            logger.error(f"Error processing query translation: {e}")
            return {
                'original_query': query,
                'translated_query': query,
                'detected_language': 'en',
                'target_language': target_language
            }
