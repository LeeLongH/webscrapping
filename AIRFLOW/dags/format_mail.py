import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from firebase_admin import db
from datetime import datetime
import firebase_admin
from firebase_admin import db, credentials

# --- helper function to build customer user-focused HTML ---
def build_html(jobs):
    if not jobs:
        return "<h3>No jobs found for today.</h3>"
    html = f"<h3>{len(jobs)} jobs today</h3>"
    
    for job in jobs:

        uri = job['uri']
        match uri:
            case _ if uri.startswith("https://www.optius"):
                source = "Optius"
            case _ if uri.startswith("https://www.ess"):
                source = "Zrszz"
            case _ if uri.startswith("https://www.studentski"):
                source = "Študentski servis"
            case _ if uri.startswith("https://www.mojedelo"):
                source = "Moje delo"
            case _ if uri.startswith("https://www.careerjet"):
                source = "Careerjet"
            case _:
                source = "source"

        html += f"""
        <p>
            <b>Title:</b> {job['title']}<br>
            <b>Location:</b> {job['location']}<br>
            <b>Description:</b> {job['description']}<br>
            <b>URI:</b> <a href="{uri}" target="_blank">{source}</a>
        </p>
        <hr>
        """
    return html
    #<b>URI:</b> <a href="{job['uri']}">{job['uri']}</a>

def compose_email(**kwargs):

    # --- Firebase reference ---
    if not firebase_admin._apps:
        cred = credentials.Certificate("/opt/airflow/db-credentials.json")
        firebase_admin.initialize_app(cred, {
            "databaseURL": "https://webscrapping-student-default-rtdb.europe-west1.firebasedatabase.app/"
        })

    ref = db.reference("/")
    today_date = datetime.today().strftime("%Y-%m-%d")

    # --- fetch today's jobs ---
    snapshot = ref.order_by_child("date").limit_to_last(20).get() or {}

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

    # --- filtering for Leon ---

    keywords = ["sql", "kafka", "airflow", "data", "engineer", "bigquery", "apache",
                "spark", "engineering", "etl", "python", "automate", "pandas", "numpy", 
                "postgre", "mysql", "mongodb", "databricks", "pipeline", "pipelines",
                "postgresql", "Tableau", "pyspark", "aws", "dashboards", "dashboard",
                "dbt", "hadoop", "snowflake", "redshift", "docker", "inženir", "podatkovni",
                "podatki", "baza", "baze"            
                ]
    
    leon_jobs = [
        job for job in todays_jobs
        if any(
            keyword in job["description"].lower() for keyword in keywords)
    ]

    # --- filtering for Tadej ---

    tadej_jobs = [job for job in todays_jobs if job['uri'].startswith("https://www.studentski")]

    # --- PREPARE EMAILS ---

    smtp_user = os.getenv("AIRFLOW__SMTP__SMTP_USER")
    smtp_pass = os.getenv("AIRFLOW__SMTP__SMTP_PASSWORD")

    recipient_info = {
        "leon.sturm2@gmail.com": leon_jobs
        ,"tadej.trobevsek10@gmail.com": tadej_jobs
        #,
        #"leelongmy@gmail.com": tadej_jobs
    }

    for recipient, job in recipient_info.items():

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Personalized job finder"
        msg["From"] = smtp_user
        msg["To"] = recipient
        msg.attach(MIMEText(build_html(job), "html"))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
                print(f"✅ Email sent successfully to {recipient}")
        except Exception as e:
            print(f"❌ Email sending failed to {recipient}: {e}")
            raise
