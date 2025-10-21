#pip install beautifulsoup4
#pip3 install beautifulsoup4

#pip install bs4
from bs4 import BeautifulSoup
import requests


URI_studentski_servis = "https://www.studentski-servis.com/studenti/prosta-dela?kljb=&page=1&isci=1&sort=&dm1=1&dm1s=1&regija%5B%5D=ljubljana-z-okolico&regija%5B%5D=domzale-kamnik&skD%5B%5D=004&skD%5B%5D=A832&skD%5B%5D=A210&skD%5B%5D=A055&skD%5B%5D=A078&skD%5B%5D=A090&skD%5B%5D=A095&hourlyratefrom=6.32&hourlyrateto=36&hourly_rate=6.32%3B36"
webpage = requests.get(URI_studentski_servis).text

soup = BeautifulSoup(webpage, 'html.parser')

#print(soup.prettify()[0:900])
#print(soup.body.main.article)
#print(soup.body.main.find_all("article"))
articles = soup.body.main.find_all("article")
for article in articles:
    print(article.get_text())
    print("#" * 100)
