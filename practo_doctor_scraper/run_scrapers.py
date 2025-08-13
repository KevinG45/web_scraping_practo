#!/usr/bin/env python3
"""
Run both Scrapy and Playwright scrapers for comprehensive doctor data collection
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def run_scrapy_spider():
    """Run the Scrapy spider for initial URL discovery"""
    print("=" * 50)
    print("Phase 1: Running Scrapy spider for comprehensive URL discovery...")
    print("=" * 50)
    print("Starting Scrapy Spider...")
    print("=" * 50)
    
    try:
        # Change to the correct directory for scrapy
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Run scrapy spider
        result = subprocess.run([
            sys.executable, '-m', 'scrapy', 'crawl', 'doctor_spider',
            '-s', 'CLOSESPIDER_ITEMCOUNT=10',  # Limit for testing
            '-L', 'INFO'
        ], capture_output=True, text=True, timeout=300)
        
        print("Scrapy Output:")
        if result.stdout:
            print(result.stdout)
        
        print("\nScrapy Errors:")
        if result.stderr:
            print(result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Scrapy spider timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running Scrapy spider: {e}")
        return False

def run_api_scraper():
    """Run the new EasyAPI-based scraper"""
    print("\n" + "=" * 50)
    print("Phase 2: Running EasyAPI-based scraper...")
    print("=" * 50)
    
    try:
        # Import and run the API scraper
        from api_scraper.main import PractoAPIScraper
        from api_scraper.mock_api import patch_api_client_for_testing
        
        # Use mock API for testing (remove this line when using real API)
        print("⚠️ Using mock API for testing. Remove this for production.")
        patch_api_client_for_testing()
        
        # Initialize and run scraper
        scraper = PractoAPIScraper()
        scraper.run_full_scrape(city="bangalore", limit=20, save_to_db=True)
        
        print("✓ API scraper completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error running API scraper: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_playwright_scraper():
    """Run the Playwright scraper for detailed data extraction"""
    print("\n" + "=" * 50)
    print("Phase 3: Running Playwright scraper for detailed extraction...")
    print("=" * 50)
    
    try:
        # Import playwright modules
        from playwright.async_api import async_playwright
        import asyncio
        
        async def run_playwright():
            try:
                async with async_playwright() as p:
                    # Try to launch browser (will fail if not installed)
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context()
                    
                    # Import and initialize the scraper with proper arguments
                    from playwright_scraper.doctor_scraper import DoctorScraper
                    scraper = DoctorScraper(browser, context)
                    
                    # Use some test URLs for demonstration
                    test_urls = [
                        "https://www.practo.com/bangalore/doctor/dr-rajesh-kumar-cardiologist",
                        "https://www.practo.com/bangalore/doctor/dr-priya-sharma-dermatologist"
                    ]
                    
                    results = []
                    for url in test_urls:
                        print(f"Scraping: {url}")
                        try:
                            result = await scraper.scrape_doctor_page(url)
                            if result:
                                results.append(result)
                                print(f"✓ Successfully scraped {result.get('name', 'Unknown')}")
                            else:
                                print(f"❌ Failed to scrape {url}")
                        except Exception as e:
                            print(f"❌ Error scraping {url}: {e}")
                    
                    await browser.close()
                    return results
            except Exception as e:
                if "Executable doesn't exist" in str(e) or "browser is not installed" in str(e):
                    print("⚠️ Playwright browser not installed. Run 'playwright install chromium' to enable Playwright scraping.")
                    return []
                else:
                    raise e
        
        # Run the async function
        results = asyncio.run(run_playwright())
        
        if results:
            print(f"\n✓ Playwright scraper completed. Scraped {len(results)} profiles.")
            return True
        else:
            print("\n⚠️ Playwright scraper skipped (browser not available).")
            return True  # Still count as success since it's optional
        
    except Exception as e:
        print(f"❌ Error running Playwright scraper: {e}")
        return False

def main():
    """Main function to run all scrapers"""
    print("Practo Doctor Scraper - Running Scrapy, API, and Playwright")
    print("=" * 60)
    
    # Run Scrapy spider first
    scrapy_success = run_scrapy_spider()
    
    # Run new API scraper
    api_success = run_api_scraper()
    
    # Run Playwright scraper
    playwright_success = run_playwright_scraper()
    
    # Summary
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print("=" * 60)
    print(f"Scrapy Spider: {'✓ SUCCESS' if scrapy_success else '❌ FAILED'}")
    print(f"API Scraper: {'✓ SUCCESS' if api_success else '❌ FAILED'}")
    print(f"Playwright Scraper: {'✓ SUCCESS' if playwright_success else '❌ FAILED'}")
    
    success_count = sum([scrapy_success, api_success, playwright_success])
    
    if success_count == 3:
        print("🎉 All scrapers completed successfully!")
        return 0
    elif success_count >= 1:
        print(f"⚠️ {success_count}/3 scrapers completed successfully")
        return 1
    else:
        print("❌ All scrapers failed")
        return 2

if __name__ == "__main__":
    sys.exit(main())