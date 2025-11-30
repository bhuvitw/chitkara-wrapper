import os
import json

def create_env_file():
    print("🎓 College Assistant Setup Wizard")
    print("===============================")
    
    if os.path.exists(".env"):
        overwrite = input("⚠️ .env file already exists. Overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            return

    print("\n[1/2] College Credentials")
    user = input("Enter your Roll No (User ID): ")
    pwd = input("Enter your Password: ")
    
    print("\n[2/2] Gmail Credentials (For OTP)")
    print("NOTE: You must use an App Password, not your normal password.")
    gmail_user = input("Enter your Personal Gmail Address: ")
    gmail_pass = input("Enter your 16-digit App Password: ")
    
    env_content = f"""
COLLEGE_LOGIN_URL=https://cuiet.codebrigade.in/loginManager/load
COLLEGE_DASHBOARD_URL=https://cuiet.codebrigade.in/chalkpadpro/studentDetails/display
COLLEGE_USER={user}
COLLEGE_PASS={pwd}

GMAIL_USER={gmail_user}
GMAIL_APP_PASS={gmail_pass}
OTP_SENDER_EMAIL=no-reply@chitkara.edu.in
HEADLESS_MODE=False
"""
    
    with open(".env", "w") as f:
        f.write(env_content.strip())
    
    print("\n✅ Configuration saved to .env")

def create_timetable_template():
    if not os.path.exists("timetable.json"):
        print("\nCreating default timetable.json...")
        default_data = {
            "Monday": [{"subject": "Example Subject", "weight": 1}],
            "Tuesday": []
        }
        with open("timetable.json", "w") as f:
            json.dump(default_data, f, indent=4)
        print("✅ Created timetable.json. Please edit it with your schedule.")

if __name__ == "__main__":
    create_env_file()
    create_timetable_template()
    print("\n🎉 Setup Complete! Run 'python src/auth.py' to login.")