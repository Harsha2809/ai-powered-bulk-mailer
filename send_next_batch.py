# send_next_batch.py
"""
Send next batch of recipients from emails.csv using send_smtp-style logic.
Safe, resumable: logs results to results.csv, moves on after sending, writes failures.csv.
Usage: python send_next_batch.py
"""

from dotenv import load_dotenv
load_dotenv()

import os
import time
import ssl
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime
import re

# Environment config
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
CSV_FILE = os.getenv("CSV_FILE", "emails.csv")
RESULTS_FILE = os.getenv("RESULTS_FILE", "results.csv")
FAILURES_FILE = os.getenv("FAILURES_FILE", "failures.csv")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))
DELAY = int(os.getenv("DELAY_BETWEEN_EMAILS", "12"))
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# Email content (customize)
SUBJECT = os.getenv("EMAIL_SUBJECT", "Python Developer Opportunity Inquiry")
BODY_PLAIN = os.getenv("EMAIL_BODY", """Dear Hiring Team,

I hope you are well.

I am a Python developer with 3+ years of experience working with Django, FastAPI, and PostgreSQL. I am writing to ask if there are any current or upcoming openings for a Python Developer in your organization.

I can share my resume or portfolio on request. Thank you for your time.

Best regards,
Harshavardhan
Phone: +917780663452
""")

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

# Helpers
def read_emails(csv_path: Path):
    if not csv_path.exists():
        raise FileNotFoundError(f"{csv_path} not found")
    df = pd.read_csv(csv_path)
    if "email" not in df.columns:
        df.columns = ["email"] + list(df.columns[1:])
    # normalize & validate
    df["email"] = df["email"].astype(str).str.strip().str.lower()
    df = df[df["email"].str.match(EMAIL_REGEX)]
    return df

def write_emails(df, csv_path: Path):
    df.to_csv(csv_path, index=False)

def init_results(path: Path):
    if not path.exists():
        pd.DataFrame(columns=["email", "status", "error", "timestamp"]).to_csv(path, index=False)

def append_result(path: Path, email: str, status: str, error: str = ""):
    ts = datetime.utcnow().isoformat()
    pd.DataFrame([{"email": email, "status": status, "error": error, "timestamp": ts}]).to_csv(path, mode="a", header=False, index=False)

def append_failure(path: Path, email: str, error: str = ""):
    if not Path(path).exists():
        pd.DataFrame(columns=["email","error","timestamp"]).to_csv(path, index=False)
    ts = datetime.utcnow().isoformat()
    pd.DataFrame([{"email": email, "error": error, "timestamp": ts}]).to_csv(path, mode="a", header=False, index=False)

def make_message(sender: str, to_email: str):
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = SUBJECT
    msg.attach(MIMEText(BODY_PLAIN, "plain"))
    return msg

def smtp_connect_and_login():
    ctx = ssl.create_default_context()
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=60)
    server.ehlo()
    server.starttls(context=ctx)
    server.ehlo()
    server.login(SENDER_EMAIL, EMAIL_PASSWORD)
    return server

def send_to_recipient(server, sender, recipient):
    msg = make_message(sender, recipient)
    server.sendmail(sender, recipient, msg.as_string())

# Main
def main():
    # basic checks
    print("DEBUG: SENDER_EMAIL =", repr(SENDER_EMAIL))
    print("DEBUG: EMAIL_PASSWORD length =", len(EMAIL_PASSWORD or ""))

    if not SENDER_EMAIL or not EMAIL_PASSWORD:
        print("ERROR: Missing SENDER_EMAIL or EMAIL_PASSWORD in .env")
        return

    csv_path = Path(CSV_FILE)
    results_path = Path(RESULTS_FILE)
    failures_path = Path(FAILURES_FILE)

    init_results(results_path)

    try:
        df = read_emails(csv_path)
    except Exception as e:
        print("Error reading emails CSV:", e)
        return

    if df.empty:
        print("No valid emails in", CSV_FILE)
        return

    # take the top BATCH_SIZE rows
    batch_df = df.head(BATCH_SIZE).copy()
    remaining_df = df.iloc[BATCH_SIZE:].copy()

    print(f"Preparing to send to {len(batch_df)} recipients (batch size = {BATCH_SIZE})")

    # connect once
    try:
        server = smtp_connect_and_login()
    except Exception as e:
        print("Failed to connect/login to SMTP server:", e)
        return

    # send loop with retries
    for idx, row in batch_df.reset_index().iterrows():
        recipient = row["email"]
        max_retries = 2
        attempt = 0
        sent = False
        last_error = ""
        while attempt <= max_retries and not sent:
            attempt += 1
            try:
                send_to_recipient(server, SENDER_EMAIL, recipient)
                append_result(results_path, recipient, "sent", "")
                print(f"[{idx+1}] Sent to {recipient}")
                sent = True
            except smtplib.SMTPRecipientsRefused as e:
                last_error = f"recipient refused: {e}"
                append_result(results_path, recipient, "failed_permanent", last_error)
                append_failure(failures_path, recipient, last_error)
                print(f"[{idx+1}] Permanent fail for {recipient}: {e}")
                break
            except Exception as e:
                last_error = str(e)
                print(f"[{idx+1}] Attempt {attempt} failed for {recipient}: {e}")
                time.sleep(5 * attempt)
                if attempt > max_retries:
                    append_result(results_path, recipient, "failed", last_error)
                    append_failure(failures_path, recipient, last_error)
        time.sleep(DELAY)

    # close server
    try:
        server.quit()
    except Exception:
        pass

    # write remaining emails back to CSV (so next run picks up where we left off)
    write_emails(remaining_df, csv_path)
    print("Batch complete. Remaining:", len(remaining_df))
    print("Results written to", RESULTS_FILE, "Failures to", FAILURES_FILE)

if __name__ == "__main__":
    main()
