from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from .base import Base, BaseModel

class User(Base, BaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    birth_date = Column(DateTime, nullable=True)
    gender = Column(String(10), nullable=True)  # 'male', 'female', 'other'
    address = Column(Text, nullable=True)
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    medical_history = Column(Text, nullable=True)
    allergies = Column(Text, nullable=True)
    medications = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Relationships
    user_symptoms = relationship("UserSymptom", back_populates="user")
    diagnosis_results = relationship("DiagnosisResult", back_populates="user")