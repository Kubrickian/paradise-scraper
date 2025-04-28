import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configure logging
logging.basicConfig(filename="scraper.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# URL of the website (replace with the actual URL)
URL = "https://paradise2.casino"  # REPLACE WITH THE ACTUAL URL

# Excel file path
EXCEL_FILE = "metric_data.xlsx"

def fetch_metric_with_selenium():
    """Fetch the metric using Selenium with webdriver-manager."""
    driver = None
    try:
        # Set up Selenium with Chrome in headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")
        driver = webdriver.Chrome(service=webdriver.chrome.service.Service(ChromeDriverManager().install()), options=chrome_options)

        # Load the page
        driver.get(URL)
        time.sleep(3)  # Wait for page to render

        # Parse page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Debugging: Save HTML to inspect
        with open("debug_selenium.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        logging.info("Saved Selenium HTML to debug_selenium.html for inspection")

        # Find the metric element (flexible selector)
        div_element = soup.find("div", attrs={"class": lambda c: c and "online-spawn" in c})
        if div_element:
            span_element = div_element.find("span", attrs={"class": lambda c: c and "ml-1" in c})
            if span_element:
                metric = span_element.text.strip()
                logging.info(f"Selenium found metric: {metric}")
                return int(metric)
            else:
                logging.error("Selenium: Span element with class 'ml-1' not found inside div")
                return None
        else:
            logging.error("Selenium: Div element with class 'online-spawn' not found")
            return None
    except Exception as e:
        logging.error(f"Error fetching data with Selenium: {e}")
        return None
    finally:
        if driver:
            driver.quit()

def load_existing_data():
    """Load existing data from Excel or create a new DataFrame."""
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE)
    return pd.DataFrame(columns=["Timestamp", "Metric"])

def save_to_excel(metric):
    """Save the metric to Excel."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        df = load_existing_data()
        new_data = pd.DataFrame({"Timestamp": [timestamp], "Metric": [metric]})
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)
        logging.info(f"Saved metric {metric} at {timestamp}")
        print(f"Saved metric {metric} at {timestamp}")
        return True
    except Exception as e:
        logging.error(f"Error saving to Excel: {e}")
        print(f"Failed to save metric {metric}. Check scraper.log.")
        return False

def main():
    """Run the metric fetch and save once."""
    logging.info("Fetching metric")
    print("Fetching metric...")

    metric = fetch_metric_with_selenium()
    if metric is not None:
        save_to_excel(metric)
    else:
        print("Failed to fetch metric. Check scraper.log and debug_selenium.html.")
        logging.error("Failed to fetch metric")

if __name__ == "__main__":
    main()