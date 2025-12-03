import time
import re
import requests
import pickle
import os
from bs4 import BeautifulSoup
from imap_tools import MailBox, AND
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from app.core.config import settings

class ChalkpadService:
    def __init__(self, headless=False):
        self.headless = headless
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_experimental_option("detach", True)

        self.driver = None
        self.session = requests.Session()
        
        # 1. AUTO-LOAD COOKIES ON STARTUP
        self.cookie_file = "session.pkl"
        self._load_cookies()

    def _load_cookies(self):
        """Loads cookies from file into the Requests session."""
        if os.path.exists(self.cookie_file):
            try:
                with open(self.cookie_file, "rb") as f:
                    cookies = pickle.load(f)
                    for cookie in cookies:
                        self.session.cookies.set(cookie['name'], cookie['value'])
                print("🍪 Loaded existing session cookies.")
            except Exception as e:
                print(f"⚠️ Failed to load cookie file: {e}")

    def check_session_valid(self):
        try:
            response = self.session.get(settings.COLLEGE_DASHBOARD_URL, allow_redirects=True)
            if "login" in response.url.lower():
                return False
            return True
        except:
            return False

    def start_browser(self):
        if not self.driver:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), 
                options=self.chrome_options
            )

    def get_latest_otp(self):
        print(f"📧 Connecting to Gmail ({settings.GMAIL_USER})...")
        try:
            with MailBox('imap.gmail.com').login(settings.GMAIL_USER, settings.GMAIL_PASS) as mailbox:
                for msg in mailbox.fetch(AND(from_=settings.OTP_SENDER), limit=1, reverse=True):
                    body = msg.text or msg.html
                    match = re.search(r'\b\d{4,6}\b', body)
                    if match:
                        return match.group(0)
        except Exception as e:
            print(f"❌ Gmail Error: {e}")
        return None

    def login(self, force=False):
        if not force and self.check_session_valid():
            print("⚡ Session is already valid! Skipping Login.")
            return True
        
        print("⚠️ Session expired or forced refresh. Starting Login Flow...")
        self.start_browser()

        try:
            print("🌍 Opening Login Page...")
            self.driver.get(settings.COLLEGE_LOGIN_URL)

            # Fill Credentials
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "txtUsername")))
            self.driver.find_element(By.ID, "txtUsername").clear()
            self.driver.find_element(By.ID, "txtUsername").send_keys(settings.USER)
            self.driver.find_element(By.ID, "txtPassword").clear()
            self.driver.find_element(By.ID, "txtPassword").send_keys(settings.PASS)

            # Smart Captcha Handler
            print("\n" + "="*50)
            print("🛑 ACTION REQUIRED: Just solve the CAPTCHA.")
            print("🤖 The script will auto-click 'Sign In' once you are verified.")
            print("="*50 + "\n")

            while True:
                try:
                    response = self.driver.execute_script("return document.getElementById('g-recaptcha-response').value")
                    if response:
                        print("✅ CAPTCHA Verified! Auto-clicking Sign In...")
                        break
                except:
                    pass
                time.sleep(0.5)

            try:
                login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                login_btn.click()
            except:
                print("⚠️ Could not auto-click Login. Please click manually.")

            # OTP Handling
            wait = WebDriverWait(self.driver, 120)
            wait.until(EC.presence_of_element_located((By.ID, "OTPText")))
            print("📩 Login clicked. Waiting for OTP...")

            time.sleep(5) 
            otp = self.get_latest_otp()
            
            if otp:
                print(f"🔑 OTP Found: {otp}")
                self.driver.find_element(By.ID, "OTPText").send_keys(otp)
                time.sleep(1)
                self.driver.find_element(By.ID, "close").click()
            else:
                raise Exception("OTP not found in email.")

            time.sleep(5)
            # Just verify we moved away from login, don't worry about exact URL yet
            if "login" in self.driver.current_url.lower():
                raise Exception("Login failed (URL is still login page).")

            # Save Cookies
            selenium_cookies = self.driver.get_cookies()
            for cookie in selenium_cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
            
            with open(self.cookie_file, "wb") as f:
                pickle.dump(selenium_cookies, f)

            print("🎉 Login Successful & Session Saved")
            return True

        except Exception as e:
            print(f"Login Error: {str(e)}")
            if self.driver: self.driver.quit()
            raise e

    def get_attendance(self):
        try:
            print("📡 Fetching Dashboard content (Fast Mode)...")
            
            # --- ATTEMPT 1: FAST HTTP REQUEST ---
            response = self.session.get(settings.COLLEGE_DASHBOARD_URL)
            
            if "login" in response.url.lower():
                print("⚠️ Fast Mode: Session appears expired (Redirected to Login).")
            else:
                data = self._parse_table(response.text)
                if data:
                    print("✅ Found data in Dashboard HTML")
                    return data
                
                # API Fallback
                match = re.search(r'var\s+studentId\s*=\s*["\'](\d+)["\']', response.text)
                if match:
                    student_id = match.group(1)
                    print(f"🆔 Found Student ID: {student_id}")
                    payload = {"studentId": student_id}
                    headers = {
                        "User-Agent": "Mozilla/5.0",
                        "Referer": settings.COLLEGE_DASHBOARD_URL,
                        "X-Requested-With": "XMLHttpRequest"
                    }
                    api_response = self.session.post(settings.SUMMARY_API_URL, data=payload, headers=headers)
                    data = self._parse_table(api_response.text)
                    if data:
                        print("✅ Found data via API")
                        return data
            
            # --- ATTEMPT 2: FRESH LOGIN FALLBACK ---
            print("☢️ Fast scrape failed. Engaging Selenium Fallback...")
            if os.path.exists(self.cookie_file):
                os.remove(self.cookie_file) 
            
            if self.driver: 
                self.driver.quit() 
                self.driver = None 
            
            print("🔄 Triggering Re-Login Flow (FORCED)...")
            self.login(force=True) 
            
            if self.driver:
                print("🌍 Login Done. FORCE NAVIGATING to Attendance Page...")
                # CRITICAL FIX: We must go to the URL specifically!
                self.driver.get(settings.COLLEGE_DASHBOARD_URL)
                
                print("✅ Waiting for table to render...")
                try:
                    WebDriverWait(self.driver, 20).until(
                        lambda d: "subject name" in d.page_source.lower()
                    )
                    print("👀 Table detected in browser!")
                except:
                    print("⚠️ Table text not found. Debugging Source...")

                # Parse Browser HTML
                data = self._parse_table(self.driver.page_source)
                if data:
                    print("✅ Found data via Selenium HTML")
                    return data

                # Steal ID and try API with browser cookies
                print("🕵️‍♀️ Table parsing failed. Trying Hybrid API...")
                match = re.search(r'var\s+studentId\s*=\s*["\'](\d+)["\']', self.driver.page_source)
                if match:
                    student_id = match.group(1)
                    selenium_cookies = self.driver.get_cookies()
                    for cookie in selenium_cookies:
                        self.session.cookies.set(cookie['name'], cookie['value'])

                    payload = {"studentId": student_id}
                    headers = {
                        "User-Agent": "Mozilla/5.0",
                        "Referer": settings.COLLEGE_DASHBOARD_URL,
                        "X-Requested-With": "XMLHttpRequest"
                    }
                    api_response = self.session.post(settings.SUMMARY_API_URL, data=payload, headers=headers)
                    data = self._parse_table(api_response.text)
                    if data:
                        return data

            print("❌ Failed to find attendance data.")
            return {}

        except Exception as e:
            print(f"❌ Scraping Error: {str(e)}")
            raise Exception(f"Fetching Attendance Failed: {str(e)}")

    def _parse_table(self, html):
        """
        MATCHES FETCH.PY EXACTLY
        """
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table')
        target_table = None

        for table in tables:
            txt = table.get_text().lower()
            # Match fetch.py strictness
            if "subject name" in txt and "delivered" in txt:
                target_table = table
                break
        
        if not target_table: return {}

        data = []
        rows = target_table.find_all('tr')
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 13:
                try:
                    subject = cols[2].text.strip()
                    delivered_txt = cols[5].text.strip()
                    attended_txt = cols[6].text.strip()
                    dl_txt = cols[11].text.strip()
                    ml_txt = cols[12].text.strip()
                    
                    if delivered_txt.isdigit() and attended_txt.isdigit():
                        delivered = int(delivered_txt)
                        attended = int(attended_txt)
                        dl = int(dl_txt) if dl_txt.isdigit() else 0
                        ml = int(ml_txt) if ml_txt.isdigit() else 0
                        
                        effective_attended = attended + dl + ml
                        percent = (effective_attended / delivered * 100) if delivered > 0 else 0.0
                        
                        data.append({
                            "subject": subject,
                            "delivered": delivered,
                            "attended": effective_attended,
                            "percentage": round(percent, 2)
                        })
                except:
                    continue
        return data

    def close(self):
        if self.driver:
            self.driver.quit()
            