# AgriAssist AI: Voice Enabled Agricultural Intelligence Platform

## Overview

AgriAssist AI is a comprehensive multilingual agricultural advisory platform designed to serve farmers in India with AI-powered recommendations and guidance. The system provides three core services: seed and fertilizer recommendations based on soil and climate conditions, weather-based irrigation advisory to optimize water usage, and government scheme eligibility checking to help farmers access subsidies and insurance programs.

The platform is built with offline capability in mind to serve low-connectivity rural areas, supports multiple Indian languages for accessibility, and uses voice input/output for farmers with limited literacy. The system employs RAG (Retrieval-Augmented Generation) architecture to provide accurate, source-cited responses while preventing AI hallucinations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
The application uses **Streamlit** as the primary frontend framework, providing a web-based interface that's simple to deploy and maintain. The UI is designed to be responsive for mobile devices and includes Progressive Web App (PWA) capabilities for offline access. Voice recording functionality is implemented through web-based audio capture with seamless integration to the backend processing pipeline.

### Backend Architecture
The system follows a **modular microservices-inspired architecture** within a monolithic Python application:

- **RAG System**: Uses FAISS vector database for document similarity search combined with OpenAI embeddings for semantic retrieval. Agricultural knowledge is stored as embeddings to enable intelligent question-answering with source attribution.

- **NLP Processing**: Implements intent classification using GPT-4o to route user queries to appropriate services (crop recommendations, irrigation advice, or government schemes). Includes language detection capabilities for multilingual support.

- **Voice Processing**: Integrates OpenAI Whisper for speech-to-text conversion and Google Text-to-Speech (gTTS) for audio output generation, supporting multiple Indian languages.

### Data Storage Strategy
The system uses a **hybrid storage approach**:

- **SQLite**: Primary database for offline capability, storing user queries, cached responses, weather data, and user preferences
- **JSON Files**: Static agricultural data including crop information, soil characteristics, fertilizer schedules, and government schemes
- **Vector Store**: FAISS index for semantic search of agricultural knowledge base

This design ensures the application remains functional in low-connectivity environments while providing comprehensive agricultural guidance.

### Offline-First Design
The **OfflineHandler** component ensures continuous operation by:
- Caching weather data locally with expiration timestamps
- Storing user queries for processing when connectivity is restored
- Maintaining local copies of all agricultural reference data
- Implementing fallback responses when external APIs are unavailable

## External Dependencies

### AI and Language Services
- **OpenAI GPT-4o**: Primary language model for generating agricultural advice and recommendations
- **OpenAI Whisper**: Speech-to-text conversion for voice input processing
- **Google Translate API**: Multilingual translation services for Indian languages
- **Google Text-to-Speech (gTTS)**: Voice output generation in multiple languages

### Weather and Geographic Data
- **OpenWeatherMap API**: Real-time weather data and forecasts for irrigation planning
- **Backup Weather Data**: Local JSON files providing weather information when API is unavailable

### Development and Deployment
- **Streamlit**: Web application framework for rapid development and deployment
- **FAISS**: Facebook's similarity search library for vector operations
- **SQLite**: Embedded database for local data storage
- **NumPy**: Numerical computing for vector operations and data processing

### Agricultural Data Sources
- **ICAR Data**: Indian Council of Agricultural Research datasets for crop and soil information
- **Government Scheme Data**: Structured data from official government portals for subsidy and insurance programs
- **Agmarknet**: Agricultural marketing data integration (planned)

The architecture prioritizes reliability and accessibility for rural users while maintaining sophisticated AI capabilities through strategic use of cloud services with comprehensive offline fallbacks.