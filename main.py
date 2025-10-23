#pip install beautifulsoup4
#pip3 install beautifulsoup4

#pip install bs4
from bs4 import BeautifulSoup
import requests
import firebase_admin
from firebase_admin import db, credentials
from datetime import datetime

URI_studentski_servis = " \
https://www.studentski-servis.com/studenti/prosta-dela?kljb=&page=1&isci=1&sort=&dd1=1&dm1s=1 \
&regija%5B%5D=ljubljana-z-okolico&regija%5B%5D=domzale-kamnik&skD%5B%5D=004&skD%5B%5D=A832&sk \
D%5B%5D=A210&skD%5B%5D=A055&skD%5B%5D=A078&skD%5B%5D=A090&skD%5B%5D=A095&hourlyratefrom=6.32&hourlyrateto=36&hourly_rate=6.32%3B41 \
"

webpage = requests.get(URI_studentski_servis).text

soup = BeautifulSoup(webpage, 'html.parser')

cred = credentials.Certificate("db-credentials.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://webscrapping-student-default-rtdb.europe-west1.firebasedatabase.app/"
})

ref = db.reference("/")

articles = soup.body.main.find_all("article")

for article in articles:
    article_content = article.div.div
    titles = article_content.find_all('h5')

    if len(titles) == 1:
        title = f"{titles[0].get_text(strip=True)}"
    else:    
        title = f"{titles[0].get_text(strip=True)} : {titles[1].get_text(strip=True)}"
    description = article_content.find_all('p')[-1].string
    location = article_content.find_all('p')[1].get_text(separator=" ", strip=True)  # the <p> tag
    #print(title)
    #print(location)
    #print(description)
    #print("\n")

    #
    ref.push({
        "title": title,
        "location": location,
        "description": description,
        "date": datetime.today().strftime("%Y-%m-%d")
    })






