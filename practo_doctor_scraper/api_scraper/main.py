"""
Main API-based scraper for Practo doctors using EasyAPI
"""

import json
import logging
import sys
import os
from typing import List, Dict, Any

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .client import PractoAPIClient
from .mapper import DoctorDataMapper
from .config import APIConfig

# Try to import database dependencies, fallback if not available
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from practo_scraper.utils.database import Base, Doctor, create_tables
    DB_AVAILABLE = True
except ImportError:
    print("⚠️ Database dependencies not available. Database functionality disabled.")
    DB_AVAILABLE = False

# Try to import export utilities, fallback if not available
try:
    from practo_scraper.utils.export import export_to_json, export_to_csv
    EXPORT_UTILS_AVAILABLE = True
except ImportError:
    print("⚠️ Export utilities not available. Using basic export functionality.")
    EXPORT_UTILS_AVAILABLE = False

# Try to import tqdm, fallback to basic iteration
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, desc="Processing"):
        print(f"{desc}...")
        return iterable

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATABASE_URI = 'sqlite:///doctors_data_api.db'

class PractoAPIScraper:
    """Main scraper class using EasyAPI for Practo doctor data"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the API scraper
        
        Args:
            api_key: Optional API key override
        """
        self.client = PractoAPIClient(api_key)
        self.mapper = DoctorDataMapper()
        
        # Setup database if available
        if DB_AVAILABLE:
            self.engine = create_engine(DATABASE_URI)
            create_tables(self.engine)
            self.Session = sessionmaker(bind=self.engine)
        else:
            self.Session = None
        
        self.doctors_data = []
    
    def scrape_doctors(self, city: str = "bangalore", limit: int = 100, 
                      specialization: str = None) -> List[Dict[str, Any]]:
        """
        Scrape doctors using the API
        
        Args:
            city: City to search in
            limit: Maximum number of doctors to retrieve
            specialization: Optional specialization filter
            
        Returns:
            List of mapped doctor data
        """
        logger.info(f"Starting API scraping for {city} (limit: {limit})")
        
        try:
            # Get doctors from API
            if specialization:
                logger.info(f"Searching for {specialization} doctors in {city}")
                api_doctors = self.client.get_doctors_by_specialization(
                    specialization=specialization, 
                    city=city
                )
            else:
                logger.info(f"Searching for all doctors in {city}")
                api_doctors = self.client.get_all_bangalore_doctors(limit=limit)
            
            logger.info(f"Retrieved {len(api_doctors)} doctors from API")
            
            # Map API data to database format
            mapped_doctors = self.mapper.batch_map_doctors(api_doctors)
            logger.info(f"Mapped {len(mapped_doctors)} doctors to database format")
            
            self.doctors_data.extend(mapped_doctors)
            return mapped_doctors
            
        except Exception as e:
            logger.error(f"Error during API scraping: {e}")
            return []
    
    def save_to_database(self, doctors: List[Dict[str, Any]]) -> int:
        """
        Save doctors data to database
        
        Args:
            doctors: List of doctor data dictionaries
            
        Returns:
            Number of doctors saved successfully
        """
        if not DB_AVAILABLE or not self.Session:
            logger.warning("Database not available, skipping database save")
            return 0
        
        saved_count = 0
        session = self.Session()
        
        try:
            for doctor_data in tqdm(doctors, desc="Saving to database"):
                try:
                    doctor = Doctor(
                        name=doctor_data.get('name', ''),
                        specialization=doctor_data.get('specialization', ''),
                        experience=doctor_data.get('experience', ''),
                        qualifications=doctor_data.get('qualifications', ''),
                        clinics=json.dumps(doctor_data.get('clinics', [])),
                        fees=doctor_data.get('fees', ''),
                        rating=doctor_data.get('rating', 0.0),
                        reviews_count=doctor_data.get('reviews_count', 0),
                        services=json.dumps(doctor_data.get('services', [])),
                        address=doctor_data.get('address', ''),
                        google_maps_link=doctor_data.get('google_maps_link', ''),
                        phone=doctor_data.get('phone', ''),
                        availability=json.dumps(doctor_data.get('availability', {})),
                        profile_url=doctor_data.get('profile_url', ''),
                        image_url=doctor_data.get('image_url', '')
                    )
                    session.add(doctor)
                    session.commit()
                    saved_count += 1
                    
                except Exception as e:
                    session.rollback()
                    logger.error(f"Error saving doctor to database: {e}")
                    
        finally:
            session.close()
        
        logger.info(f"Saved {saved_count} doctors to database")
        return saved_count
    
    def _basic_export_to_json(self, data: List[Dict], filename: str):
        """Basic JSON export without external dependencies"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _basic_export_to_csv(self, data: List[Dict], filename: str):
        """Basic CSV export without external dependencies"""
        import csv
        
        if not data:
            return
        
        fieldnames = data[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                # Convert complex objects to strings for CSV
                csv_row = {}
                for key, value in row.items():
                    if isinstance(value, (dict, list)):
                        csv_row[key] = json.dumps(value)
                    else:
                        csv_row[key] = str(value)
                writer.writerow(csv_row)
    
    def export_data(self, output_format: str = "all"):
        """
        Export scraped data to various formats
        
        Args:
            output_format: Format to export ("json", "csv", "all")
        """
        if not self.doctors_data:
            logger.warning("No data to export")
            return
        
        try:
            if output_format in ["json", "all"]:
                json_file = "doctors_data_api.json"
                if EXPORT_UTILS_AVAILABLE:
                    export_to_json(self.doctors_data, json_file)
                else:
                    self._basic_export_to_json(self.doctors_data, json_file)
                logger.info(f"Exported data to {json_file}")
            
            if output_format in ["csv", "all"]:
                csv_file = "doctors_data_api.csv"
                if EXPORT_UTILS_AVAILABLE:
                    export_to_csv(self.doctors_data, csv_file)
                else:
                    self._basic_export_to_csv(self.doctors_data, csv_file)
                logger.info(f"Exported data to {csv_file}")
                
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
    
    def run_full_scrape(self, city: str = "bangalore", limit: int = 100, 
                       save_to_db: bool = True, export_formats: str = "all"):
        """
        Run a complete scraping operation
        
        Args:
            city: City to scrape
            limit: Maximum number of doctors
            save_to_db: Whether to save to database
            export_formats: Export formats ("json", "csv", "all")
        """
        logger.info("=" * 60)
        logger.info(f"Starting full API scrape for {city}")
        logger.info("=" * 60)
        
        # Scrape doctors
        doctors = self.scrape_doctors(city=city, limit=limit)
        
        if not doctors:
            logger.warning("No doctors found")
            return
        
        # Save to database
        if save_to_db and DB_AVAILABLE:
            self.save_to_database(doctors)
        elif save_to_db:
            logger.warning("Database save requested but not available")
        
        # Export data
        self.export_data(export_formats)
        
        logger.info("=" * 60)
        logger.info(f"Scraping completed! Total doctors: {len(self.doctors_data)}")
        logger.info("=" * 60)

def main():
    """Main function to run the API scraper"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Practo Doctor API Scraper")
    parser.add_argument("--city", default="bangalore", help="City to scrape")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of doctors")
    parser.add_argument("--api-key", help="EasyAPI key override")
    parser.add_argument("--specialization", help="Filter by specialization")
    parser.add_argument("--no-db", action="store_true", help="Skip database save")
    parser.add_argument("--export", choices=["json", "csv", "all"], default="all", 
                       help="Export format")
    
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = PractoAPIScraper(api_key=args.api_key)
    
    # Run scraping
    scraper.run_full_scrape(
        city=args.city,
        limit=args.limit,
        save_to_db=not args.no_db,
        export_formats=args.export
    )

if __name__ == "__main__":
    main()