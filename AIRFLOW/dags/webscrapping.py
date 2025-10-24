#pip install beautifulsoup4
#pip3 install beautifulsoup4

#pip install bs4
from bs4 import BeautifulSoup
import requests
import firebase_admin
from firebase_admin import db, credentials
from datetime import datetime, timedelta

from studentski_servis import scrap_studentski_servis


# --- Firebase setup ---
cred = credentials.Certificate("db-credentials.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://webscrapping-student-default-rtdb.europe-west1.firebasedatabase.app/"
})
ref = db.reference("/")

# --- Dates ---
today_date = datetime.today().strftime("%Y-%m-%d")
yesterday_date = (datetime.today() - timedelta(days=1))


# --- SHared functions ---

def push_to_db(title,location,description,today_date):
    ref.push({
        "title": title,
        "location": location,
        "description": description,
        "date": today_date
    })



    # Send webscrapped data from STUDETNSKI SERVIS to firebase

def insert_to_db_if_new_record(title,location,description):
    # Get newest 10 records from DB
    records = ref.order_by_key().limit_to_last(10).get()
    
    # push straight away if no prior records in DB
    if not records:
        push_to_db(title,location,description,today_date)
        return

    # loop thru sorted records
    for key in sorted(records.keys(), reverse=True):
        record = records[key]
        record_date = datetime.strptime(record.get("date"), "%Y-%m-%d")
        if record_date < yesterday_date:
            # No new-ish record exists, add it to DB
            push_to_db(title,location,description,today_date)
            break
        else:
            if  record.get("title") == title and \
                record.get("location") == location and \
                record.get("description", "")[:10] == description[:10]:
                # The current record exists in DB, skip it
                print(f"Record {title[0:13]} exists in DB")
                break


# STUDENTKSI SERVIS ////////////////////////////////////////////////////////////////

URI_studentski_servis = " \
https://www.studentski-servis.com/studenti/prosta-dela?kljb=&page=1&isci=1&sort=&dd1=1&dm1s=1 \
&regija%5B%5D=ljubljana-z-okolico&regija%5B%5D=domzale-kamnik&skD%5B%5D=004&skD%5B%5D=A832&sk \
D%5B%5D=A210&skD%5B%5D=A055&skD%5B%5D=A078&skD%5B%5D=A090&skD%5B%5D=A095&hourlyratefrom=6.32&hourlyrateto=36&hourly_rate=6.32%3B41 \
"

webpage = requests.get(URI_studentski_servis).text
soup = BeautifulSoup(webpage, 'html.parser')

scrap_studentski_servis(soup, insert_to_db_if_new_record)














if __name__ == "__main__":
    print("main executed")

