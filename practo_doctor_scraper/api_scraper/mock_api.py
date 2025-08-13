"""
Mock API implementation for testing the EasyAPI Practo scraper
This provides sample data in the expected format for development and testing
"""

import json
import random
import time
from typing import Dict, List, Any, Optional

class MockPractoAPI:
    """Mock implementation of the EasyAPI Practo service for testing"""
    
    def __init__(self):
        self.sample_doctors = self._generate_sample_doctors()
    
    def _generate_sample_doctors(self) -> List[Dict[str, Any]]:
        """Generate sample doctor data for testing"""
        
        specializations = [
            "Cardiologist", "Dermatologist", "Pediatrician", "Orthopedic",
            "Neurologist", "Gynecologist", "ENT Specialist", "Dentist",
            "Ophthalmologist", "General Physician", "Psychiatrist", "Urologist"
        ]
        
        qualifications = [
            ["MBBS", "MD", "DM"],
            ["MBBS", "MS"],
            ["BDS", "MDS"],
            ["MBBS", "MD"],
            ["MBBS", "MS", "MCh"],
            ["MBBS", "DNB"]
        ]
        
        sample_doctors = []
        
        for i in range(50):  # Generate 50 sample doctors
            doctor_id = f"dr_{i+1}"
            specialization = random.choice(specializations)
            quals = random.choice(qualifications)
            experience_years = random.randint(2, 25)
            rating = round(random.uniform(3.5, 5.0), 1)
            reviews = random.randint(10, 500)
            
            # Generate clinic data
            clinics = []
            num_clinics = random.randint(1, 3)
            
            for j in range(num_clinics):
                clinic = {
                    "name": f"Healthcare Clinic {j+1}",
                    "address": f"#123, {random.choice(['MG Road', 'Brigade Road', 'Koramangala', 'Indiranagar', 'Whitefield'])}, Bangalore - 560001",
                    "google_maps_link": f"https://maps.google.com/clinic_{doctor_id}_{j}"
                }
                clinics.append(clinic)
            
            # Generate availability
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
            availability = {}
            for day in random.sample(days, random.randint(4, 6)):
                time_slots = ["09:00 AM - 12:00 PM", "02:00 PM - 06:00 PM"]
                availability[day] = random.sample(time_slots, random.randint(1, 2))
            
            # Generate services
            all_services = [
                "Consultation", "Follow-up", "Diagnosis", "Treatment", 
                "Emergency Care", "Surgery", "Health Checkup"
            ]
            services = random.sample(all_services, random.randint(2, 5))
            
            doctor = {
                "id": doctor_id,
                "name": f"Dr. {random.choice(['Rajesh', 'Priya', 'Amit', 'Sunita', 'Vikram', 'Kavitha', 'Suresh', 'Meera'])} {random.choice(['Kumar', 'Sharma', 'Patel', 'Singh', 'Reddy', 'Nair', 'Gupta', 'Iyer'])}",
                "specialization": specialization,
                "experience": experience_years,
                "qualifications": quals,
                "clinics": clinics,
                "fees": {
                    "consultation": random.randint(300, 1500),
                    "currency": "INR"
                },
                "rating": rating,
                "reviews_count": reviews,
                "services": services,
                "phone": f"+91 {random.randint(8000000000, 9999999999)}",
                "availability": availability,
                "profile_url": f"https://www.practo.com/bangalore/doctor/{doctor_id}",
                "image_url": f"https://images.practo.com/doctors/{doctor_id}.jpg"
            }
            
            sample_doctors.append(doctor)
        
        return sample_doctors
    
    def search_doctors(self, city: str = "bangalore", limit: int = 100, 
                      offset: int = 0, specialization: Optional[str] = None) -> Dict[str, Any]:
        """Mock search doctors endpoint"""
        time.sleep(0.1)  # Simulate API delay
        
        doctors = self.sample_doctors[:]
        
        # Filter by specialization if provided
        if specialization:
            doctors = [d for d in doctors if d["specialization"].lower() == specialization.lower()]
        
        # Apply pagination
        end_index = min(offset + limit, len(doctors))
        paginated_doctors = doctors[offset:end_index]
        
        return {
            "doctors": paginated_doctors,
            "total": len(doctors),
            "offset": offset,
            "limit": limit
        }
    
    def get_doctor_details(self, doctor_id: str) -> Dict[str, Any]:
        """Mock get doctor details endpoint"""
        time.sleep(0.1)  # Simulate API delay
        
        doctor = next((d for d in self.sample_doctors if d["id"] == doctor_id), None)
        
        if doctor:
            return {"doctor": doctor}
        else:
            return {"error": "Doctor not found"}
    
    def get_doctors_by_city(self, city: str, limit: int = 100) -> Dict[str, Any]:
        """Mock get doctors by city endpoint"""
        return self.search_doctors(city=city, limit=limit)
    
    def get_doctors_by_specialization(self, specialization: str, 
                                    city: Optional[str] = None) -> Dict[str, Any]:
        """Mock get doctors by specialization endpoint"""
        return self.search_doctors(specialization=specialization, city=city or "bangalore")

# Monkey patch the API client to use mock data for testing
def patch_api_client_for_testing():
    """Replace the real API client with mock implementation for testing"""
    from .client import PractoAPIClient
    
    # Store original methods
    original_make_request = PractoAPIClient._make_request
    
    # Create mock API instance
    mock_api = MockPractoAPI()
    
    def mock_make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Mock implementation of _make_request"""
        time.sleep(0.1)  # Simulate network delay
        
        # Extract endpoint from URL
        if "/practo/search/doctors" in url:
            params = kwargs.get("params", {})
            return mock_api.search_doctors(
                city=params.get("city", "bangalore"),
                limit=params.get("limit", 100),
                offset=params.get("offset", 0),
                specialization=params.get("specialization")
            )
        elif "/practo/doctor/" in url:
            doctor_id = url.split("/")[-1]
            return mock_api.get_doctor_details(doctor_id)
        elif "/practo/doctors/city/" in url:
            city = url.split("/")[-1]
            params = kwargs.get("params", {})
            return mock_api.get_doctors_by_city(city, params.get("limit", 100))
        elif "/practo/doctors/specialization/" in url:
            specialization = url.split("/")[-1]
            params = kwargs.get("params", {})
            return mock_api.get_doctors_by_specialization(
                specialization, params.get("city")
            )
        else:
            return {"error": "Unknown endpoint"}
    
    # Patch the method
    PractoAPIClient._make_request = mock_make_request
    
    return mock_api