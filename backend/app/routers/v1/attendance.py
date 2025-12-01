# app/routers/v1/attendance.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.scraper import ChalkpadService
from app.database import get_db
from app import crud

router = APIRouter()

# --- THE MAGIC BUTTON (Get Cached Data) ---
@router.get("/")
async def read_attendance(db: Session = Depends(get_db)):
    """
    Get attendance from Database (Instant, No Scraping).
    This is the 'Magic Trick' endpoint.
    """
    return crud.get_attendance(db)

# --- THE SYNC BUTTON (Trigger Scraper) ---
@router.post("/sync")
async def sync_attendance(db: Session = Depends(get_db)):
    """
    Trigger Scraper -> Update Database -> Return Data.
    Use this when you want to refresh data from the college.
    """
    service = ChalkpadService(headless=False)
    try:
        # 1. Scrape
        data = service.get_attendance()
        service.close()
        
        # 2. Save to DB
        if data:
            crud.create_attendance(db, data)
            
        return {"status": "success", "data": data}
    except Exception as e:
        service.close()
        raise HTTPException(status_code=500, detail=str(e))