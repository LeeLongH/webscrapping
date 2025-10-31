# webscrapping







docker exec -it dag_jobs_webscrapping-webscrapping-1 bash
pip install firebase-admin

pip list | grep firebase-admin

docker-compose down
docker-compose build
docker-compose up -d

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
