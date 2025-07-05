import os
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager


# ✅ Create Chrome driver safely for cloud containers
def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Headless for servers
    # options.add_argument("--no-sandbox")  # Safe for containerized build
    # options.add_argument("--disable-dev-shm-usage")  # Avoid shared memory problems
    # options.add_argument("--disable-gpu")
    # options.add_argument("--disable-software-rasterizer")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


# ✅ Perform YellowPages search
def perform_search(driver, keyword, city):
    base_url = "https://www.yellowpages-uae.com/"
    driver.get(base_url)

    for _ in range(3):  # Retry loop for stability
        try:
            keyword_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//input[@placeholder="Products, Services, Brand or Company"]')
                )
            )
            keyword_input.clear()
            keyword_input.send_keys(keyword)
            break
        except:
            time.sleep(1)

    if city:
        city_input = driver.find_element(By.XPATH, '//input[@placeholder="Search..."]')
        city_input.clear()
        city_input.send_keys(city)
        time.sleep(1.5)

        all_lis = driver.find_elements(By.XPATH, '//ul[contains(@class, "absolute")]//li')
        found_emirates = False
        city_matched = False

        for li in all_lis:
            li_text = li.text.strip().lower()
            li_class = li.get_attribute("class") or ""
            if "font-bold" in li_class:
                found_emirates = "emirates" in li_text
            elif found_emirates and li_text == city.lower():
                driver.execute_script("arguments[0].click();", li)
                print(f"✅ Selected '{city}' from Emirates.")
                city_matched = True
                break

        if not city_matched:
            print(f"⚠️ Could not find '{city}' under Emirates. Proceeding without selecting.")

    search_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Search")]')
    driver.execute_script("arguments[0].click();", search_btn)

    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, '//div[contains(@class, "min-h-[200px]") and contains(@class, "lg:flex-row")]')
        )
    )


# ✅ Scrape all pages with deduplication
def scrape_all_pages(driver, max_pages=None):
    all_results = []
    seen = set()
    page_num = 1

    while True:
        print(f"🔎 Scraping page {page_num}...")
        page_results = scrape_one_page(driver)

        for r in page_results:
            key = (r['Company Name'], r['Phone'])
            if key not in seen:
                seen.add(key)
                all_results.append(r)

        if max_pages and page_num >= max_pages:
            print(f"✅ Reached max pages ({max_pages}). Stopping.")
            break

        try:
            next_btn = driver.find_element(By.XPATH, '//button[@name="page" and text()="Next"]')
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(2)
            page_num += 1
        except:
            print("✅ No more pages.")
            break

    return all_results


# ✅ Scrape listings on one page
def scrape_one_page(driver):
    listings = driver.find_elements(By.XPATH, '//div[contains(@class, "min-h-[200px]") and contains(@class, "lg:flex-row")]')
    print(f"✅ Found {len(listings)} listings on this page.")

    results = []

    for listing in listings:
        try:
            name = listing.find_element(By.TAG_NAME, 'h3').text.strip()
        except:
            name = "N/A"

        try:
            phone_span = listing.find_element(By.XPATH, './/p[contains(., "Phone")]//span[contains(@id, "lblShortPhone")]')
            driver.execute_script("arguments[0].click();", phone_span)
            time.sleep(0.3)
            phone = listing.find_element(By.XPATH, './/a[contains(@id, "lblPhone-")]').get_attribute('href').replace('tel:', '').strip()
        except:
            phone = "N/A"

        try:
            mobile_span = listing.find_element(By.XPATH, './/p[contains(., "Mobile")]//span[contains(@id, "lblShortMobile")]')
            driver.execute_script("arguments[0].click();", mobile_span)
            time.sleep(0.3)
            mobile = listing.find_element(By.XPATH, './/a[contains(@id, "lblMobile-")]').get_attribute('href').replace('tel:', '').strip()
        except:
            mobile = "N/A"

        try:
            location = listing.find_element(By.XPATH, './/span[text()="Location : "]/following-sibling::span').text.strip()
        except:
            location = "N/A"

        try:
            city = listing.find_element(By.XPATH, './/span[text()="City : "]/following-sibling::span').text.strip()
        except:
            city = "N/A"

        whatsapp = bool(listing.find_elements(By.XPATH, './/button[contains(@class, "bg-[#28C281]")]'))

        try:
            products_span = listing.find_element(By.XPATH, './/span[contains(text(), "Products")]')
            products_block = products_span.find_element(By.XPATH, './ancestor::div[contains(@class, "flex-wrap")]')
            try:
                read_more_btn = products_block.find_element(By.XPATH, './/button[contains(text(), "Read More")]')
                driver.execute_script("arguments[0].click();", read_more_btn)
                time.sleep(0.3)
            except:
                pass
            links = products_block.find_elements(By.XPATH, './/a')
            products = ', '.join([a.text.strip() for a in links]) if links else "N/A"
        except:
            products = "N/A"

        try:
            brands_span = listing.find_element(By.XPATH, './/span[contains(text(), "Brands")]')
            brands_block = brands_span.find_element(By.XPATH, './ancestor::div[contains(@class, "flex-wrap")]')
            try:
                read_more_btn = brands_block.find_element(By.XPATH, './/button[contains(text(), "Read More")]')
                driver.execute_script("arguments[0].click();", read_more_btn)
                time.sleep(0.3)
            except:
                pass
            links = brands_block.find_elements(By.XPATH, './/a')
            brands = ', '.join([a.text.strip() for a in links]) if links else "N/A"
        except:
            brands = "N/A"

        try:
            website = listing.find_element(By.XPATH, './/button[contains(@class, "listing_button") and @data-url]').get_attribute('data-url').strip()
        except:
            website = "N/A"

        try:
            brochure = listing.find_element(By.XPATH, './/a[contains(@href, ".pdf")]').get_attribute('href').strip()
        except:
            brochure = "N/A"

        verified = bool(listing.find_elements(By.XPATH, './/img[@alt="verified"]'))

        results.append({
            "Company Name": name,
            "Verified": verified,
            "Phone": phone,
            "Mobile": mobile,
            "Location": location,
            "City": city,
            "WhatsApp": whatsapp,
            "Products": products,
            "Brands": brands,
            "Website": website,
            "Brochure": brochure
        })

    return results


# ✅ Run & save to Excel
def run_scraper(keyword, city, max_pages=None):
    driver = create_driver()
    try:
        perform_search(driver, keyword, city)
        all_data = scrape_all_pages(driver, max_pages=max_pages)
        df = pd.DataFrame(all_data)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, "data")
        os.makedirs(output_dir, exist_ok=True)

        file_name = f"yellowpages_{keyword.replace(' ', '_')}.xlsx"
        file_path = os.path.join(output_dir, file_name)
        df.to_excel(file_path, index=False)

        print(f"✅ All data saved to {file_path} with {len(df)} unique companies.")
        return file_path

    finally:
        driver.quit()


# ✅ CLI runner for local use
if __name__ == "__main__":
    keyword = input("Enter your search keyword: ").strip()
    city = input("Enter city (or leave blank for all UAE): ").strip()
    max_pages_input = input("Max pages to scrape (leave blank for all): ").strip()
    max_pages = int(max_pages_input) if max_pages_input.isdigit() else None

    run_scraper(keyword, city, max_pages)