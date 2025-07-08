from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from .base import Base, BaseModel

class Diagnosis(Base, BaseModel):
    __tablename__ = "diagnoses"

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    icd_10_code = Column(String(10), nullable=True)  # ICD-10 diagnosis code
    category = Column(String(100), nullable=False)
    severity_level = Column(Integer, default=1)  # 1-5 scale
    recommended_specialties = Column(Text, nullable=True)  # JSON string
    treatment_options = Column(Text, nullable=True)
    prognosis = Column(Text, nullable=True)
    prevention_tips = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    diagnosis_results = relationship("DiagnosisResult", back_populates="diagnosis")

class DiagnosisResult(Base, BaseModel):
    __tablename__ = "diagnosis_results"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    diagnosis_id = Column(Integer, ForeignKey("diagnoses.id"), nullable=False)
    confidence_score = Column(Float, nullable=False)  # 0.0-1.0
    symptoms_data = Column(JSON, nullable=False)  # Stored symptom data
    ai_analysis = Column(Text, nullable=True)
    recommended_actions = Column(Text, nullable=True)
    urgency_level = Column(String(20), default="low")  # 'low', 'medium', 'high', 'emergency'
    follow_up_date = Column(Integer, nullable=True)  # Days until follow-up
    status = Column(String(20), default="pending")  # 'pending', 'reviewed', 'resolved'

    # Relationships
    user = relationship("User", back_populates="diagnosis_results")
    diagnosis = relationship("Diagnosis", back_populates="diagnosis_results")