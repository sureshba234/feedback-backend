
from fastapi import FastAPI, Depends, UploadFile, File, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from typing import Optional
import csv, io, os

from .database import Base, engine, get_db
from .models import Feedback
from .schemas import FeedbackCreate, FeedbackOut, FeedbackList, AnalyticsSummary
from .utils import analyze_sentiment
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Customer Feedback Analysis API", version="1.0.0")

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.get("/", tags=["health"])
def health():
    return {"status": "ok"}

@app.post("/feedback", response_model=FeedbackOut, tags=["feedback"])
def create_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)):
    label, score = analyze_sentiment(payload.text)
    obj = Feedback(product=payload.product, text=payload.text, sentiment=label, score=score)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@app.post("/feedback/bulk", tags=["feedback"])
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")
    content = await file.read()
    f = io.StringIO(content.decode('utf-8', errors='ignore'))
    reader = csv.DictReader(f)
    required = {'product', 'text'}
    headers = set([h.strip().lower() for h in (reader.fieldnames or [])])
    if not required.issubset(headers):
        raise HTTPException(status_code=400, detail="CSV must have headers: product,text")
    count = 0
    for row in reader:
        product = (row.get('product') or '').strip()
        text = (row.get('text') or '').strip()
        if not product or not text:
            continue
        label, score = analyze_sentiment(text)
        db.add(Feedback(product=product, text=text, sentiment=label, score=score))
        count += 1
        if count % 100 == 0:
            db.flush()
    db.commit()
    return {"inserted": count}

@app.get("/feedback", response_model=FeedbackList, tags=["feedback"])
def list_feedback(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    product: Optional[str] = None,
    sentiment: Optional[str] = Query(None, pattern="^(positive|neutral|negative)$"),
):
    stmt = select(Feedback)
    if search:
        like = f"%{search.lower()}%"
        stmt = stmt.where(func.lower(Feedback.text).like(like))
    if product:
        stmt = stmt.where(Feedback.product == product)
    if sentiment:
        stmt = stmt.where(Feedback.sentiment == sentiment)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.execute(stmt.order_by(desc(Feedback.created_at)).offset(skip).limit(limit)).scalars().all()
    return {"items": items, "total": total or 0}

@app.get("/analytics/summary", response_model=AnalyticsSummary, tags=["analytics"])
def analytics_summary(db: Session = Depends(get_db)):
    sentiment_rows = db.execute(select(Feedback.sentiment, func.count()).group_by(Feedback.sentiment)).all()
    by_sentiment = {s or "unknown": c for s, c in sentiment_rows}

    product_rows = db.execute(select(Feedback.product, func.count()).group_by(Feedback.product)).all()
    by_product = {p or "unknown": c for p, c in product_rows}

    daily_rows = db.execute(
        select(func.date(Feedback.created_at), func.count())
        .group_by(func.date(Feedback.created_at))
        .order_by(func.date(Feedback.created_at))
    ).all()
    daily_counts = [{"date": str(d), "count": c} for d, c in daily_rows]

    return {"by_sentiment": by_sentiment, "by_product": by_product, "daily_counts": daily_counts}
