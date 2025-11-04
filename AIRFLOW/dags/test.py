import smtplib

smtp_user = "leon.sturm2@gmail.com"
smtp_pass = ""

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(smtp_user, smtp_pass)
server.sendmail(
    smtp_user,
    "leon.sturm2@gmail.com",
    "Subject: Test\n\nThis is a test email from Airflow container."
)
server.quit()
print("✅ Email sent successfully!")

