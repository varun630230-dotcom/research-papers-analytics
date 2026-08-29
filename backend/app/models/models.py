from sqlalchemy import Column, String, Text, DateTime
from app.database import Base
import uuid
from datetime import datetime, timezone

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    idea = Column(Text, nullable=False)
    goal = Column(String, nullable=True)
    domain = Column(String, nullable=True)
    technical_level = Column(String, nullable=True)
    constraints = Column(Text, nullable=True)
    status = Column(String, default="pending")
    progress_data = Column(Text, nullable=True)
    results_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
