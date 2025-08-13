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
        # Extract doctor profile links
        doctor_links = response.css('div.info-section a.doctor-name::attr(href)').getall()
        
        for link in doctor_links:
            full_url = urljoin(response.url, link)
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
        item['specialization'] = response.css('div.specialization::text').get('').strip()
        
        # Experience
        experience = response.css('div.experience::text').get()
        if experience:
            item['experience'] = re.search(r'(\d+)', experience).group(1) if re.search(r'(\d+)', experience) else ''
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
        item['rating'] = float(rating_text) if rating_text.strip() else 0.0
        
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
        
        yield item