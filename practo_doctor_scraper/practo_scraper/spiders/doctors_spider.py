import scrapy
import json
import re
from urllib.parse import urljoin
from ..items import DoctorItem

class DoctorSpider(scrapy.Spider):
    name = 'doctor_spider'
    allowed_domains = ['practo.com']
    start_urls = ['https://www.practo.com/bangalore/doctors']
    
    def start_requests(self):
        # Starting with the main doctors page for Bangalore
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse_doctor_listing)
            
    def parse_doctor_listing(self, response):
        # Extract doctor profile links using multiple selectors
        link_selectors = [
            'div.info-section a.doctor-name::attr(href)',
            'a[href*="/doctor/"]::attr(href)',
            '.doctor-card a::attr(href)',
            '.listing-item a::attr(href)'
        ]
        
        doctor_links = self.get_text_by_selectors_all(response, link_selectors)
        
        self.logger.info(f"Found {len(doctor_links)} doctor links using multiple selectors")
        
        for link in doctor_links:
            full_url = urljoin(response.url, link)
            yield scrapy.Request(full_url, callback=self.parse)
            
        # Follow pagination if available
        next_page_selectors = [
            'li.next a::attr(href)',
            '.pagination .next::attr(href)',
            'a[aria-label="Next"]::attr(href)'
        ]
        
        next_page = self.get_text_by_selectors(response, next_page_selectors)
        if next_page:
            yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse_doctor_listing)
    
    def parse(self, response):
        # Extract doctor information
        item = DoctorItem()
        
        # Basic info - using multiple selectors for robustness
        name_selectors = [
            'h1.doctor-name::text',
            'h1[data-qa-id="doctor_name"]::text',
            '.doctor-info h1::text',
            '.profile-header h1::text'
        ]
        item['name'] = self.get_text_by_selectors(response, name_selectors) or ''
        
        specialization_selectors = [
            'div.specialization::text',
            '.doctor-speciality::text',
            '[data-qa-id="doctor_speciality"]::text',
            '.speciality::text'
        ]
        item['specialization'] = self.get_text_by_selectors(response, specialization_selectors) or ''
        
        # Experience
        experience_selectors = [
            'div.experience::text',
            '.experience-years::text',
            '[data-qa-id="doctor_experience"]::text'
        ]
        experience = self.get_text_by_selectors(response, experience_selectors)
        if experience:
            experience_match = re.search(r'(\d+)', experience)
            item['experience'] = experience_match.group(1) if experience_match else ''
        else:
            item['experience'] = ''
        
        # Qualifications
        qualification_selectors = [
            'div.education::text',
            '.qualifications::text',
            '[data-qa-id="doctor_education"]::text'
        ]
        item['qualifications'] = self.get_text_by_selectors(response, qualification_selectors) or ''
        
        # Clinics with improved selectors
        clinics = []
        clinic_selectors = [
            'div.c-profile--clinic',
            '.clinic-card',
            '.practice-location'
        ]
        
        clinic_cards = []
        for selector in clinic_selectors:
            try:
                cards = response.css(selector)
                if cards:
                    clinic_cards = cards
                    break
            except Exception as e:
                self.logger.warning(f"Clinic selector error with '{selector}': {e}")
                continue
        
        for clinic in clinic_cards:
            clinic_name_selectors = [
                'h2.c-profile--clinic__name::text',
                '.clinic-name::text',
                'h3::text'
            ]
            clinic_name = self.get_text_by_selectors(clinic, clinic_name_selectors) or ''
            
            clinic_address_selectors = [
                'div.c-profile--clinic__address::text',
                '.clinic-address::text',
                '.address::text'
            ]
            clinic_address = self.get_text_by_selectors(clinic, clinic_address_selectors) or ''
            
            # Try to extract Google Maps link
            maps_selectors = [
                'a.map-directions::attr(href)',
                'a[href*="maps.google"]::attr(href)',
                'a[href*="maps"]::attr(href)'
            ]
            maps_link = self.get_text_by_selectors(clinic, maps_selectors) or ''
            
            if not maps_link:
                # Try to find it in the script
                maps_script = response.xpath('//script[contains(., "googleMapLink")]/text()').get()
                if maps_script:
                    match = re.search(r'"googleMapLink"\s*:\s*"([^"]+)"', maps_script)
                    if match:
                        maps_link = match.group(1)
            
            if clinic_name or clinic_address:  # Only add if we have some data
                clinics.append({
                    'name': clinic_name,
                    'address': clinic_address,
                    'google_maps_link': maps_link
                })
        
        item['clinics'] = clinics
        
        # Address and Google Maps link from first clinic
        if clinics:
            item['address'] = clinics[0].get('address', '')
            item['google_maps_link'] = clinics[0].get('google_maps_link', '')
        else:
            item['address'] = ''
            item['google_maps_link'] = ''
        
        # Fees with multiple selectors
        fee_selectors = [
            'span.consultation-fee::text',
            '.fee-amount::text',
            '[data-qa-id="consultation_fee"]::text',
            '.price::text'
        ]
        fees = self.get_text_by_selectors(response, fee_selectors)
        item['fees'] = fees if fees else ''
        
        # Rating and reviews with improved selectors
        rating_selectors = [
            'span.common__star-rating__value::text',
            '.rating-value::text',
            '[data-qa-id="doctor_rating"]::text'
        ]
        rating_text = self.get_text_by_selectors(response, rating_selectors) or ''
        try:
            item['rating'] = float(rating_text.strip()) if rating_text.strip() else 0.0
        except ValueError:
            item['rating'] = 0.0
        
        reviews_selectors = [
            'span.u-bold::text',
            '.review-count::text',
            '[data-qa-id="review_count"]::text'
        ]
        reviews_text = self.get_text_by_selectors(response, reviews_selectors) or ''
        if reviews_text:
            reviews_match = re.search(r'(\d+)', reviews_text)
            item['reviews_count'] = int(reviews_match.group(1)) if reviews_match else 0
        else:
            item['reviews_count'] = 0
        
        # Services with multiple selectors
        service_selectors = [
            'div.service-name::text',
            '.service-list li::text',
            '.services::text'
        ]
        services = self.get_text_by_selectors_all(response, service_selectors)
        item['services'] = services
        
        # Phone with multiple selectors
        phone_selectors = [
            'span.u-no-margin::text',
            '.phone-number::text',
            '[data-qa-id="phone_number"]::text',
            'a[href^="tel:"]::attr(href)'
        ]
        phone = self.get_text_by_selectors(response, phone_selectors)
        if phone and phone.startswith('tel:'):
            phone = phone[4:]  # Remove 'tel:' prefix
        item['phone'] = phone if phone else ''
        
        # Availability with improved selectors
        availability = {}
        day_selectors = [
            'div.c-profile--clinic__day',
            '.availability-day',
            '.schedule-day'
        ]
        
        days = []
        for selector in day_selectors:
            try:
                day_elements = response.css(selector)
                if day_elements:
                    days = day_elements
                    break
            except Exception as e:
                self.logger.warning(f"Day selector error with '{selector}': {e}")
                continue
        
        for day in days:
            day_name_selectors = [
                'div.c-profile--clinic__day__title::text',
                '.day-name::text',
                'h4::text'
            ]
            day_name = self.get_text_by_selectors(day, day_name_selectors) or ''
            
            timing_selectors = [
                'div.c-profile--clinic__day__timings::text',
                '.time-slots::text',
                '.timings::text'
            ]
            time_slots = self.get_text_by_selectors_all(day, timing_selectors)
            
            if day_name:
                availability[day_name] = time_slots
        
        item['availability'] = availability
        
        # Profile URL
        item['profile_url'] = response.url
        
        # Image URL - using multiple selectors for robustness
        img_selectors = [
            'div.doctor-photo img::attr(src)',
            'img.doctor-image::attr(src)',
            '.doctor-avatar img::attr(src)',
            '.profile-photo img::attr(src)',
            'img[alt*="doctor"]::attr(src)',  # Fixed: removed case-insensitive flag
            'img[alt*="Doctor"]::attr(src)'   # Added capitalized version instead
        ]
        
        image_url = self.get_text_by_selectors(response, img_selectors)
        item['image_url'] = image_url if image_url else ''
        
        yield item
    
    def get_text_by_selectors(self, response, selectors):
        """
        Try multiple CSS selectors and return the first successful result.
        Handles potential CSS selector syntax errors gracefully.
        """
        for selector in selectors:
            try:
                result = response.css(selector).get()
                if result and result.strip():
                    return result.strip()
            except Exception as e:
                # Handle CSS selector syntax errors
                self.logger.warning(f"CSS selector error with '{selector}': {e}")
                continue
        return None
    
    def get_text_by_selectors_all(self, response, selectors):
        """
        Try multiple CSS selectors and return all results from the first successful selector.
        """
        for selector in selectors:
            try:
                results = response.css(selector).getall()
                if results:
                    return [r.strip() for r in results if r.strip()]
            except Exception as e:
                # Handle CSS selector syntax errors
                self.logger.warning(f"CSS selector error with '{selector}': {e}")
                continue
        return []