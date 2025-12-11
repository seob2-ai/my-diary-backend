# app/models.py
from sqlalchemy import Column, String, Text, Date, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base
import uuid


def generate_uuid():
    return f"diary_{uuid.uuid4().hex[:8]}"


class DiaryEntry(Base):
    __tablename__ = "diary_entries"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, index=True, nullable=False)
    date = Column(Date, nullable=False)

    emotion = Column(Text, nullable=True)
    event = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    insight = Column(Text, nullable=True)
    tomorrow = Column(Text, nullable=True)

    mode = Column(String, nullable=True)
    mode_label = Column(String, nullable=True)
    mode_description = Column(Text, nullable=True)
    coaching = Column(Text, nullable=True)
    analysis_meta = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

