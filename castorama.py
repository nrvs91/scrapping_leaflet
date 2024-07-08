import time
import re
import json
import requests
import os
import uuid
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import hashlib

# Log file path
log_file = r'C:\Users\bartd\Desktop\Bartus files\PYTHON\scrapping_log\scrapping_log.txt'

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run headless Chrome (optional)
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument("--enable-logging")
chrome_options.add_argument("--log-level=0")
chrome_options.add_argument("--v=99")
chrome_options.add_argument("--single-process")

# Set up Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Define the URL
url = "https://www.castorama.pl/gazetka-castorama-pdf"

# Open the URL
driver.get(url)

# Wait for the page to load
time.sleep(5)  # Adjust the sleep time based on your needs

# Start capturing network requests
driver.execute_cdp_cmd('Network.enable', {})

fetch_requests = []

def capture_request(request):
    if re.search(r"/api/catalogue/\w{8}-\w{4}-\w{4}-\w{4}-\w{12}", request['url']):
        fetch_requests.append(request['url'])

# Function to check if a file with UUID has already been downloaded
def check_already_downloaded(file_uuid, log_file):
    try:
        with open(log_file, 'r') as log:
            for line in log:
                # Check if the line contains the specific UUID
                if f"UUID {file_uuid} -" in line:
                    return True
    except IOError as e:
        print(f"Error checking log file: {e}")
    return False

# Function to log download details
def log_download(file_uuid, download_path, log_file=log_file):
    log_directory = os.path.dirname(log_file)
    try:
        os.makedirs(log_directory, exist_ok=True)
    except OSError as e:
        print(f"Error creating log directory: {e}")

    timestamp = datetime.now().strftime('%d-%m-%y %H:%M')
    log_message = f"{timestamp}: UUID {file_uuid} - Folder {download_path} created.\n"
    try:
        with open(log_file, 'a') as log:
            log.write(log_message)
        print(f"Logged download: {log_message.strip()}")
    except IOError as e:
        print(f"Error writing to log file: {e}")

# Monitor network requests
start_time = time.time()
timeout = 30  # Adjust the timeout based on your needs

while time.time() - start_time < timeout:
    # Get the performance logs
    logs = driver.execute_script("return window.performance.getEntriesByType('resource');")
    for log in logs:
        capture_request({'url': log['name']})
    
    if fetch_requests:
        break

# Fetch and download individual pages from captured URL
if fetch_requests:
    fetch_url = fetch_requests[0]  # Assuming you want to process the first captured URL
    print(f"Fetching contents of URL: {fetch_url}")
    
    # Generate UUID based on the fetch URL
    url_hash = hashlib.md5(fetch_url.encode()).hexdigest()
    directory_uuid = str(uuid.UUID(hex=url_hash))
    
    try:
        # Check if UUID has already been logged
        if check_already_downloaded(directory_uuid, log_file):
            print(f"UUID {directory_uuid} already processed. Skipping.")
        else:
            # Define download directory path
            download_dir = rf'C:\Users\bartd\Desktop\Bartus files\WORK\upload\{directory_uuid}'
            
            # Create the directory
            os.makedirs(download_dir)
            print(f"Created directory: {download_dir}")
            
            # Log download
            log_download(directory_uuid, download_dir)
            
            # Open the captured URL
            driver.get(fetch_url)
            
            # Wait for the content to load (adjust sleep time as necessary)
            time.sleep(5)
            
            # Get the content of the page
            page_source = driver.page_source
            
            # Extract JSON data from the page source
            json_start = page_source.find('{"name"')
            json_end = page_source.find('</pre>', json_start)
            json_data_str = page_source[json_start:json_end]
            
            # Parse JSON data
            try:
                json_data = json.loads(json_data_str)
                pages = json_data.get('pages', [])
                
                if pages:
                    for page in pages:
                        image_url = page.get('image')
                        if image_url:
                            # Download the image
                            image_filename = image_url.split('/')[-1]
                            image_path = os.path.join(download_dir, image_filename)
                            response = requests.get(image_url)
                            
                            # Save the image to a file
                            with open(image_path, 'wb') as image_file:
                                image_file.write(response.content)
                            
                            print(f"Page image downloaded: {image_filename}")
                        else:
                            print("Error: Image URL not found in page data.")
                else:
                    print("Error: No pages found in JSON.")
            
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {str(e)}")
            
            except Exception as e:
                print(f"An error occurred: {str(e)}")
    
    except OSError as e:
        print(f"Error creating directory: {str(e)}")

# Close the browser
driver.quit()
