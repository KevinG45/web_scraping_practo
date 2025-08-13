#!/usr/bin/env python3
"""
Test script to verify spider functionality without network access
"""

import sys
import os
from io import StringIO

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_spider_syntax():
    """Test that the spider can be imported and instantiated without errors"""
    try:
        from practo_scraper.spiders.doctors_spider import DoctorSpider
        spider = DoctorSpider()
        print("✓ Spider imported and instantiated successfully")
        
        # Test the helper methods exist
        if hasattr(spider, 'get_text_by_selectors'):
            print("✓ get_text_by_selectors method exists")
        else:
            print("❌ get_text_by_selectors method missing")
            return False
            
        if hasattr(spider, 'get_text_by_selectors_all'):
            print("✓ get_text_by_selectors_all method exists")
        else:
            print("❌ get_text_by_selectors_all method missing")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Spider import/instantiation error: {e}")
        return False

def test_css_selectors():
    """Test CSS selectors for syntax errors"""
    try:
        from practo_scraper.spiders.doctors_spider import DoctorSpider
        from scrapy.http import HtmlResponse
        from scrapy import Request
        
        spider = DoctorSpider()
        
        # Create a mock response
        mock_html = """
        <html>
            <body>
                <h1 class="doctor-name">Dr. Test Doctor</h1>
                <div class="specialization">Cardiologist</div>
                <img class="doctor-image" src="/test.jpg" alt="doctor photo">
            </body>
        </html>
        """
        
        response = HtmlResponse(
            url='http://test.com',
            body=mock_html.encode('utf-8'),
            encoding='utf-8'
        )
        
        # Test the selectors that were causing errors
        test_selectors = [
            'div.doctor-photo img::attr(src)',
            'img.doctor-image::attr(src)',
            '.doctor-avatar img::attr(src)',
            '.profile-photo img::attr(src)',
            'img[alt*="doctor"]::attr(src)',
            'img[alt*="Doctor"]::attr(src)'
        ]
        
        for selector in test_selectors:
            try:
                result = response.css(selector).get()
                print(f"✓ Selector '{selector}' works correctly")
            except Exception as e:
                print(f"❌ Selector '{selector}' failed: {e}")
                return False
        
        # Test the helper method
        result = spider.get_text_by_selectors(response, test_selectors)
        print(f"✓ get_text_by_selectors returned: {result}")
        
        return True
    except Exception as e:
        print(f"❌ CSS selector test error: {e}")
        return False

def test_run_scrapers_file():
    """Test that run_scrapers.py exists and can be imported"""
    try:
        import run_scrapers
        print("✓ run_scrapers.py imported successfully")
        
        if hasattr(run_scrapers, 'main'):
            print("✓ main function exists in run_scrapers.py")
        else:
            print("❌ main function missing in run_scrapers.py")
            return False
            
        return True
    except Exception as e:
        print(f"❌ run_scrapers.py import error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Practo Scraper Fix")
    print("=" * 60)
    
    tests = [
        test_spider_syntax,
        test_css_selectors,
        test_run_scrapers_file
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All fixes appear to be working correctly!")
        return 0
    else:
        print("❌ Some issues remain. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())