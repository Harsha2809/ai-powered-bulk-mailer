# 📧 Bulk Email Automation – Python

A Python-based automation tool to:

* Extract emails from a PDF
* Clean & deduplicate email list
* Send emails in batches (e.g., 50 at a time)
* Support HTML emails + plain text fallback
* Attach resume automatically
* Log results (sent / failed)

---

# 🚀 Features

* 📄 Extract emails from PDF (`pdfplumber`)
* 🧹 Remove duplicates & invalid emails
* 📬 Send bulk emails via Gmail SMTP
* 🎨 Attractive HTML email template
* 📎 Resume attachment support
* 🔁 Batch sending (safe sending)
* 📊 Logging system (`results.csv`)
* ⚡ Easy configuration using `.env`

---

# 📂 Project Structure

```
bulk_mailer/
│
├── .env
├── emails.pdf
├── emails.csv
├── results.csv
├── extract_emails.py
├── send_smtp.py
├── send_html_email.py
├── preview_html.py
├── requirements.txt
├── README.md
│
├── templates/
│   ├── email_template.html
│   └── email_template.txt
│
└── static/
    └── logo.png
```

---

# ⚙️ Setup Instructions

## 1️⃣ Navigate to Project

```
cd bulk_mailer
```

## 2️⃣ Create Virtual Environment

```
python -m venv venv
venv\Scripts\activate
```

## 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

# 🔐 Gmail Setup (IMPORTANT)

## Step 1: Enable 2-Step Verification

https://myaccount.google.com/security

## Step 2: Generate App Password

https://myaccount.google.com/apppasswords

Example:

```
abcdefghijklmnop
```

## Step 3: Update `.env`

```
SENDER_EMAIL=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
BATCH_SIZE=50
DELAY_BETWEEN_EMAILS=10
CSV_FILE=emails.csv
RESULTS_FILE=results.csv
LINKEDIN_URL=https://www.linkedin.com/in/harsha2323
RESUME_FILE=resume.pdf
```

---

# 📄 Extract Emails from PDF

```
python extract_emails.py
```

---

# 👀 Preview HTML Email

```
python preview_html.py
```

---

# 📬 Send Emails

## Plain Text

```
python send_smtp.py
```

## HTML Version (Recommended)

```
python send_html_email.py
```

---

# 🔁 Batch Sending Logic

* Sends first **N emails** (BATCH_SIZE)
* Removes them from CSV
* Next run → sends next batch

---

# 📊 Output (Logs)

`results.csv`

| email                                   | status | error | timestamp |
| --------------------------------------- | ------ | ----- | --------- |
| [test@gmail.com](mailto:test@gmail.com) | sent   |       | 2025-...  |

---

# ✏️ Customize Email

## Plain Email

Edit:

```
send_smtp.py
```

## HTML Email

Edit:

```
templates/email_template.html
```

---

# 📎 Add Resume

Place file:

```
resume.pdf
```

Update `.env`:

```
RESUME_FILE=resume.pdf
```

---

# 🚨 Common Issues

* Use App Password (not Gmail password)
* Ensure `emails.csv` is not empty
* Run commands in correct folder

---

# 💡 Best Practices

* Start with **BATCH_SIZE=1**
* Increase to **50** after testing
* Use delay to avoid spam flags

---

# 👨‍💻 Author

Harsha Vardhan
📞 +91 6302146916
🔗 https://www.linkedin.com/in/harsha2323

---

# 🎯 Final Result

✔ Automated job application system
✔ Saves time
✔ Improves reach
✔ Professional email delivery
