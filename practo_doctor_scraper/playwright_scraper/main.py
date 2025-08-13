import asyncio
import json
import pandas as pd
from playwright.async_api import async_playwright
from tqdm import tqdm
import os
import sys
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from practo_scraper.utils.database import Base, Doctor, create_tables
from .doctor_scraper import DoctorScraper

DATABASE_URI = 'sqlite:///doctors_data.db'

async def get_bangalore_doctor_urls_from_sitemap():
    """Extract doctor profile URLs for Bangalore from the sitemap"""
    print("Fetching doctor URLs from sitemap...")
    sitemap_url = 'https://www.practo.com/profiles-sitemap.xml'
    response = requests.get(sitemap_url)
    
    if response.status_code != 200:
        print(f"Failed to fetch sitemap: {response.status_code}")
        return []
    
    # Parse the sitemap XML
    root = ET.fromstring(response.content)
    
    # Extract URLs that contain 'bangalore'
    bangalore_urls = []
    for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
        loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        if loc_elem is not None and loc_elem.text:
            loc = loc_elem.text
            if 'bangalore' in loc.lower() and '/doctor/' in loc.lower():
                bangalore_urls.append(loc)
    
    print(f"Found {len(bangalore_urls)} doctor URLs for Bangalore")
    return bangalore_urls

async def main():
    # Create the engine and tables
    engine = create_engine(DATABASE_URI)
    create_tables(engine)
    Session = sessionmaker(bind=engine)
    
    # Get doctor URLs from sitemap
    doctor_urls = await get_bangalore_doctor_urls_from_sitemap()
    
    # If no URLs found from sitemap, use the base URL
    if not doctor_urls:
        print("No URLs found in sitemap. Using base URL...")
        doctor_urls = ['https://www.practo.com/bangalore/doctors']
    
    # Initialize lists to store the data
    doctors_data = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Create a doctor scraper instance
        scraper = DoctorScraper(browser, context)
        
        # Process the base URL first to extract doctor profile links
        if 'doctors' in doctor_urls[0]:
            profile_urls = await scraper.extract_doctor_links(doctor_urls[0])
            doctor_urls = profile_urls[:100]  # Limit to 100 doctors
        
        print(f"Processing {len(doctor_urls)} doctor profiles...")
        
        # Process each doctor profile
        for url in tqdm(doctor_urls, desc="Scraping doctor profiles"):
            try:
                doctor_data = await scraper.scrape_doctor_page(url)
                if doctor_data:
                    doctors_data.append(doctor_data)
                    
                    # Save to database
                    session = Session()
                    try:
                        doctor = Doctor(
                            name=doctor_data.get('name', ''),
                            specialization=doctor_data.get('specialization', ''),
                            experience=doctor_data.get('experience', ''),
                            qualifications=doctor_data.get('qualifications', ''),
                            clinics=json.dumps(doctor_data.get('clinics', [])),
                            fees=doctor_data.get('fees', ''),
                            rating=doctor_data.get('rating', 0.0),
                            reviews_count=doctor_data.get('reviews_count', 0),
                            services=json.dumps(doctor_data.get('services', [])),
                            address=doctor_data.get('address', ''),
                            google_maps_link=doctor_data.get('google_maps_link', ''),
                            phone=doctor_data.get('phone', ''),
                            availability=json.dumps(doctor_data.get('availability', {})),
                            profile_url=doctor_data.get('profile_url', ''),
                            image_url=doctor_data.get('image_url', '')
                        )
                        session.add(doctor)
                        session.commit()
                    except Exception as e:
                        session.rollback()
                        print(f"Error saving to database: {e}")
                    finally:
                        session.close()
                    
                    # Add delay between requests
                    await asyncio.sleep(2)
            except Exception as e:
                print(f"Error scraping {url}: {e}")
        
        await browser.close()
    
    # Save to JSON
    with open('doctors_data.json', 'w', encoding='utf-8') as f:
        json.dump(doctors_data, f, ensure_ascii=False, indent=4)
    
    # Save to CSV
    df = pd.DataFrame(doctors_data)
    df.to_csv('doctors_data.csv', index=False)
    
    print(f"Scraped {len(doctors_data)} doctors. Data saved to JSON, CSV, and SQLite database.")

if __name__ == '__main__':
    asyncio.run(main())