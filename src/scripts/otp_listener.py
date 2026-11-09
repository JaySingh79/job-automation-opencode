"""
Automated IMAP OTP Listener for Greenhouse / ATS Email Verification Codes.
Listens to Gmail INBOX via IMAP SSL to fetch verification codes sent to jays.iitkgp@gmail.com.
"""
import imaplib
import email
from email.header import decode_header
import re
import time
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

DEFAULT_EMAIL = "jays.iitkgp@gmail.com"
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

def clean_header(val):
    if not val:
        return ""
    decoded_list = decode_header(val)
    parts = []
    for text, encoding in decoded_list:
        if isinstance(text, bytes):
            parts.append(text.decode(encoding or "utf-8", errors="ignore"))
        else:
            parts.append(str(text))
    return "".join(parts)

def extract_otp_from_body(body_text: str) -> str:
    """
    Extracts 6 to 8 character alphanumeric verification code from email body.
    Greenhouse typically uses 8 alphanumeric characters or 6 digits.
    """
    # Pattern 1: Explicit 'verification code is XXXXXXXX' or 'security code: XXXXXXXX'
    m = re.search(r'(?:verification|security)\s+code\s+(?:is|:)?\s*([A-Za-z0-9]{6,8})\b', body_text, re.IGNORECASE)
    if m:
        return m.group(1).strip()

    # Pattern 1b: Greenhouse 'Copy and paste this code into the security code field...: XXXXXXXX'
    m = re.search(r'security\s+code\s+field[^\n\r]*?[:\s\n]+([A-Za-z0-9]{8})\b', body_text, re.IGNORECASE)
    if m:
        return m.group(1).strip()

    # Pattern 2: 'enter the 8-character code to confirm... : XXXXXXXX'
    m = re.search(r'(?:enter\s+the\s+8-character\s+code[^\n\r]*?)[:\s]+([A-Za-z0-9]{8})\b', body_text, re.IGNORECASE)
    if m:
        return m.group(1).strip()

    # Pattern 3: Standalone 8-character block (uppercase/mixed alphanumeric)
    # Greenhouse often places code in <h2> or prominent paragraph
    m = re.findall(r'\b[A-Za-z0-9]{8}\b', body_text)
    for code in m:
        # Avoid common false positive 8-char words
        if code.lower() not in ["greenhou", "security", "received", "complete", "settings", "feedback", "personal"]:
            # Check if has both letters and numbers or uppercase
            if any(c.isdigit() for c in code) or code.isupper():
                return code

    # Pattern 4: 6-digit numeric OTP
    m = re.search(r'\b(\d{6})\b', body_text)
    if m:
        return m.group(1).strip()

    return ""

def fetch_latest_otp(
    email_address: str = DEFAULT_EMAIL,
    app_password: str = None,
    max_wait_seconds: int = 40,
    poll_interval: int = 3,
    sender_filter: str = "greenhouse",
    min_date_epoch: float = None
) -> str:
    """
    Polls IMAP INBOX for the latest verification code received after min_date_epoch (or within last 3 minutes).
    """
    pw = app_password or os.getenv("GMAIL_APP_PASSWORD") or os.getenv("IMAP_PASSWORD")
    if not pw:
        print("[OTP LISTENER] Error: No GMAIL_APP_PASSWORD found in environment or arguments.", file=sys.stderr)
        return ""

    # Clean whitespace in app password if user passed with spaces
    pw = pw.replace(" ", "")

    t_start = time.time()
    min_timestamp = min_date_epoch or (time.time() - 180)
    print(f"[OTP LISTENER] Connecting to {IMAP_SERVER} for {email_address} (min_timestamp={min_timestamp})...")

    while (time.time() - t_start) < max_wait_seconds:
        try:
            mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
            mail.login(email_address, pw)
            mail.select("INBOX")

            # Search recent messages
            status, messages = mail.search(None, 'ALL')
            if status != "OK" or not messages[0]:
                mail.logout()
                time.sleep(poll_interval)
                continue

            msg_ids = messages[0].split()
            # Inspect last 7 messages from newest to oldest
            for msg_id in reversed(msg_ids[-7:]):
                res, data = mail.fetch(msg_id, '(RFC822)')
                if res != "OK":
                    continue

                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)

                sender = clean_header(msg.get("From", "")).lower()
                subject = clean_header(msg.get("Subject", "")).lower()
                date_str = msg.get("Date", "")
                
                # Check email timestamp if available
                if date_str and min_timestamp:
                    try:
                        msg_time = email.utils.parsedate_to_datetime(date_str).timestamp()
                        # Allow up to 10s clock skew
                        if msg_time < (min_timestamp - 10):
                            continue
                    except Exception:
                        pass

                # Filter sender or subject
                is_match = False
                if sender_filter and sender_filter in sender:
                    is_match = True
                elif any(k in subject for k in ["verification", "security code", "confirm you're a human", "code"]):
                    is_match = True

                if not is_match:
                    continue

                # Extract plain text body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        cdispo = str(part.get("Content-Disposition"))
                        if ctype == "text/plain" and "attachment" not in cdispo:
                            body += part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        elif ctype == "text/html" and not body and "attachment" not in cdispo:
                            html_text = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                            # Simple strip tags
                            body += re.sub(r'<[^>]+>', ' ', html_text)
                else:
                    body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

                otp = extract_otp_from_body(body)
                if otp:
                    print(f"[OTP LISTENER] Extracted OTP code: {otp} from '{subject}'")
                    mail.logout()
                    return otp

            mail.logout()
        except Exception as e:
            print(f"[OTP LISTENER] Poll warning: {e}", file=sys.stderr)

        time.sleep(poll_interval)

    print("[OTP LISTENER] Timeout waiting for OTP email.", file=sys.stderr)
    return ""


if __name__ == "__main__":
    test_pw = sys.argv[1] if len(sys.argv) > 1 else None
    print("Testing OTP Listener...")
    code = fetch_latest_otp(app_password=test_pw, max_wait_seconds=15)
    print(f"Result OTP: {code}")
