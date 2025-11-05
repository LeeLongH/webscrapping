import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from firebase_admin import db
from datetime import datetime
import firebase_admin
from firebase_admin import db, credentials

def compose_email(**kwargs):
    # --- Firebase reference ---
    if not firebase_admin._apps:
        cred = credentials.Certificate("/opt/airflow/db-credentials.json")
        firebase_admin.initialize_app(cred, {
            "databaseURL": "https://webscrapping-student-default-rtdb.europe-west1.firebasedatabase.app/"
        })

    ref = db.reference("/")
    today_date = datetime.today().strftime("%Y-%m-%d")

    # --- fetch todays jobs ---
    snapshot = ref.get()

    todays_jobs = [
        {
            "title": data.get("title", "No title"),
            "location": data.get("location", "No location"),
            "description": data.get("description", "No description"),
            "uri": data.get("uri", "No link")
        }
        for key, data in (snapshot or {}).items()
        if data.get("date") == today_date
    ]

    # --- compose email ---
    subject = "Webscraping DAG Report"

    if not todays_jobs:
        html_content = "<h3>No jobs found for today.</h3>"
    else:
        html_content = f"""<h3>Today's Jobs = {len(todays_jobs)}</h3>"""
        for job in todays_jobs:
            html_content += f"""
            <p>
                <b>Title:</b> {job['title']}<br>
                <b>Location:</b> {job['location']}<br>
                <b>Description:</b> {job['description']}<br>
                <b>URI:</b> <a href="{job['uri']}">{job['uri']}</a>
            </p>
            <hr>
            """

    # --- use smtplib directly instead of Airflow's send_email ---
    smtp_user = os.getenv("AIRFLOW__SMTP__SMTP_USER")
    smtp_pass = os.getenv("AIRFLOW__SMTP__SMTP_PASSWORD")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    #msg["To"] = "leon.sturm2@gmail.com"
    recipients = "leon.sturm2@gmail.com, aljaz.trobevsek1@gmail.com"
    msg["To"] = recipients
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            print("✅ Email sent successfully from Airflow DAG!")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        raise
