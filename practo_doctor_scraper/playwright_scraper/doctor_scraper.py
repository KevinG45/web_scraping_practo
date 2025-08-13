import asyncio
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class DoctorScraper:
    def __init__(self, browser, context):
        self.browser = browser
        self.context = context
    
    async def extract_doctor_links(self, url):
        """Extract doctor profile links from the listing page"""
        doctor_urls = []
        page = await self.context.new_page()
        
        try:
            await page.goto(url, wait_until="networkidle")
            
            # Get the current page's doctor links
            doctor_elements = await page.query_selector_all('div.info-section a.doctor-name')
            for element in doctor_elements:
                href = await element.get_attribute('href')
                if href:
                    full_url = urljoin('https://www.practo.com', href)
                    doctor_urls.append(full_url)
            
            # Check for pagination and follow next pages
            next_button = await page.query_selector('li.next a')
            while next_button:
                next_href = await next_button.get_attribute('href')
                if not next_href:
                    break
                
                next_url = urljoin('https://www.practo.com', next_href)
                await page.goto(next_url, wait_until="networkidle")
                
                # Get the current page's doctor links
                doctor_elements = await page.query_selector_all('div.info-section a.doctor-name')
                for element in doctor_elements:
                    href = await element.get_attribute('href')
                    if href:
                        full_url = urljoin('https://www.practo.com', href)
                        doctor_urls.append(full_url)
                
                # Check for next page
                next_button = await page.query_selector('li.next a')
        except Exception as e:
            print(f"Error extracting doctor links: {e}")
        finally:
            await page.close()
        
        return doctor_urls

    async def scrape_doctor_page(self, url):
        """Scrape a single doctor's profile page"""
        page = await self.context.new_page()
        
        try:
            await page.goto(url, wait_until="networkidle")
            
            # Extract HTML content
            content = await page.content()
            soup = BeautifulSoup(content, 'lxml')
            
            # Basic info
            name = soup.select_one('h1.doctor-name')
            name = name.text.strip() if name else ''
            
            specialization = soup.select_one('div.specialization')
            specialization = specialization.text.strip() if specialization else ''
            
            # Experience
            experience_elem = soup.select_one('div.experience')
            experience = ''
            if experience_elem:
                experience_text = experience_elem.text
                experience_match = re.search(r'(\d+)', experience_text)
                if experience_match:
                    experience = experience_match.group(1)
            
            # Qualifications
            qualifications_elem = soup.select_one('div.education')
            qualifications = qualifications_elem.text.strip() if qualifications_elem else ''
            
            # Clinics
            clinics = []
            clinic_cards = soup.select('div.c-profile--clinic')
            for clinic in clinic_cards:
                clinic_name_elem = clinic.select_one('h2.c-profile--clinic__name')
                clinic_name = clinic_name_elem.text.strip() if clinic_name_elem else ''
                
                clinic_address_elem = clinic.select_one('div.c-profile--clinic__address')
                clinic_address = clinic_address_elem.text.strip() if clinic_address_elem else ''
                
                # Google Maps link
                maps_link_elem = clinic.select_one('a.map-directions')
                maps_link = maps_link_elem['href'] if maps_link_elem and maps_link_elem.has_attr('href') else ''
                
                if not maps_link:
                    # Try to extract from script
                    scripts = soup.select('script')
                    for script in scripts:
                        if script.string and 'googleMapLink' in script.string:
                            match = re.search(r'"googleMapLink"\s*:\s*"([^"]+)"', script.string)
                            if match:
                                maps_link = match.group(1)
                                break
                
                clinics.append({
                    'name': clinic_name,
                    'address': clinic_address,
                    'google_maps_link': maps_link
                })
            
            # Address and Google Maps link from first clinic
            address = clinics[0]['address'] if clinics else ''
            google_maps_link = clinics[0]['google_maps_link'] if clinics else ''
            
            # Fees
            fees_elem = soup.select_one('span.consultation-fee')
            fees = fees_elem.text.strip() if fees_elem else ''
            
            # Rating and reviews
            rating_elem = soup.select_one('span.common__star-rating__value')
            rating = 0.0
            if rating_elem and rating_elem.text.strip():
                try:
                    rating = float(rating_elem.text.strip())
                except ValueError:
                    pass
            
            reviews_elem = soup.select_one('span.u-bold')
            reviews_count = 0
            if reviews_elem:
                reviews_match = re.search(r'(\d+)', reviews_elem.text)
                if reviews_match:
                    reviews_count = int(reviews_match.group(1))
            
            # Services
            services = []
            service_elems = soup.select('div.service-name')
            for service_elem in service_elems:
                services.append(service_elem.text.strip())
            
            # Phone
            phone_elem = soup.select_one('span.u-no-margin')
            phone = phone_elem.text.strip() if phone_elem else ''
            
            # Availability
            availability = {}
            day_elems = soup.select('div.c-profile--clinic__day')
            for day_elem in day_elems:
                day_title_elem = day_elem.select_one('div.c-profile--clinic__day__title')
                day_name = day_title_elem.text.strip() if day_title_elem else ''
                
                time_slot_elems = day_elem.select('div.c-profile--clinic__day__timings')
                time_slots = [elem.text.strip() for elem in time_slot_elems if elem.text.strip()]
                
                if day_name:
                    availability[day_name] = time_slots
            
            # Image URL
            image_elem = soup.select_one('div.doctor-photo img')
            image_url = image_elem['src'] if image_elem and image_elem.has_attr('src') else ''
            
            doctor_data = {
                'name': name,
                'specialization': specialization,
                'experience': experience,
                'qualifications': qualifications,
                'clinics': clinics,
                'fees': fees,
                'rating': rating,
                'reviews_count': reviews_count,
                'services': services,
                'address': address,
                'google_maps_link': google_maps_link,
                'phone': phone,
                'availability': availability,
                'profile_url': url,
                'image_url': image_url
            }
            
            return doctor_data
            
        except Exception as e:
            print(f"Error scraping doctor page {url}: {e}")
            return None
        finally:
            await page.close()