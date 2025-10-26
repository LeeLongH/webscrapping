
def scrap_studentski_servis(soup, inserted_func, to_lower):
    """
        soup:           BeautifulSoup object of the webpage
        insert_func:    function to insert a record into Firebase
    """
        
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

        # Insert into DB using the function passed from the controller
        inserted_func(to_lower(title), to_lower(location), to_lower(description))
