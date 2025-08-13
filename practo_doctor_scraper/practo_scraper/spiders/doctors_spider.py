import scrapy
import json
import re
from urllib.parse import urljoin
from ..items import DoctorItem

class DoctorSpider(scrapy.Spider):
    name = 'doctor_spider'
    allowed_domains = ['practo.com']
    start_urls = ['https://www.practo.com/bangalore/doctors']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    def start_requests(self):
        # Starting with the main doctors page for Bangalore
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse_doctor_listing)
            
    def parse_doctor_listing(self, response):
        # Extract doctor profile links - try multiple selectors
        doctor_links = []
        
        # Try different possible selectors for doctor links
        selectors_to_try = [
            'div.info-section a.doctor-name::attr(href)',
            'a[data-qa-id="doctor_name"]::attr(href)',
            'h2 a[href*="/doctor/"]::attr(href)',
            '.listing-item h2 a::attr(href)',
            'a[href*="/bangalore/doctor/"]::attr(href)'
        ]
        
        for selector in selectors_to_try:
            doctor_links = response.css(selector).getall()
            if doctor_links:
                self.logger.info(f"Found {len(doctor_links)} doctor links using selector: {selector}")
                break
        
        if not doctor_links:
            # Fallback: look for any doctor profile links
            all_links = response.xpath('//a[contains(@href, "/doctor/")]/@href').getall()
            doctor_links = [link for link in all_links if 'bangalore' in link.lower()]
            self.logger.info(f"Found {len(doctor_links)} doctor links using fallback method")
        
        for link in doctor_links:
            full_url = urljoin(response.url, link)
            yield scrapy.Request(full_url, callback=self.parse)
            
        # Follow pagination if available - try multiple selectors
        pagination_selectors = [
            'li.next a::attr(href)',
            '.pagination .next a::attr(href)',
            'a[aria-label="Next"]::attr(href)'
        ]
        
        for selector in pagination_selectors:
            next_page = response.css(selector).get()
            if next_page:
                yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse_doctor_listing)
                break
    
    def parse(self, response):
        # Extract doctor information with updated selectors
        item = DoctorItem()
        
        # Basic info - try multiple selectors for each field
        # Name
        name_selectors = [
            'h1.doctor-name::text',
            'h1[data-qa-id="doctor_name"]::text',
            '.doctor-profile h1::text',
            'h1::text'
        ]
        item['name'] = self.get_text_by_selectors(response, name_selectors)
        
        # Specialization
        spec_selectors = [
            'div.specialization::text',
            '[data-qa-id="doctor_specialization"]::text',
            '.doctor-specialization::text',
            '.specialization-text::text'
        ]
        item['specialization'] = self.get_text_by_selectors(response, spec_selectors)
        
        # Experience
        exp_selectors = [
            'div.experience::text',
            '[data-qa-id="doctor_experience"]::text',
            '.experience-text::text'
        ]
        experience_text = self.get_text_by_selectors(response, exp_selectors)
        if experience_text:
            experience_match = re.search(r'(\d+)', experience_text)
            item['experience'] = experience_match.group(1) if experience_match else ''
        else:
            item['experience'] = ''
        
        # Qualifications
        qual_selectors = [
            'div.education::text',
            '[data-qa-id="doctor_qualifications"]::text',
            '.qualifications::text'
        ]
        item['qualifications'] = self.get_text_by_selectors(response, qual_selectors)
        
        # Clinics - try multiple approaches
        clinics = []
        clinic_selectors = [
            'div.c-profile--clinic',
            '.clinic-card',
            '.clinic-info',
            '[data-qa-id="clinic"]'
        ]
        
        clinic_elements = []
        for selector in clinic_selectors:
            clinic_elements = response.css(selector)
            if clinic_elements:
                break
        
        for clinic in clinic_elements:
            # Clinic name
            clinic_name_selectors = [
                'h2.c-profile--clinic__name::text',
                '.clinic-name::text',
                'h3::text',
                '.clinic-title::text'
            ]
            clinic_name = self.get_text_by_selectors_from_element(clinic, clinic_name_selectors)
            
            # Clinic address
            clinic_address_selectors = [
                'div.c-profile--clinic__address::text',
                '.clinic-address::text',
                '.address::text'
            ]
            clinic_address = self.get_text_by_selectors_from_element(clinic, clinic_address_selectors)
            
            # Google Maps link
            maps_selectors = [
                'a.map-directions::attr(href)',
                'a[href*="maps.google"]::attr(href)',
                'a[href*="goo.gl"]::attr(href)'
            ]
            maps_link = self.get_text_by_selectors_from_element(clinic, maps_selectors)
            
            if clinic_name or clinic_address:
                clinics.append({
                    'name': clinic_name,
                    'address': clinic_address,
                    'google_maps_link': maps_link or ''
                })
        
        item['clinics'] = clinics
        
        # Address and Google Maps link from first clinic
        if clinics:
            item['address'] = clinics[0].get('address', '')
            item['google_maps_link'] = clinics[0].get('google_maps_link', '')
        else:
            item['address'] = ''
            item['google_maps_link'] = ''
        
        # Fees
        fee_selectors = [
            'span.consultation-fee::text',
            '[data-qa-id="consultation_fee"]::text',
            '.fee-amount::text',
            '.consultation-price::text'
        ]
        item['fees'] = self.get_text_by_selectors(response, fee_selectors)
        
        # Rating and reviews
        rating_selectors = [
            'span.common__star-rating__value::text',
            '[data-qa-id="doctor_rating"]::text',
            '.rating-value::text'
        ]
        rating_text = self.get_text_by_selectors(response, rating_selectors)
        try:
            item['rating'] = float(rating_text) if rating_text else 0.0
        except ValueError:
            item['rating'] = 0.0
        
        review_selectors = [
            'span.u-bold::text',
            '[data-qa-id="review_count"]::text',
            '.review-count::text'
        ]
        reviews_text = self.get_text_by_selectors(response, review_selectors)
        if reviews_text:
            reviews_match = re.search(r'(\d+)', reviews_text)
            item['reviews_count'] = int(reviews_match.group(1)) if reviews_match else 0
        else:
            item['reviews_count'] = 0
        
        # Services
        service_selectors = [
            'div.service-name::text',
            '[data-qa-id="service"]::text',
            '.service-item::text',
            '.treatment-list li::text'
        ]
        services = []
        for selector in service_selectors:
            services = response.css(selector).getall()
            if services:
                break
        item['services'] = [service.strip() for service in services if service.strip()]
        
        # Phone
        phone_selectors = [
            'span.u-no-margin::text',
            '[data-qa-id="phone_number"]::text',
            '.phone-number::text',
            'a[href^="tel:"]::attr(href)'
        ]
        phone = self.get_text_by_selectors(response, phone_selectors)
        if phone and phone.startswith('tel:'):
            phone = phone.replace('tel:', '')
        item['phone'] = phone
        
        # Availability
        availability = {}
        day_selectors = [
            'div.c-profile--clinic__day',
            '.availability-day',
            '.schedule-day'
        ]
        
        day_elements = []
        for selector in day_selectors:
            day_elements = response.css(selector)
            if day_elements:
                break
        
        for day in day_elements:
            day_title_selectors = [
                'div.c-profile--clinic__day__title::text',
                '.day-name::text',
                '.day-title::text'
            ]
            day_name = self.get_text_by_selectors_from_element(day, day_title_selectors)
            
            if day_name:
                time_slot_selectors = [
                    'div.c-profile--clinic__day__timings::text',
                    '.time-slot::text',
                    '.timing::text'
                ]
                time_slots = []
                for selector in time_slot_selectors:
                    time_slots = day.css(selector).getall()
                    if time_slots:
                        break
                availability[day_name] = [slot.strip() for slot in time_slots if slot.strip()]
        
        item['availability'] = availability
        
        # Profile URL
        item['profile_url'] = response.url
        
        # Image URL
        img_selectors = [
            'div.doctor-photo img::attr(src)',
            '.doctor-image img::attr(src)',
            '.profile-image img::attr(src)',
            'img[alt*="doctor" i]::attr(src)'
        ]
        image_url = self.get_text_by_selectors(response, img_selectors)
        if image_url:
            if image_url.startswith('//'):
                image_url = 'https:' + image_url
            elif image_url.startswith('/'):
                image_url = 'https://www.practo.com' + image_url
        item['image_url'] = image_url or ''
        
        yield item
    
    def get_text_by_selectors(self, response, selectors):
        """Try multiple CSS selectors and return the first non-empty result"""
        for selector in selectors:
            result = response.css(selector).get()
            if result and result.strip():
                return result.strip()
        return ''
    
    def get_text_by_selectors_from_element(self, element, selectors):
        """Try multiple CSS selectors on a specific element and return the first non-empty result"""
        for selector in selectors:
            result = element.css(selector).get()
            if result and result.strip():
                return result.strip()
        return ''