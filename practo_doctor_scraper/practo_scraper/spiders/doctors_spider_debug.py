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
        # Debug: Save the page content to see structure
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        self.logger.info(f"Page title: {response.css('title::text').get()}")
        self.logger.info(f"Page length: {len(response.text)}")
        
        # Try multiple selectors for doctor links
        selectors_to_try = [
            'div.info-section a.doctor-name::attr(href)',
            'a[href*="/doctor/"]::attr(href)',
            'a[href*="/bangalore/doctor/"]::attr(href)', 
            '.listing-doctor-card a::attr(href)',
            '.doctor-card a::attr(href)',
            '.c-card a::attr(href)',
            '[data-qa-id*="doctor"] a::attr(href)'
        ]
        
        doctor_links = []
        for selector in selectors_to_try:
            links = response.css(selector).getall()
            if links:
                self.logger.info(f"Found {len(links)} links with selector: {selector}")
                doctor_links = links
                break
            else:
                self.logger.info(f"No links found with selector: {selector}")
        
        if not doctor_links:
            # Log some sample links to see what's available
            all_links = response.css('a::attr(href)').getall()[:20]
            self.logger.info(f"Sample links found: {all_links}")
            return
        
        # Process first 5 doctor links for testing
        for link in doctor_links[:5]:
            full_url = urljoin(response.url, link)
            self.logger.info(f"Requesting doctor profile: {full_url}")
            yield scrapy.Request(full_url, callback=self.parse)
            
        # Follow pagination if available
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse_doctor_listing)
    
    def parse(self, response):
        # Extract doctor information
        item = DoctorItem()
        
        # Basic info
        item['name'] = response.css('h1.doctor-name::text').get('').strip()
        if not item['name']:
            item['name'] = response.css('h1::text').get('').strip()
            
        item['specialization'] = response.css('div.specialization::text').get('').strip()
        
        # Experience
        experience = response.css('div.experience::text').get()
        if experience:
            experience_match = re.search(r'(\d+)', experience)
            item['experience'] = experience_match.group(1) if experience_match else ''
        else:
            item['experience'] = ''
        
        # Qualifications
        item['qualifications'] = response.css('div.education::text').get('').strip()
        
        # Clinics
        clinics = []
        clinic_cards = response.css('div.c-profile--clinic')
        for clinic in clinic_cards:
            clinic_name = clinic.css('h2.c-profile--clinic__name::text').get('').strip()
            clinic_address = clinic.css('div.c-profile--clinic__address::text').get('').strip()
            
            # Try to extract Google Maps link
            maps_link = clinic.css('a.map-directions::attr(href)').get('')
            if not maps_link:
                # Try to find it in the script
                maps_script = response.xpath('//script[contains(., "googleMapLink")]/text()').get()
                if maps_script:
                    match = re.search(r'"googleMapLink"\s*:\s*"([^"]+)"', maps_script)
                    if match:
                        maps_link = match.group(1)
            
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
        
        # Fees
        fees = response.css('span.consultation-fee::text').get()
        item['fees'] = fees.strip() if fees else ''
        
        # Rating and reviews
        rating_text = response.css('span.common__star-rating__value::text').get('')
        try:
            item['rating'] = float(rating_text.strip()) if rating_text.strip() else 0.0
        except ValueError:
            item['rating'] = 0.0
        
        reviews_text = response.css('span.u-bold::text').get('')
        if reviews_text:
            reviews_match = re.search(r'(\d+)', reviews_text)
            item['reviews_count'] = int(reviews_match.group(1)) if reviews_match else 0
        else:
            item['reviews_count'] = 0
        
        # Services
        services = response.css('div.service-name::text').getall()
        item['services'] = [service.strip() for service in services if service.strip()]
        
        # Phone
        item['phone'] = response.css('span.u-no-margin::text').get('').strip()
        
        # Availability
        availability = {}
        days = response.css('div.c-profile--clinic__day')
        for day in days:
            day_name = day.css('div.c-profile--clinic__day__title::text').get('').strip()
            time_slots = day.css('div.c-profile--clinic__day__timings::text').getall()
            availability[day_name] = [slot.strip() for slot in time_slots if slot.strip()]
        
        item['availability'] = availability
        
        # Profile URL
        item['profile_url'] = response.url
        
        # Image URL
        item['image_url'] = response.css('div.doctor-photo img::attr(src)').get('')
        
        self.logger.info(f"Extracted doctor: {item['name']}")
        yield item
