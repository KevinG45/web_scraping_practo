"""
API Client for EasyAPI Practo Doctor Scraper
"""

import requests
import time
import json
import logging
from typing import Dict, List, Any, Optional, Union
from .config import APIConfig

logger = logging.getLogger(__name__)

class PractoAPIClient:
    """Client for interacting with EasyAPI Practo Doctor Scraper service"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the API client
        
        Args:
            api_key: Optional API key override
        """
        self.config = APIConfig()
        if api_key:
            self.config.API_KEY = api_key
        
        self.session = requests.Session()
        self.session.headers.update(self.config.get_headers())
        
        # Rate limiting
        self.last_request_time = 0
        
    def _rate_limit(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.config.REQUEST_DELAY:
            sleep_time = self.config.REQUEST_DELAY - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request with retry logic
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional request parameters
            
        Returns:
            Dict containing the API response
            
        Raises:
            requests.RequestException: If request fails after retries
        """
        self._rate_limit()
        
        for attempt in range(self.config.MAX_RETRIES):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.config.TIMEOUT,
                    **kwargs
                )
                
                # Check for successful response
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limited
                    logger.warning("Rate limited, waiting longer...")
                    time.sleep(self.config.RETRY_DELAY * (attempt + 1) * 2)
                    continue
                else:
                    response.raise_for_status()
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt == self.config.MAX_RETRIES - 1:
                    raise
                time.sleep(self.config.RETRY_DELAY * (attempt + 1))
        
        raise requests.RequestException("All retry attempts failed")
    
    def search_doctors(self, city: str = "bangalore", limit: int = 100, offset: int = 0, 
                      specialization: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for doctors in a city
        
        Args:
            city: City name to search in
            limit: Maximum number of results
            offset: Offset for pagination
            specialization: Optional specialization filter
            
        Returns:
            List of doctor data dictionaries
        """
        url = self.config.get_endpoint_url("search_doctors")
        
        params = {
            "city": city,
            "limit": limit,
            "offset": offset
        }
        
        if specialization:
            params["specialization"] = specialization
        
        try:
            response = self._make_request("GET", url, params=params)
            return response.get("doctors", [])
        except Exception as e:
            logger.error(f"Error searching doctors: {e}")
            return []
    
    def get_doctor_details(self, doctor_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific doctor
        
        Args:
            doctor_id: Unique doctor identifier
            
        Returns:
            Doctor details dictionary or None if not found
        """
        url = self.config.get_endpoint_url("doctor_details", doctor_id=doctor_id)
        
        try:
            response = self._make_request("GET", url)
            return response.get("doctor")
        except Exception as e:
            logger.error(f"Error getting doctor details for {doctor_id}: {e}")
            return None
    
    def get_doctors_by_city(self, city: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all doctors in a specific city
        
        Args:
            city: City name
            limit: Maximum number of results
            
        Returns:
            List of doctor data dictionaries
        """
        url = self.config.get_endpoint_url("doctors_by_city", city=city)
        
        params = {"limit": limit}
        
        try:
            response = self._make_request("GET", url, params=params)
            return response.get("doctors", [])
        except Exception as e:
            logger.error(f"Error getting doctors by city {city}: {e}")
            return []
    
    def get_doctors_by_specialization(self, specialization: str, 
                                    city: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get doctors by specialization
        
        Args:
            specialization: Medical specialization
            city: Optional city filter
            
        Returns:
            List of doctor data dictionaries
        """
        url = self.config.get_endpoint_url("doctors_by_specialization", 
                                         specialization=specialization)
        
        params = {}
        if city:
            params["city"] = city
        
        try:
            response = self._make_request("GET", url, params=params)
            return response.get("doctors", [])
        except Exception as e:
            logger.error(f"Error getting doctors by specialization {specialization}: {e}")
            return []
    
    def get_all_bangalore_doctors(self, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Get all doctors in Bangalore with pagination
        
        Args:
            limit: Total number of doctors to retrieve
            
        Returns:
            List of all doctor data dictionaries
        """
        all_doctors = []
        offset = 0
        page_size = 100  # API pagination size
        
        while len(all_doctors) < limit:
            batch = self.search_doctors(
                city="bangalore",
                limit=min(page_size, limit - len(all_doctors)),
                offset=offset
            )
            
            if not batch:
                break
                
            all_doctors.extend(batch)
            offset += len(batch)
            
            # If we got less than page_size, we've reached the end
            if len(batch) < page_size:
                break
        
        return all_doctors[:limit]