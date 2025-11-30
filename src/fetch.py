import requests
import pickle
import os
import re
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

# --- CONFIGURATION ---
DASHBOARD_URL = os.getenv("COLLEGE_DASHBOARD_URL", "https://cuiet.codebrigade.in/chalkpadpro/studentDetails/display")
SUMMARY_API_URL = "https://cuiet.codebrigade.in/chalkpadpro/studentDetails/getAttendance" 
COOKIE_FILE = "session.pkl"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": DASHBOARD_URL,
    "X-Requested-With": "XMLHttpRequest"
}

def get_internal_student_id(session):
    try:
        response = session.get(DASHBOARD_URL, headers=HEADERS)
        if "login" in response.url.lower():
            # Session expired
            return None, None
        
        match = re.search(r'var\s+studentId\s*=\s*["\'](\d+)["\']', response.text)
        if match:
            return match.group(1), response.text
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    return None, None

def parse_html_to_dict(html):
    """
    Parses HTML and returns CLEAN data for other scripts to use.
    """
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')
    target_table = None
    
    # Find the correct table
    for table in tables:
        txt = table.get_text().lower()
        if "subject name" in txt and "delivered" in txt and "attended" in txt:
            target_table = table
            break
    
    if not target_table:
        return None

    data = {}
    rows = target_table.find_all('tr')
    
    for row in rows:
        cols = row.find_all('td')
        # Check column length based on your screenshot structure
        if len(cols) >= 13:
            try:
                # Extract Text
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
                    
                    # Total Effective Attendance
                    effective_attended = attended + dl + ml
                    
                    if delivered > 0:
                        percent = (effective_attended / delivered) * 100
                        
                        data[subject] = {
                            "attended": effective_attended,
                            "delivered": delivered,
                            "percent": percent
                        }
            except:
                continue
    return data

def get_attendance_data():
    """
    This is the function planner.py calls.
    It returns the dictionary { 'Subject': {data}, ... }
    """
    if not os.path.exists(COOKIE_FILE):
        print("❌ 'session.pkl' missing. Run auth.py first.")
        return None

    session = requests.Session()
    with open(COOKIE_FILE, "rb") as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])

    student_id, dashboard_html = get_internal_student_id(session)
    if not student_id: return None

    # 1. Try Dashboard
    data = parse_html_to_dict(dashboard_html)
    if data: return data

    # 2. Try Secret API
    try:
        payload = {"studentId": student_id}
        response = session.post(SUMMARY_API_URL, data=payload, headers=HEADERS)
        if response.status_code == 200:
            return parse_html_to_dict(response.text)
    except:
        pass
    
    return None

def main():
    """
    Runs when you type 'python fetch.py'
    Prints the table for the user.
    """
    print("📡 Fetching data...")
    data = get_attendance_data()
    
    if not data:
        print("❌ Failed to find attendance table.")
        print("Tip: Run auth.py again.")
        return

    print(f"\n📊 ATTENDANCE REPORT")
    print("=" * 85)
    print(f"{'Subject':<35} | {'Att+DL/Del':<10} | {'%':<6} | {'Status'}")
    print("-" * 85)

    for sub, info in data.items():
        att = info['attended']
        dell = info['delivered']
        pct = info['percent']
        
        # Calc Status for display
        next_pct = (att / (dell + 1)) * 100
        if pct >= 75:
            status = "✅ SAFE" if next_pct >= 75 else "⚠️ BORDERLINE"
        else:
            needed = 0
            t_a, t_d = att, dell
            while (t_a / t_d) < 0.75:
                t_a += 1; t_d += 1; needed += 1
            status = f"🚨 DANGER (+{needed})"

        print(f"{sub[:33]:<35} | {att}/{dell:<7} | {pct:.1f}% | {status}")

if __name__ == "__main__":
    main()