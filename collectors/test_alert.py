
from dotenv import load_dotenv
import os

# load file .env trong cùng folder script
load_dotenv(dotenv_path=".env")

print("SMTP_SERVER:", os.environ.get("ALERT_EMAIL_SMTP"))
print("SMTP_USER:", os.environ.get("ALERT_EMAIL_USER"))
print("SMTP_PASS:", os.environ.get("ALERT_EMAIL_PASS"))


from alerts import send_email_alert

send_email_alert(
    subject="Test Email",
    body="This is a test alert email",
    to_addrs=["ngothiphucqn12345@gmail.com"]
)
