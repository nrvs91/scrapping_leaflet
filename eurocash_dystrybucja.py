import requests
from urllib.parse import urlparse
import os
import uuid
from datetime import datetime

# List of URLs to send the JSON requests
urls = [
    'https://apimoj.eurocash.pl/newspaper-module?type=makroregion_polnocny_wschod',
    'https://apimoj.eurocash.pl/newspaper-module?type=makroregion_poludniowy_wschod', 
    'https://apimoj.eurocash.pl/newspaper-module?type=makroregion_poludnie',
    'https://apimoj.eurocash.pl/newspaper-module?type=makroregion_polnocny_zachod',
    'https://apimoj.eurocash.pl/newspaper-module?type=makroregion_polnoc',
    'https://apimoj.eurocash.pl/newspaper-module?type=makroregion_polnocny_wschod'
]

# Headers to include in the request
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
    "app-id": "cf40a7ef-98d7-4dbc-ac09-429ec44a3b36",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "token": "45aee5549820a8ada1cf80b984da7024",
    "referrer": "https://dystrybucja.grupaeurocash.pl/",
    "referrerPolicy": "strict-origin-when-cross-origin"
}

# Directory to save downloaded PDFs
download_dir = r'C:\Users\bartd\Desktop\Bartus files\WORK\upload'

# Log file path
log_file = r'C:\Users\bartd\Desktop\Bartus files\PYTHON\scrapping_log\scrapping_log.txt'

# Ensure download directory exists
os.makedirs(download_dir, exist_ok=True)
os.makedirs(os.path.dirname(log_file), exist_ok=True)

# Function to fetch JSON data from URL
def fetch_json(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print(f"Fetched JSON data from {url}")
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.text}")
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
    return None

# Function to extract newsletter URLs from JSON data
def extract_newsletter_urls(json_data):
    newsletter_urls = set()
    if json_data and 'others' in json_data:
        for sublist in json_data['others']:
            for item in sublist:
                if isinstance(item, dict) and 'newsletter_url' in item:
                    newsletter_urls.add(item['newsletter_url'])
    return newsletter_urls

# Function to log download details
def log_download(file_uuid, filename, log_file=log_file):
    timestamp = datetime.now().strftime('%d-%m-%y %H:%M')
    log_message = f"{timestamp}: UUID {file_uuid} - File {filename} downloaded.\n"
    try:
        with open(log_file, 'a') as log:
            log.write(log_message)
        print(f"Logged download: {log_message.strip()}")
    except IOError as e:
        print(f"Error writing to log file: {e}")

# Function to generate UUID based on URL
def generate_uuid_from_url(url):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, url))

# Function to rename file with UUID
def rename_file_with_uuid(filepath, file_uuid):
    base_name, extension = os.path.splitext(filepath)
    new_filepath = os.path.join(os.path.dirname(filepath), f"{file_uuid}{extension}")
    try:
        os.rename(filepath, new_filepath)
        return new_filepath
    except OSError as e:
        print(f"Error renaming file: {e}")
        return filepath

# Function to check if a file with UUID has already been downloaded
def check_already_downloaded(file_uuid, log_file):
    try:
        with open(log_file, 'r') as log:
            for line in log:
                if f"UUID {file_uuid}" in line:
                    return True
    except IOError as e:
        print(f"Error checking log file: {e}")
    return False

# Function to download PDF from URL
def download_pdf(url, download_directory, log_file):
    filename = os.path.basename(urlparse(url).path)
    file_uuid = generate_uuid_from_url(url)
    
    if check_already_downloaded(file_uuid, log_file):
        print(f"File with UUID {file_uuid} has already been downloaded. Skipping.")
        return None
    
    filepath = os.path.join(download_directory, filename)
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        new_filepath = rename_file_with_uuid(filepath, file_uuid)
        
        log_download(file_uuid, os.path.basename(new_filepath))
        
        print(f"Downloaded and renamed: {os.path.basename(new_filepath)}")
        return new_filepath
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return None

# Set to store unique newsletter URLs
unique_newsletter_urls = set()

# Fetch JSON data from each URL and extract newsletter URLs
for url in urls:
    json_data = fetch_json(url, headers)
    if json_data:
        newsletter_urls = extract_newsletter_urls(json_data)
        unique_newsletter_urls.update(newsletter_urls)
    else:
        print(f"Failed to fetch or parse JSON data from {url}")

# Download PDFs from unique newsletter URLs
for newsletter_url in unique_newsletter_urls:
    if newsletter_url.lower().endswith('.pdf'):
        download_pdf(newsletter_url, download_dir, log_file)
    else:
        print(f"Skipping non-PDF URL: {newsletter_url}")
