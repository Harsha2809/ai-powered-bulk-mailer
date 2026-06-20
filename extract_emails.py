# extract_emails.py (UPDATED FINAL VERSION)

import re
import pdfplumber
import pandas as pd
from pathlib import Path
import sys

# Regex to match email addresses
EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE
)

# Input and output paths
PDF_PATH = Path("emails.pdf")   # your PDF file
OUT_CSV = Path("emails.csv")    # extracted email list output

def extract_emails(pdf_path: Path):
    """Extract emails from a PDF, page by page."""
    emails = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                found = EMAIL_RE.findall(text)
                emails.extend(found)
    except Exception as e:
        print(f"❌ Error reading PDF {pdf_path}: {e}")
        sys.exit(1)

    return emails

def clean_and_dedupe(emails):
    """Normalize case, trim whitespace, remove duplicates."""
    cleaned = []
    seen = set()

    for e in emails:
        e2 = e.strip().lower()
        if e2 and e2 not in seen:
            seen.add(e2)
            cleaned.append(e2)

    return cleaned

def main():
    # Check PDF existence
    if not PDF_PATH.exists():
        print(f"⚠️ PDF file not found: {PDF_PATH.resolve()}")
        return

    print(f"📄 Starting extraction from: {PDF_PATH}")

    # Extract raw emails
    raw_emails = extract_emails(PDF_PATH)
    print(f"📥 Raw matches found: {len(raw_emails)}")

    # Clean, lowercase, dedupe
    emails = clean_and_dedupe(raw_emails)
    print(f"✨ Unique cleaned emails: {len(emails)}")

    if not emails:
        print("❌ No valid emails found. Stopping.")
        return

    # Save to CSV
    df = pd.DataFrame({"email": emails})
    df.to_csv(OUT_CSV, index=False)

    print(f"✅ Successfully saved to: {OUT_CSV}")
    print(f"📌 Preview of extracted emails:\n{df.head(10).to_string(index=False)}")

if __name__ == "__main__":
    main()
