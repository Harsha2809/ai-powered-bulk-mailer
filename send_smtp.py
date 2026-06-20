# send_smtp.py - REPLACED CLEAN VERSION

from dotenv import load_dotenv
load_dotenv()  # MUST run before os.getenv

import os
import time
import smtplib
import ssl
import pandas as pd
from tqdm import tqdm
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime
import re
from ai_email_generator import generate_email

# --- load env ---
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
CSV_FILE = os.getenv("CSV_FILE", "emails.csv")
RESULTS_FILE = os.getenv("RESULTS_FILE", "results.csv")
try:
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))
except:
    BATCH_SIZE = 50
try:
    DELAY = int(os.getenv("DELAY_BETWEEN_EMAILS", "12"))
except:
    DELAY = 12

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# quick debug to confirm env loading
print("DEBUG: SENDER_EMAIL =", repr(SENDER_EMAIL))
print("DEBUG: EMAIL_PASSWORD length =", len(EMAIL_PASSWORD or ""))

# --- content ---
# SUBJECT = "Python Developer Opportunity"

# BODY_PLAIN = """Hello,

# I am Harsha Vardhan, a Python Developer with ~4 years of experience in Django, FastAPI, PostgreSQL, and AWS (Lambda, S3, SQS).

# I have worked on scalable REST APIs, ETL pipelines, and real-time data processing systems in projects like Profitero and Royalty Exchange.

# I am currently looking for Python Developer opportunities. Please let me know if there are any openings.

# LinkedIn: www.linkedin.com/in/harsha2323

# Phone: +91 6302146916

# Thanks & Regards,  
# Harsha Vardhan
# """

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

# --- helpers ---
def read_emails(csv_path: str):
    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(f"{csv_path} not found")
    df = pd.read_csv(p)
    if "email" not in df.columns:
        df.columns = ["email"] + list(df.columns[1:])
    emails = [str(e).strip().lower() for e in df["email"].tolist() if str(e).strip()]
    validated = [e for e in emails if EMAIL_REGEX.match(e)]
    return validated

def init_results_file(path: str):
    p = Path(path)
    if not p.exists():
        df = pd.DataFrame(columns=["email","status","error","timestamp"])
        df.to_csv(p, index=False)

def log_result(path: str, email: str, status: str, error: str = ""):
    ts = datetime.utcnow().isoformat()
    df = pd.DataFrame([{"email": email, "status": status, "error": error, "timestamp": ts}])
    df.to_csv(path, mode="a", header=False, index=False)

def make_message(to_email: str):

    ai_content = generate_email("Company")

    msg = MIMEMultipart()

    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = "Python Developer Opportunity"

    msg.attach(MIMEText(ai_content, "plain"))

    return msg

def send_batch(emails):
    # ensure we have valid credentials before connecting
    if not SENDER_EMAIL or not EMAIL_PASSWORD:
        print("ERROR: Missing SENDER_EMAIL or EMAIL_PASSWORD. Check your .env file.")
        return

    context = ssl.create_default_context()
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=60)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
    except Exception as e:
        print(f"Failed to connect/login to SMTP server: {e}")
        return

    for idx, recipient in enumerate(tqdm(emails, desc="Sending")):
        try:
            msg = make_message(recipient)
            server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
            log_result(RESULTS_FILE, recipient, "sent", "")
            print(f"[{idx+1}] Sent to {recipient}")
        except Exception as e:
            log_result(RESULTS_FILE, recipient, "failed", str(e))
            print(f"[{idx+1}] Failed to {recipient}: {e}")
        time.sleep(DELAY)

    try:
        server.quit()
    except Exception:
        pass

def main():
    try:
        emails = read_emails(CSV_FILE)
    except Exception as e:
        print(f"Error reading emails CSV: {e}")
        return

    if not emails:
        print("No valid emails to send to. Check CSV_FILE contents.")
        return
    print("\nAI GENERATED EMAIL:\n")
    print(generate_email("Google"))
    print("\n" + "="*60 + "\n")
    targets = emails[:BATCH_SIZE]
    print(f"Will send to {len(targets)} recipients (batch size = {BATCH_SIZE}).")
    init_results_file(RESULTS_FILE)
    send_batch(targets)
    print("Done. Check results.csv for details.")

if __name__ == "__main__":
    main()

