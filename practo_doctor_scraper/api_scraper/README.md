# EasyAPI Practo Doctor Scraper

This module provides a modern, API-based approach to scraping Practo doctor data using the EasyAPI service.

## Features

- **Fast and Reliable**: Uses API calls instead of web scraping for better performance and reliability
- **Rate Limited**: Built-in rate limiting to respect API limits
- **Comprehensive Data**: Extracts all doctor information including clinics, ratings, availability, etc.
- **Multiple Export Formats**: Supports JSON, CSV, and database storage
- **Specialization Filtering**: Filter doctors by medical specialization
- **Error Handling**: Robust error handling and retry logic
- **Mock Testing**: Built-in mock API for development and testing

## Quick Start

### Using the Standalone Script

```bash
# Basic usage - scrape 50 doctors from Bangalore
python run_api_scraper.py

# Test with mock data
python run_api_scraper.py --test --limit 10

# Filter by specialization
python run_api_scraper.py --specialization "Cardiologist" --limit 20

# Custom city and export format
python run_api_scraper.py --city mumbai --export json --limit 30

# Use custom API key
python run_api_scraper.py --api-key "your-api-key-here"
```

### Using as a Module

```python
from api_scraper.main import PractoAPIScraper
from api_scraper.mock_api import patch_api_client_for_testing

# For testing with mock data
patch_api_client_for_testing()

# Initialize scraper
scraper = PractoAPIScraper(api_key="easyapi/practo-doctor-scraper")

# Scrape doctors
doctors = scraper.scrape_doctors(city="bangalore", limit=100)

# Run full scrape with all features
scraper.run_full_scrape(
    city="bangalore",
    limit=50,
    save_to_db=True,
    export_formats="all"
)
```

## Configuration

### API Key

Set your EasyAPI key in several ways:

1. **Environment Variable**: `export EASYAPI_KEY="your-key"`
2. **Command Line**: `--api-key "your-key"`
3. **Code**: `PractoAPIScraper(api_key="your-key")`

### Rate Limiting

The scraper includes built-in rate limiting:
- 1 second delay between requests
- Automatic retry on rate limit errors
- Configurable timeout and retry counts

## Data Structure

The scraper extracts comprehensive doctor information:

```json
{
  "name": "Dr. John Smith",
  "specialization": "Cardiologist",
  "experience": "15 years",
  "qualifications": "MBBS, MD, DM",
  "clinics": [
    {
      "name": "Heart Care Clinic",
      "address": "#123, MG Road, Bangalore",
      "google_maps_link": "https://maps.google.com/..."
    }
  ],
  "fees": "₹800",
  "rating": 4.5,
  "reviews_count": 150,
  "services": ["Consultation", "ECG", "Heart Surgery"],
  "phone": "+91 9876543210",
  "availability": {
    "Monday": ["09:00 AM - 12:00 PM", "02:00 PM - 06:00 PM"],
    "Tuesday": ["09:00 AM - 12:00 PM"]
  },
  "profile_url": "https://www.practo.com/bangalore/doctor/dr-john-smith",
  "image_url": "https://images.practo.com/doctors/dr-john-smith.jpg"
}
```

## Command Line Options

```bash
usage: run_api_scraper.py [-h] [--city CITY] [--limit LIMIT] [--api-key API_KEY] 
                         [--specialization SPECIALIZATION] [--no-db] 
                         [--export {json,csv,all}] [--test] [--verbose]

optional arguments:
  --city CITY                    City to scrape (default: bangalore)
  --limit LIMIT                  Maximum number of doctors (default: 50)
  --api-key API_KEY             EasyAPI key
  --specialization SPECIALIZATION Filter by medical specialization
  --no-db                       Skip database save
  --export {json,csv,all}       Export format (default: all)
  --test                        Run in test mode with mock data
  --verbose, -v                 Verbose logging
```

## Architecture

### Components

1. **Client** (`client.py`): HTTP client for EasyAPI communication
2. **Mapper** (`mapper.py`): Data transformation from API to database format
3. **Config** (`config.py`): Configuration management
4. **Main** (`main.py`): Main scraper class and CLI interface
5. **Mock API** (`mock_api.py`): Testing infrastructure with sample data

### API Endpoints

The scraper supports multiple EasyAPI endpoints:

- `/practo/search/doctors` - Search doctors by city and filters
- `/practo/doctor/{id}` - Get detailed doctor information
- `/practo/doctors/city/{city}` - Get all doctors in a city
- `/practo/doctors/specialization/{spec}` - Get doctors by specialization

### Error Handling

- **Rate Limiting**: Automatic backoff on 429 errors
- **Network Errors**: Retry logic with exponential backoff
- **Data Validation**: Graceful handling of missing/invalid data
- **Logging**: Comprehensive logging for debugging

## Testing

Run the test suite:

```bash
python test_api_scraper.py
```

Test specific functionality:

```bash
# Test with mock data
python run_api_scraper.py --test --limit 5

# Test specialization filtering
python run_api_scraper.py --test --specialization "Cardiologist"
```

## Integration

### With Existing Scrapers

The API scraper integrates seamlessly with existing scraping infrastructure:

```python
# In run_scrapers.py
from api_scraper.main import PractoAPIScraper

def run_all_scrapers():
    # Run API scraper
    api_scraper = PractoAPIScraper()
    api_scraper.run_full_scrape(limit=100)
    
    # Run other scrapers...
```

### Database Compatibility

Uses the same database schema as existing scrapers for seamless data integration.

## Performance

- **Speed**: ~1-2 seconds per doctor (including rate limiting)
- **Reliability**: No browser dependencies or JavaScript execution
- **Scalability**: Easy to parallelize and scale
- **Resource Usage**: Minimal memory and CPU footprint

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure valid EasyAPI key is set
2. **Rate Limiting**: Increase delays if getting rate limited
3. **Network Timeouts**: Check internet connection and API availability

### Debug Mode

Enable verbose logging:

```bash
python run_api_scraper.py --verbose
```

### Mock Testing

Always test with mock data first:

```bash
python run_api_scraper.py --test
```

## Comparison with Web Scraping

| Feature | API Scraper | Web Scraper |
|---------|-------------|-------------|
| Speed | Fast (1-2s per doctor) | Slower (5-10s per doctor) |
| Reliability | High | Medium (site changes) |
| Rate Limits | Built-in handling | Manual implementation |
| Browser Required | No | Yes (Playwright/Selenium) |
| JavaScript | Not needed | Often required |
| Maintenance | Low | High (site changes) |
| Data Quality | Consistent | Variable |

## License

This implementation is designed to work with the EasyAPI Practo Doctor Scraper service. Ensure you have proper API access and follow the service's terms of use.