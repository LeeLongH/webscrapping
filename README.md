# webscrapping

1) webscrapping from:
- Študentski servis
- Optius
- ZRSZZ
- Careerjet
- Moje delo

2) Loaded into Firebase (DAG)

3) Job posts notified via emails (DAG), adjusted for different users 

Batch file turns Docker on/off, unpaused the DAG and starts it


# Some commands

docker exec -it dag_jobs_webscrapping-webscrapping-1 bash

docker-compose down
docker-compose build
docker-compose up -d --build

python -m pip show firebase-admin
python -m pip show beautifulsoup4

# Enter container shell
docker exec -it dag_jobs_webscrapping-webscrapping-1 bash

# Install packages for Airflow user
pip install --user firebase-admin beautifulsoup4 requests selenium webdriver_manager

# Verify
pip list | grep -e firebase -e firebase-admin -e beautifulsoup4 -e selenium -e webdriver_manager -e requests


docker exec -it dag_jobs_webscrapping-webscrapping-1 airflow dags trigger Job_Scrapping


