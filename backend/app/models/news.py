from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base, BaseModel

class HealthNews(Base, BaseModel):
    __tablename__ = "health_news"

    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    author = Column(String(255), nullable=True)
    source = Column(String(255), nullable=True)
    source_url = Column(String(1000), nullable=True)
    image_url = Column(String(1000), nullable=True)
    category = Column(String(100), nullable=False)  # 'general', 'research', 'prevention', etc.
    tags = Column(Text, nullable=True)  # JSON string
    published_date = Column(DateTime, nullable=False)
    is_featured = Column(Boolean, default=False)
    is_published = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)

class HealthAlert(Base, BaseModel):
    __tablename__ = "health_alerts"

    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)
    alert_type = Column(String(50), nullable=False)  # 'info', 'warning', 'emergency'
    severity_level = Column(Integer, default=1)  # 1-5 scale
    affected_areas = Column(Text, nullable=True)  # JSON string of geographic areas
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    source_authority = Column(String(255), nullable=False)
    source_url = Column(String(1000), nullable=True)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)