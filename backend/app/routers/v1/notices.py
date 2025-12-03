# app/routers/v1/notices.py
from fastapi import APIRouter
from app.services.notice_scraper import NoticeService

router = APIRouter()

@router.get("/")
async def get_notices():
    """
    Live scrapes the top 5 notices and returns PDF links.
    """
    service = NoticeService(headless=False) # Run invisible
    data = service.get_notices(limit=5)
    return {
        "status": "success",
        "count": len(data), 
        "data": data
    }