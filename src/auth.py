import time
import pickle
import re
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from imap_tools import MailBox, AND

# Load variables from .env file
load_dotenv()

# --- CONFIGURATION ---
# Login URL found from your screenshots
LOGIN_URL = os.getenv("COLLEGE_LOGIN_URL", "https://cuiet.codebrigade.in/loginManager/load")
USER = os.getenv("COLLEGE_USER")
PASS = os.getenv("COLLEGE_PASS")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_APP_PASS")
OTP_SENDER = os.getenv("OTP_SENDER_EMAIL")
COOKIE_FILE = "session.pkl"

def get_latest_otp():
    """Connects to Gmail and finds the latest OTP email."""
    print(f"📧 Connecting to Gmail ({GMAIL_USER})...")
    try:
        with MailBox('imap.gmail.com').login(GMAIL_USER, GMAIL_PASS) as mailbox:
            # Fetch the newest email from the college sender
            # We look for the sender defined in your .env
            for msg in mailbox.fetch(AND(from_=OTP_SENDER), limit=1, reverse=True):
                body = msg.text or msg.html
                # Regex to find a 4 to 6 digit number
                match = re.search(r'\b\d{4,6}\b', body)
                if match:
                    return match.group(0)
    except Exception as e:
        print(f"❌ Gmail Error: {e}")
    return None

def run_auth():
    print("🚀 Launching Browser...")
    
    # Configure Chrome to stay open so you can interact with it
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Set a long timeout (120 seconds) so you have plenty of time to solve the Captcha
    wait = WebDriverWait(driver, 120)

    try:
        # --- STEP 1: OPEN LOGIN PAGE ---
        print("🌍 Opening Login Page...")
        driver.get(LOGIN_URL)

        # Attempt to auto-fill username and password
        print("⌨️ Pre-filling Credentials...")
        try:
            driver.find_element(By.ID, "txtUsername").clear()
            driver.find_element(By.ID, "txtUsername").send_keys(USER)
            driver.find_element(By.ID, "txtPassword").clear()
            driver.find_element(By.ID, "txtPassword").send_keys(PASS)
        except:
            print("⚠️ Auto-fill failed. Please type user/pass manually.")

        # --- STEP 2: MANUAL USER ACTION ---
        print("\n" + "="*60)
        print("🛑 ACTION REQUIRED: ")
        print("1. Click the 'I'm not a robot' checkbox.")
        print("2. Click the 'Sign In' button.")
        print("⏳ The script is now watching for the OTP page...")
        print("="*60 + "\n")

        # --- STEP 3: AUTOMATIC OTP HANDLING ---
        # The script waits here until it sees the element with ID "OTPText"
        print("👀 Watching for OTP Input Box (ID: OTPText)...")
        wait.until(EC.presence_of_element_located((By.ID, "OTPText")))
        
        print("✅ OTP Page Detected! Taking control...")

        print("⏳ Waiting 10s for the email to arrive...")
        time.sleep(10) 
        
        otp = get_latest_otp()
        
        if otp:
            print(f"🔑 OTP Found in Email: {otp}")
            
            # Type the OTP into the box
            driver.find_element(By.ID, "OTPText").send_keys(otp)
            time.sleep(1)

            # Click the Submit button (ID: close)
            print("🖱️ Clicking Submit (ID: close)...")
            driver.find_element(By.ID, "close").click()
            
        else:
            print("❌ No OTP found in Gmail. Please enter it manually.")

        # --- STEP 4: SAVE SESSION ---
        print("⏳ Waiting for Dashboard to load...")
        time.sleep(8) # Wait for the redirect to complete
        
        # Verify if we are inside
        if "studentDetails/display" in driver.current_url or "dashboard" in driver.current_url.lower():
            print("🎉 We are logged in!")
        elif "multiAuthentication" in driver.current_url:
            print("⚠️ Warning: It seems we are still on the OTP page.")

        # Save the cookies to a file
        cookies = driver.get_cookies()
        with open(COOKIE_FILE, "wb") as f:
            pickle.dump(cookies, f)
            
        print(f"✅ SUCCESS: Session cookies saved to {COOKIE_FILE}")
        print("👉 You can now run 'python src/fetch.py' to get your attendance.")

    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter to close browser...") 
    finally:
        driver.quit()

if __name__ == "__main__":
    run_auth()