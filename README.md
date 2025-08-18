# AgriAssist AI 🌾

## Voice Enabled Agricultural Intelligence Platform for Indian Farmers

AgriAssist AI is a comprehensive, multilingual agricultural advisory platform designed specifically for Indian farmers. It combines advanced AI technology with deep agricultural knowledge to provide personalized crop recommendations, irrigation guidance, and government scheme information through voice-enabled interactions.

![AgriAssist AI Platform](https://img.shields.io/badge/Status-Active-brightgreen) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Features

### Core Services
- **🌱 Seed & Fertilizer Recommendations**: Personalized suggestions based on soil type, climate, and seasonal trends
- **💧 Weather-Based Irrigation Advisory**: Optimal irrigation timing to prevent water waste and crop stress
- **🏛️ Government Scheme Eligibility**: Real-time information about subsidies, insurance, and agricultural schemes

### Advanced Capabilities
- **🗣️ Voice Input/Output**: Natural language processing in Hindi and English
- **🌍 Multilingual Support**: Hindi, English with expandable language support
- **📱 Mobile-First Design**: Optimized for smartphones and tablets
- **🤖 AI-Powered RAG System**: Retrieval-Augmented Generation for accurate, cited responses
- **📊 Explainable AI**: All recommendations come with source citations and confidence scores
- **🔄 Offline Capability**: Works in low-connectivity areas with cached data

## 🛠️ Technology Stack

### Backend
- **Framework**: Streamlit with Flask components
- **AI Engine**: Groq API (Llama models)
- **Vector Database**: FAISS for document retrieval
- **Speech Processing**: Google Text-to-Speech (gTTS)
- **Translation**: Google Translate API
- **Database**: SQLite for offline data, PostgreSQL ready

### Frontend
- **UI Framework**: Streamlit
- **Responsive Design**: Mobile-optimized interface
- **Voice Integration**: Web-based audio processing
- **PWA Support**: Progressive Web App capabilities

### APIs & Services
- **Weather Data**: OpenWeatherMap API
- **Agricultural Data**: ICAR datasets
- **Government Schemes**: Structured official data
- **AI Processing**: Groq API for language models

## 📁 Project Structure

```
agriassist-ai/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── data/
│   ├── soil_data.json       # ICAR soil datasets
│   ├── crop_data.json       # Crop recommendation database
│   ├── schemes_data.json    # Government schemes information
│   └── weather_backup.json  # Offline weather data
├── models/
│   ├── rag_system.py        # RAG implementation with FAISS
│   ├── nlp_processor.py     # Natural language processing
│   └── voice_handler.py     # Speech processing
├── utils/
│   ├── data_fetcher.py      # API integration utilities
│   ├── translator.py        # Multi-language support
│   └── offline_handler.py   # Offline functionality
├── static/
│   └── styles.css           # Custom styling
└── templates/               # Additional UI templates
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Groq API key
- OpenWeatherMap API key (optional, for real-time weather)
- Internet connection for initial setup

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/SimranShaikh20/agriassist-ai.git
   cd agriassist-ai
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up API Keys**
   
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   ```

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```

5. **Access the Platform**
   
   Open your browser and navigate to `http://localhost:8501`

### Docker Setup (Alternative)

```bash
# Build the Docker image
docker build -t agriassist-ai .

# Run the container
docker run -p 8501:8501 --env-file .env agriassist-ai
```

## 🎯 Usage Guide

### Getting Started
1. **Select Your Language**: Choose between Hindi and English
2. **Set Your Location**: Enter your city/district for location-specific advice
3. **Configure Farm Details**: 
   - Soil type (alluvial, clay, sandy, etc.)
   - Land size in hectares
   - Current or planned crops

### Voice Interaction
1. Click the **Voice Input** button
2. Upload an audio file or use the microphone
3. Speak your question in Hindi or English
4. Receive AI-powered responses with audio playback

### Text Interaction
1. Type your agricultural question in the text box
2. Use natural language (e.g., "मुझे धान की फसल के लिए सलाह चाहिए")
3. Get detailed recommendations with sources

### Sample Questions
- **Crop Recommendations**: "What crops should I plant in sandy soil during monsoon?"
- **Irrigation Advice**: "When should I water my wheat crop?"
- **Government Schemes**: "Which subsidies are available for organic farming?"
- **Disease Management**: "My tomato plants have yellow leaves, what should I do?"

## 🔧 Configuration

### API Keys Setup
Edit `config.py` to add your API credentials:

```python
# Groq API Configuration
GROQ_API_KEY = "your_groq_api_key"

# Weather API Configuration  
OPENWEATHER_API_KEY = "your_openweather_key"

# Translation Settings
SUPPORTED_LANGUAGES = ["hi", "en", "te", "ta", "bn"]
DEFAULT_LANGUAGE = "hi"
```

### Customization Options
- **Language Support**: Add new languages in `utils/translator.py`
- **Crop Database**: Update `data/crop_data.json` with regional crops
- **Government Schemes**: Modify `data/schemes_data.json` for state-specific schemes
- **UI Themes**: Customize appearance in `static/styles.css`

## 📊 Features Deep Dive

### RAG System
The platform uses Retrieval-Augmented Generation to provide accurate, source-backed responses:
- **Vector Database**: FAISS stores agricultural document embeddings
- **Semantic Search**: Finds relevant information based on query context
- **Citation System**: All responses include source references
- **Confidence Scoring**: Provides reliability metrics for each recommendation

### Multilingual Processing
- **Auto-Detection**: Identifies input language automatically  
- **Translation Pipeline**: Seamless conversion between supported languages
- **Code-Switching**: Handles mixed-language conversations
- **Cultural Context**: Understands regional agricultural practices

### Offline Functionality
- **Data Caching**: Stores frequently accessed information locally
- **Fallback Responses**: Basic recommendations without internet
- **Sync Capability**: Updates cached data when connectivity returns
- **SMS Integration**: Alternative communication channel for remote areas

## 🧪 Testing

### Run Unit Tests
```bash
python -m pytest tests/ -v
```

### Test Voice Processing
```bash
python tests/test_voice_handler.py
```

### Test RAG System
```bash
python tests/test_rag_system.py
```

### Load Testing
```bash
# Install locust for load testing
pip install locust

# Run load tests
locust -f tests/load_test.py --host=http://localhost:8501
```

## 📈 Performance Optimization

### Response Times
- **Average Query Response**: < 2 seconds
- **Voice Processing**: < 5 seconds
- **Offline Mode**: < 1 second

### Caching Strategy
- **API Responses**: Cached for 1 hour
- **Translation Results**: Cached for 24 hours  
- **Agricultural Data**: Static caching with periodic updates
- **Weather Data**: 30-minute refresh cycle

### Resource Usage
- **Memory**: ~500MB during normal operation
- **Storage**: ~100MB for offline data
- **Bandwidth**: Optimized API usage with compression



## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test thoroughly
4. Commit with clear messages: `git commit -m 'Add amazing feature'`
5. Push to your branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Contribution Areas
- **New Languages**: Add support for regional Indian languages
- **Crop Databases**: Expand agricultural knowledge base
- **UI/UX Improvements**: Enhance user experience
- **Performance Optimization**: Speed and efficiency improvements
- **Documentation**: Help improve guides and tutorials

### Code Style
- Follow PEP 8 for Python code
- Use descriptive variable names
- Add docstrings for all functions
- Include type hints where appropriate
- Write unit tests for new features

## 🐛 Troubleshooting

### Common Issues

**Voice Input Not Working**
- Check microphone permissions in browser
- Ensure audio file format is supported (WAV, MP3, OGG)
- Verify file size is under 200MB

**API Errors**
- Verify API keys are correctly set in config
- Check API rate limits and usage quotas
- Ensure internet connectivity for API calls

**Translation Issues**
- Clear browser cache and cookies
- Check supported language codes
- Verify Google Translate API quota

**Performance Problems**
- Restart the application
- Clear cached data
- Check system memory usage
- Update to latest version

### Debug Mode
Enable detailed logging:
```python
# In config.py
DEBUG = True
LOG_LEVEL = "DEBUG"
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Indian Council of Agricultural Research (ICAR)** for agricultural datasets
- **Google AI** for translation and speech services  
- **Groq** for providing fast AI inference
- **OpenWeatherMap** for weather data APIs
- **Streamlit Community** for the amazing framework
- **Indian Farmers** who provided feedback and insights



---

**Made with ❤️ for Indian Farmers**

*Empowering agriculture through artificial intelligence*
