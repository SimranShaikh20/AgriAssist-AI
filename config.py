import os

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")

# Model Configuration
GROQ_MODEL = "llama3-8b-8192"  # Using Groq's Llama model
TTS_ENABLED = True

# API Endpoints
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5"
WEATHER_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

# Language Configuration
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "bn": "Bengali",
    "mr": "Marathi",
    "gu": "Gujarati"
}

# Application Configuration
APP_TITLE = "AgriAssist AI"
APP_DESCRIPTION = "Voice Enabled Agricultural Intelligence Platform"

# Database Configuration
SQLITE_DB_PATH = "agriassist.db"

# File Paths
DATA_DIR = "data"
MODELS_DIR = "models"
UTILS_DIR = "utils"
