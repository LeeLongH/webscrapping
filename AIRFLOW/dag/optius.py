def scrap_optius(soup, insert_to_db_if_new_record, to_lower):
    job_list = soup.body.select_one('div.job-results').find("ul").find_all("li")
    
    job_links = []

    for job in job_list:
        links = job.find_all("a")
        #print(links)

        for a in links:
            if a.has_attr("href"):
                job_links.append("https://www.optius.com/" + a["href"])
                break
    print(job_links)
            
                 
    

