# chitkara-wrapper
---

# 🎓 Autonomous Academic Assistant

**(Day 1 – Core Engine Release)**

An intelligent automation layer built on top of the **Chalkpad Pro ERP** system.
This project handles login, OTP bypass, session reuse, and performs predictive analytics for attendance and grades.

---

## 🚀 Features (Phase 1 – Core Engine)

### 🔐 **Auto-Login + OTP Bypass**

Automates the entire login flow using Selenium + Gmail IMAP to retrieve OTPs.

### 🍪 **Session Hijacking / Reuse**

Extracts and stores the active `PHPSESSID` to avoid repeated logins and reduce server load.

### 📉 **Safe Bunk Calculator**

Parses attendance data and computes:

* How many classes you can safely skip
* Whether tomorrow is a risky bunk
* Subject-wise attendance vulnerability

---

## 🛠️ Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/academic-assistant.git
cd academic-assistant
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Fill in:

* `COLLEGE_ID`
* `COLLEGE_PASSWORD`
* `GMAIL_USER`
* `GMAIL_APP_PASSWORD`
* `OTP_EMAIL_SUBJECT_KEYWORD` (optional)

### 4️⃣ Run the Auth Engine

Logs into Chalkpad and saves the session cookie locally:

```bash
python auth.py
```

### 5️⃣ Run the Data Fetcher

Fetches attendance using the saved session and analyzes it:

```bash
python fetch.py
```

---

## ⚠️ Security Notice

* **Never** commit your `.env` file or `session.pkl` / `session_cookie.json`.
* `.gitignore` is preconfigured to keep sensitive files out of version control.
* Use **App Passwords** for Gmail instead of your real account password.

