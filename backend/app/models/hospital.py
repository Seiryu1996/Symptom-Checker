from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Float, Time
from sqlalchemy.orm import relationship
from .base import Base, BaseModel

class Hospital(Base, BaseModel):
    __tablename__ = "hospitals"

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    address = Column(Text, nullable=False)
    phone_number = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    rating = Column(Float, default=0.0)  # 0.0-5.0
    total_reviews = Column(Integer, default=0)
    
    # Operating hours
    monday_open = Column(Time, nullable=True)
    monday_close = Column(Time, nullable=True)
    tuesday_open = Column(Time, nullable=True)
    tuesday_close = Column(Time, nullable=True)
    wednesday_open = Column(Time, nullable=True)
    wednesday_close = Column(Time, nullable=True)
    thursday_open = Column(Time, nullable=True)
    thursday_close = Column(Time, nullable=True)
    friday_open = Column(Time, nullable=True)
    friday_close = Column(Time, nullable=True)
    saturday_open = Column(Time, nullable=True)
    saturday_close = Column(Time, nullable=True)
    sunday_open = Column(Time, nullable=True)
    sunday_close = Column(Time, nullable=True)
    
    # Services
    emergency_services = Column(Boolean, default=False)
    accepts_insurance = Column(Boolean, default=True)
    parking_available = Column(Boolean, default=True)
    wheelchair_accessible = Column(Boolean, default=True)
    
    is_active = Column(Boolean, default=True)

    # Relationships
    specialties = relationship("HospitalSpecialty", back_populates="hospital")

class HospitalSpecialty(Base, BaseModel):
    __tablename__ = "hospital_specialties"

    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    specialty_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    department_phone = Column(String(20), nullable=True)
    wait_time_avg = Column(Integer, nullable=True)  # Average wait time in minutes
    is_available = Column(Boolean, default=True)

    # Relationships
    hospital = relationship("Hospital", back_populates="specialties")