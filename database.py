from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional
import hashlib

from config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DataEntry(Base):
    __tablename__ = "data_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), unique=True, index=True, nullable=False)
    data_type = Column(String(50), nullable=False)
    source = Column(String(100), nullable=True)
    similarity_score = Column(Float, nullable=True)
    is_duplicate = Column(Boolean, default=False)
    is_false_positive = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RedundancyLog(Base):
    __tablename__ = "redundancy_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    original_entry_id = Column(Integer, nullable=False)
    duplicate_entry_id = Column(Integer, nullable=True)
    similarity_score = Column(Float, nullable=False)
    detection_method = Column(String(50), nullable=False)
    action_taken = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)

def generate_content_hash(content: str) -> str:
    """Generate SHA-256 hash of content for exact duplicate detection"""
    return hashlib.sha256(content.encode()).hexdigest()
