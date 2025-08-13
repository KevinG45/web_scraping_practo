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
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Wait for content to load
            await page.wait_for_timeout(3000)
            
            # Updated selectors based on current Practo structure
            possible_selectors = [
                'div.info-section a.doctor-name',
                'a[data-qa-id="doctor_name"]',
                'h2 a[href*="/doctor/"]',
                '.listing-item h2 a',
                'a[href*="/bangalore/doctor/"]'
            ]
            
            # Get the current page's doctor links
            for selector in possible_selectors:
                doctor_elements = await page.query_selector_all(selector)
                if doctor_elements:
                    print(f"Found {len(doctor_elements)} doctors using selector: {selector}")
                    for element in doctor_elements:
                        href = await element.get_attribute('href')
                        if href:
                            full_url = urljoin('https://www.practo.com', href)
                            doctor_urls.append(full_url)
                    break
            
            if not doctor_urls:
                # Fallback: extract any links that look like doctor profiles
                all_links = await page.query_selector_all('a[href*="/doctor/"]')
                for link in all_links:
                    href = await link.get_attribute('href')
                    if href and 'bangalore' in href:
                        full_url = urljoin('https://www.practo.com', href)
                        doctor_urls.append(full_url)
            
            # Check for pagination and follow next pages (limit to 5 pages)
            page_count = 1
            next_button = await page.query_selector('li.next a, .pagination .next a, a[aria-label="Next"]')
            
            while next_button and page_count < 5:  # Limit pagination
                next_href = await next_button.get_attribute('href')
                if not next_href:
                    break
                
                next_url = urljoin('https://www.practo.com', next_href)
                await page.goto(next_url, wait_until="networkidle", timeout=60000)
                await page.wait_for_timeout(3000)
                
                # Get the current page's doctor links
                for selector in possible_selectors:
                    doctor_elements = await page.query_selector_all(selector)
                    if doctor_elements:
                        for element in doctor_elements:
                            href = await element.get_attribute('href')
                            if href:
                                full_url = urljoin('https://www.practo.com', href)
                                doctor_urls.append(full_url)
                        break
                
                # Check for next page
                next_button = await page.query_selector('li.next a, .pagination .next a, a[aria-label="Next"]')
                page_count += 1
                
        except Exception as e:
            print(f"Error extracting doctor links: {e}")
        finally:
            await page.close()
        
        # Remove duplicates
        doctor_urls = list(set(doctor_urls))
        return doctor_urls

    async def scrape_doctor_page(self, url):
        """Scrape a single doctor's profile page with updated selectors"""
        page = await self.context.new_page()
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)  # Wait for dynamic content
            
            # Extract HTML content
            content = await page.content()
            soup = BeautifulSoup(content, 'lxml')
            
            # Basic info - try multiple selectors
            name = ''
            name_selectors = ['h1.doctor-name', 'h1[data-qa-id="doctor_name"]', '.doctor-profile h1', 'h1']
            for selector in name_selectors:
                name_elem = soup.select_one(selector)
                if name_elem and name_elem.text.strip():
                    name = name_elem.text.strip()
                    break
            
            # Specialization
            specialization = ''
            spec_selectors = [
                'div.specialization', 
                '[data-qa-id="doctor_specialization"]',
                '.doctor-specialization',
                '.specialization-text'
            ]
            for selector in spec_selectors:
                spec_elem = soup.select_one(selector)
                if spec_elem and spec_elem.text.strip():
                    specialization = spec_elem.text.strip()
                    break
            
            # Experience
            experience = ''
            exp_selectors = ['div.experience', '[data-qa-id="doctor_experience"]', '.experience-text']
            for selector in exp_selectors:
                experience_elem = soup.select_one(selector)
                if experience_elem:
                    experience_text = experience_elem.text
                    experience_match = re.search(r'(\d+)', experience_text)
                    if experience_match:
                        experience = experience_match.group(1)
                        break
            
            # Qualifications
            qualifications = ''
            qual_selectors = ['div.education', '[data-qa-id="doctor_qualifications"]', '.qualifications']
            for selector in qual_selectors:
                qualifications_elem = soup.select_one(selector)
                if qualifications_elem and qualifications_elem.text.strip():
                    qualifications = qualifications_elem.text.strip()
                    break
            
            # Clinics - try multiple approaches
            clinics = []
            
            # Method 1: Current structure
            clinic_selectors = [
                'div.c-profile--clinic',
                '.clinic-card',
                '.clinic-info',
                '[data-qa-id="clinic"]'
            ]
            
            for clinic_selector in clinic_selectors:
                clinic_cards = soup.select(clinic_selector)
                if clinic_cards:
                    for clinic in clinic_cards:
                        clinic_name_selectors = [
                            'h2.c-profile--clinic__name',
                            '.clinic-name',
                            'h3',
                            '.clinic-title'
                        ]
                        clinic_name = ''
                        for name_sel in clinic_name_selectors:
                            name_elem = clinic.select_one(name_sel)
                            if name_elem and name_elem.text.strip():
                                clinic_name = name_elem.text.strip()
                                break
                        
                        clinic_address_selectors = [
                            'div.c-profile--clinic__address',
                            '.clinic-address',
                            '.address'
                        ]
                        clinic_address = ''
                        for addr_sel in clinic_address_selectors:
                            addr_elem = clinic.select_one(addr_sel)
                            if addr_elem and addr_elem.text.strip():
                                clinic_address = addr_elem.text.strip()
                                break
                        
                        # Google Maps link
                        maps_link = ''
                        maps_selectors = ['a.map-directions', 'a[href*="maps.google"]', 'a[href*="goo.gl"]']
                        for maps_sel in maps_selectors:
                            maps_elem = clinic.select_one(maps_sel)
                            if maps_elem and maps_elem.has_attr('href'):
                                maps_link = maps_elem['href']
                                break
                        
                        if clinic_name or clinic_address:
                            clinics.append({
                                'name': clinic_name,
                                'address': clinic_address,
                                'google_maps_link': maps_link
                            })
                    break
            
            # If no clinics found, try to extract from scripts
            if not clinics:
                scripts = soup.select('script')
                for script in scripts:
                    if script.string and 'googleMapLink' in script.string:
                        try:
                            # Extract clinic data from JavaScript
                            clinic_data_match = re.search(r'clinics?\s*[:\=]\s*(\[.*?\])', script.string, re.DOTALL)
                            if clinic_data_match:
                                # This is a simplified extraction - you might need more sophisticated parsing
                                pass
                        except:
                            pass
            
            # Address and Google Maps link from first clinic
            address = clinics[0]['address'] if clinics else ''
            google_maps_link = clinics[0]['google_maps_link'] if clinics else ''
            
            # Fees
            fees = ''
            fee_selectors = [
                'span.consultation-fee', 
                '[data-qa-id="consultation_fee"]',
                '.fee-amount',
                '.consultation-price'
            ]
            for selector in fee_selectors:
                fees_elem = soup.select_one(selector)
                if fees_elem and fees_elem.text.strip():
                    fees = fees_elem.text.strip()
                    break
            
            # Rating and reviews
            rating = 0.0
            rating_selectors = [
                'span.common__star-rating__value',
                '[data-qa-id="doctor_rating"]',
                '.rating-value'
            ]
            for selector in rating_selectors:
                rating_elem = soup.select_one(selector)
                if rating_elem and rating_elem.text.strip():
                    try:
                        rating = float(rating_elem.text.strip())
                        break
                    except ValueError:
                        pass
            
            reviews_count = 0
            review_selectors = [
                'span.u-bold',
                '[data-qa-id="review_count"]',
                '.review-count'
            ]
            for selector in review_selectors:
                reviews_elem = soup.select_one(selector)
                if reviews_elem:
                    reviews_match = re.search(r'(\d+)', reviews_elem.text)
                    if reviews_match:
                        reviews_count = int(reviews_match.group(1))
                        break
            
            # Services
            services = []
            service_selectors = [
                'div.service-name',
                '[data-qa-id="service"]',
                '.service-item',
                '.treatment-list li'
            ]
            for selector in service_selectors:
                service_elems = soup.select(selector)
                if service_elems:
                    services = [elem.text.strip() for elem in service_elems if elem.text.strip()]
                    break
            
            # Phone
            phone = ''
            phone_selectors = [
                'span.u-no-margin',
                '[data-qa-id="phone_number"]',
                '.phone-number',
                'a[href^="tel:"]'
            ]
            for selector in phone_selectors:
                phone_elem = soup.select_one(selector)
                if phone_elem:
                    if phone_elem.has_attr('href'):
                        phone = phone_elem['href'].replace('tel:', '')
                    else:
                        phone = phone_elem.text.strip()
                    if phone:
                        break
            
            # Availability
            availability = {}
            day_selectors = ['div.c-profile--clinic__day', '.availability-day', '.schedule-day']
            for day_selector in day_selectors:
                day_elems = soup.select(day_selector)
                if day_elems:
                    for day_elem in day_elems:
                        day_title_selectors = [
                            'div.c-profile--clinic__day__title',
                            '.day-name',
                            '.day-title'
                        ]
                        day_name = ''
                        for title_sel in day_title_selectors:
                            day_title_elem = day_elem.select_one(title_sel)
                            if day_title_elem and day_title_elem.text.strip():
                                day_name = day_title_elem.text.strip()
                                break
                        
                        if day_name:
                            time_slot_selectors = [
                                'div.c-profile--clinic__day__timings',
                                '.time-slot',
                                '.timing'
                            ]
                            time_slots = []
                            for slot_sel in time_slot_selectors:
                                time_slot_elems = day_elem.select(slot_sel)
                                if time_slot_elems:
                                    time_slots = [elem.text.strip() for elem in time_slot_elems if elem.text.strip()]
                                    break
                            
                            availability[day_name] = time_slots
                    break
            
            # Image URL
            image_url = ''
            img_selectors = [
                'div.doctor-photo img',
                '.doctor-image img',
                '.profile-image img',
                'img[alt*="doctor" i]'
            ]
            for selector in img_selectors:
                image_elem = soup.select_one(selector)
                if image_elem and image_elem.has_attr('src'):
                    image_url = image_elem['src']
                    if image_url.startswith('//'):
                        image_url = 'https:' + image_url
                    elif image_url.startswith('/'):
                        image_url = 'https://www.practo.com' + image_url
                    break
            
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