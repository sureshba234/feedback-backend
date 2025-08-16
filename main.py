from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# List of allowed frontend origins
origins = [
    "https://custumer-feedback-dashboard.web.app"  # Firebase frontend URL
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Frontend domains allowed
    allow_credentials=True,
    allow_methods=["*"],            # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"]             # Allow all headers
)

# Example route
@app.get("/")
def read_root():
    return {"message": "Backend is working!"}
    from fastapi import Depends
from sqlalchemy.orm import Session
from . import models, database

@app.post("/seed")
def seed_data(db: Session = Depends(database.get_db)):
    sample = [
        models.Feedback(product="App", sentiment="positive", comment="Great app!"),
        models.Feedback(product="App", sentiment="negative", comment="Needs improvement"),
        models.Feedback(product="Website", sentiment="positive", comment="Nice UI"),
    ]
    db.add_all(sample)
    db.commit()
    return {"message": "Sample data added"}


