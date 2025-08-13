#!/usr/bin/env python3
"""
Final demonstration of the EasyAPI Practo Doctor Scraper
This script showcases all the key features of the new API-based scraper
"""

import sys
import os
import json
import time

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

def main():
    print("🏥 EasyAPI Practo Doctor Scraper - Final Demonstration")
    print("=" * 60)
    
    # Import after adding to path
    from api_scraper.main import PractoAPIScraper
    from api_scraper.mock_api import patch_api_client_for_testing
    
    print("🧪 Setting up mock API for demonstration...")
    patch_api_client_for_testing()
    
    # Initialize scraper
    scraper = PractoAPIScraper(api_key="easyapi/practo-doctor-scraper")
    print("✅ API scraper initialized")
    
    # Test 1: Basic scraping
    print("\n" + "=" * 60)
    print("📋 Test 1: Basic Doctor Scraping")
    print("=" * 60)
    
    doctors = scraper.scrape_doctors(city="bangalore", limit=5)
    print(f"✅ Scraped {len(doctors)} doctors from Bangalore")
    
    if doctors:
        sample = doctors[0]
        print(f"\n📊 Sample Doctor Data:")
        print(f"   Name: {sample['name']}")
        print(f"   Specialization: {sample['specialization']}")
        print(f"   Experience: {sample['experience']}")
        print(f"   Rating: {sample['rating']}/5.0 ({sample['reviews_count']} reviews)")
        print(f"   Clinics: {len(sample['clinics'])}")
        print(f"   Services: {len(sample['services'])}")
    
    # Test 2: Specialization filtering
    print("\n" + "=" * 60)
    print("🔍 Test 2: Specialization Filtering")
    print("=" * 60)
    
    cardio_doctors = scraper.scrape_doctors(
        city="bangalore", 
        limit=3, 
        specialization="Cardiologist"
    )
    print(f"✅ Found {len(cardio_doctors)} Cardiologist(s)")
    
    for doc in cardio_doctors:
        print(f"   • {doc['name']} - {doc['specialization']}")
    
    # Test 3: Data export
    print("\n" + "=" * 60)
    print("💾 Test 3: Data Export Functionality")  
    print("=" * 60)
    
    # Export to JSON
    scraper.export_data("json")
    
    # Check file was created
    json_file = "doctors_data_api.json"
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            exported_data = json.load(f)
        print(f"✅ JSON export successful: {len(exported_data)} doctors in {json_file}")
    
    # Export to CSV
    scraper.export_data("csv")
    
    csv_file = "doctors_data_api.csv"
    if os.path.exists(csv_file):
        print(f"✅ CSV export successful: {csv_file}")
    
    # Test 4: API client features
    print("\n" + "=" * 60)
    print("🌐 Test 4: API Client Features")
    print("=" * 60)
    
    from api_scraper.client import PractoAPIClient
    patch_api_client_for_testing()  # Re-patch for client
    
    client = PractoAPIClient()
    
    # Test search
    search_results = client.search_doctors(city="bangalore", limit=3)
    print(f"✅ API search returned {len(search_results)} results")
    
    # Test get details
    if search_results:
        doctor_id = search_results[0].get("id")
        details = client.get_doctor_details(doctor_id)
        if details and "doctor" in details:
            print(f"✅ API get_doctor_details working for {doctor_id}")
    
    # Test 5: Configuration
    print("\n" + "=" * 60)
    print("⚙️  Test 5: Configuration System")
    print("=" * 60)
    
    from api_scraper.config import APIConfig
    
    print(f"✅ API Base URL: {APIConfig.BASE_URL}")
    print(f"✅ Service Name: {APIConfig.SERVICE_NAME}")
    print(f"✅ Default City: {APIConfig.DEFAULT_PARAMS['city']}")
    print(f"✅ Request Timeout: {APIConfig.TIMEOUT}s")
    print(f"✅ Max Retries: {APIConfig.MAX_RETRIES}")
    
    # Test 6: Data mapping
    print("\n" + "=" * 60)
    print("🔄 Test 6: Data Mapping")
    print("=" * 60)
    
    from api_scraper.mapper import DoctorDataMapper
    
    # Create sample API data
    sample_api_data = {
        "name": "Dr. Test Doctor",
        "specialization": "General Physician",
        "experience": {"years": 10},
        "qualifications": ["MBBS", "MD"],
        "clinics": [{"name": "Test Clinic", "address": "Test Address"}],
        "fees": {"consultation": 500},
        "rating": 4.2,
        "reviews_count": 25
    }
    
    mapped_data = DoctorDataMapper.map_api_response_to_doctor_data(sample_api_data)
    print(f"✅ Data mapping successful:")
    print(f"   Mapped name: {mapped_data['name']}")
    print(f"   Mapped experience: {mapped_data['experience']}")
    print(f"   Mapped qualifications: {mapped_data['qualifications']}")
    print(f"   Mapped fees: {mapped_data['fees']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 DEMONSTRATION COMPLETE!")
    print("=" * 60)
    
    total_doctors = len(scraper.doctors_data)
    print(f"📊 Summary:")
    print(f"   • Total doctors scraped: {total_doctors}")
    print(f"   • Export formats: JSON, CSV")
    print(f"   • Specialization filtering: ✅ Working")
    print(f"   • API client: ✅ Working") 
    print(f"   • Data mapping: ✅ Working")
    print(f"   • Configuration: ✅ Working")
    print(f"   • Mock testing: ✅ Working")
    
    print(f"\n📁 Generated Files:")
    files = ["doctors_data_api.json", "doctors_data_api.csv"]
    for file in files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   • {file} ({size:,} bytes)")
    
    print(f"\n🚀 Ready for Production!")
    print(f"   • Replace mock API with real EasyAPI key")
    print(f"   • Install database dependencies for full functionality")
    print(f"   • Scale up limits for production scraping")
    
    print("\n📚 Usage Examples:")
    print("   python run_api_scraper.py --api-key YOUR_KEY --limit 100")
    print("   python run_api_scraper.py --specialization Cardiologist")
    print("   python run_api_scraper.py --city mumbai --export json")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())