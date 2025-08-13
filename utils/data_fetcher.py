import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    def __init__(self, weather_api_key: str):
        """Initialize data fetcher with API keys"""
        self.weather_api_key = weather_api_key
        self.weather_base_url = "https://api.openweathermap.org/data/2.5"
        
        # Load backup weather data
        self.load_backup_weather_data()
    
    def load_backup_weather_data(self):
        """Load backup weather data for offline scenarios"""
        try:
            with open('data/weather_backup.json', 'r', encoding='utf-8') as f:
                self.backup_weather = json.load(f)
        except Exception as e:
            logger.error(f"Error loading backup weather data: {e}")
            self.backup_weather = {"cities": {}}
    
    def get_weather_data(self, city: str, lat: float = None, lon: float = None) -> Dict[str, Any]:
        """Get current weather data"""
        try:
            # Try API first
            if self.weather_api_key:
                if lat and lon:
                    url = f"{self.weather_base_url}/weather"
                    params = {
                        'lat': lat,
                        'lon': lon,
                        'appid': self.weather_api_key,
                        'units': 'metric'
                    }
                else:
                    url = f"{self.weather_base_url}/weather"
                    params = {
                        'q': f"{city},IN",
                        'appid': self.weather_api_key,
                        'units': 'metric'
                    }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'temperature': data['main']['temp'],
                        'humidity': data['main']['humidity'],
                        'rainfall': data.get('rain', {}).get('1h', 0),
                        'wind_speed': data['wind']['speed'],
                        'weather_description': data['weather'][0]['description'],
                        'pressure': data['main']['pressure'],
                        'visibility': data.get('visibility', 10000) / 1000,  # Convert to km
                        'source': 'api',
                        'timestamp': datetime.now().isoformat()
                    }
        
        except Exception as e:
            logger.error(f"Error fetching weather data from API: {e}")
        
        # Fallback to backup data
        city_lower = city.lower()
        if city_lower in self.backup_weather['cities']:
            backup_data = self.backup_weather['cities'][city_lower].copy()
            backup_data['source'] = 'backup'
            backup_data['timestamp'] = datetime.now().isoformat()
            return backup_data
        
        # Default fallback
        return {
            'temperature': 25,
            'humidity': 60,
            'rainfall': 0,
            'wind_speed': 10,
            'weather_description': 'data unavailable',
            'pressure': 1013,
            'visibility': 10,
            'source': 'default',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_weather_forecast(self, city: str, lat: float = None, lon: float = None) -> Dict[str, Any]:
        """Get 5-day weather forecast"""
        try:
            if self.weather_api_key:
                if lat and lon:
                    url = f"{self.weather_base_url}/forecast"
                    params = {
                        'lat': lat,
                        'lon': lon,
                        'appid': self.weather_api_key,
                        'units': 'metric'
                    }
                else:
                    url = f"{self.weather_base_url}/forecast"
                    params = {
                        'q': f"{city},IN",
                        'appid': self.weather_api_key,
                        'units': 'metric'
                    }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    forecast_list = []
                    
                    for item in data['list'][:5]:  # Next 5 periods
                        forecast_list.append({
                            'datetime': item['dt_txt'],
                            'temperature': item['main']['temp'],
                            'humidity': item['main']['humidity'],
                            'rainfall': item.get('rain', {}).get('3h', 0),
                            'weather_description': item['weather'][0]['description']
                        })
                    
                    return {
                        'forecast': forecast_list,
                        'source': 'api',
                        'timestamp': datetime.now().isoformat()
                    }
        
        except Exception as e:
            logger.error(f"Error fetching weather forecast: {e}")
        
        # Fallback forecast data
        return {
            'forecast': [
                {
                    'datetime': '2024-01-01 12:00:00',
                    'temperature': 25,
                    'humidity': 60,
                    'rainfall': 0,
                    'weather_description': 'clear sky'
                }
            ],
            'source': 'default',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_soil_recommendations(self, soil_type: str, crop: str = None) -> Dict[str, Any]:
        """Get soil-based recommendations"""
        try:
            with open('data/soil_data.json', 'r', encoding='utf-8') as f:
                soil_data = json.load(f)
            
            if soil_type in soil_data['soil_types']:
                soil_info = soil_data['soil_types'][soil_type]
                
                recommendations = {
                    'soil_type': soil_info['name'],
                    'characteristics': soil_info['characteristics'],
                    'suitable_crops': soil_info['suitable_crops'],
                    'fertilizer_recommendations': soil_info['fertilizer_recommendations'],
                    'regions': soil_info['regions']
                }
                
                if crop and crop in soil_info['suitable_crops']:
                    recommendations['crop_suitability'] = 'highly_suitable'
                elif crop:
                    recommendations['crop_suitability'] = 'check_requirements'
                
                return recommendations
        
        except Exception as e:
            logger.error(f"Error getting soil recommendations: {e}")
        
        return {'error': 'Soil data not available'}
    
    def get_crop_information(self, crop_name: str) -> Dict[str, Any]:
        """Get detailed crop information"""
        try:
            with open('data/crop_data.json', 'r', encoding='utf-8') as f:
                crop_data = json.load(f)
            
            if crop_name.lower() in crop_data['crops']:
                return crop_data['crops'][crop_name.lower()]
        
        except Exception as e:
            logger.error(f"Error getting crop information: {e}")
        
        return {'error': 'Crop data not available'}
    
    def get_government_schemes(self, scheme_type: str = None) -> Dict[str, Any]:
        """Get government schemes information"""
        try:
            with open('data/schemes_data.json', 'r', encoding='utf-8') as f:
                schemes_data = json.load(f)
            
            if scheme_type and scheme_type in schemes_data['government_schemes']:
                return {scheme_type: schemes_data['government_schemes'][scheme_type]}
            else:
                return schemes_data['government_schemes']
        
        except Exception as e:
            logger.error(f"Error getting government schemes: {e}")
        
        return {'error': 'Schemes data not available'}
    
    def check_irrigation_recommendation(self, weather_data: Dict[str, Any], crop: str = None) -> Dict[str, Any]:
        """Generate irrigation recommendations based on weather"""
        try:
            temp = weather_data.get('temperature', 25)
            humidity = weather_data.get('humidity', 60)
            rainfall = weather_data.get('rainfall', 0)
            
            # Simple irrigation logic
            irrigation_needed = False
            recommendation = ""
            
            if rainfall > 5:
                recommendation = "No irrigation needed. Recent rainfall is sufficient."
            elif humidity < 40 and temp > 35:
                irrigation_needed = True
                recommendation = "High temperature and low humidity. Immediate irrigation recommended."
            elif humidity < 50 and temp > 30:
                irrigation_needed = True
                recommendation = "Moderate irrigation needed due to warm weather and low humidity."
            elif humidity > 80:
                recommendation = "High humidity levels. Monitor soil moisture before irrigating."
            else:
                recommendation = "Monitor soil condition. Light irrigation may be needed."
            
            return {
                'irrigation_needed': irrigation_needed,
                'recommendation': recommendation,
                'weather_factors': {
                    'temperature': temp,
                    'humidity': humidity,
                    'rainfall': rainfall
                },
                'timing': 'early_morning_or_evening' if irrigation_needed else 'not_needed'
            }
        
        except Exception as e:
            logger.error(f"Error generating irrigation recommendation: {e}")
            return {
                'irrigation_needed': False,
                'recommendation': 'Unable to generate recommendation. Please consult local agricultural expert.',
                'error': str(e)
            }
