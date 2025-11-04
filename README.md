# webscrapping




docker exec -it dag_jobs_webscrapping-webscrapping-1 bash
telnet smtp.gmail.com 587


docker exec -it dag_jobs_webscrapping-webscrapping-1 bash
pip install firebase-admin

pip list | grep firebase-admin

docker-compose down
docker-compose build
docker-compose up -d

docker compose down
docker compose up -d --build


docker exec -it dag_jobs_webscrapping-webscrapping-1 bash
python -m pip show firebase-admin
python -m pip show beautifulsoup4

# Enter container shell
docker exec -it dag_jobs_webscrapping-webscrapping-1 bash

# Install packages for Airflow user
pip install --user firebase-admin beautifulsoup4 requests selenium

# Verify
pip list | grep -e firebase -e firebase-admin -e beautifulsoup4 -e selenium



docker exec -it dag_jobs_webscrapping-webscrapping-1 bash
python -m pip show firebase-admin
python -m pip show beautifulsoup4

docker exec -it dag_jobs_webscrapping-webscrapping-1 airflow dags trigger Job_Scrapping



import smtplib

smtp_user = "leon.sturm2@gmail.com" 
smtp_pass = "..."

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(smtp_user, smtp_pass)
    server.sendmail(
        smtp_user,
        "leon.sturm2@gmail.com", 
        "Subject: SMTP Test\n\nThis is a test email from Airflow container."
    )

print("✅ Email sent successfully!")


