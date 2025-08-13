from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from scrapy.utils.reactor import install_reactor

# Install the required reactor BEFORE importing other Scrapy components
install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')

from practo_scraper.spiders.doctors_spider import DoctorSpider

if __name__ == '__main__':
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(DoctorSpider)
    process.start()