import json
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scrapy.exporters import JsonItemExporter, CsvItemExporter

# Fixed import paths
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from practo_scraper.utils.database import Base, Doctor, create_tables
from practo_scraper.settings import DATABASE_URI, JSON_FILE, CSV_FILE

class JsonPipeline:
    def __init__(self):
        self.file = None
        self.exporter = None

    def open_spider(self, spider):
        self.file = open(JSON_FILE, 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class CSVPipeline:
    def __init__(self):
        self.file = None
        self.exporter = None

    def open_spider(self, spider):
        self.file = open(CSV_FILE, 'wb')
        self.exporter = CsvItemExporter(self.file, encoding='utf-8')
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class DatabasePipeline:
    def __init__(self):
        self.engine = create_engine(DATABASE_URI)
        create_tables(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def process_item(self, item, spider):
        session = self.Session()
        
        # Safely serialize JSON fields with better error handling
        try:
            clinics_data = item.get('clinics', [])
            if isinstance(clinics_data, list):
                clinics_json = json.dumps(clinics_data, ensure_ascii=False)
            else:
                clinics_json = json.dumps([clinics_data] if clinics_data else [], ensure_ascii=False)
        except (TypeError, ValueError) as e:
            spider.logger.warning(f"Error serializing clinics data: {e}")
            clinics_json = '[]'
            
        try:
            services_data = item.get('services', [])
            if isinstance(services_data, list):
                services_json = json.dumps(services_data, ensure_ascii=False)
            else:
                services_json = json.dumps([services_data] if services_data else [], ensure_ascii=False)
        except (TypeError, ValueError) as e:
            spider.logger.warning(f"Error serializing services data: {e}")
            services_json = '[]'
            
        try:
            availability_data = item.get('availability', {})
            if isinstance(availability_data, dict):
                availability_json = json.dumps(availability_data, ensure_ascii=False)
            else:
                availability_json = json.dumps({}, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            spider.logger.warning(f"Error serializing availability data: {e}")
            availability_json = '{}'
        
        # Ensure rating is a valid float
        try:
            rating = float(item.get('rating', 0.0))
        except (ValueError, TypeError):
            rating = 0.0
        
        # Ensure reviews_count is a valid integer
        try:
            reviews_count = int(item.get('reviews_count', 0))
        except (ValueError, TypeError):
            reviews_count = 0
        
        doctor = Doctor(
            name=str(item.get('name', '')),
            specialization=str(item.get('specialization', '')),
            experience=str(item.get('experience', '')),
            qualifications=str(item.get('qualifications', '')),
            clinics=clinics_json,
            fees=str(item.get('fees', '')),
            rating=rating,
            reviews_count=reviews_count,
            services=services_json,
            address=str(item.get('address', '')),
            google_maps_link=str(item.get('google_maps_link', '')),
            phone=str(item.get('phone', '')),
            availability=availability_json,
            profile_url=str(item.get('profile_url', '')),
            image_url=str(item.get('image_url', ''))
        )
        
        try:
            # Check if doctor already exists to avoid duplicates
            existing_doctor = session.query(Doctor).filter(Doctor.profile_url == doctor.profile_url).first()
            if not existing_doctor:
                session.add(doctor)
                session.commit()
                spider.logger.info(f"Successfully saved doctor: {doctor.name}")
            else:
                spider.logger.info(f"Doctor already exists in database: {doctor.name}")
        except Exception as e:
            session.rollback()
            spider.logger.error(f"Error saving doctor to database: {e}")
        finally:
            session.close()
            
        return item