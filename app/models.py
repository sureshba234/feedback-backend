
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from .database import Base

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    product = Column(String(100), index=True, nullable=False)
    text = Column(String(2000), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    sentiment = Column(String(20), index=True)
    score = Column(Float)
