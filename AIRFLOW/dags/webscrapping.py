#pip install beautifulsoup4
#pip3 install beautifulsoup4
#pip install bs4

from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import db, credentials
import requests
from datetime import datetime, timedelta
from functools import reduce

from studentski_servis import scrap_studentski_servis
from zrszz import scrap_ZRSZZ
from optius import scrap_optius
from mojedelo import scrap_mojedelo
from careerjet import scrap_careerjet

NUM_OF_JOBS_TO_READ = 30

def run_webscrapping(is_manually_ran=False):

    # --- Firebase setup ---
    if __name__ == "__main__":
        cred = credentials.Certificate("db-credentials.json")
    else:
        cred = credentials.Certificate("/opt/airflow/db-credentials.json")

    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://webscrapping-student-default-rtdb.europe-west1.firebasedatabase.app/"
    })
    ref = db.reference("/")

    # --- Dates ---
    today_date = datetime.today().strftime("%Y-%m-%d")
    yesterday_date = (datetime.today() - timedelta(days=1))

    def get_todays_jobs():
        """
        Fetch all Firebase jobs where 'date' equals today.
        Returns a list of dicts with fields: title, location, description, uri.
        """
        jobs_ref = db.reference("jobs")  # replace "jobs" with your node name
        snapshot = jobs_ref.get()  # fetch all jobs

        jobs = []
        if snapshot:
            for key, data in snapshot.items():
                if data.get("date") == today_date:
                    jobs.append({
                        "title": data.get("title", "No title"),
                        "location": data.get("location", "No location"),
                        "description": data.get("description", "No description"),
                        "uri": data.get("uri", "No link")
                    })
        return jobs


    def to_lower(str):

        if not str:
            return ""
        
        str = str.lower()
        dict = \
            ('študenti/ke', 'študenti'), \
            ('študenta/ko', 'študenta'), \
            ('študenta/ki', '2 študenta'), \
            ('asistenta/ko','asistenta')
        
        #m/ž
        
        str = reduce(lambda a, kv: a.replace(*kv), dict, str).capitalize()
        return str

    def push_to_db(*, title, location, description, uri, ti=None):
        ref.push({
            "title": title,
            "location": location,
            "description": description,
            "uri": uri,
            "date": today_date
        })
        print(f"{title[:10]} pushed to DB")

    def insert_to_db_if_new_record(title, location, description, uri=False):
        # Get newest 10 records from DB
        records = ref.order_by_key().limit_to_last(NUM_OF_JOBS_TO_READ).get()
        
        # push straight away if no prior records in DB
        if not records:
            print("No prior records in Firebase")
            push_to_db(title=title, location=location, description=description, uri=uri)
            return

        duplicate_found = False 

        # loop thru sorted records
        for key in sorted(records.keys(), reverse=True):
            record = records[key]
            record_date = datetime.strptime(record.get("date"), "%Y-%m-%d")

            if record_date >= yesterday_date: # get only recent DB records
                if  record.get("uri") == uri:
                    duplicate_found = True
                    print(f"Record {title[0:13]} exists in DB")
                    break

                
        if not duplicate_found:
            push_to_db(title=title, location=location, description=description, uri=uri)


    URI_studentski_servis = ("https://www.studentski-servis.com/studenti/prosta-dela?isci=1&dd1=1&dm1s=1&skD[]=004&skD[]=A832&skD[]=A210&skD[]=A055&skD[]=A078&skD[]=A090&skD[]=A095&hourlyratefrom=6.32&hourlyrateto=36&hourly_rate=6.32%3B26&regija[]=ljubljana-z-okolico&regija[]=domzale-kamnik")

    URL1_ZRSZZ = ("https://apigateway-osk8sdmz.ess.gov.si/iskalnik-po-pdm/v1/delovno-mesto/prosta-delovna-mesta-filtri")
    URL2_ZRSZZ = ("https://apigateway-osk8sdmz.ess.gov.si/iskalnik-po-pdm/v1/delovno-mesto/podrobnosti-prosto-delovno-mesto")

    URI_optius = ("https://www.optius.com/iskalci/prosta-delovna-mesta/?Keywords=&Fields%5B%5D=37&Regions%5B%5D=26&Time=1&doSearch=")

    # Incomplete URI with missing UUID date for job post query. URI gets correctly filled up inside mojdelo.py after API call inquiring today's UUID
    URI_mojedelo="https://api.mojedelo.com/job-ads-search?jobCategoryIds=64f003ff-6d8b-4be0-b58c-4580e4eeeb8a&regionIds=d1dce9b1-9fa4-438b-b582-10d371d442e6&pageSize=20&startFrom=0"

    URI_careerjet = ("https://www.careerjet.si/delovna-mesta?s=podatkovni&l=Osrednjeslovenska&nw=1")

    #URI_webpage = URI_optius
    #webpage = requests.get(URI_webpage).text
    #soup = BeautifulSoup(webpage, 'html.parser')

    scrap_studentski_servis(BeautifulSoup(requests.get(URI_studentski_servis).text, 'html.parser'), insert_to_db_if_new_record, to_lower)
    scrap_ZRSZZ(URL1_ZRSZZ, URL2_ZRSZZ, insert_to_db_if_new_record, to_lower)
    scrap_optius(BeautifulSoup(requests.get(URI_optius).text, 'html.parser'), insert_to_db_if_new_record)
    scrap_mojedelo(URI_mojedelo, insert_to_db_if_new_record)
    if __name__ != "__main__":
        scrap_careerjet(URI_careerjet, insert_to_db_if_new_record)

    if not is_manually_ran:
        with open("/opt/airflow/logs/log.txt", "w") as f:
            log = "Great success: " + str(datetime.now())
            f.write(log)

    # Get today's Firebase jobs
    todays_jobs = get_todays_jobs()
     # Return results so DAG can include them in email
    return {"jobs": todays_jobs}


if __name__ == "__main__":
    run_webscrapping(is_manually_ran=True)

