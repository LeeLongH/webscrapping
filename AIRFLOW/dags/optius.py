"""

Find today's job posts from:

https://www.optius.com/iskalci/prosta-delovna-mesta/?Keywords=&Fields%5B%5D=37&
Regions%5B%5D=26&doSearch=&Time=&Types%5B%5D=6&Types%5B%5D=7&Hours%5B%5D=8

(tick "last 24h" option)

using BeautifulSoup and REST API.

Insert job posts into Firebase if the entry there doesnt exist

"""

import requests
from bs4 import BeautifulSoup

def scrap_specific_job(uri, insert_to_db):
    print(uri)
    webpage = requests.get(uri).text
    soup = BeautifulSoup(webpage, 'html.parser')
    job_section = soup.body.select_one('section.col.typography.job-detail-col.wholesize')
    
    company = job_section.find("h2")

    if company:
        company = company.text
    else:
        company = "/"

    header_info = soup.body.select_one("ul.job-info")
    location = header_info.find_all("li")[-1].text.replace("Kraj dela", "").strip()

    intro_paragraphs = job_section.find_all("p")  # ✅ no .text here
    if intro_paragraphs:
        intro = "\n".join(intro_p.get_text(strip=True) for intro_p in intro_paragraphs)
    else:
        intro = ""

    requirements = job_section.find_all("ul")

    if len(requirements) > 1:
        responsibilities = "- " + "\n- ".join(li.get_text(strip=True).capitalize() for li in requirements[1].find_all("li"))
    else:
        description = intro
    if len(requirements) > 2:
        qualifications  = "- " + "\n- ".join(li.get_text(strip=True).capitalize() for li in requirements[2].find_all("li"))
        description = intro + "\nOpis delovnega mesta:\n" + responsibilities + "\nPričakujejo:\n" + qualifications
    else:
        description = intro + "\nOpis delovnega mesta:\n" + responsibilities

    if not description:
        description = "/"

    insert_to_db(company, location, description.strip(), uri)

def scrap_optius(soup, insert_to_db):

    #job_list = soup.body.select_one('div.job-results').find("ul").find_all("li")
    
    job_section = soup.body.select_one('div.job-results').find("ul")
    
    #No jobs today
    if not job_section:
        print(f"{'Optius':<10}: 0 jobs")
        return

    job_list = job_section.find_all("li")
    job_links = []

    number_of_jobs = 0

    for job in job_list:
        links = job.find_all("a")
        #print("\nlinks ", links)

        for a in links:
            if a.has_attr("href") and a["href"].startswith("/iskalci/"):
                link = a["href"]
                if link[-6:-1].isdigit():
                    #print("link", link)
                    if link not in job_links:
                        job_links.append(link)
                        number_of_jobs += 1
                        break

    #print(f"{'Optius':<10}: len{job_list} jobs")
    for uri in job_links:
        scrap_specific_job("https://www.optius.com" + uri, insert_to_db)
            
                 
    

