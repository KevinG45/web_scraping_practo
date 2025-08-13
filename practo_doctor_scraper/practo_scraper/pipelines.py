import json
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scrapy.exporters import JsonItemExporter, CsvItemExporter
from .utils.database import Base, Doctor, create_tables
from .settings import DATABASE_URI, JSON_FILE, CSV_FILE

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
        
        # Safely serialize JSON fields
        try:
            clinics_json = json.dumps(item.get('clinics', []))
        except (TypeError, ValueError):
            clinics_json = '[]'
            
        try:
            services_json = json.dumps(item.get('services', []))
        except (TypeError, ValueError):
            services_json = '[]'
            
        try:
            availability_json = json.dumps(item.get('availability', {}))
        except (TypeError, ValueError):
            availability_json = '{}'
        
        doctor = Doctor(
            name=item.get('name', ''),
            specialization=item.get('specialization', ''),
            experience=item.get('experience', ''),
            qualifications=item.get('qualifications', ''),
            clinics=clinics_json,
            fees=item.get('fees', ''),
            rating=item.get('rating', 0.0),
            reviews_count=item.get('reviews_count', 0),
            services=services_json,
            address=item.get('address', ''),
            google_maps_link=item.get('google_maps_link', ''),
            phone=item.get('phone', ''),
            availability=availability_json,
            profile_url=item.get('profile_url', ''),
            image_url=item.get('image_url', '')
        )
        
        try:
            session.add(doctor)
            session.commit()
        except Exception as e:
            session.rollback()
            spider.logger.error(f"Error saving doctor to database: {e}")
        finally:
            session.close()
            
        return item