"""
Test script for the new API-based Practo scraper
"""

import sys
import os
import json
import logging

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_scraper.main import PractoAPIScraper
from api_scraper.mock_api import patch_api_client_for_testing

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_api_scraper():
    """Test the API scraper with mock data"""
    logger.info("=" * 60)
    logger.info("Testing API-based Practo Doctor Scraper")
    logger.info("=" * 60)
    
    try:
        # Patch the API client to use mock data
        logger.info("Setting up mock API for testing...")
        patch_api_client_for_testing()
        
        # Initialize the scraper
        logger.info("Initializing API scraper...")
        scraper = PractoAPIScraper(api_key="test_key")
        
        # Test basic scraping
        logger.info("Testing basic doctor scraping...")
        doctors = scraper.scrape_doctors(city="bangalore", limit=10)
        
        if doctors:
            logger.info(f"✓ Successfully scraped {len(doctors)} doctors")
            
            # Print sample doctor data
            sample_doctor = doctors[0]
            logger.info("\nSample doctor data:")
            logger.info(f"  Name: {sample_doctor.get('name')}")
            logger.info(f"  Specialization: {sample_doctor.get('specialization')}")
            logger.info(f"  Experience: {sample_doctor.get('experience')}")
            logger.info(f"  Rating: {sample_doctor.get('rating')}")
            logger.info(f"  Clinics: {len(sample_doctor.get('clinics', []))}")
            
        else:
            logger.error("❌ No doctors scraped")
            return False
        
        # Test database saving
        logger.info("\nTesting database save...")
        saved_count = scraper.save_to_database(doctors[:5])  # Save first 5 doctors
        
        if saved_count > 0:
            logger.info(f"✓ Successfully saved {saved_count} doctors to database")
        else:
            logger.error("❌ Failed to save doctors to database")
            return False
        
        # Test data export
        logger.info("\nTesting data export...")
        scraper.export_data("all")
        
        # Check if files were created
        json_file = "doctors_data_api.json"
        csv_file = "doctors_data_api.csv"
        
        json_exists = os.path.exists(json_file)
        csv_exists = os.path.exists(csv_file)
        
        if json_exists and csv_exists:
            logger.info(f"✓ Export files created: {json_file}, {csv_file}")
            
            # Check JSON file content
            with open(json_file, 'r') as f:
                json_data = json.load(f)
                logger.info(f"  JSON file contains {len(json_data)} doctors")
                
        else:
            logger.error("❌ Export files not created")
            return False
        
        # Test specialization filtering
        logger.info("\nTesting specialization filtering...")
        cardio_doctors = scraper.scrape_doctors(
            city="bangalore", 
            limit=5, 
            specialization="Cardiologist"
        )
        
        if cardio_doctors:
            # Check if all doctors are cardiologists
            all_cardio = all(
                d.get('specialization', '').lower() == 'cardiologist' 
                for d in cardio_doctors
            )
            if all_cardio:
                logger.info(f"✓ Specialization filter working: {len(cardio_doctors)} cardiologists found")
            else:
                logger.warning("⚠️ Specialization filter may not be working correctly")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ All API scraper tests passed!")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_client_directly():
    """Test the API client directly"""
    logger.info("\nTesting API client directly...")
    
    try:
        from api_scraper.client import PractoAPIClient
        
        # Patch for testing
        patch_api_client_for_testing()
        
        client = PractoAPIClient(api_key="test_key")
        
        # Test search
        doctors = client.search_doctors(city="bangalore", limit=5)
        logger.info(f"✓ Client search returned {len(doctors)} doctors")
        
        if doctors:
            # Test get details
            doctor_id = doctors[0].get("id")
            if doctor_id:
                details = client.get_doctor_details(doctor_id)
                if details and "doctor" in details:
                    logger.info(f"✓ Client get_doctor_details working for {doctor_id}")
                else:
                    logger.error("❌ Client get_doctor_details failed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ API client test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("Starting comprehensive API scraper tests...\n")
    
    success = True
    
    # Test API client
    if not test_api_client_directly():
        success = False
    
    # Test full scraper
    if not test_api_scraper():
        success = False
    
    if success:
        logger.info("\n🎉 All tests passed! API scraper is working correctly.")
        return 0
    else:
        logger.error("\n❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())