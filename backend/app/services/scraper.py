# app/services/notice_scraper.py
import time
import os
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from app.core.config import settings

class NoticeService:
    def __init__(self, headless=True):
        self.cookie_file = "session.pkl"
        
        # Setup Chrome
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=chrome_options
        )

    def get_notices(self, limit=5):
        """
        Scrapes the Notice Board.
        limit: Number of notices to fetch (Default 5 to keep it fast)
        """
        notices = []
        try:
            print("👁️ Opening Notice Board...")
            
            # 1. Load Cookies & Navigate
            self.driver.get(settings.COLLEGE_LOGIN_URL) # Go to domain first
            if os.path.exists(self.cookie_file):
                with open(self.cookie_file, "rb") as f:
                    cookies = pickle.load(f)
                    for cookie in cookies:
                        try:
                            self.driver.add_cookie(cookie)
                        except: pass
            
            # 2. Go to Dashboard (Where notices live)
            # Based on your HTML, this seems to be the main dashboard feed
            self.driver.get(settings.COLLEGE_DASHBOARD_URL)
            
            # Wait for the feed to appear
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ui-feed")))

            # 3. Find all Notice Elements
            feed_items = self.driver.find_elements(By.CLASS_NAME, "ui-feed")
            print(f"found {len(feed_items)} feed items. Processing top {limit}...")

            count = 0
            for item in feed_items:
                if count >= limit: break
                
                try:
                    # Extract Basic Info from the list (Before clicking)
                    title_elem = item.find_element(By.CLASS_NAME, "ui-circular-title")
                    title = title_elem.text.strip()
                    
                    # 4. CLICK to open details (The "Pop-up")
                    # We use execute_script because sometimes other elements block the click
                    self.driver.execute_script("arguments[0].click();", item)
                    
                    # 5. Wait for the Slide/Modal to open and show the Attachment link
                    # Your HTML shows the link is inside a div class 'ui-feed-det-attach'
                    try:
                        link_elem = wait.until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, ".ui-feed-det-attach a")
                        ))
                        link = link_elem.get_attribute("href")
                    except:
                        link = None # Some notices might just be text, no PDF
                    
                    # 6. Close the Slide (So we can click the next one)
                    # Your HTML shows a div with class 'slide-close-button'
                    close_btn = self.driver.find_element(By.CLASS_NAME, "slide-close-button")
                    self.driver.execute_script("arguments[0].click();", close_btn)
                    
                    # Brief pause for animation to close
                    time.sleep(1)

                    notices.append({
                        "title": title,
                        "link": link,
                        "date": "Recent" # We can improve date extraction later using Regex on the title
                    })
                    count += 1
                    print(f"✅ Scraped: {title[:30]}...")

                except Exception as inner_e:
                    print(f"⚠️ Failed to scrape one notice: {inner_e}")
                    continue

            return notices

        except Exception as e:
            print(f"❌ Notice Error: {str(e)}")
            return []
        finally:
            self.driver.quit()