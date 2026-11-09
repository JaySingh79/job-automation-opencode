import imaplib
import email
import os
from dotenv import load_dotenv

load_dotenv()
mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
mail.login("jays.iitkgp@gmail.com", os.getenv("GMAIL_APP_PASSWORD"))
mail.select("INBOX")

res, data = mail.fetch("10675", "(RFC822)")
msg = email.message_from_bytes(data[0][1])

for part in msg.walk():
    if part.get_content_type() == "text/plain":
        print("--- TEXT/PLAIN ---")
        print(part.get_payload(decode=True).decode("utf-8", errors="ignore"))
    elif part.get_content_type() == "text/html":
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(part.get_payload(decode=True).decode("utf-8", errors="ignore"), "html.parser")
        print("--- TEXT IN HTML ---")
        print(soup.get_text())

mail.logout()
