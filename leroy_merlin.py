from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# URL to scrape
url = "https://www.leroymerlin.pl/gazetki/"

# Selenium options
options = Options()
options.add_argument("--headless")  # Run Chrome in headless mode, i.e., without a GUI
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Set up Selenium Chrome WebDriver
service = Service('C:\WebDriver\chromedriver.exe')  # Update with the path to your chromedriver executable
driver = webdriver.Chrome(service=service, options=options)

try:
    # Open the URL
    driver.get(url)
    
    # Wait for the page to fully load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))

    # Get the page source after fully loaded
    page_source = driver.page_source

    # Parse the HTML content
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find the link with the specified attributes
    link = soup.find('a', {'target': '_blank', 'href': True, 'style': 'text-decoration: none;'})

    if link:
        leaflet_url = link['href']
        print("Found leaflet URL:", leaflet_url)
    else:
        print("Leaflet URL not found.")

finally:
    # Close the WebDriver
    driver.quit()
