"""
careerjet_selenium.py
Open Careerjet in a real browser, let you solve the captcha manually,
save cookies to reuse session, then fetch page HTML and parse with BeautifulSoup.

Adjust the CSS selectors in `parse_jobs()` to match Careerjet's current HTML.
"""

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


# --- CONFIG ---
URI_CAREERJET = "https://www.careerjet.si/delovna-mesta?s=podatkovni+in%C5%BEenir&l=Slovenija"  # example; change query/location
COOKIES_FILE = "careerjet_cookies.pkl"
OUT_HTML = "out.html"
WAIT_TIMEOUT = 30  # seconds to wait for you to solve captcha and page to load

# --- helpers ---
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

    # Use Service to specify driver path
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    return driver

def wait_for_human_and_page(driver):
    """
    Wait for either a known job-list container to appear or for the user to press ENTER in terminal.
    We try to detect a job-listing element automatically; if not found, we ask the user to press ENTER when they solved the CAPTCHA.
    """
    try:
        # Try to wait for a job-list container — you'll likely need to customize this selector to the site.
        # Common candidate selectors: ".job", ".job_listing", ".result", ".searchResult", etc.
        candidate_selectors = [
            ".job", ".job-click", ".job-item", ".searchResult", ".search-result", ".joblisting", ".search-results"
        ]
        wait = WebDriverWait(driver, WAIT_TIMEOUT)
        for sel in candidate_selectors:
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
                print(f"Detected page content via selector `{sel}`.")
                return
            except Exception:
                pass

        # If we didn't detect a job container automatically, fall back to manual confirmation:
        print("\nCouldn't auto-detect job listings. Please solve the CAPTCHA in the opened browser.")
        print("When you've solved it and the search results are visible, press ENTER here to continue.")
        input("Press ENTER after captcha is solved and results are visible...")
    except Exception as e:
        print("Waiting interrupted:", e)

def parse_jobs(html):
    """Parse job results from HTML with BeautifulSoup. Customize selectors to match Careerjet structure."""
    soup = BeautifulSoup(html, "html.parser")

    # Example: try a few likely selectors and print results
    selectors_to_try = [
        ".job",               # generic
        ".searchResult",      # some sites
        ".result",            # fallback
        ".job_listing",       # WordPress-style
        ".listing"            # other
    ]

    found = []
    for sel in selectors_to_try:
        items = soup.select(sel)
        if items:
            print(f"\nFound {len(items)} items with selector `{sel}` — parsing a few examples.")
            for job in items[:20]:  # limit for demo
                title = job.select_one("a") or job.select_one(".title") or job.select_one("h2") or job.select_one("h3")
                link = title["href"] if title and title.has_attr("href") else None
                text = (title.get_text(strip=True) if title else job.get_text(" ", strip=True))[:200]
                found.append({"selector": sel, "title": text, "link": link})
            break

    if not found:
        # fallback: return entire page for inspection
        print("No job-listing selectors matched. Dumping HTML so you can inspect and adapt selectors.")
    return found, soup

# --- main flow ---
def main():
    driver = start_browser()
    try:
        driver.get("https://www.careerjet.si/")  # first visit to set domain for cookies
        # If we have saved cookies from a previous run, try loading them to reuse session:
        if os.path.exists(COOKIES_FILE):
            print("Loading cookies from previous session...")
            try:
                load_cookies(driver, COOKIES_FILE)
                time.sleep(1)
                driver.get(URI_CAREERJET)  # reload after cookies set
            except Exception as e:
                print("Could not load cookies:", e)
        else:
            driver.get(URI_CAREERJET)

        # Wait for the page content or manual captcha solve
        wait_for_human_and_page(driver)

        # Save cookies for future runs
        try:
            save_cookies(driver, COOKIES_FILE)
            print("Cookies saved to", COOKIES_FILE)
        except Exception as e:
            print("Could not save cookies:", e)

        # Grab HTML and save to file
        html = driver.page_source
        with open(OUT_HTML, "w", encoding="utf-8") as f:
            f.write(html)
        print("Saved HTML to", OUT_HTML)

        # Parse with BeautifulSoup (and show some sample results)
        found, soup = parse_jobs(html)
        if found:
            for i, j in enumerate(found[:20], 1):
                print(f"{i}. {j['title']}\n   link: {j['link']}\n")
        else:
            print("No jobs parsed. Inspect the saved file ( car.html) and pick a correct CSS selector to parse.")
            print("Open out.html in your browser and use Inspect Element to find the container & link/title selectors.")

    finally:
        print("Keeping browser open for 5 seconds; it will close after that.")
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    main()

