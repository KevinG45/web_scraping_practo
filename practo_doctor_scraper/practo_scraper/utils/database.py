from sqlalchemy import Column, Integer, String, Float, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Doctor(Base):
    __tablename__ = 'doctors'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    specialization = Column(String(255))
    experience = Column(String(50))
    qualifications = Column(String(255))
    clinics = Column(Text)  # JSON string of clinic details
    fees = Column(String(50))
    rating = Column(Float)
    reviews_count = Column(Integer)
    services = Column(Text)  # JSON string of services
    address = Column(Text)
    google_maps_link = Column(String(500))
    phone = Column(String(50))
    availability = Column(Text)  # JSON string of availability
    profile_url = Column(String(500))
    image_url = Column(String(500))

def create_tables(engine):
    Base.metadata.create_all(engine)