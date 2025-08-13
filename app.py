import streamlit as st
import os
import json
import logging
from datetime import datetime
from io import BytesIO
import tempfile

# Import custom modules
from config import *
from models.rag_system import RAGSystem
from models.nlp_processor import NLPProcessor
from models.voice_handler import VoiceHandler
from utils.data_fetcher import DataFetcher
from utils.translator import TranslatorService
from utils.offline_handler import OfflineHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AgriAssist AI",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'user_preferences' not in st.session_state:
    st.session_state.user_preferences = {}
if 'current_language' not in st.session_state:
    st.session_state.current_language = 'en'

class AgriAssistApp:
    def __init__(self):
        """Initialize the AgriAssist AI application"""
        self.setup_components()
        self.setup_ui()
    
    def setup_components(self):
        """Initialize all AI and utility components"""
        try:
            # Initialize components with API keys
            self.rag_system = RAGSystem(GROQ_API_KEY) if GROQ_API_KEY else None
            self.nlp_processor = NLPProcessor(GROQ_API_KEY) if GROQ_API_KEY else None
            self.voice_handler = VoiceHandler(GROQ_API_KEY) if GROQ_API_KEY else None
            self.data_fetcher = DataFetcher(WEATHER_API_KEY)
            self.translator = TranslatorService()
            self.offline_handler = OfflineHandler()
            
            # Check component status
            self.ai_enabled = bool(GROQ_API_KEY)
            self.weather_enabled = bool(WEATHER_API_KEY)
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            st.error("Error initializing application components. Please check your configuration.")
    
    def setup_ui(self):
        """Setup the user interface"""
        # Header
        st.title("🌾 AgriAssist AI")
        st.markdown("**Voice Enabled Agricultural Intelligence Platform for Indian Farmers**")
        
        # Sidebar for settings
        with st.sidebar:
            st.header("Settings")
            
            # Language selection
            selected_language = self.translator.create_language_selector()
            st.session_state.current_language = selected_language
            
            # Location input
            st.subheader("Location")
            location = st.text_input("Enter your location/city", value="Delhi")
            
            # User preferences
            st.subheader("Farm Details")
            soil_type = st.selectbox(
                "Soil Type",
                ["alluvial", "black", "red", "laterite", "not_sure"],
                index=0
            )
            
            land_size = st.text_input("Land Size (hectares)", value="1")
            
            # Current crop (optional)
            current_crop = st.selectbox(
                "Current/Planned Crop",
                ["", "rice", "wheat", "cotton", "sugarcane", "other"],
                index=0
            )
            
            # Store preferences
            st.session_state.user_preferences = {
                'location': location,
                'soil_type': soil_type,
                'land_size': land_size,
                'current_crop': current_crop,
                'language': selected_language
            }
            
            # Status indicators
            st.subheader("System Status")
            st.write("🤖 AI Services:", "✅ Active" if self.ai_enabled else "❌ Offline")
            st.write("🌤️ Weather API:", "✅ Active" if self.weather_enabled else "❌ Offline")
    
    def render_main_interface(self):
        """Render the main chat interface"""
        # Service selection tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "💬 Chat Assistant",
            "🌱 Crop Recommendations", 
            "💧 Irrigation Advisory",
            "🏛️ Government Schemes"
        ])
        
        with tab1:
            self.render_chat_interface()
        
        with tab2:
            self.render_crop_recommendations()
        
        with tab3:
            self.render_irrigation_advisory()
        
        with tab4:
            self.render_government_schemes()
    
    def render_chat_interface(self):
        """Render the main chat interface with voice support"""
        st.header("Agricultural Assistant")
        
        # Chat input methods
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Text input
            user_query = st.text_input(
                "Ask your agricultural question:",
                placeholder="Type your question here... (e.g., 'मुझे बताओ कि अगले सीजन में कौन सी फसल लगाऊं')"
            )
        
        with col2:
            # Voice input
            st.write("**Voice Input**")
            audio_file = st.file_uploader(
                "Upload audio file",
                type=['wav', 'mp3', 'ogg'],
                help="Record and upload your voice question"
            )
        
        # Process query
        if user_query or audio_file:
            self.process_user_query(user_query, audio_file)
        
        # Display conversation history
        self.display_conversation_history()
    
    def process_user_query(self, text_query: str = None, audio_file=None):
        """Process user query (text or voice)"""
        try:
            query_text = ""
            
            # Handle voice input
            if audio_file and self.voice_handler:
                with st.spinner("Processing voice input..."):
                    query_text = self.voice_handler.process_voice_query(audio_file)
                    if query_text:
                        st.success(f"Voice recognized: {query_text}")
                    else:
                        st.error("Could not process voice input. Please try again.")
                        return
            
            # Handle text input
            if text_query:
                query_text = text_query
            
            if not query_text:
                return
            
            # Process the query
            with st.spinner("Generating response..."):
                response = self.generate_response(query_text)
                
                # Add to conversation history
                st.session_state.conversation_history.append({
                    'timestamp': datetime.now(),
                    'query': query_text,
                    'response': response,
                    'language': st.session_state.current_language
                })
                
                # Display response
                st.markdown("### Response:")
                st.write(response['text'])
                
                # Voice output
                if self.voice_handler and response['text']:
                    with st.expander("🔊 Listen to Response"):
                        self.voice_handler.create_voice_response(
                            response['text'], 
                            st.session_state.current_language
                        )
                
                # Show sources if available
                if 'sources' in response and response['sources']:
                    with st.expander("📚 Information Sources"):
                        for source in response['sources']:
                            st.write(f"- {source}")
                
                # Clear input
                st.rerun()
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            st.error("Sorry, I encountered an error processing your request. Please try again.")
    
    def generate_response(self, query: str) -> dict:
        """Generate AI response for the query"""
        try:
            # Store query for offline processing
            self.offline_handler.store_query(
                query, 
                language=st.session_state.current_language
            )
            
            if not self.ai_enabled:
                return {
                    'text': 'AI services are currently offline. Please check your internet connection and API keys.',
                    'sources': [],
                    'confidence': 0.0
                }
            
            # Process with NLP
            nlp_result = self.nlp_processor.process_query(query)
            intent = nlp_result.get('intent', {}).get('intent', 'general')
            
            # Get relevant context from RAG system
            context = ""
            sources = []
            if self.rag_system:
                context = self.rag_system.get_context(query)
                relevant_docs = self.rag_system.search(query, top_k=3)
                sources = [f"{doc['type'].title()}: {doc['category']}" for doc in relevant_docs]
            
            # Add weather context for irrigation queries
            if intent == 'irrigation':
                weather_data = self.data_fetcher.get_weather_data(
                    st.session_state.user_preferences.get('location', 'Delhi')
                )
                irrigation_rec = self.data_fetcher.check_irrigation_recommendation(
                    weather_data, 
                    st.session_state.user_preferences.get('current_crop')
                )
                context += f"\n\nCurrent weather: {weather_data['weather_description']}, "
                context += f"Temperature: {weather_data['temperature']}°C, "
                context += f"Humidity: {weather_data['humidity']}%. "
                context += f"Irrigation recommendation: {irrigation_rec['recommendation']}"
            
            # Generate response
            response_text = nlp_result.get('response', 'I apologize, but I could not generate a response.')
            
            # Translate if needed
            if st.session_state.current_language != 'en':
                response_text = self.translator.translate_from_english(
                    response_text, 
                    st.session_state.current_language
                )
            
            return {
                'text': response_text,
                'sources': sources,
                'confidence': nlp_result.get('confidence', 0.5),
                'intent': intent
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                'text': 'I apologize, but I encountered an error while processing your request.',
                'sources': [],
                'confidence': 0.0
            }
    
    def render_crop_recommendations(self):
        """Render crop recommendation interface"""
        st.header("🌱 Crop Recommendations")
        
        # Get user preferences
        location = st.session_state.user_preferences.get('location', 'Delhi')
        soil_type = st.session_state.user_preferences.get('soil_type', 'alluvial')
        
        # Current season detection
        current_month = datetime.now().month
        if current_month in [6, 7, 8, 9]:
            season = "Kharif (Monsoon)"
        elif current_month in [10, 11, 12, 1, 2, 3]:
            season = "Rabi (Winter)"
        else:
            season = "Summer"
        
        st.write(f"**Current Season:** {season}")
        st.write(f"**Soil Type:** {soil_type.title()}")
        st.write(f"**Location:** {location}")
        
        # Get soil recommendations
        soil_recommendations = self.data_fetcher.get_soil_recommendations(soil_type)
        
        if 'error' not in soil_recommendations:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Suitable Crops")
                suitable_crops = soil_recommendations.get('suitable_crops', [])
                for crop in suitable_crops:
                    crop_info = self.data_fetcher.get_crop_information(crop)
                    if 'error' not in crop_info:
                        with st.expander(f"🌾 {crop.title()}"):
                            st.write(f"**Season:** {', '.join(crop_info.get('season', []))}")
                            st.write(f"**Duration:** {crop_info.get('duration_days', 'N/A')} days")
                            st.write(f"**Water Requirement:** {crop_info.get('water_requirement', 'N/A')}")
                            
                            if 'varieties' in crop_info:
                                st.write("**Popular Varieties:**")
                                for variety, details in crop_info['varieties'].items():
                                    st.write(f"- {variety.upper()}: {details.get('yield_per_hectare', 'N/A')}")
            
            with col2:
                st.subheader("Soil Characteristics")
                characteristics = soil_recommendations.get('characteristics', {})
                st.write(f"**pH Range:** {characteristics.get('ph_range', 'N/A')}")
                st.write(f"**Drainage:** {characteristics.get('drainage', 'N/A')}")
                st.write(f"**Fertility:** {characteristics.get('fertility', 'N/A')}")
                
                st.subheader("Fertilizer Recommendations")
                fertilizer = soil_recommendations.get('fertilizer_recommendations', {})
                st.write(f"**Nitrogen:** {fertilizer.get('nitrogen', 'N/A')}")
                st.write(f"**Phosphorus:** {fertilizer.get('phosphorus', 'N/A')}")
                st.write(f"**Potassium:** {fertilizer.get('potassium', 'N/A')}")
        else:
            st.error("Could not load soil recommendations.")
    
    def render_irrigation_advisory(self):
        """Render irrigation advisory interface"""
        st.header("💧 Irrigation Advisory")
        
        location = st.session_state.user_preferences.get('location', 'Delhi')
        current_crop = st.session_state.user_preferences.get('current_crop', '')
        
        # Get current weather
        weather_data = self.data_fetcher.get_weather_data(location)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Current Weather")
            st.metric("Temperature", f"{weather_data['temperature']}°C")
            st.metric("Humidity", f"{weather_data['humidity']}%")
            st.metric("Rainfall", f"{weather_data['rainfall']} mm")
            st.write(f"**Conditions:** {weather_data['weather_description'].title()}")
            st.write(f"**Wind Speed:** {weather_data['wind_speed']} km/h")
            
            if weather_data.get('source') != 'api':
                st.warning("⚠️ Using cached/backup weather data")
        
        with col2:
            st.subheader("Irrigation Recommendation")
            
            # Get irrigation recommendation
            irrigation_rec = self.data_fetcher.check_irrigation_recommendation(weather_data, current_crop)
            
            if irrigation_rec['irrigation_needed']:
                st.success("💧 **Irrigation Recommended**")
            else:
                st.info("⏸️ **No Immediate Irrigation Needed**")
            
            st.write(irrigation_rec['recommendation'])
            
            if irrigation_rec.get('timing'):
                st.write(f"**Best Timing:** {irrigation_rec['timing'].replace('_', ' ').title()}")
            
            # Weather forecast
            st.subheader("5-Day Forecast")
            forecast = self.data_fetcher.get_weather_forecast(location)
            
            if 'forecast' in forecast and forecast['forecast']:
                for day in forecast['forecast'][:3]:  # Show 3 days
                    with st.expander(f"📅 {day.get('datetime', 'N/A')[:10]}"):
                        st.write(f"Temp: {day.get('temperature', 'N/A')}°C")
                        st.write(f"Humidity: {day.get('humidity', 'N/A')}%")
                        st.write(f"Rain: {day.get('rainfall', 'N/A')} mm")
                        st.write(f"Conditions: {day.get('weather_description', 'N/A').title()}")
    
    def render_government_schemes(self):
        """Render government schemes interface"""
        st.header("🏛️ Government Schemes")
        
        # Get schemes data
        schemes = self.data_fetcher.get_government_schemes()
        
        if 'error' not in schemes:
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                scheme_filter = st.selectbox(
                    "Filter by scheme:",
                    ["All Schemes"] + list(schemes.keys())
                )
            
            # Display schemes
            display_schemes = schemes if scheme_filter == "All Schemes" else {scheme_filter: schemes[scheme_filter]}
            
            for scheme_id, scheme_info in display_schemes.items():
                with st.expander(f"📋 {scheme_info['name']}"):
                    st.write(f"**Description:** {scheme_info['description']}")
                    st.write(f"**Benefits:** {scheme_info['benefits']}")
                    st.write(f"**Ministry:** {scheme_info['ministry']}")
                    st.write(f"**Launch Year:** {scheme_info['launch_year']}")
                    
                    if 'eligibility' in scheme_info:
                        st.write("**Eligibility:**")
                        eligibility = scheme_info['eligibility']
                        
                        for key, value in eligibility.items():
                            if isinstance(value, list):
                                st.write(f"- {key.replace('_', ' ').title()}: {', '.join(value)}")
                            elif isinstance(value, dict):
                                st.write(f"- {key.replace('_', ' ').title()}:")
                                for sub_key, sub_value in value.items():
                                    st.write(f"  - {sub_key.replace('_', ' ').title()}: {sub_value}")
                            else:
                                st.write(f"- {key.replace('_', ' ').title()}: {value}")
                    
                    if 'application_process' in scheme_info:
                        st.write(f"**How to Apply:** {scheme_info['application_process']}")
                    
                    # Simple eligibility check
                    if st.button(f"Check Eligibility for {scheme_info['name']}", key=f"check_{scheme_id}"):
                        self.check_scheme_eligibility(scheme_id, scheme_info)
        else:
            st.error("Could not load government schemes data.")
    
    def check_scheme_eligibility(self, scheme_id: str, scheme_info: dict):
        """Simple eligibility checker"""
        st.subheader(f"Eligibility Check: {scheme_info['name']}")
        
        user_prefs = st.session_state.user_preferences
        
        if scheme_id == 'pm_kisan':
            land_size = float(user_prefs.get('land_size', 0) or 0)
            if land_size <= 2:
                st.success("✅ You appear eligible for PM-KISAN scheme!")
                st.write("You have small/marginal farmland (≤2 hectares)")
            else:
                st.warning("❌ You may not be eligible (land holding > 2 hectares)")
            
            st.info("Required documents: Aadhar card, bank account details, land records")
        
        elif scheme_id == 'fasal_bima':
            st.success("✅ All farmers are eligible for Pradhan Mantri Fasal Bima Yojana!")
            current_crop = user_prefs.get('current_crop', '')
            if current_crop:
                st.write(f"Your crop ({current_crop}) can be insured under this scheme.")
            st.info("Apply through banks, insurance companies, or CSC centers")
        
        elif scheme_id == 'soil_health_card':
            st.success("✅ All farmers are eligible for Soil Health Card!")
            st.info("Visit your nearest agriculture department office to apply")
        
        elif scheme_id == 'kisan_credit_card':
            st.success("✅ All farmers are eligible for Kisan Credit Card!")
            land_size = float(user_prefs.get('land_size', 0) or 0)
            if land_size > 0:
                estimated_limit = min(land_size * 50000, 300000)  # Rough estimation
                st.write(f"Estimated loan limit: ₹{estimated_limit:,}")
            st.info("Apply at banks with land records and identity proof")
        
        else:
            st.info("Manual eligibility check required. Contact local agriculture office.")
    
    def display_conversation_history(self):
        """Display conversation history"""
        if st.session_state.conversation_history:
            st.subheader("Conversation History")
            
            # Show recent conversations
            for i, conv in enumerate(reversed(st.session_state.conversation_history[-5:])):
                with st.expander(f"💬 {conv['timestamp'].strftime('%H:%M')} - {conv['query'][:50]}..."):
                    st.write(f"**Question:** {conv['query']}")
                    st.write(f"**Answer:** {conv['response']['text'] if isinstance(conv['response'], dict) else conv['response']}")
                    st.write(f"**Time:** {conv['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Clear history button
            if st.button("Clear History"):
                st.session_state.conversation_history = []
                st.rerun()
    
    def run(self):
        """Run the main application"""
        try:
            self.render_main_interface()
            
            # Footer
            st.markdown("---")
            st.markdown(
                "**AgriAssist AI** - Empowering Indian farmers with AI-driven agricultural intelligence. "
                "🌾 For technical support, contact your local agricultural extension office."
            )
            
        except Exception as e:
            logger.error(f"Error in main app: {e}")
            st.error("An error occurred in the application. Please refresh the page.")

# Run the application
if __name__ == "__main__":
    app = AgriAssistApp()
    app.run()
