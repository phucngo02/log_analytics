# alerts.py
import os
import requests
import smtplib
from email.message import EmailMessage

SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK_URL")
SMTP_SERVER = os.environ.get("ALERT_EMAIL_SMTP")
SMTP_USER = os.environ.get("ALERT_EMAIL_USER")
SMTP_PASS = os.environ.get("ALERT_EMAIL_PASS")

def send_slack_alert(text):
    if not SLACK_WEBHOOK:
        print("[alerts] No SLACK_WEBHOOK_URL configured.")
        return
    payload = {"text": text}
    try:
        r = requests.post(SLACK_WEBHOOK, json=payload, timeout=5)
        r.raise_for_status()
        print("[alerts] Slack alert sent.")
    except Exception as e:
        print("[alerts] Slack send failed:", e)

def send_email_alert(subject, body, to_addrs):
    if not (SMTP_SERVER and SMTP_USER and SMTP_PASS):
        print("[alerts] SMTP not configured.")
        return
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = ", ".join(to_addrs)
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(SMTP_SERVER, 587) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        print("[alerts] Email alert sent.")
    except Exception as e:
        print("[alerts] Email send failed:", e)
