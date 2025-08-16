
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class FeedbackCreate(BaseModel):
    product: str = Field(..., min_length=1, max_length=100)
    text: str = Field(..., min_length=1, max_length=2000)

class FeedbackOut(BaseModel):
    id: int
    product: str
    text: str
    created_at: datetime
    sentiment: str
    score: float

    class Config:
        from_attributes = True

class FeedbackList(BaseModel):
    items: List[FeedbackOut]
    total: int

class AnalyticsSummary(BaseModel):
    by_sentiment: Dict[str, int]
    by_product: Dict[str, int]
    daily_counts: List[dict]
