import json
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .database import Doctor

def export_to_json(doctors, filename='doctors_data.json'):
    """Export doctors data to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(doctors, f, ensure_ascii=False, indent=4)

def export_to_csv(doctors, filename='doctors_data.csv'):
    """Export doctors data to CSV file"""
    df = pd.DataFrame(doctors)
    df.to_csv(filename, index=False)

def get_all_doctors_from_db(db_uri):
    """Retrieve all doctors from the database"""
    engine = create_engine(db_uri)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    doctors = []
    try:
        for doctor in session.query(Doctor).all():
            doc_dict = {
                'name': doctor.name,
                'specialization': doctor.specialization,
                'experience': doctor.experience,
                'qualifications': doctor.qualifications,
                'clinics': json.loads(doctor.clinics) if doctor.clinics else [],
                'fees': doctor.fees,
                'rating': doctor.rating,
                'reviews_count': doctor.reviews_count,
                'services': json.loads(doctor.services) if doctor.services else [],
                'address': doctor.address,
                'google_maps_link': doctor.google_maps_link,
                'phone': doctor.phone,
                'availability': json.loads(doctor.availability) if doctor.availability else {},
                'profile_url': doctor.profile_url,
                'image_url': doctor.image_url
            }
            doctors.append(doc_dict)
    finally:
        session.close()
    
    return doctors