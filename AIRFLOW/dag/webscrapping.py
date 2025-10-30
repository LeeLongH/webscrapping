#pip install beautifulsoup4
#pip3 install beautifulsoup4

#pip install bs4
from bs4 import BeautifulSoup
import requests
import firebase_admin
from firebase_admin import db, credentials
from datetime import datetime, timedelta
from functools import reduce

from studentski_servis import scrap_studentski_servis
from zrszz import scrap_ZRSZZ
from optius import scrap_optius
from mojedelo import scrap_mojedelo
from careerjet import scrap_careerjet

# --- Firebase setup ---
cred = credentials.Certificate("db-credentials.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://webscrapping-student-default-rtdb.europe-west1.firebasedatabase.app/"
})
ref = db.reference("/")

# --- Dates ---
today_date = datetime.today().strftime("%Y-%m-%d")
yesterday_date = (datetime.today() - timedelta(days=1))

def to_lower(str):

    if not str:
        return ""
    
    str = str.lower()
    dict = \
        ('študenti/ke', 'študenti'), \
        ('študenta/ko', 'študenta'), \
        ('študenta/ki', '2 študenta')
    
    str = reduce(lambda a, kv: a.replace(*kv), dict, str).capitalize()
    return str

# --- Shared functions ---

def push_to_db(*, title, location, description, uri):
    ref.push({
        "title": title,
        "location": location,
        "description": description,
        "uri": uri,
        "date": today_date
    })
    print(f"{title[:10]} pushed to DB")



    # Send webscrapped data from STUDETNSKI SERVIS to firebase

def insert_to_db_if_new_record(title, location, description, uri=False):
    # Get newest 10 records from DB
    records = ref.order_by_key().limit_to_last(10).get()
    
    # push straight away if no prior records in DB
    if not records:
        push_to_db(title=title, location=location, description=description, uri=uri)
        return

    # loop thru sorted records
    for key in sorted(records.keys(), reverse=True):
        record = records[key]
        record_date = datetime.strptime(record.get("date"), "%Y-%m-%d")
        if record_date < yesterday_date:
            # No new-ish record exists, add it to DB
            push_to_db(title=title, location=location, description=description, uri=uri)
            break
        else:
            if  record.get("title") == title and \
                record.get("location") == location and \
                record.get("description", "")[:10] == description[:10]:
                # The current record exists in DB, skip it
                print(f"Record {title[0:13]} exists in DB")
                break


# STUDENTKSI SERVIS ////////////////////////////////////////////////////////////////

URI_studentski_servis = ("https://www.studentski-servis.com/studenti/prosta-dela?isci=1&dd1=1&dm1s=1&skD[]=004&skD[]=A832&skD[]=A210&skD[]=A055&skD[]=A078&skD[]=A090&skD[]=A095&hourlyratefrom=6.32&hourlyrateto=36&hourly_rate=6.32%3B26&regija[]=ljubljana-z-okolico&regija[]=domzale-kamnik")

URL1_ZRSZZ = ("https://apigateway-osk8sdmz.ess.gov.si/iskalnik-po-pdm/v1/delovno-mesto/prosta-delovna-mesta-filtri")
URL2_ZRSZZ = ("https://apigateway-osk8sdmz.ess.gov.si/iskalnik-po-pdm/v1/delovno-mesto/podrobnosti-prosto-delovno-mesto")

URI_optius = ("https://www.optius.com/iskalci/prosta-delovna-mesta/?Keywords=&Fields%5B%5D=37&Regions%5B%5D=26&Time=1&doSearch=")

URI_mojedelo = ("https://www.mojedelo.com/iskanje-zaposlitve?jobCategoryIds=64f003ff-6d8b-4be0-b58c-4580e4eeeb8a&regionIds=d1dce9b1-9fa4-438b-b582-10d371d442e6&jobAdPostingDateId=3fafe213-6f6c-4fff-b07b-4747daf62260")

URI_careerjet = ("https://www.careerjet.si/delovna-mesta?s=podatkovni&l=Osrednjeslovenska")

#URI_webpage = URI_optius
#webpage = requests.get(URI_webpage).text
#soup = BeautifulSoup(webpage, 'html.parser')

#scrap_studentski_servis(BeautifulSoup(requests.get(URI_studentski_servis).text, 'html.parser'), insert_to_db_if_new_record, to_lower)
#scrap_ZRSZZ(URL1_ZRSZZ, URL2_ZRSZZ, insert_to_db_if_new_record, to_lower)
#scrap_optius(BeautifulSoup(requests.get(URI_optius).text, 'html.parser'), insert_to_db_if_new_record)
#scrap_mojedelo(insert_to_db_if_new_record)
scrap_careerjet(BeautifulSoup(requests.get(URI_careerjet).text, 'html.parser'), insert_to_db_if_new_record)








if __name__ == "__main__":
    print("\nmain executed")

