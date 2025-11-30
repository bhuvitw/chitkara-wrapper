# 🎓 College Assistant CLI

*A smart automation tool for Chalkpad Pro ERP users.*

College Assistant CLI is a command-line companion that handles your Chalkpad login, tracks your attendance, and uses predictive analytics to help you decide exactly when you can safely bunk without dropping below your target percentage.

---

## ✨ Features

* **🔐 Auto-Login**
  Automatically bypasses OTP fatigue using Gmail automation.

* **🧠 Session Caching**
  Authenticate once — stay logged in for hours.

* **📊 Smart Attendance Planner**
  Enter your target attendance (e.g., 76%) and get precise recommendations on which classes to attend or skip.

* **🎨 Rich CLI Dashboard**
  Clean, colorful terminal UI powered by `rich`.


## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/college-assistant.git
cd college-assistant
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

* Rename `.env.example` → `.env`
* Add your Chalkpad + Gmail credentials.
* Update `timetable.json` with your class schedule.

---

## 🛠️ Usage

### Login

```bash
python auth.py
```
<img width="725" height="392" alt="image" src="https://github.com/user-attachments/assets/e659caef-758b-48e5-bcbe-17bdfa906d98" />


### Fetch Attendance

```bash
python fetch.py
```
<img width="998" height="320" alt="image" src="https://github.com/user-attachments/assets/97dfb29d-8bf5-43c9-82ae-16d4500bf245" />


### Weekly Planner

```bash
python planner.py
```
<img width="1123" height="293" alt="image" src="https://github.com/user-attachments/assets/5f5e178a-74d5-4806-85a4-7de9a176066d" />


---

## ⚠️ Disclaimer

This project is for **educational and personal automation purposes only**.
Use responsibly and at your own risk.

