# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.v1 import attendance
from app.database import engine, Base
from app.models import sql_models

# 1. Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Autonomous Academic Assistant API",
    description="Backend engine for scraping Chalkpad and predicting grades.",
    version="0.1.0"
)

# 2. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Routes
app.include_router(attendance.router, prefix="/api/v1", tags=["Attendance"]) 

@app.get("/")
async def root():
    return {
        "message": "System Operational", 
        "phase": "Phase 2 - Backend API",
        "status": "Online"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.v1 import attendance, notices  # <--- IMPORT NOTICES HERE
from app.database import engine, Base
from app.models import sql_models

# 1. Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Autonomous Academic Assistant API",
    description="Backend engine for scraping Chalkpad and predicting grades.",
    version="0.1.0"
)

# 2. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Routes
app.include_router(attendance.router, prefix="/api/v1", tags=["Attendance"]) 
app.include_router(notices.router, prefix="/api/v1/notices", tags=["Notices"]) # <--- REGISTER NOTICES HERE

@app.get("/")
async def root():
    return {
        "message": "System Operational", 
        "phase": "Phase 2 - Backend API",
        "status": "Online"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}