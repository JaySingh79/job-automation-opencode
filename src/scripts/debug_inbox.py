import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv()

user = "jays.iitkgp@gmail.com"
password = os.getenv("GMAIL_APP_PASSWORD")

mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
mail.login(user, password)
mail.select("INBOX")

status, messages = mail.search(None, "ALL")
msg_ids = messages[0].split()
print("Total messages in INBOX:", len(msg_ids))

for mid in msg_ids[-10:]:
    res, data = mail.fetch(mid, "(RFC822.HEADER)")
    msg = email.message_from_bytes(data[0][1])
    subj = msg.get("Subject", "")
    print(f"ID {mid.decode()}: Subject: '{subj}', From: '{msg.get('From')}', Date: '{msg.get('Date')}'")

mail.logout()
