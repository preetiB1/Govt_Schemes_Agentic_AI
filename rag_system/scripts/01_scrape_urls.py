import csv
import time
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import Config 

def scrape_links():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    BASE_URL = "https://www.myscheme.gov.in/search"
    all_links = set()

    print("Starting Scraper...")
    driver.get(BASE_URL)
    time.sleep(5)

    try:
        while True:
            schemes = driver.find_elements(By.XPATH, '//a[contains(@href, "/schemes/")]')
            for s in schemes:
                href = s.get_attribute("href")
                if href and "search" not in href:
                    all_links.add(href)
            
            print(f"Collected {len(all_links)} unique links...")

            try:
                # Try finding next button
                next_btns = driver.find_elements(By.XPATH, '//button[contains(@aria-label, "next")] | //li[contains(@class, "next")]/a')
                if next_btns and next_btns[0].is_enabled():
                    driver.execute_script("arguments[0].click();", next_btns[0])
                    time.sleep(3)
                else:
                    print("Reached last page.")
                    break
            except:
                break

    except Exception as e:
        print(f"error: {e}")
    finally:
        driver.quit()

    os.makedirs(Config.SCRIPTS_DIR, exist_ok=True)
    with open(Config.LINKS_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Link'])
        for link in all_links:
            writer.writerow([link])
    
    print(f"Saved to {Config.LINKS_FILE}")

if __name__ == "__main__":
    scrape_links()