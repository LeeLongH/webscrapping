import time
import pickle
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

COOKIES_FILE = "careerjet_cookies.pkl"

def save_cookies(driver, path):
    with open(path, "wb") as f:
        pickle.dump(driver.get_cookies(), f)

def load_cookies(driver, path):
    with open(path, "rb") as f:
        cookies = pickle.load(f)
    for c in cookies:
        # Selenium requires cookie domain to match current domain; ensure no invalid fields
        cookie = {k: v for k, v in c.items() if k in ("name","value","domain","path","expiry","secure","httpOnly","sameSite")}
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            # ignore cookies that cannot be set
            pass

def start_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    )

    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    #driver.maximize_window()
    return driver

def parse_specific_job(uri):
    driver = start_browser()
    driver.get(uri)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    section = soup.find("section", class_="content")
    if section:
        # Handle unordered lists separately
        for ul in section.find_all("ul"):
            items = []
            for li in ul.find_all("li"):
                items.append(li.get_text(strip=True))
            # Replace <ul> with newline-separated text
            ul.replace_with("\n".join(items))

        description = section.get_text("\n", strip=True)
    else:
        description = None

    return description

def parse_jobs(html, insert_to_db):
    soup = BeautifulSoup(html, "html.parser")

    items = soup.select(".job.clicky")
    print(f"{'Careerjet':<10}: {len(items)} jobs")

    if items:
        
        for job in items[:10]:  # 10 jobs as limit

            title = job.select_one("a") or job.select_one(".title") or job.select_one("h2") or job.select_one("h3")
            
            # Get short description (part of long description)
            #desc_tag = job.find("div", class_="desc")
            #desc = desc_tag.get_text(strip=True) if desc_tag else None

            # Get location (inside <ul class="location">)
            loc_tag = job.find_next("ul", class_="location")
            location = loc_tag.get_text(strip=True) if loc_tag else None

            link = title["href"] if title and title.has_attr("href") else None
            desciption = parse_specific_job("https://www.careerjet.si" + link)

            #print(f"Title: {title.text.strip()}")
            #print(f"Link: {link}")
            #print(f"Location: {location}")
            #print(f"desc.: {desc}")
            #print(f"desciption: {desciption}")
            insert_to_db(title, location, desciption, link)

def scrap_careerjet(URI_careerjet, insert_to_db):
    driver = start_browser()
    try:
        driver.get("https://www.careerjet.si/")  # first visit to set domain for cookies
        # If we have saved cookies from a previous run, try loading them to reuse session:
        if os.path.exists(COOKIES_FILE):
            #print("Loading cookies from previous session...")
            try:
                load_cookies(driver, COOKIES_FILE)
                time.sleep(1)
                driver.get(URI_careerjet)  # reload after cookies set
            except Exception as e:
                print("Could not load cookies:", e)
        else:
            driver.get(URI_careerjet)

        # Save cookies for future runs
        try:
            save_cookies(driver, COOKIES_FILE)
            #print("Cookies saved to", COOKIES_FILE)
        except Exception as e:
            #print("Could not save cookies:", e)
            pass

        html = driver.page_source
        parse_jobs(html, insert_to_db)

    finally:
        #time.sleep(1)
        driver.quit()