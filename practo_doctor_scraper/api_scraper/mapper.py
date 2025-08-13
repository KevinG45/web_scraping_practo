"""
Data mapping utilities for converting API responses to database models
"""

import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DoctorDataMapper:
    """Maps API response data to database schema format"""
    
    @staticmethod
    def map_api_response_to_doctor_data(api_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert API response to database-compatible doctor data
        
        Args:
            api_data: Raw API response data for a doctor
            
        Returns:
            Dictionary matching the existing database schema
        """
        try:
            # Extract basic information
            name = api_data.get("name", "")
            specialization = api_data.get("specialization", "")
            experience = DoctorDataMapper._format_experience(api_data.get("experience"))
            qualifications = DoctorDataMapper._format_qualifications(api_data.get("qualifications", []))
            
            # Extract clinic information
            clinics = DoctorDataMapper._format_clinics(api_data.get("clinics", []))
            
            # Extract fees
            fees = DoctorDataMapper._format_fees(api_data.get("fees"))
            
            # Extract rating and reviews
            rating = float(api_data.get("rating", 0.0))
            reviews_count = int(api_data.get("reviews_count", 0))
            
            # Extract services
            services = api_data.get("services", [])
            if isinstance(services, str):
                try:
                    services = json.loads(services)
                except json.JSONDecodeError:
                    services = [services] if services else []
            
            # Extract contact information
            address = DoctorDataMapper._extract_primary_address(clinics)
            google_maps_link = DoctorDataMapper._extract_primary_maps_link(clinics)
            phone = api_data.get("phone", "")
            
            # Extract availability
            availability = DoctorDataMapper._format_availability(api_data.get("availability", {}))
            
            # Extract URLs
            profile_url = api_data.get("profile_url", "")
            image_url = api_data.get("image_url", "")
            
            return {
                "name": name,
                "specialization": specialization,
                "experience": experience,
                "qualifications": qualifications,
                "clinics": clinics,
                "fees": fees,
                "rating": rating,
                "reviews_count": reviews_count,
                "services": services,
                "address": address,
                "google_maps_link": google_maps_link,
                "phone": phone,
                "availability": availability,
                "profile_url": profile_url,
                "image_url": image_url
            }
            
        except Exception as e:
            logger.error(f"Error mapping API data: {e}")
            return DoctorDataMapper._get_empty_doctor_data()
    
    @staticmethod
    def _format_experience(experience_data: Any) -> str:
        """Format experience data into a string"""
        if isinstance(experience_data, (int, float)):
            years = int(experience_data)
            return f"{years} {'year' if years == 1 else 'years'}"
        elif isinstance(experience_data, str):
            return experience_data
        elif isinstance(experience_data, dict):
            years = experience_data.get("years", 0)
            return f"{years} {'year' if years == 1 else 'years'}"
        return ""
    
    @staticmethod
    def _format_qualifications(qualifications_data: Any) -> str:
        """Format qualifications data into a string"""
        if isinstance(qualifications_data, list):
            return ", ".join(str(q) for q in qualifications_data if q)
        elif isinstance(qualifications_data, str):
            return qualifications_data
        return ""
    
    @staticmethod
    def _format_clinics(clinics_data: Any) -> List[Dict[str, Any]]:
        """Format clinics data into standardized format"""
        if not clinics_data:
            return []
        
        if isinstance(clinics_data, str):
            try:
                clinics_data = json.loads(clinics_data)
            except json.JSONDecodeError:
                return []
        
        if not isinstance(clinics_data, list):
            clinics_data = [clinics_data]
        
        formatted_clinics = []
        for clinic in clinics_data:
            if isinstance(clinic, dict):
                formatted_clinic = {
                    "name": clinic.get("name", ""),
                    "address": clinic.get("address", ""),
                    "google_maps_link": clinic.get("google_maps_link", "")
                }
                formatted_clinics.append(formatted_clinic)
        
        return formatted_clinics
    
    @staticmethod
    def _format_fees(fees_data: Any) -> str:
        """Format fees data into a string"""
        if isinstance(fees_data, (int, float)):
            return f"₹{fees_data}"
        elif isinstance(fees_data, str):
            return fees_data
        elif isinstance(fees_data, dict):
            consultation_fee = fees_data.get("consultation", fees_data.get("amount", 0))
            return f"₹{consultation_fee}"
        return ""
    
    @staticmethod
    def _format_availability(availability_data: Any) -> Dict[str, List[str]]:
        """Format availability data into standardized format"""
        if isinstance(availability_data, str):
            try:
                availability_data = json.loads(availability_data)
            except json.JSONDecodeError:
                return {}
        
        if not isinstance(availability_data, dict):
            return {}
        
        formatted_availability = {}
        for day, times in availability_data.items():
            if isinstance(times, list):
                formatted_availability[day] = [str(t) for t in times if t]
            elif isinstance(times, str):
                formatted_availability[day] = [times] if times else []
        
        return formatted_availability
    
    @staticmethod
    def _extract_primary_address(clinics: List[Dict[str, Any]]) -> str:
        """Extract primary address from clinics list"""
        if clinics and len(clinics) > 0:
            return clinics[0].get("address", "")
        return ""
    
    @staticmethod
    def _extract_primary_maps_link(clinics: List[Dict[str, Any]]) -> str:
        """Extract primary Google Maps link from clinics list"""
        if clinics and len(clinics) > 0:
            return clinics[0].get("google_maps_link", "")
        return ""
    
    @staticmethod
    def _get_empty_doctor_data() -> Dict[str, Any]:
        """Return empty doctor data structure"""
        return {
            "name": "",
            "specialization": "",
            "experience": "",
            "qualifications": "",
            "clinics": [],
            "fees": "",
            "rating": 0.0,
            "reviews_count": 0,
            "services": [],
            "address": "",
            "google_maps_link": "",
            "phone": "",
            "availability": {},
            "profile_url": "",
            "image_url": ""
        }
    
    @staticmethod
    def batch_map_doctors(api_doctors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Map a batch of doctors from API format to database format
        
        Args:
            api_doctors: List of doctor data from API
            
        Returns:
            List of mapped doctor data
        """
        mapped_doctors = []
        for doctor_data in api_doctors:
            mapped_doctor = DoctorDataMapper.map_api_response_to_doctor_data(doctor_data)
            if mapped_doctor["name"]:  # Only include doctors with names
                mapped_doctors.append(mapped_doctor)
        
        return mapped_doctors