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
