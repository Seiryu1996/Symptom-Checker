from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base, BaseModel

class Symptom(Base, BaseModel):
    __tablename__ = "symptoms"

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)
    severity_level = Column(Integer, default=1)  # 1-5 scale
    common_causes = Column(Text, nullable=True)
    related_specialties = Column(Text, nullable=True)  # JSON string
    is_active = Column(Boolean, default=True)

    # Relationships
    user_symptoms = relationship("UserSymptom", back_populates="symptom")

class UserSymptom(Base, BaseModel):
    __tablename__ = "user_symptoms"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symptom_id = Column(Integer, ForeignKey("symptoms.id"), nullable=False)
    severity = Column(Integer, nullable=False)  # 1-10 scale
    duration_days = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)  # Body location
    frequency = Column(String(50), nullable=True)  # 'constant', 'intermittent', etc.

    # Relationships
    user = relationship("User", back_populates="user_symptoms")
    symptom = relationship("Symptom", back_populates="user_symptoms")