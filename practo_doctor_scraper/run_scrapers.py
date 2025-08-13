#!/usr/bin/env python3
"""
Main script to run both Scrapy and Playwright scrapers
"""

import os
import sys
import subprocess
import asyncio
import time

def run_scrapy_spider():
    """Run the Scrapy spider"""
    print("=" * 50)
    print("Starting Scrapy Spider...")
    print("=" * 50)
    
    try:
        # Change to the practo_scraper directory
        os.chdir('practo_scraper')
        
        # Run the scrapy spider
        result = subprocess.run([
            'scrapy', 'crawl', 'doctor_spider', 
            '-s', 'CLOSESPIDER_ITEMCOUNT=50'  # Limit to 50 items for testing
        ], capture_output=True, text=True)
        
        print("Scrapy Output:")
        print(result.stdout)
        if result.stderr:
            print("Scrapy Errors:")
            print(result.stderr)
        
        # Change back to parent directory
        os.chdir('..')
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running Scrapy spider: {e}")
        os.chdir('..')  # Ensure we change back
        return False

async def run_playwright_spider():
    """Run the Playwright spider"""
    print("=" * 50)
    print("Starting Playwright Spider...")
    print("=" * 50)
    
    try:
        # Change to the playwright_scraper directory
        os.chdir('playwright_scraper')
        
        # Import and run the main function
        sys.path.append(os.getcwd())
        from main import main
        await main()
        
        # Change back to parent directory
        os.chdir('..')
        
        return True
        
    except Exception as e:
        print(f"Error running Playwright spider: {e}")
        os.chdir('..')  # Ensure we change back
        return False

def main():
    """Main function to run both scrapers"""
    print("Practo Doctor Scraper - Running Both Scrapy and Playwright")
    print("=" * 60)
    
    start_time = time.time()
    
    # Check if required directories exist
    if not os.path.exists('practo_scraper'):
        print("Error: practo_scraper directory not found!")
        return
    
    if not os.path.exists('playwright_scraper'):
        print("Error: playwright_scraper directory not found!")
        return
    
    # Run Scrapy spider first
    print("Phase 1: Running Scrapy spider for comprehensive URL discovery...")
    scrapy_success = run_scrapy_spider()
    
    if scrapy_success:
        print("✅ Scrapy spider completed successfully")
    else:
        print("❌ Scrapy spider encountered issues")
    
    print("\nWaiting 5 seconds before starting Playwright spider...")
    time.sleep(5)
    
    # Run Playwright spider
    print("Phase 2: Running Playwright spider for detailed data extraction...")
    try:
        playwright_success = asyncio.run(run_playwright_spider())
        if playwright_success:
            print("✅ Playwright spider completed successfully")
        else:
            print("❌ Playwright spider encountered issues")
    except Exception as e:
        print(f"❌ Error running Playwright spider: {e}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 60)
    print("SCRAPING COMPLETE")
    print(f"Total time: {duration:.2f} seconds")
    print("Check the following files for results:")
    print("- doctors_data.json")
    print("- doctors_data.csv") 
    print("- doctors_data.db")
    print("=" * 60)

if __name__ == '__main__':
    main()