import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ✅ Your email credentials
SENDER_EMAIL = "yogeshdark2527@gmail.com"          # 🔁 Replace with your Gmail
SENDER_PASSWORD = "gpzb hszg thff mevr"          # 🔁 Replace with App Password if 2FA is on

# 📤 Email subject and body (template with {name})
EMAIL_SUBJECT = "Welcome to the Team!"
EMAIL_BODY = """
Hi {name},

Welcome to our organization! We're excited to have you on board.

If you have any questions, feel free to reach out.

Best regards,  
HR Team
"""

# 📁 Read recipients from CSV
try:
    data = pd.read_csv(r"C:\areef\thaha1.csv")
except Exception as e:
    print(f"❌ Error reading CSV: {e}")
    exit()

# 📬 Function to send email
def send_email(to_email, to_name):
    try:
        # Compose email
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = EMAIL_SUBJECT

        personalized_body = EMAIL_BODY.format(name=to_name)
        msg.attach(MIMEText(personalized_body, "plain"))

        # Connect to Gmail SMTP
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        print(f"✅ Email sent to {to_name} ({to_email})")

    except Exception as e:
        print(f"❌ Failed to send email to {to_name} ({to_email}): {e}")

# 🚀 Send emails in loop
for index, row in data.iterrows():
    name = row["name"]
    email = row["Email"]
    send_email(email, name)
print("success")
