import asyncio
import json
import re
import random
import pandas as pd
from playwright.async_api import async_playwright
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import hashlib
import time

from practo_scraper.utils.database import Base, Doctor, create_tables

# Database settings
DATABASE_URI = 'sqlite:///doctors_data.db'
SCREENSHOTS_DIR = 'debug_screenshots'

class PractoScraper:
    def __init__(self):
        self.base_url = "https://www.practo.com/bangalore/doctors"
        self.doctors_data = []
        self.processed_urls = set()  # For deduplication
        
        # Create screenshots directory if it doesn't exist
        if not os.path.exists(SCREENSHOTS_DIR):
            os.makedirs(SCREENSHOTS_DIR)
        
    async def init_browser(self):
        self.playwright = await async_playwright().start()
        
        # Use a persistent context to maintain cookies/cache like a real browser
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
        )
        
        # Create a context with more realistic browser parameters
        self.context = await self.browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='Asia/Kolkata',
            permissions=['geolocation'],
            is_mobile=False
        )
        
        # Add webGL fingerprint evasion
        await self.context.add_init_script("""
        () => {
            // WebGL fingerprint randomization
            const getParameterProxyHandler = {
                apply: function(target, thisArg, args) {
                    const param = args[0];
                    if (param === 37445) {
                        return 'Intel Inc.';
                    } else if (param === 37446) {
                        return 'Intel Iris OpenGL Engine';
                    }
                    return Reflect.apply(target, thisArg, args);
                }
            };
            
            if (WebGLRenderingContext.prototype.getParameter) {
                WebGLRenderingContext.prototype.getParameter = new Proxy(
                    WebGLRenderingContext.prototype.getParameter, 
                    getParameterProxyHandler
                );
            }
        }
        """)
    
    async def close_browser(self):
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()
    
    def normalize_url(self, url):
        """Normalize URL to help with deduplication"""
        # Parse the URL
        parsed = urlparse(url)
        
        # Extract the doctor's name and specialty from the path
        path_parts = parsed.path.strip('/').split('/')
        
        # Generate a unique identifier based on doctor name and specialty
        if len(path_parts) >= 3 and path_parts[0] == 'bangalore' and path_parts[1] == 'doctor':
            doctor_id = path_parts[2]  # This usually contains the doctor's name and specialty
            return f"https://www.practo.com/bangalore/doctor/{doctor_id}"
        
        return url
    
    async def extract_doctor_links(self):
        print("Extracting doctor links...")
        page = await self.context.new_page()
        doctor_urls = []
        
        try:
            # Add human-like behavior
            await self._add_human_behavior(page)
            
            # Set a shorter timeout to avoid hanging
            await page.goto(self.base_url, timeout=20000)
            
            # Take a screenshot for debugging
            await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, 'listing_page.png'))
            
            # Wait for content to load
            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
            except:
                print("Timeout waiting for network idle, continuing anyway...")
            
            # More human-like behavior - scroll the page
            await self._scroll_page(page)
            
            print("Looking for doctor links...")
            
            # Get the page HTML for debugging
            html_content = await page.content()
            with open(os.path.join(SCREENSHOTS_DIR, 'listing_page.html'), 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Extract links directly from HTML to avoid complex selectors
            doctor_urls = await page.evaluate("""
            () => {
                const links = [];
                // Get all anchor tags
                const anchors = document.querySelectorAll('a');
                
                // Filter for doctor links
                for (const a of anchors) {
                    if (a.href && a.href.includes('/doctor/')) {
                        links.push(a.href);
                    }
                }
                return [...new Set(links)]; // Return unique links
            }
            """)
            
            if not doctor_urls:
                print("No doctor links found using JavaScript. Trying CSS selectors...")
                links = await page.query_selector_all('a')
                for link in links:
                    href = await link.get_attribute('href')
                    if href and '/doctor/' in href:
                        full_url = urljoin('https://www.practo.com', href)
                        doctor_urls.append(full_url)
            
            # Remove duplicates
            doctor_urls = list(set(doctor_urls))
            print(f"Found {len(doctor_urls)} unique doctor links")
            
            # Save the list of URLs for debugging
            with open('doctor_urls.json', 'w') as f:
                json.dump(doctor_urls, f, indent=4)
            
            # Limit to 5 for testing - change this number as needed
            doctor_urls = doctor_urls[:5]
            
        except Exception as e:
            print(f"Error extracting doctor links: {e}")
            
            # Take a screenshot to see what went wrong
            try:
                await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, 'error_listing_page.png'))
            except:
                pass
                
        finally:
            await page.close()
        
        return doctor_urls
    
    async def _scroll_page(self, page):
        """Scroll the page like a human would"""
        try:
            # Get page height
            page_height = await page.evaluate('document.body.scrollHeight')
            
            # Scroll down in chunks with random pauses
            view_port_height = await page.evaluate('window.innerHeight')
            current_position = 0
            
            while current_position < page_height:
                scroll_amount = random.randint(100, 800)
                current_position += scroll_amount
                await page.evaluate(f'window.scrollTo(0, {current_position})')
                await asyncio.sleep(random.uniform(0.5, 1.2))
        except Exception as e:
            print(f"Error during scrolling: {e}")
    
    async def _add_human_behavior(self, page):
        """Add random mouse movements and other human-like behavior"""
        try:
            # Random mouse movements
            for _ in range(random.randint(2, 5)):
                x = random.randint(100, 1000)
                y = random.randint(100, 600)
                await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.1, 0.5))
                
            # Occasionally click somewhere neutral
            if random.random() < 0.3:
                await page.mouse.click(random.randint(300, 500), random.randint(200, 400))
        except Exception as e:
            print(f"Error during human behavior simulation: {e}")
    
    async def scrape_doctor_page(self, url):
        # Skip if already processed (deduplication)
        normalized_url = self.normalize_url(url)
        if normalized_url in self.processed_urls:
            print(f"Skipping already processed URL: {url}")
            return None
        
        self.processed_urls.add(normalized_url)
        
        print(f"Scraping {url}")
        page = await self.context.new_page()
        
        # Generate a unique filename for this URL
        url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
        
        try:
            # Add random delay between requests to avoid detection
            delay = random.uniform(1, 3)
            await asyncio.sleep(delay)
            
            # Add human-like behavior
            await self._add_human_behavior(page)
            
            # Go to the page with a shorter timeout
            await page.goto(url, timeout=15000)
            
            # Take a screenshot immediately
            await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f'doctor_page_initial_{url_hash}.png'))
            
            # Try to wait for key elements but don't fail if timeout
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=5000)
                
                # Add small delay to let JavaScript run
                await asyncio.sleep(2)
                
                # Scroll down to trigger lazy loading
                await self._scroll_page(page)
            except:
                print("Timeout waiting for page load, continuing with what we have...")
            
            # Take a screenshot after waiting and scrolling
            await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f'doctor_page_{url_hash}.png'))
            
            # Extract HTML content for debugging
            html_content = await page.content()
            with open(os.path.join(SCREENSHOTS_DIR, f'doctor_page_{url_hash}.html'), 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Extract data using JavaScript to be more resilient
            doctor_data = await page.evaluate("""
            () => {
                // Helper function to get text content safely
                const getText = (selector) => {
                    const el = document.querySelector(selector);
                    return el ? el.textContent.trim() : '';
                };
                
                // Extract name with fallbacks
                let name = getText('h1.doctor-name, h1[data-qa-id="doctor-name"], .doctor-name');
                
                // If name not found, try any heading that might contain the doctor name
                if (!name) {
                    const h1s = document.querySelectorAll('h1');
                    for (const h1 of h1s) {
                        if (h1.textContent.includes('Dr.')) {
                            name = h1.textContent.trim();
                            break;
                        }
                    }
                }
                
                // Specialization
                const specialization = getText('div.specialization, [data-qa-id="doctor-specialization"], .uCard__headerInfo__speciality');
                
                // Experience
                const experienceText = getText('div.experience, [data-qa-id="doctor-experience"]');
                const experienceMatch = experienceText.match(/\\d+/);
                const experience = experienceMatch ? experienceMatch[0] : '';
                
                // Qualifications
                const qualifications = getText('div.education, [data-qa-id="doctor-qualification"], .uCard__headerInfo__details--qualification');
                
                // Fees
                const feesText = getText('span.consultation-fee, [data-qa-id="consultation_fee"], .uCard__price');
                const feesMatch = feesText.match(/₹\\s*(\\d+)/);
                const fees = feesMatch ? '₹' + feesMatch[1] : feesText;
                
                // Rating
                const ratingText = getText('span.common__star-rating__value, [data-qa-id="doctor-rating"], .rating-value');
                const ratingMatch = ratingText.match(/(\\d+\\.?\\d*)/);
                const rating = ratingMatch ? parseFloat(ratingMatch[0]) : 0;
                
                // Reviews
                const reviewsText = getText('span.u-bold, [data-qa-id="doctor-feedback-count"], .rating-count');
                const reviewsMatch = reviewsText.match(/(\\d+)/);
                const reviews_count = reviewsMatch ? parseInt(reviewsMatch[0]) : 0;
                
                // Services
                const serviceElements = document.querySelectorAll('div.service-name, [data-qa-id="doctor-service"], .uCard__service');
                const services = Array.from(serviceElements).map(el => el.textContent.trim());
                
                // Clinics
                const clinics = [];
                const clinicElements = document.querySelectorAll('div.c-profile--clinic, [data-qa-id="clinic-card"], .clinic-container');
                
                if (clinicElements.length > 0) {
                    for (const clinic of clinicElements) {
                        const name = getText.bind(null, 'h2.c-profile--clinic__name, [data-qa-id="clinic-name"], .clinic-name')(clinic);
                        const address = getText.bind(null, 'div.c-profile--clinic__address, [data-qa-id="clinic-address"], .clinic-address')(clinic);
                        const mapsLink = clinic.querySelector('a.map-directions, a[data-qa-id="directions"], a[href*="maps.google.com"]');
                        
                        clinics.push({
                            name: name || 'Clinic',
                            address: address || '',
                            google_maps_link: mapsLink ? mapsLink.href : ''
                        });
                    }
                } else {
                    // Try to extract address from anywhere on the page
                    const addressText = getText('.clinic-address, .address, [data-qa-id="clinic-address"]');
                    if (addressText) {
                        clinics.push({
                            name: 'Clinic',
                            address: addressText,
                            google_maps_link: ''
                        });
                    }
                }
                
                // Image URL
                const imgElement = document.querySelector('div.doctor-photo img, img[data-qa-id="doctor-image"], .doctor-photo img');
                const imageUrl = imgElement ? imgElement.src : '';
                
                // Phone
                const phone = getText('span.u-no-margin, [data-qa-id="doctor-phone"], .doctor-phone');
                
                // Availability (simplified)
                const availability = {};
                const dayElements = document.querySelectorAll('div.c-profile--clinic__day, [data-qa-id="clinic-day"], .clinic-day');
                
                for (const day of dayElements) {
                    const dayName = getText.bind(null, 'div.c-profile--clinic__day__title, [data-qa-id="day-title"], .day-title')(day);
                    const slots = Array.from(
                        day.querySelectorAll('div.c-profile--clinic__day__timings, [data-qa-id="time-slot"], .time-slot')
                    ).map(el => el.textContent.trim());
                    
                    if (dayName) {
                        availability[dayName] = slots;
                    }
                }
                
                // Address from first clinic
                const address = clinics.length > 0 ? clinics[0].address : '';
                const google_maps_link = clinics.length > 0 ? clinics[0].google_maps_link : '';
                
                return {
                    name,
                    specialization,
                    experience,
                    qualifications,
                    clinics,
                    fees,
                    rating,
                    reviews_count,
                    services,
                    address,
                    google_maps_link,
                    phone,
                    availability,
                    image_url: imageUrl
                };
            }
            """)
            
            # Add the URL to the data
            doctor_data['profile_url'] = url
            
            print(f"Extracted doctor: {doctor_data['name']}")
            return doctor_data
            
        except Exception as e:
            print(f"Error scraping doctor page {url}: {e}")
            # Take error screenshot
            try:
                await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f'error_doctor_page_{url_hash}.png'))
            except:
                pass
            return None
        finally:
            await page.close()
    
    async def run(self):
        await self.init_browser()
        
        try:
            # Get doctor URLs
            doctor_urls = await self.extract_doctor_links()
            
            # Process each URL with retry mechanism
            for url in tqdm(doctor_urls, desc="Scraping doctors"):
                # Try up to 3 times with exponential backoff
                for attempt in range(3):
                    try:
                        doctor_data = await self.scrape_doctor_page(url)
                        if doctor_data:
                            self.doctors_data.append(doctor_data)
                            # Successful - break the retry loop
                            break
                    except Exception as e:
                        wait_time = (2 ** attempt) * 3  # Exponential backoff: 3, 6, 12 seconds
                        print(f"Attempt {attempt+1} failed for {url}: {e}")
                        print(f"Waiting {wait_time} seconds before retrying...")
                        await asyncio.sleep(wait_time)
                        
                # Random delay between processing different doctors
                await asyncio.sleep(random.uniform(4, 7))
            
            # Save the data
            self.save_data()
            
        finally:
            await self.close_browser()
    
    def save_data(self):
        # Create the engine and tables
        engine = create_engine(DATABASE_URI)
        create_tables(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Save to database
            for doctor_data in self.doctors_data:
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
        
        # Save to JSON
        with open('doctors_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.doctors_data, f, ensure_ascii=False, indent=4)
        
        # Save to CSV
        df = pd.DataFrame(self.doctors_data)
        df.to_csv('doctors_data.csv', index=False)
        
        print(f"Scraped {len(self.doctors_data)} doctors. Data saved to JSON, CSV, and SQLite database.")

# Run the scraper
if __name__ == "__main__":
    scraper = PractoScraper()
    asyncio.run(scraper.run())