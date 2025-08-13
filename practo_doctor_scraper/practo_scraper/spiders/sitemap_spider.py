import scrapy
from scrapy.spiders import SitemapSpider
import re

class DoctorSitemapSpider(SitemapSpider):
    name = 'doctor_sitemap'
    sitemap_urls = ['https://www.practo.com/profiles-sitemap.xml']
    
    # We'll filter for Bangalore doctors
    sitemap_rules = [
        ('/bangalore/', 'parse_doctor_profile')
    ]

    def parse_doctor_profile(self, response):
        # Delegate the actual parsing to doctor_spider.py
        from practo_scraper.spiders.doctor_spider import DoctorSpider
        doctor_spider = DoctorSpider()
        yield from doctor_spider.parse(response)