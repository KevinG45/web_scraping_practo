BOT_NAME = 'practo_scraper'

SPIDER_MODULES = ['practo_scraper.spiders']
NEWSPIDER_MODULE = 'practo_scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure user agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Configure maximum concurrent requests (matching error output)
CONCURRENT_REQUESTS = 1

# Configure delay for requests (matching error output)
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True

# Enable cookies
COOKIES_ENABLED = True

# Configure autothrottle (matching error output)
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 10

# Retry settings (matching error output)
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Fix the deprecated request fingerprinter warning
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'

# Set twisted reactor (matching error output)
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

# Configure item pipelines
ITEM_PIPELINES = {
   'practo_scraper.pipelines.JsonPipeline': 300,
   'practo_scraper.pipelines.CSVPipeline': 400,
   'practo_scraper.pipelines.DatabasePipeline': 500,
}

# Enable and configure HTTP caching
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Output files
JSON_FILE = 'doctors_data.json'
CSV_FILE = 'doctors_data.csv'

# Database settings
DATABASE_URI = 'sqlite:///doctors_data.db'