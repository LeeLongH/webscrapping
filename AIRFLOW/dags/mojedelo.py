"""

Find today's job posts from:

https://www.mojedelo.com/iskanje-zaposlitve?jobCategoryIds=64f003ff-6d8b-
4be0-b58c-4580e4eeeb8a&regionIds=d1dce9b1-9fa4-438b-b582-10d371d442e6
&jobAdPostingDateId=3fafe213-6f6c-4fff-b07b-4747daf62260

using BeautifulSoup and REST API.

Insert job posts into Firebase if the entry there doesnt exist

"""

import requests
import re
from bs4 import BeautifulSoup
import httpx

def scrap_specific_job(job_link, id, today_id):
    uri = "https://api.mojedelo.com/job-ads/" + id

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "sl-SI,sl;q=0.9,en-GB;q=0.8,en;q=0.7",
        "origin": "https://www.mojedelo.com",
        "referer": job_link,
        "tenantid": "5947a585-ad25-47dc-bff3-f08620d1ce17",
        "languageid": "db3c58e6-a083-4f72-b30b-39f2127bb18d",
        "channelid": "8805c1b8-a0a9-4f57-ad42-329af3c92a61",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    params = {
        "jobCategoryIds": "64f003ff-6d8b-4be0-b58c-4580e4eeeb8a",
        "regionIds": "d1dce9b1-9fa4-438b-b582-10d371d442e6",
        "jobAdPostingDateId": today_id,
        "pageSize": 20,
        "startFrom": 0
    }

    response = requests.get(uri, headers=headers, params=params)
    #print("s: ", response.status_code)

    if response.status_code == 200:
        data = response.json()
        info = data.get("data", {}).get("jobAdTranslations", {})
        
        jobDescription  = info[0].get("jobDescription", {})
        weOffer         = info[0].get("weOffer", {})
        weExpect        = info[0].get("weExpect", {})
        aboutTheCompany = info[0].get("aboutTheCompany", {})
        adSummary       = info[0].get("adSummary", {})

        text_jobDescription  = BeautifulSoup(jobDescription  or "", 'html.parser').get_text()
        text_aboutTheCompany = BeautifulSoup(aboutTheCompany or "", 'html.parser').get_text()
        text_adSummary       = BeautifulSoup(adSummary       or "", 'html.parser').get_text()

        tag_weOffer          = BeautifulSoup(weOffer         or "", 'html.parser')
        tag_weExpect         = BeautifulSoup(weExpect        or "", 'html.parser')

        text_weOffer = "- " + "\n- ".join(li.get_text(strip=True).capitalize() for li in tag_weOffer.find_all("li"))
        text_weExpect = "- " + "\n- ".join(li.get_text(strip=True).capitalize() for li in tag_weExpect.find_all("li"))

        description =  text_adSummary + "\n" + text_jobDescription + "\n" + text_weOffer + "\n" + text_weExpect + "\n" + text_aboutTheCompany

        return description

def scrap_jobs(uri, today_id, insert_to_db):

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "sl-SI,sl;q=0.9,en-GB;q=0.8,en;q=0.7",
        "origin": "https://www.mojedelo.com",
        "referer": "https://www.mojedelo.com/",
        "tenantid": "5947a585-ad25-47dc-bff3-f08620d1ce17",
        "languageid": "db3c58e6-a083-4f72-b30b-39f2127bb18d",
        "channelid": "8805c1b8-a0a9-4f57-ad42-329af3c92a61",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    params = {
        "jobCategoryIds": "64f003ff-6d8b-4be0-b58c-4580e4eeeb8a",
        "regionIds": "d1dce9b1-9fa4-438b-b582-10d371d442e6",
        "jobAdPostingDateId": today_id,
        "pageSize": 20,
        "startFrom": 0
    }

    response = requests.get(uri, headers=headers, params=params)
    #with httpx.Client(http2=True) as client:
        #response = client.get(uri, headers=headers, params=params)


    #print("Status:", response.status_code)
    if response.status_code == 200:
        data = response.json()
        items = data.get("data", {}).get("items", [])

        print(f"{'mojedelo':<10}: {len(items)} jobs")

        for item in items:
            id = item.get("id")
            title = item.get("title")
            company = item.get("company").get("name")
            #description = item.get("adSummary")
            location = item.get("town", {}).get("name")
            if location is None:
                location = ", ".join([r.get("translation") for r in item.get("regions", [])])
            #print(f"{company}\n{title}\n{description}\n{location}\n\n")

            base = "https://www.mojedelo.com/oglas/"

            cleaned_title = re.sub(r'[^A-Za-z]', '-', title.lower().replace("č","c").replace("š","s").replace("ž","z"))
            url_like_title = re.sub(r'-+', '-', cleaned_title)
            formated_title = url_like_title.replace("m/z", "mz")
            job_link = base + formated_title + "/" + id
            #print(job_link)

            # Merge company name into location
            location = company + ", " + location
    
            description = scrap_specific_job(job_link, id, today_id)
            insert_to_db(title=title, location=location, uri=job_link, description=description)

        
    else:
        print("Error:", response.text[:500])
    
    return (False, False, False, False)
    
def get_todays_UUID():
    uri = "https://api.mojedelo.com/taxonomy/job-ad-posting-dates"

    headers = {
        "accept": "application/json, text/plain, */*",
        "tenantid": "5947a585-ad25-47dc-bff3-f08620d1ce17",
        "languageid": "db3c58e6-a083-4f72-b30b-39f2127bb18d",
        "channelid": "8805c1b8-a0a9-4f57-ad42-329af3c92a61",
        "user-agent": "Mozilla/5.0",
    }

    response = requests.get(uri, headers=headers)
    data = response.json()

    """
    {
    "data": {
        "items": [
                    {
                        "id": "3fafe213-6f6c-4fff-b07b-4747daf62260",
                        "nameTranslation": "Zadnjih 24 ur"
                    },
                    {
                        "id": "a0c0fd2d-0328-4303-8e56-98fadf781d9c",
                        "nameTranslation": "Zadnjih 48 ur"
                    },
                    {
                        "id": "464312df-f4ba-4bc9-8041-2c5e0a85763b",
                        "nameTranslation": "Zadnjih 72 ur"
                    }
                ]
            }
    }
    """
    # [0] = Zadnjih 24 ur
    # [1] = Zadnjih 48 ur
    # [2] = Zadnjih 72 ur
    today_uuid = data["data"]["items"][0]["id"]

    return today_uuid

def scrap_mojedelo(uri, insert_to_db):
    today_id = get_todays_UUID()
    #print("id: ", today_id)
    scrap_jobs(uri, today_id, insert_to_db)


