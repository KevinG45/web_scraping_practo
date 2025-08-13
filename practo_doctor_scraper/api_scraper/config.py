"""
Configuration for EasyAPI Practo Doctor Scraper
"""

import os
from typing import Dict, Any

class APIConfig:
    """Configuration class for EasyAPI settings"""
    
    # API Base Configuration
    BASE_URL = "https://api.easyapi.com/v1"
    SERVICE_NAME = "practo-doctor-scraper"
    
    # API Key - can be set via environment variable
    API_KEY = os.getenv("EASYAPI_KEY", "easyapi/practo-doctor-scraper")
    
    # Request Configuration
    TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    # Rate Limiting
    REQUESTS_PER_MINUTE = 60
    REQUEST_DELAY = 1.0  # seconds between requests
    
    # Endpoints
    ENDPOINTS = {
        "search_doctors": "/practo/search/doctors",
        "doctor_details": "/practo/doctor/{doctor_id}",
        "doctors_by_city": "/practo/doctors/city/{city}",
        "doctors_by_specialization": "/practo/doctors/specialization/{specialization}"
    }
    
    # Default search parameters
    DEFAULT_PARAMS = {
        "city": "bangalore",
        "limit": 100,
        "offset": 0
    }
    
    @classmethod
    def get_endpoint_url(cls, endpoint_name: str, **kwargs) -> str:
        """Get full URL for an endpoint with path parameters"""
        if endpoint_name not in cls.ENDPOINTS:
            raise ValueError(f"Unknown endpoint: {endpoint_name}")
        
        endpoint = cls.ENDPOINTS[endpoint_name]
        
        # Replace path parameters
        for key, value in kwargs.items():
            endpoint = endpoint.replace(f"{{{key}}}", str(value))
        
        return cls.BASE_URL + endpoint
    
    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        """Get standard headers for API requests"""
        return {
            "Authorization": f"Bearer {cls.API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Practo-Doctor-Scraper/1.0"
        }