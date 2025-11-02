"""

Using beautifulSoup, get today's job posts from:

https://www.studentski-servis.com/studenti/prosta-dela?kljb=&page=1&isci=1&
sort=&dd1=1&dm1s=1&regija%5B%5D=ljubljana-z-okolico&regija%5B%5D=domzale-kamnik
&skD%5B%5D=004&skD%5B%5D=A832&skD%5B%5D=A210&skD%5B%5D=A055&skD%5B%5D=A078&skD
%5B%5D=A090&skD%5B%5D=A095&hourlyratefrom=6.32&hourlyrateto=36&hourly_rate=6.32%3B26

and insert into Firebase if the entry there doesnt exist

"""


def scrap_studentski_servis(soup, insert_to_db, to_lower):
    """
        soup:           BeautifulSoup object of the webpage
        insert_func:    function to insert a record into Firebase
    """
        
    articles = soup.body.main.find_all("article")
    print(f"{'stud.serv.':<10}: {len(articles)} jobs")
    for article in articles:
        article_content = article.div.div
        titles = article_content.find_all('h5')

        if len(titles) == 1:
            title = f"{titles[0].get_text(strip=True)}"
        else:    
            title = f"{titles[0].get_text(strip=True)} : {titles[1].get_text(strip=True)}"
        description = article_content.find_all('p')[-1].string
        location = article_content.find_all('p')[1].get_text(separator=" ", strip=True)
        #print(f"{title}\n{location}\n{description}\n\n")

        # Insert into DB using the function passed from the controller
        insert_to_db(to_lower(title), to_lower(location), to_lower(description))