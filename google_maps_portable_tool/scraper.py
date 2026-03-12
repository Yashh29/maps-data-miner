import time
import re
import requests
import pandas as pd
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"


def get_emails_from_html(html):
    return list(set(re.findall(EMAIL_REGEX, html)))


def extract_email_from_website(url):

    if not url:
        return ""

    try:

        if not url.startswith("http"):
            url = "http://" + url

        emails_found = set()

        response = requests.get(url, timeout=5)
        html = response.text

        emails_found.update(get_emails_from_html(html))

        mailtos = re.findall(r"mailto:([^\"]+)", html)
        emails_found.update(mailtos)

        contact_match = re.search(r'href="([^"]*(contact|Contact)[^"]*)"', html)

        if contact_match:

            contact_url = urljoin(url, contact_match.group(1))

            try:

                contact_response = requests.get(contact_url, timeout=5)
                contact_html = contact_response.text

                emails_found.update(get_emails_from_html(contact_html))

                mailtos_contact = re.findall(
                    r"mailto:([^\"]+)", contact_html
                )

                emails_found.update(mailtos_contact)

            except:
                pass

        return "; ".join(list(emails_found)[:2])

    except:
        return ""


def run_scraper(query):

    # ---------------- CHROME OPTIONS ----------------

    options = webdriver.ChromeOptions()

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # ------------------------------------------------

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    wait = WebDriverWait(driver, 20)

    driver.get("https://www.google.com/maps")

    # Accept cookies
    try:

        consent = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[contains(text(),"Accept")]')
            )
        )

        consent.click()

    except:
        pass

    # Search query
    search_box = wait.until(
        EC.presence_of_element_located((By.NAME, "q"))
    )

    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.ENTER)

    time.sleep(4)

    scrollable_div = wait.until(
        EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]'))
    )

    last_height = 0

    while True:

        driver.execute_script(
            'arguments[0].scrollTop = arguments[0].scrollHeight',
            scrollable_div
        )

        time.sleep(2)

        new_height = driver.execute_script(
            'return arguments[0].scrollHeight',
            scrollable_div
        )

        if new_height == last_height:
            break

        last_height = new_height

    listings = driver.find_elements(By.XPATH, '//a[contains(@href, "/place")]')

    data = []
    unique_links = set()

    for listing in listings:

        try:

            link = listing.get_attribute("href")

            if link in unique_links:
                continue

            unique_links.add(link)

            driver.execute_script("arguments[0].click();", listing)

            time.sleep(2)

            name = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//h1[contains(@class,"DUwDvf")]')
                )
            ).text

            try:
                rating = driver.find_element(
                    By.XPATH, '//span[@class="MW4etd"]'
                ).text
            except:
                rating = ""

            try:
                address = driver.find_element(
                    By.XPATH,
                    '//button[contains(@data-item-id,"address")]'
                ).text.replace("", "")
            except:
                address = ""

            try:
                phone = driver.find_element(
                    By.XPATH,
                    '//button[contains(@data-item-id,"phone")]'
                ).text.replace("", "")
            except:
                phone = ""

            try:
                website = driver.find_element(
                    By.XPATH,
                    '//a[@data-item-id="authority"]'
                ).get_attribute("href")
            except:
                website = ""

            email = extract_email_from_website(website)

            data.append({

                "name": name,
                "rating": rating,
                "address": address,
                "phone": phone,
                "website": website,
                "email": email,
                "maps_link": link,
                "source_query": query

            })

        except:
            continue

    driver.quit()

    df = pd.DataFrame(data)

    print(f"Extracted {len(df)} listings for query: {query}")

    return df