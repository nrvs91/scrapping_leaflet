import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import uuid

# URL to scrape
url = 'https://hurtownie.eurocash.pl/gazetki/aktualne-gazetki.html'
base_url = 'https://hurtownie.eurocash.pl'
download_directory = "C:\\Users\\bartd\\Desktop\\Bartus files\\WORK\\upload"
log_file = "C:\\Users\\bartd\\Desktop\\Bartus files\\PYTHON\\scrapping_log\\scrapping_log.txt"

# Create the download directory if it doesn't exist
os.makedirs(download_directory, exist_ok=True)

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

def check_already_downloaded(file_uuid, log_file):
    try:
        with open(log_file, 'r') as log:
            log_content = log.read()
            return file_uuid in log_content
    except IOError as e:
        print(f"Error reading log file: {e}")
        return False

def download_pdf(pdf_url, download_directory, log_file):
    """Download a PDF from the given URL and save it to the specified directory."""
    file_uuid = generate_uuid_from_url(pdf_url)
    
    if check_already_downloaded(file_uuid, log_file):
        print(f"File with UUID {file_uuid} already downloaded. Skipping.")
        return None
    
    response = requests.get(pdf_url)
    if response.status_code == 200:
        file_name = os.path.basename(pdf_url)
        file_path = os.path.join(download_directory, file_name)
        
        with open(file_path, 'wb') as file:
            file.write(response.content)
        
        print(f'Downloaded: {file_path}')
        
        # Log the download with UUID
        log_download(file_uuid, file_name)
        
        # Rename file with UUID
        new_file_path = rename_file_with_uuid(file_path, file_uuid)
        return new_file_path
    else:
        print(f'Failed to download {pdf_url}. Status code: {response.status_code}')
        return None

# Fetch the content from the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    pdf_links = soup.find_all('a', href=True, title="Pobierz PDF", class_="enable-age-popup")
    unique_hrefs = set()
    
    for link in pdf_links:
        href = link['href']
        if '/pub/pl/uploaddocs/gazetka' in href:
            unique_hrefs.add(href)
    
    for href in unique_hrefs:
        full_url = base_url + href
        download_pdf(full_url, download_directory, log_file)
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")