
import requests
import re
from bs4 import BeautifulSoup

def scrap_specific_job(job_link, id, push_to_db):
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
        "jobAdPostingDateId": "3fafe213-6f6c-4fff-b07b-4747daf62260",
        "pageSize": 20,
        "startFrom": 0
    }

    response = requests.get(uri, headers=headers)
    print("s: ", response.status_code)
    if response.status_code == 200:
        data = response.json()
        info = data.get("data", {}).get("jobAdTranslations", {})
        
        
        jobDescription  = info[0].get("jobDescription", {})
        weOffer         = info[0].get("weOffer", {})
        weExpect        = info[0].get("weExpect", {})
        aboutTheCompany = info[0].get("aboutTheCompany", {})
        adSummary       = info[0].get("adSummary", {})

        tag_jobDescription  = BeautifulSoup(jobDescription  or "", 'html.parser')
        tag_weOffer         = BeautifulSoup(weOffer         or "", 'html.parser')
        tag_weExpect        = BeautifulSoup(weExpect        or "", 'html.parser')
        tag_aboutTheCompany = BeautifulSoup(aboutTheCompany or "", 'html.parser')
        tag_adSummary       = BeautifulSoup(adSummary       or "", 'html.parser')

        print(tag_weOffer.get_text())

def scrap_mojedelo(soup, push_to_db):

    uri = "https://api.mojedelo.com/job-ads-search"
    #?jobCategoryIds=64f003ff-6d8b-4be0-b58c-4580e4eeeb8a&regionIds=d1dce9b1-9fa4-438b-b582-10d371d442e6&jobAdPostingDateId=3fafe213-6f6c-4fff-b07b-4747daf62260&pageSize=20&startFrom=0"
    
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
        "jobAdPostingDateId": "3fafe213-6f6c-4fff-b07b-4747daf62260",
        "pageSize": 20,
        "startFrom": 0
    }

    response = requests.get(uri, headers=headers, params=params)

    print("Status:", response.status_code)

    if response.status_code == 200:
        data = response.json()
        items = data.get("data", {}).get("items", [])

        print(f"Found {len(items)} job ads:\n")
        for item in items:
            id = item.get("id")
            title = item.get("title")
            company = item.get("company").get("name")
            description = item.get("adSummary")
            location = item.get("town", {}).get("name")
            if location is None:
                location = ", ".join([r.get("translation") for r in item.get("regions", [])])
            print(f"{company}\n{title}\n{description}\n{location}\n\n")

            base = "https://www.mojedelo.com/oglas/"

            cleaned_title = re.sub(r'[^A-Za-z]', '-', title.lower().replace("č","c").replace("š","s").replace("ž","z"))
            url_like_title = re.sub(r'-+', '-', cleaned_title)
            formated_title = url_like_title.replace("m/z", "mz")
            job_link = base + formated_title + "/" + id
            #print(job_link)

            scrap_specific_job(job_link, id, push_to_db)
    else:
        print("Error:", response.text[:500])
    


