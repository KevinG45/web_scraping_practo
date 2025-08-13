#!/usr/bin/env python3
"""
Standalone runner for the EasyAPI Practo Doctor Scraper
"""

import sys
import os
import argparse

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

def main():
    parser = argparse.ArgumentParser(description="EasyAPI Practo Doctor Scraper")
    parser.add_argument("--city", default="bangalore", help="City to scrape (default: bangalore)")
    parser.add_argument("--limit", type=int, default=50, help="Maximum number of doctors (default: 50)")
    parser.add_argument("--api-key", help="EasyAPI key (defaults to easyapi/practo-doctor-scraper)")
    parser.add_argument("--specialization", help="Filter by medical specialization")
    parser.add_argument("--no-db", action="store_true", help="Skip database save")
    parser.add_argument("--export", choices=["json", "csv", "all"], default="all", help="Export format")
    parser.add_argument("--test", action="store_true", help="Run in test mode with mock data")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging level
    import logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        from api_scraper.main import PractoAPIScraper
        
        # If test mode, use mock API
        if args.test:
            from api_scraper.mock_api import patch_api_client_for_testing
            print("🧪 Running in test mode with mock data")
            patch_api_client_for_testing()
        
        # Initialize scraper
        scraper = PractoAPIScraper(api_key=args.api_key)
        
        # Configure scraping parameters
        kwargs = {
            "city": args.city,
            "limit": args.limit,
            "save_to_db": not args.no_db,
            "export_formats": args.export
        }
        
        # Add specialization if provided
        if args.specialization:
            print(f"🔍 Filtering by specialization: {args.specialization}")
            # For specialization filtering, we'll override the scrape_doctors call
            doctors = scraper.scrape_doctors(
                city=args.city,
                limit=args.limit,
                specialization=args.specialization
            )
            
            if doctors and not args.no_db:
                scraper.save_to_database(doctors)
            
            scraper.export_data(args.export)
            
            print(f"✅ Completed! Scraped {len(doctors)} {args.specialization} doctors in {args.city}")
        else:
            # Run full scrape
            scraper.run_full_scrape(**kwargs)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Scraping interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())