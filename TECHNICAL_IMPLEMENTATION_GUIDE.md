# 🔧 Technical Implementation Guide

This document provides specific technical guidance for implementing the **Bangalore Doctors Execution Plan** using the existing codebase structure.

---

## 📁 Project Structure Mapping

```
practo_doctor_scraper/
├── 📋 EXECUTION_PLAN.md              # Complete execution plan (this document references)
├── 🔧 TECHNICAL_IMPLEMENTATION.md    # Technical implementation guide (this document)
├── requirements.txt                   # Dependencies
├── scrapy.cfg                        # Scrapy configuration
├── 
├── practo_scraper/                   # Scrapy-based scraper
│   ├── items.py                      # ✅ Data schema definitions
│   ├── settings.py                   # ⚙️ Scrapy configuration
│   ├── pipelines.py                  # 🔄 Data processing pipelines
│   ├── middlewares.py                # 🛡️ Anti-detection middleware
│   │
│   ├── spiders/
│   │   ├── doctors_spider.py         # 🕷️ Main doctor scraping spider
│   │   └── sitemap_spider.py         # 🗺️ URL discovery spider
│   │
│   └── utils/
│       ├── database.py               # 💾 SQLite database models
│       └── export.py                 # 📤 Data export utilities
│
├── playwright_scraper/               # Playwright-based dynamic scraper
│   ├── main.py                       # 🎮 Main execution script
│   └── doctor_scraper.py             # 🎭 Playwright page interaction
│
└── implementation_scripts/           # 🚀 Ready-to-run scripts
    ├── bangalore_complete_scraper.py # Complete implementation
    ├── specialty_scraper.py          # Specialty-specific scraping
    └── data_validator.py             # Quality validation
```

---

## 🎯 Implementation Roadmap

### Phase 1: Foundation Setup ✅ (Current State)
- [x] **Scrapy Framework**: Configured with items, pipelines, settings
- [x] **Playwright Integration**: Basic page rendering and data extraction
- [x] **Database Schema**: SQLite with all required fields
- [x] **Export Functionality**: JSON, CSV, and database export
- [x] **Google Maps Integration**: Link generation utility

### Phase 2: Speciality Coverage Enhancement 🔄 (Next Steps)
**File**: `practo_scraper/spiders/specialty_spider.py` (to be created)

```python
# Comprehensive specialty coverage
BANGALORE_SPECIALITIES = [
    "Cardiologist", "Chiropractor", "Dentist", "Dermatologist", 
    "Dietitian/Nutritionist", "Gastroenterologist", "Bariatric-surgeon", 
    "Gynecologist", "Infertility-Specialist", "Neurologist", "Neurosurgeon", 
    "Ophthalmologist", "Orthopedist", "Pediatrician", "Physiotherapist", 
    "Psychiatrist", "Pulmonologist", "Rheumatologist", "Urologist"
]

class SpecialtyDoctorSpider(scrapy.Spider):
    name = 'specialty_spider'
    
    def start_requests(self):
        for specialty in BANGALORE_SPECIALITIES:
            url = f"https://www.practo.com/search/doctors?results_type=doctor&q=[{{%22word%22:%22{specialty}%22,%22autocompleted%22:true,%22category%22:%22subspeciality%22}}]&city=Bangalore"
            yield scrapy.Request(url, callback=self.parse_specialty_listing, 
                               meta={'specialty': specialty})
```

### Phase 3: Enhanced Data Extraction 🔄 (Improvement Required)
**File**: `practo_scraper/spiders/doctors_spider.py` (update required)

**Current State**: Basic field extraction
**Required Enhancement**: Complete field coverage as per execution plan

```python
# Enhanced field extraction (to be added)
def parse(self, response):
    item = DoctorItem()
    
    # Enhanced extraction logic
    item['name'] = self.extract_doctor_name(response)
    item['specialization'] = self.extract_specialization(response)
    item['experience'] = self.extract_experience(response)
    item['qualifications'] = self.extract_qualifications(response)
    item['clinics'] = self.extract_clinic_details(response)
    item['fees'] = self.extract_consultation_fee(response)
    item['rating'] = self.extract_rating(response)
    item['reviews_count'] = self.extract_reviews_count(response)
    item['services'] = self.extract_services(response)
    item['address'] = self.extract_address(response)
    item['phone'] = self.extract_phone(response)
    item['availability'] = self.extract_availability(response)
    item['profile_url'] = response.url
    item['image_url'] = self.extract_image_url(response)
    
    # Generate Google Maps link
    item['google_maps_link'] = self.generate_maps_link(
        item['name'], item['address']
    )
```

### Phase 4: Robust Error Handling 🔄 (Enhancement Required)
**File**: `practo_scraper/middlewares.py` (update required)

**Current State**: Basic middleware structure
**Required Enhancement**: Comprehensive anti-detection and retry logic

```python
# Enhanced middleware (to be implemented)
class EnhancedDownloaderMiddleware:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) Firefox/120.0'
        ]
        self.retry_delays = [2, 5, 10, 20]
    
    def process_request(self, request, spider):
        # Implement user agent rotation
        # Add random delays
        # Handle rate limiting
        pass
```

### Phase 5: Scalability & Performance 🔄 (Optimization Required)
**File**: `practo_scraper/settings.py` (update required)

**Current State**: Basic settings
**Required Enhancement**: Production-ready configuration

```python
# Enhanced settings for large-scale scraping
ENHANCED_SETTINGS = {
    # Concurrency control
    'CONCURRENT_REQUESTS': 8,
    'CONCURRENT_REQUESTS_PER_DOMAIN': 4,
    
    # Request delays
    'DOWNLOAD_DELAY': 3,
    'RANDOMIZE_DOWNLOAD_DELAY': True,
    
    # Auto-throttling
    'AUTOTHROTTLE_ENABLED': True,
    'AUTOTHROTTLE_START_DELAY': 1,
    'AUTOTHROTTLE_MAX_DELAY': 10,
    'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
    
    # Memory optimization
    'MEMDEBUG_ENABLED': True,
    'MEMUSAGE_ENABLED': True,
    'MEMUSAGE_LIMIT_MB': 2048,
    
    # Enhanced pipelines
    'ITEM_PIPELINES': {
        'practo_scraper.pipelines.ValidationPipeline': 200,
        'practo_scraper.pipelines.DeduplicationPipeline': 300,
        'practo_scraper.pipelines.JsonPipeline': 400,
        'practo_scraper.pipelines.CSVPipeline': 500,
        'practo_scraper.pipelines.DatabasePipeline': 600,
    }
}
```

---

## 🛠️ Ready-to-Use Implementation Scripts

### Script 1: Complete Bangalore Scraper
**File**: `implementation_scripts/bangalore_complete_scraper.py` (to be created)

```python
#!/usr/bin/env python3
"""
Complete Bangalore Doctors Scraper
Implements the full execution plan in a single script
"""

import asyncio
import pandas as pd
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import sys
import os

# Add project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class BangaloreDoctorsScraper:
    def __init__(self):
        self.specialties = [
            "Cardiologist", "Dermatologist", "Dentist", "Gynecologist",
            "Pediatrician", "Orthopedist", "Neurologist", "Ophthalmologist",
            # ... complete list from execution plan
        ]
        self.total_doctors = 0
        self.scraped_data = []
    
    def run_complete_scraping(self):
        """Execute the complete scraping process"""
        print("🚀 Starting Complete Bangalore Doctors Scraping")
        print(f"📊 Target: {len(self.specialties)} specialties")
        
        # Phase 1: URL Discovery
        self.discover_doctor_urls()
        
        # Phase 2: Data Extraction
        self.extract_doctor_data()
        
        # Phase 3: Data Processing
        self.process_and_export()
        
        print(f"✅ Scraping completed: {self.total_doctors} doctors extracted")

if __name__ == '__main__':
    scraper = BangaloreDoctorsScraper()
    scraper.run_complete_scraping()
```

### Script 2: Specialty-Specific Scraper
**File**: `implementation_scripts/specialty_scraper.py` (to be created)

```python
#!/usr/bin/env python3
"""
Specialty-specific scraper for targeted extraction
Usage: python specialty_scraper.py --specialty "Cardiologist"
"""

import argparse
import asyncio
from playwright.async_api import async_playwright
import pandas as pd

class SpecialtyScraper:
    def __init__(self, specialty_name):
        self.specialty = specialty_name
        self.doctors_data = []
    
    async def scrape_specialty(self):
        """Scrape all doctors for a specific specialty"""
        print(f"🔍 Scraping {self.specialty} specialists in Bangalore...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Navigate to specialty page
            url = f"https://www.practo.com/bangalore/{self.specialty.lower()}"
            await page.goto(url)
            
            # Handle infinite scroll
            await self.scroll_and_extract(page)
            
            await browser.close()
        
        # Export results
        self.export_to_csv()
    
    async def scroll_and_extract(self, page):
        """Handle infinite scroll and extract doctor data"""
        # Implementation as per execution plan
        pass
    
    def export_to_csv(self):
        """Export scraped data to CSV"""
        df = pd.DataFrame(self.doctors_data)
        filename = f"bangalore_{self.specialty.lower()}_doctors.csv"
        df.to_csv(filename, index=False)
        print(f"📄 Exported {len(df)} doctors to {filename}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--specialty', required=True, 
                       help='Medical specialty to scrape')
    args = parser.parse_args()
    
    scraper = SpecialtyScraper(args.specialty)
    asyncio.run(scraper.scrape_specialty())
```

### Script 3: Data Validator
**File**: `implementation_scripts/data_validator.py` (to be created)

```python
#!/usr/bin/env python3
"""
Data quality validation and reporting
"""

import pandas as pd
import json
from typing import Dict, List
import re

class DataValidator:
    def __init__(self, csv_file: str):
        self.df = pd.read_csv(csv_file)
        self.validation_results = {}
    
    def validate_completeness(self) -> Dict:
        """Validate data completeness"""
        mandatory_fields = ['doctor_name', 'speciality', 'clinic_address']
        results = {}
        
        for field in mandatory_fields:
            completion_rate = self.df[field].notna().sum() / len(self.df)
            results[field] = {
                'completion_rate': completion_rate,
                'missing_count': self.df[field].isna().sum(),
                'status': 'PASS' if completion_rate > 0.95 else 'FAIL'
            }
        
        return results
    
    def validate_data_formats(self) -> Dict:
        """Validate data format correctness"""
        results = {}
        
        # Phone number validation
        phone_pattern = r'^\+91-\d{10}$'
        valid_phones = self.df['contact_phone'].str.match(phone_pattern, na=False).sum()
        results['phone_format'] = {
            'valid_count': valid_phones,
            'total_count': self.df['contact_phone'].notna().sum(),
            'validity_rate': valid_phones / max(1, self.df['contact_phone'].notna().sum())
        }
        
        # Rating validation
        valid_ratings = self.df['rating'].between(0, 5, inclusive='both').sum()
        results['rating_range'] = {
            'valid_count': valid_ratings,
            'total_count': self.df['rating'].notna().sum(),
            'validity_rate': valid_ratings / max(1, self.df['rating'].notna().sum())
        }
        
        return results
    
    def check_duplicates(self) -> Dict:
        """Check for duplicate doctor entries"""
        # Duplicate detection based on name + clinic address
        duplicate_mask = self.df.duplicated(subset=['doctor_name', 'clinic_address'], keep=False)
        duplicate_count = duplicate_mask.sum()
        
        return {
            'total_records': len(self.df),
            'duplicate_count': duplicate_count,
            'duplication_rate': duplicate_count / len(self.df),
            'unique_doctors': len(self.df) - duplicate_count
        }
    
    def generate_quality_report(self) -> Dict:
        """Generate comprehensive quality report"""
        report = {
            'dataset_overview': {
                'total_records': len(self.df),
                'total_specialties': self.df['speciality'].nunique(),
                'specialty_distribution': self.df['speciality'].value_counts().to_dict()
            },
            'completeness': self.validate_completeness(),
            'format_validation': self.validate_data_formats(),
            'duplication_analysis': self.check_duplicates(),
            'google_maps_coverage': {
                'total_links': self.df['google_maps_link'].notna().sum(),
                'coverage_rate': self.df['google_maps_link'].notna().sum() / len(self.df)
            }
        }
        
        return report
    
    def save_report(self, output_file: str = 'data_quality_report.json'):
        """Save quality report to JSON file"""
        report = self.generate_quality_report()
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=4, default=str)
        
        print(f"📊 Quality report saved to {output_file}")
        return report

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python data_validator.py <csv_file>")
        sys.exit(1)
    
    validator = DataValidator(sys.argv[1])
    report = validator.save_report()
    
    # Print summary
    print("\n📈 Data Quality Summary:")
    print(f"Total Records: {report['dataset_overview']['total_records']}")
    print(f"Specialties: {report['dataset_overview']['total_specialties']}")
    print(f"Duplication Rate: {report['duplication_analysis']['duplication_rate']:.2%}")
    print(f"Google Maps Coverage: {report['google_maps_coverage']['coverage_rate']:.2%}")
```

---

## 🎮 Execution Commands

### Complete Scraping Process
```bash
# Set up environment
cd practo_doctor_scraper
pip install -r requirements.txt
playwright install chromium

# Run complete scraping
python implementation_scripts/bangalore_complete_scraper.py

# Validate results
python implementation_scripts/data_validator.py bangalore_doctors_complete.csv
```

### Specialty-Specific Scraping
```bash
# Scrape specific specialty
python implementation_scripts/specialty_scraper.py --specialty "Cardiologist"
python implementation_scripts/specialty_scraper.py --specialty "Dermatologist"

# Merge specialty files
python -c "
import pandas as pd
import glob

csv_files = glob.glob('bangalore_*_doctors.csv')
combined_df = pd.concat([pd.read_csv(f) for f in csv_files])
combined_df.to_csv('bangalore_doctors_complete.csv', index=False)
print(f'Combined {len(csv_files)} files into bangalore_doctors_complete.csv')
"
```

### Using Existing Scrapy Infrastructure
```bash
# Run enhanced Scrapy spider
cd practo_doctor_scraper
scrapy crawl doctor_spider -o bangalore_doctors.csv -s USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'

# Run with custom settings
scrapy crawl doctor_spider -s DOWNLOAD_DELAY=5 -s CONCURRENT_REQUESTS=4
```

---

## 🔧 Configuration Management

### Environment Variables
```bash
# Create .env file
cat > .env << EOF
PRACTO_BASE_URL=https://www.practo.com
SCRAPING_DELAY=3
MAX_CONCURRENT_REQUESTS=8
OUTPUT_DIRECTORY=./output
DATABASE_URL=sqlite:///doctors_data.db
ENABLE_PROXY_ROTATION=false
LOG_LEVEL=INFO
EOF
```

### Runtime Configuration
```python
# config.py (to be created)
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PRACTO_BASE_URL = os.getenv('PRACTO_BASE_URL', 'https://www.practo.com')
    SCRAPING_DELAY = int(os.getenv('SCRAPING_DELAY', 3))
    MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', 8))
    OUTPUT_DIRECTORY = os.getenv('OUTPUT_DIRECTORY', './output')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///doctors_data.db')
    
    # Specialty configuration
    BANGALORE_SPECIALTIES = [
        "Cardiologist", "Dermatologist", "Dentist", "Gynecologist",
        "Pediatrician", "Orthopedist", "Neurologist", "Ophthalmologist",
        "Psychiatrist", "Gastroenterologist", "Urologist", "ENT",
        "Pulmonologist", "Endocrinologist", "Rheumatologist",
        "Oncologist", "Radiologist", "Anesthesiologist",
        "Emergency-Medicine", "General-Physician"
    ]
    
    # Quality thresholds
    MIN_COMPLETION_RATE = 0.95
    MAX_DUPLICATION_RATE = 0.01
    MIN_DOCTORS_PER_SPECIALTY = 50
```

---

## 📊 Monitoring & Debugging

### Real-time Progress Tracking
```python
# progress_monitor.py (to be created)
import json
import time
from datetime import datetime

class ProgressMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {
            'doctors_scraped': 0,
            'specialties_completed': 0,
            'success_rate': 0.0,
            'current_specialty': '',
            'errors_encountered': 0,
            'estimated_completion': None
        }
    
    def update_progress(self, specialty: str, doctors_count: int, errors: int = 0):
        """Update progress metrics"""
        self.metrics['current_specialty'] = specialty
        self.metrics['doctors_scraped'] += doctors_count
        self.metrics['errors_encountered'] += errors
        
        if doctors_count > 0:
            self.metrics['specialties_completed'] += 1
        
        # Calculate success rate
        total_attempts = self.metrics['doctors_scraped'] + self.metrics['errors_encountered']
        if total_attempts > 0:
            self.metrics['success_rate'] = self.metrics['doctors_scraped'] / total_attempts
        
        # Estimate completion time
        elapsed = time.time() - self.start_time
        if self.metrics['specialties_completed'] > 0:
            avg_time_per_specialty = elapsed / self.metrics['specialties_completed']
            remaining_specialties = 20 - self.metrics['specialties_completed']
            self.metrics['estimated_completion'] = remaining_specialties * avg_time_per_specialty
        
        self.save_progress()
        self.print_status()
    
    def save_progress(self):
        """Save progress to file"""
        with open('scraping_progress.json', 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def print_status(self):
        """Print current status"""
        print(f"\n📊 Progress Update - {datetime.now().strftime('%H:%M:%S')}")
        print(f"Current Specialty: {self.metrics['current_specialty']}")
        print(f"Doctors Scraped: {self.metrics['doctors_scraped']}")
        print(f"Specialties Completed: {self.metrics['specialties_completed']}/20")
        print(f"Success Rate: {self.metrics['success_rate']:.2%}")
        if self.metrics['estimated_completion']:
            eta_minutes = int(self.metrics['estimated_completion'] / 60)
            print(f"ETA: {eta_minutes} minutes")
        print("-" * 50)
```

### Error Handling & Recovery
```python
# error_handler.py (to be created)
import json
import traceback
from datetime import datetime

class ErrorHandler:
    def __init__(self):
        self.error_log = []
        self.failed_urls = []
    
    def log_error(self, error_type: str, url: str, error_message: str, 
                  stack_trace: str = None):
        """Log error with details"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'url': url,
            'message': error_message,
            'stack_trace': stack_trace or traceback.format_exc()
        }
        
        self.error_log.append(error_entry)
        self.failed_urls.append(url)
        
        # Save to file immediately
        self.save_error_log()
    
    def save_error_log(self):
        """Save error log to file"""
        with open('error_log.json', 'w') as f:
            json.dump(self.error_log, f, indent=2)
        
        # Also save failed URLs for retry
        with open('failed_urls.txt', 'w') as f:
            f.write('\n'.join(self.failed_urls))
    
    def get_retry_urls(self) -> list:
        """Get list of URLs that need retry"""
        return list(set(self.failed_urls))  # Remove duplicates
```

---

## 🚀 Quick Start Guide

### 1. Initial Setup (5 minutes)
```bash
# Clone and setup
cd web_scraping_practo/practo_doctor_scraper
pip install -r requirements.txt
playwright install chromium

# Verify setup
python test_implementation.py
```

### 2. Run Sample Scraping (15 minutes)
```bash
# Test with single specialty
python implementation_scripts/specialty_scraper.py --specialty "Cardiologist"

# Validate sample data
python implementation_scripts/data_validator.py bangalore_cardiologist_doctors.csv
```

### 3. Full Production Run (4-6 hours)
```bash
# Complete scraping
python implementation_scripts/bangalore_complete_scraper.py

# Final validation
python implementation_scripts/data_validator.py bangalore_doctors_complete.csv
```

---

## 📋 Success Checklist

- [ ] **Environment Setup**: All dependencies installed and verified
- [ ] **Specialty Coverage**: All 20 specialties configured and tested
- [ ] **Data Schema**: Complete field extraction implemented
- [ ] **Error Handling**: Robust retry and logging mechanisms
- [ ] **Anti-Detection**: User agent rotation and delay management
- [ ] **Quality Validation**: Automated quality checks implemented
- [ ] **Export Pipeline**: CSV generation with all required fields
- [ ] **Google Maps**: Link generation for all clinic addresses
- [ ] **Monitoring**: Progress tracking and error logging
- [ ] **Documentation**: Complete setup and usage instructions

---

**Implementation Status**: 🔄 **Foundation Complete - Ready for Enhancement**  
**Next Phase**: Implement enhanced specialty coverage and robust error handling  
**Estimated Time to Complete**: 1-2 weeks with existing foundation

This technical guide provides a clear roadmap for implementing the complete execution plan using the existing codebase structure. The foundation is solid and ready for the enhancements outlined in the execution plan.