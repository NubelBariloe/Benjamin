from smtplib import SMTP_SSL
from email.message import EmailMessage

msg = EmailMessage()
msg["Subject"] = "Registration Confirmation"
msg["From"] = my_email
msg["To"] = mail

msg.set_content(
    f"""Dear {name},

Thank you for registering for the {course} course at Nubels Digital Academy.

We're delighted to have you join us and look forward to supporting you throughout your learning journey. Get ready to learn, develop new skills, and make the most of your training experience.

Thank you for choosing Nubels Digital Academy.

Welcome aboard! 🚀

Best regards,
Nubels Digital Academy
"""
)

with SMTP_SSL("smtp.gmail.com", 465, timeout=30) as connection:
    connection.login(my_email, password)
    connection.send_message(msg)