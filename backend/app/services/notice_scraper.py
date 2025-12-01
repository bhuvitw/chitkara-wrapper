# app/services/notice_scraper.py
import requests
import re
from bs4 import BeautifulSoup
from app.core.config import settings

class NoticeService:
    def __init__(self):
        # We reuse the same session logic as attendance to share cookies
        self.session = requests.Session()
        self.notice_url = "https://cuiet.codebrigade.in/chalkpadpro/noticeBoard/display"  # Verify this URL!

    def get_notices(self, limit=10):
        """
        Fetches notices from the dashboard.
        Returns a list of dictionaries: {date, title, link}
        """
        try:
            # 1. Load Cookies (Reuse the session.pkl from attendance scraper)
            import pickle
            import os
            if os.path.exists("session.pkl"):
                with open("session.pkl", "rb") as f:
                    cookies = pickle.load(f)
                    for cookie in cookies:
                        self.session.cookies.set(cookie['name'], cookie['value'])
            
            # 2. Fetch HTML
            print("📡 Fetching Notice Board...")
            response = self.session.get(self.notice_url)
            
            if "login" in response.url.lower():
                print("⚠️ Session expired. Cannot fetch notices.")
                return []

            # 3. Parse Table
            soup = BeautifulSoup(response.text, 'html.parser')
            # Finding the table is tricky without seeing HTML, but typically it's the main table
            # We look for a table containing "Date" or "Subject" in headers
            target_table = None
            for table in soup.find_all('table'):
                if "date" in table.get_text().lower() and "subject" in table.get_text().lower():
                    target_table = table
                    break
            
            if not target_table:
                print("❌ Notice table not found.")
                return []

            notices = []
            rows = target_table.find_all('tr')[1:] # Skip header
            
            for row in rows[:limit]: # Limit to newest 10
                cols = row.find_all('td')
                if len(cols) >= 3:
                    date = cols[0].text.strip()
                    title = cols[1].text.strip()
                    
                    # Extract Link (if any)
                    link = None
                    a_tag = row.find('a')
                    if a_tag and 'href' in a_tag.attrs:
                        link = a_tag['href']
                        # Handle relative URLs
                        if link.startswith("/"):
                            link = "https://cuiet.codebrigade.in" + link

                    notices.append({
                        "date": date,
                        "title": title,
                        "link": link
                    })
            
            return notices

        except Exception as e:
            print(f"❌ Notice Scraping Failed: {e}")
            return []