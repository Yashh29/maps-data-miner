import time
import re
import requests
import pandas as pd
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright


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

        response = requests.get(url, timeout=6)
        html = response.text

        emails_found.update(get_emails_from_html(html))

        mailtos = re.findall(r"mailto:([^\"]+)", html)
        emails_found.update(mailtos)

        contact_match = re.search(r'href="([^"]*(contact|Contact)[^"]*)"', html)

        if contact_match:

            contact_url = urljoin(url, contact_match.group(1))

            try:
                contact_response = requests.get(contact_url, timeout=6)
                contact_html = contact_response.text

                emails_found.update(get_emails_from_html(contact_html))

                mailtos_contact = re.findall(r"mailto:([^\"]+)", contact_html)
                emails_found.update(mailtos_contact)

            except:
                pass

        return "; ".join(list(emails_found)[:2])

    except:
        return ""


def run_scraper(query):

    data = []
    unique_links = set()

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        page = browser.new_page()

        page.goto("https://www.google.com/maps")

        page.wait_for_selector('input[name="q"]')

        page.fill('input[name="q"]', query)
        page.keyboard.press("Enter")

        page.wait_for_timeout(5000)

        # Scroll the results panel
        for _ in range(25):

            page.mouse.wheel(0, 8000)
            page.wait_for_timeout(2000)

        listings = page.locator('a[href*="/place"]').all()

        for listing in listings:

            try:

                link = listing.get_attribute("href")

                if not link or link in unique_links:
                    continue

                unique_links.add(link)

                listing.click()

                page.wait_for_timeout(2500)

                # Extract fields safely
                try:
                    name = page.locator("h1.DUwDvf").first.inner_text(timeout=3000)
                except:
                    name = ""

                try:
                    rating = page.locator("span.MW4etd").first.inner_text(timeout=2000)
                except:
                    rating = ""

                try:
                    address = page.locator('button[data-item-id="address"]').first.inner_text(timeout=2000)
                except:
                    address = ""

                try:
                    phone = page.locator('button[data-item-id="phone"]').first.inner_text(timeout=2000)
                except:
                    phone = ""

                try:
                    website = page.locator('a[data-item-id="authority"]').first.get_attribute("href", timeout=2000)
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

        browser.close()

    df = pd.DataFrame(data)

    print(f"Extracted {len(df)} listings for query: {query}")

    return df