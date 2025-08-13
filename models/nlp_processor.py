import json
import re
from typing import Dict, List, Tuple, Any
from groq import Groq
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NLPProcessor:
    def __init__(self, groq_api_key: str):
        """Initialize NLP processor with Groq client"""
        self.client = Groq(api_key=groq_api_key)
        
        # Intent patterns for classification
        self.intent_patterns = {
            'crop_recommendation': [
                'crop', 'seed', 'plant', 'grow', 'cultivation', 'farming', 'harvest',
                'फसल', 'बीज', 'खेती', 'उगाना', 'बोना'
            ],
            'irrigation': [
                'water', 'irrigation', 'watering', 'rain', 'drought', 'moisture',
                'पानी', 'सिंचाई', 'बारिश', 'सूखा'
            ],
            'government_schemes': [
                'scheme', 'subsidy', 'government', 'loan', 'insurance', 'support',
                'योजना', 'सब्सिडी', 'सरकार', 'लोन', 'बीमा', 'सहायता'
            ],
            'fertilizer': [
                'fertilizer', 'manure', 'nutrition', 'nutrient', 'soil health',
                'खाद', 'उर्वरक', 'पोषण'
            ]
        }
    
    def detect_language(self, text: str) -> str:
        """Detect language of input text"""
        try:
            # Simple heuristic: check for Devanagari script
            if re.search(r'[\u0900-\u097F]', text):
                return 'hi'  # Hindi
            else:
                return 'en'  # English
        except Exception as e:
            logger.error(f"Error in language detection: {e}")
            return 'en'  # Default to English
    
    def classify_intent(self, text: str) -> Dict[str, Any]:
        """Classify user intent using Groq"""
        try:
            prompt = f"""
            Classify the following agricultural query into one of these intents:
            1. crop_recommendation - questions about what crops to grow, seed selection
            2. irrigation - questions about watering, irrigation timing, water management
            3. government_schemes - questions about government schemes, subsidies, loans
            4. fertilizer - questions about fertilizers, soil nutrition, soil health
            5. general - any other agricultural questions
            
            Text: "{text}"
            
            Respond with JSON in this format:
            {{"intent": "intent_name", "confidence": 0.95, "entities": ["extracted", "entities"]}}
            """
            
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}]
            )
            
            try:
                result = json.loads(response.choices[0].message.content)
                return result
            except:
                # If JSON parsing fails, fallback to pattern matching
                return self._fallback_intent_classification(text)
            
        except Exception as e:
            logger.error(f"Error in intent classification: {e}")
            # Fallback to pattern matching
            return self._fallback_intent_classification(text)
    
    def _fallback_intent_classification(self, text: str) -> Dict[str, Any]:
        """Fallback intent classification using pattern matching"""
        text_lower = text.lower()
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text_lower)
            if score > 0:
                intent_scores[intent] = score / len(patterns)
        
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[best_intent]
        else:
            best_intent = 'general'
            confidence = 0.5
        
        return {
            'intent': best_intent,
            'confidence': confidence,
            'entities': []
        }
    
    def extract_location(self, text: str) -> Dict[str, Any]:
        """Extract location information from text"""
        try:
            prompt = f"""
            Extract location information from this text: "{text}"
            
            Look for:
            - State names
            - City names
            - District names
            - Village names
            - Geographic regions
            
            Respond with JSON in this format:
            {{"state": "state_name", "city": "city_name", "district": "district_name", "found": true}}
            
            If no location found, set found to false.
            """
            
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}]
            )
            
            try:
                result = json.loads(response.choices[0].message.content)
                return result
            except:
                return {"found": False}
            
        except Exception as e:
            logger.error(f"Error in location extraction: {e}")
            return {"found": False}
    
    def extract_crop_info(self, text: str) -> Dict[str, Any]:
        """Extract crop-related information from text"""
        try:
            prompt = f"""
            Extract crop and farming information from this text: "{text}"
            
            Look for:
            - Crop names (rice, wheat, cotton, etc.)
            - Season information (kharif, rabi, summer)
            - Soil type mentions
            - Land size
            - Current crop status
            
            Respond with JSON in this format:
            {{"crops": ["crop1", "crop2"], "season": "season_name", "soil_type": "soil_type", "land_size": "size", "found_crop_info": true}}
            
            If no crop information found, set found_crop_info to false.
            """
            
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}]
            )
            
            try:
                result = json.loads(response.choices[0].message.content)
                return result
            except:
                return {"found_crop_info": False}
            
        except Exception as e:
            logger.error(f"Error in crop info extraction: {e}")
            return {"found_crop_info": False}
    
    def generate_response(self, query: str, context: str, intent: str, language: str = 'en') -> str:
        """Generate response using Groq with context"""
        try:
            # Language-specific prompts
            if language == 'hi':
                system_prompt = """आप एक कृषि सलाहकार हैं जो भारतीय किसानों की मदद करते हैं। 
                हिंदी में जवाब दें और व्यावहारिक सलाह दें। स्रोत की जानकारी का उपयोग करें।"""
                user_prompt = f"""संदर्भ: {context}\n\nप्रश्न: {query}\n\nकृपया हिंदी में उत्तर दें।"""
            else:
                system_prompt = """You are an agricultural advisor helping Indian farmers. 
                Provide practical, actionable advice based on the given context. 
                Be specific and include source information when available."""
                user_prompt = f"""Context: {context}\n\nQuestion: {query}\n\nPlease provide a helpful response."""
            
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in response generation: {e}")
            if language == 'hi':
                return "माफ़ करें, मैं अभी आपकी मदद नहीं कर सकता। कृपया बाद में कोशिश करें।"
            else:
                return "I'm sorry, I'm unable to help you right now. Please try again later."
    
    def process_query(self, query: str, context: str = "") -> Dict[str, Any]:
        """Process a complete query through the NLP pipeline"""
        try:
            # Detect language
            language = self.detect_language(query)
            
            # Classify intent
            intent_result = self.classify_intent(query)
            
            # Extract location and crop info
            location_info = self.extract_location(query)
            crop_info = self.extract_crop_info(query)
            
            # Generate response
            response = self.generate_response(
                query, context, intent_result['intent'], language
            )
            
            return {
                'language': language,
                'intent': intent_result,
                'location': location_info,
                'crop_info': crop_info,
                'response': response,
                'confidence': intent_result.get('confidence', 0.5)
            }
            
        except Exception as e:
            logger.error(f"Error in query processing: {e}")
            return {
                'language': 'en',
                'intent': {'intent': 'general', 'confidence': 0.5},
                'location': {'found': False},
                'crop_info': {'found_crop_info': False},
                'response': "I'm sorry, I encountered an error processing your query.",
                'confidence': 0.0
            }
