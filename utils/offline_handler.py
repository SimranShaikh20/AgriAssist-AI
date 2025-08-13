import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OfflineHandler:
    def __init__(self, db_path: str = "agriassist.db"):
        """Initialize offline handler with SQLite database"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for offline storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_text TEXT NOT NULL,
                    response_text TEXT,
                    language TEXT DEFAULT 'en',
                    intent TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    location TEXT NOT NULL,
                    weather_data TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    language TEXT DEFAULT 'en',
                    location TEXT,
                    crop_preferences TEXT,
                    soil_type TEXT,
                    land_size TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recommendations_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE,
                    recommendation_data TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def cache_weather_data(self, location: str, weather_data: Dict[str, Any], cache_hours: int = 1):
        """Cache weather data for offline access"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            expires_at = datetime.now() + timedelta(hours=cache_hours)
            
            cursor.execute('''
                INSERT OR REPLACE INTO weather_cache 
                (location, weather_data, expires_at) 
                VALUES (?, ?, ?)
            ''', (location, json.dumps(weather_data), expires_at))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Weather data cached for {location}")
            
        except Exception as e:
            logger.error(f"Error caching weather data: {e}")
    
    def get_cached_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """Get cached weather data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT weather_data FROM weather_cache 
                WHERE location = ? AND expires_at > CURRENT_TIMESTAMP
                ORDER BY timestamp DESC LIMIT 1
            ''', (location,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached weather: {e}")
            return None
    
    def store_query(self, query: str, response: str = None, language: str = 'en', intent: str = None) -> int:
        """Store user query for offline processing"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO queries (query_text, response_text, language, intent, processed)
                VALUES (?, ?, ?, ?, ?)
            ''', (query, response, language, intent, response is not None))
            
            query_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Query stored with ID: {query_id}")
            return query_id
            
        except Exception as e:
            logger.error(f"Error storing query: {e}")
            return -1
    
    def get_unprocessed_queries(self) -> List[Dict[str, Any]]:
        """Get queries that haven't been processed yet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, query_text, language, intent, timestamp 
                FROM queries 
                WHERE processed = FALSE
                ORDER BY timestamp ASC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            queries = []
            for result in results:
                queries.append({
                    'id': result[0],
                    'query': result[1],
                    'language': result[2],
                    'intent': result[3],
                    'timestamp': result[4]
                })
            
            return queries
            
        except Exception as e:
            logger.error(f"Error getting unprocessed queries: {e}")
            return []
    
    def update_query_response(self, query_id: int, response: str):
        """Update query with response"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE queries 
                SET response_text = ?, processed = TRUE 
                WHERE id = ?
            ''', (response, query_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Query {query_id} updated with response")
            
        except Exception as e:
            logger.error(f"Error updating query response: {e}")
    
    def cache_recommendation(self, cache_key: str, recommendation: Dict[str, Any], cache_hours: int = 24):
        """Cache recommendation data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            expires_at = datetime.now() + timedelta(hours=cache_hours)
            
            cursor.execute('''
                INSERT OR REPLACE INTO recommendations_cache 
                (cache_key, recommendation_data, expires_at) 
                VALUES (?, ?, ?)
            ''', (cache_key, json.dumps(recommendation), expires_at))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Recommendation cached with key: {cache_key}")
            
        except Exception as e:
            logger.error(f"Error caching recommendation: {e}")
    
    def get_cached_recommendation(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached recommendation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT recommendation_data FROM recommendations_cache 
                WHERE cache_key = ? AND expires_at > CURRENT_TIMESTAMP
                ORDER BY timestamp DESC LIMIT 1
            ''', (cache_key,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached recommendation: {e}")
            return None
    
    def store_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Store user preferences for personalized recommendations"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_preferences 
                (user_id, language, location, crop_preferences, soil_type, land_size)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                preferences.get('language', 'en'),
                preferences.get('location', ''),
                json.dumps(preferences.get('crops', [])),
                preferences.get('soil_type', ''),
                preferences.get('land_size', '')
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"User preferences stored for: {user_id}")
            
        except Exception as e:
            logger.error(f"Error storing user preferences: {e}")
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT language, location, crop_preferences, soil_type, land_size 
                FROM user_preferences 
                WHERE user_id = ?
                ORDER BY updated_at DESC LIMIT 1
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'language': result[0],
                    'location': result[1],
                    'crops': json.loads(result[2]) if result[2] else [],
                    'soil_type': result[3],
                    'land_size': result[4]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return None
    
    def cleanup_expired_cache(self):
        """Clean up expired cache entries"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clean expired weather cache
            cursor.execute('''
                DELETE FROM weather_cache 
                WHERE expires_at < CURRENT_TIMESTAMP
            ''')
            
            # Clean expired recommendations cache
            cursor.execute('''
                DELETE FROM recommendations_cache 
                WHERE expires_at < CURRENT_TIMESTAMP
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Expired cache cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
    
    def get_offline_recommendations(self, query_type: str, location: str = None) -> Dict[str, Any]:
        """Get basic offline recommendations"""
        try:
            if query_type == 'irrigation':
                return {
                    'recommendation': 'Monitor soil moisture. Water early morning or evening if soil is dry.',
                    'source': 'offline',
                    'confidence': 0.7
                }
            elif query_type == 'crop_recommendation':
                return {
                    'recommendation': 'Consider local climate and soil conditions. Consult with local agricultural officer.',
                    'source': 'offline',
                    'confidence': 0.6
                }
            elif query_type == 'government_schemes':
                return {
                    'recommendation': 'Check PM-KISAN, Fasal Bima Yojana, and Soil Health Card schemes. Visit nearest CSC or agriculture office.',
                    'source': 'offline',
                    'confidence': 0.8
                }
            else:
                return {
                    'recommendation': 'Limited offline information available. Please connect to internet for detailed advice.',
                    'source': 'offline',
                    'confidence': 0.5
                }
                
        except Exception as e:
            logger.error(f"Error getting offline recommendations: {e}")
            return {
                'recommendation': 'Offline service temporarily unavailable.',
                'source': 'error',
                'confidence': 0.0
            }
