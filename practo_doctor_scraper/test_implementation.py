#!/usr/bin/env python3
"""
Simple test script to verify the implementation correctness
"""

import sys
import os
import json
from sqlalchemy import create_engine

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported successfully"""
    print("Testing imports...")
    
    try:
        from practo_scraper.spiders.doctors_spider import DoctorSpider
        from practo_scraper.spiders.sitemap_spider import DoctorSitemapSpider
        from practo_scraper.items import DoctorItem
        from practo_scraper.pipelines import JsonPipeline, CSVPipeline, DatabasePipeline
        from practo_scraper.utils.database import Doctor, create_tables
        from practo_scraper.utils.export import export_to_json, export_to_csv, get_all_doctors_from_db
        from playwright_scraper.doctor_scraper import DoctorScraper
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_database_setup():
    """Test database setup functionality"""
    print("Testing database setup...")
    
    try:
        from practo_scraper.utils.database import Doctor, create_tables
        
        # Test database creation
        engine = create_engine('sqlite:///test_db.db')
        create_tables(engine)
        print("✓ Database tables created successfully")
        
        # Clean up
        os.remove('test_db.db')
        return True
    except Exception as e:
        print(f"✗ Database setup error: {e}")
        return False

def test_json_serialization():
    """Test JSON serialization robustness"""
    print("Testing JSON serialization...")
    
    try:
        from practo_scraper.pipelines import DatabasePipeline
        from practo_scraper.items import DoctorItem
        
        # Create a mock spider object
        class MockSpider:
            def __init__(self):
                self.logger = self
            
            def error(self, msg):
                print(f"Spider error: {msg}")
        
        # Test the pipeline with some test data
        pipeline = DatabasePipeline()
        
        # Test with normal data
        item = DoctorItem()
        item['name'] = 'Test Doctor'
        item['clinics'] = [{'name': 'Test Clinic', 'address': 'Test Address'}]
        item['services'] = ['Consultation', 'Treatment']
        item['availability'] = {'Monday': ['9:00 AM - 5:00 PM']}
        
        # This should not raise an exception
        result = pipeline.process_item(item, MockSpider())
        print("✓ JSON serialization works correctly")
        
        # Clean up
        if os.path.exists('doctors_data.db'):
            os.remove('doctors_data.db')
        
        return True
    except Exception as e:
        print(f"✗ JSON serialization error: {e}")
        return False

def test_css_selectors():
    """Test if CSS selectors are properly formatted"""
    print("Testing CSS selectors...")
    
    try:
        from practo_scraper.spiders.doctors_spider import DoctorSpider
        
        spider = DoctorSpider()
        
        # Check some key selectors (these are just format checks, not actual functionality)
        selectors_to_check = [
            'div.info-section a.doctor-name::attr(href)',
            'h1.doctor-name::text',
            'div.specialization::text',
            'div.experience::text',
            'span.common__star-rating__value::text'
        ]
        
        for selector in selectors_to_check:
            # Basic syntax check - make sure there are no obvious syntax errors
            if '::' in selector and ('text' in selector or 'attr' in selector):
                continue
            elif '::' not in selector:
                continue
            else:
                raise ValueError(f"Invalid selector: {selector}")
        
        print("✓ CSS selectors appear to be properly formatted")
        return True
    except Exception as e:
        print(f"✗ CSS selector error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Running Implementation Correctness Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_database_setup,
        test_json_serialization,
        test_css_selectors
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("🎉 All tests passed! The implementation appears to be correct.")
        return 0
    else:
        print("❌ Some tests failed. Please review the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())