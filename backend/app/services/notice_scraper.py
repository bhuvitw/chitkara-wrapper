# app/services/notice_scraper.py
import time
import os
import pickle
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from app.core.config import settings

class NoticeService:
    def __init__(self, headless=True):
        self.cookie_file = "session.pkl"
        
        # 1. Setup Lightweight Chrome (No Images)
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        
        # Optimization Flags to prevent crashing
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false") # 🚀 Speed boost
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=chrome_options
        )

    def get_notices(self, limit=10):
        try:
            print("👁️ Opening Notice Board (JS Injection Mode)...")
            
            # 1. Load Cookies & Navigate
            self.driver.get(settings.COLLEGE_LOGIN_URL) 
            
            if os.path.exists(self.cookie_file):
                with open(self.cookie_file, "rb") as f:
                    cookies = pickle.load(f)
                    for cookie in cookies:
                        try:
                            self.driver.add_cookie(cookie)
                        except: pass
            
            # 2. Go to the Feed Page
            self.driver.get("https://cuiet.codebrigade.in/dashboardFeed/feed")
            
            # Quick check if logged in
            if "login" in self.driver.current_url.lower():
                print("⚠️ Session expired.")
                return []

            # 3. Find Notice Elements
            feed_items = self.driver.find_elements(By.CLASS_NAME, "ui-feed")
            print(f"✅ Found {len(feed_items)} notices.")

            notices = []
            for item in feed_items[:limit]:
                try:
                    # Extract Title (Selenium Text)
                    title = item.find_element(By.CLASS_NAME, "ui-circular-title").text.strip()
                    
                    # Date Regex
                    date_match = re.search(r'\d{1,2}(?:st|nd|rd|th)?\s+\w+,\s+\d{4}', title)
                    date = date_match.group(0) if date_match else "Recent"

                    # Extract ID and Secret from 'onclick' attribute
                    onclick_text = item.get_attribute("onclick")
                    match = re.search(r"getCircular\((\d+),\s*['\"]([^'\"]+)['\"]", onclick_text)
                    
                    pdf_link = None
                    notice_id = None
                    
                    if match:
                        notice_id = match.group(1)
                        secret_key = match.group(2) 
                        
                        # --- THE MAGIC TRICK 🪄 ---
                        # We use the browser's own engine to fetch the link.
                        # This guarantees cookies and headers are 100% correct.
                        pdf_link = self._fetch_link_via_js(notice_id, secret_key)
                    
                    notices.append({
                        "id": notice_id,
                        "date": date,
                        "title": title,
                        "link": pdf_link
                    })
                    
                    status = "✅" if pdf_link else "❌"
                    print(f"📄 {title[:20]}... Link: {status}")

                except Exception as e:
                    print(f"⚠️ Error parsing item: {e}")
                    continue

            return notices

        except Exception as e:
            print(f"❌ Scraper Error: {str(e)}")
            return []
        finally:
            # Always close the browser to prevent memory leaks!
            if self.driver:
                self.driver.quit()

    def _fetch_link_via_js(self, notice_id, secret_key):
        """
        Injects a jQuery AJAX call directly into the page context.
        """
        try:
            # This JS code runs inside Chrome. 
            # It uses the page's existing jQuery ($) session.
            js_script = """
            var callback = arguments[arguments.length - 1];
            $.ajax({
                url: '/dashboardFeed/getFeedItem', 
                type: 'POST',
                data: {
                    'feedId': arguments[0], 
                    'dateId': arguments[1], 
                    'feedType': '1', 
                    'isSeen': '0'
                },
                success: function(response) { callback(response); },
                error: function(xhr) { callback(null); }
            });
            """
            # execute_async_script allows us to wait for the AJAX result
            response_html = self.driver.execute_async_script(js_script, notice_id, secret_key)
            
            if response_html:
                # Regex to find the link in the returned HTML
                link_match = re.search(r'href=["\']([^"\']+downloadAttachment[^"\']+)["\']', response_html)
                if link_match:
                    full_link = link_match.group(1)
                    if full_link.startswith("/"):
                        full_link = "https://cuiet.codebrigade.in" + full_link
                    return full_link
            
            return None
        except Exception as e:
            print(f"   ⚠️ JS Injection Failed: {e}")
            return None