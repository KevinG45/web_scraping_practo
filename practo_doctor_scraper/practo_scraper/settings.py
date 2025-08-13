BOT_NAME = 'practo_scraper'

SPIDER_MODULES = ['practo_scraper.spiders']
NEWSPIDER_MODULE = 'practo_scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False  # Changed to False for testing

# Configure user agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 1  # Reduced for testing

# Configure delay for requests
DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = True

# Enable cookies
COOKIES_ENABLED = True

# Configure item pipelines
ITEM_PIPELINES = {
   'practo_scraper.pipelines.JsonPipeline': 300,
   'practo_scraper.pipelines.CSVPipeline': 400,
   'practo_scraper.pipelines.DatabasePipeline': 500,
}

# Disable HTTP caching for testing
HTTPCACHE_ENABLED = False

# Output files
JSON_FILE = 'doctors_data.json'
CSV_FILE = 'doctors_data.csv'

# Database settings
DATABASE_URI = 'sqlite:///doctors_data.db'

# Playwright settings for JavaScript rendering
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Playwright specific settings
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": False,  # Set to True for production
    "timeout": 30000,
}

# Enable AutoThrottle for better rate limiting
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "timeout": 60 * 1000,  # 60 seconds timeout
}

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 60 * 1000  # 60 seconds timeout

# Additional request retry middleware
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Add logging level
LOG_LEVEL = 'INFO'