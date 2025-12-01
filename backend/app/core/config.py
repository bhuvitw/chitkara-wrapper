# app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # URLs
    COLLEGE_LOGIN_URL = os.getenv("COLLEGE_LOGIN_URL", "https://cuiet.codebrigade.in/loginManager/load")
    COLLEGE_DASHBOARD_URL = os.getenv("COLLEGE_DASHBOARD_URL", "https://cuiet.codebrigade.in/chalkpadpro/studentDetails/display")
    SUMMARY_API_URL = "https://cuiet.codebrigade.in/chalkpadpro/studentDetails/getAttendance"
    
    # Secrets
    USER = os.getenv("COLLEGE_USER")
    PASS = os.getenv("COLLEGE_PASS")
    
    GMAIL_USER = os.getenv("GMAIL_USER")
    GMAIL_PASS = os.getenv("GMAIL_APP_PASS")
    OTP_SENDER = os.getenv("OTP_SENDER_EMAIL")

settings = Settings()