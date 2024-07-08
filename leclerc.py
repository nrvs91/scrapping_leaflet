import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import uuid

# Base URL of the starting directory
base_url = "https://leclerc.pl/wp-content/uploads/sites/"
download_directory = "C:\\Users\\bartd\\Desktop\\Bartus files\\WORK\\upload"
log_file = "C:\\Users\\bartd\\Desktop\\Bartus files\\PYTHON\\scrapping_log\\scrapping_log.txt"

# Function to log download
def log_download(url, log_file=log_file):
    log_directory = os.path.dirname(log_file)
    try:
        os.makedirs(log_directory, exist_ok=True)
    except OSError as e:
        print(f"Error creating directory: {e}")
    
    timestamp = datetime.now().strftime('%d-%m-%y %H:%M')
    log_message = f"{timestamp}: File from URL {url} downloaded.\n"
    try:
        with open(log_file, 'a') as log:
            log.write(log_message)
    except IOError as e:
        print(f"Error writing to log file: {e}")

# Function to check if file with URL is already downloaded
def check_already_downloaded(url, log_file):
    try:
        with open(log_file, 'r') as log:
            log_content = log.read()
            return url in log_content
    except IOError as e:
        print(f"Error reading log file: {e}")

# Function to generate UUID from URL
def generate_uuid_from_url(url):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, url))

# Function to rename file with UUID
def rename_file_with_uuid(filename, uuid):
    base_name, extension = os.path.splitext(filename)
    new_filename = f"{uuid}{extension}"

    new_filepath = os.path.join(download_directory, new_filename)
    
    try:
        os.rename(filename, new_filepath)
        return new_filepath
    except OSError as e:
        print(f"Error renaming file: {e}")
        return filename

# Function to download a file given its URL
def download_file(url, directory):
    local_filename = os.path.join(directory, url.split('/')[-1])
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Downloaded: {local_filename}")
    return local_filename

# Function to fetch and process each directory
def process_directories(url):
    # Fetch the HTML content
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Error accessing {url}: {e}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all links (directories)
    for link in soup.find_all('a', href=True):
        href = link['href']
        
        # Filter out parent directory link ('../') and non-directory links
        if href.endswith('/'):
            # Construct full URL of the directory
            directory_url = urljoin(url, href)
            
            # Process the 2024/07/ subdirectory for this directory
            process_subdirectory(urljoin(directory_url, "2024/07/"))

# Function to process the 2024/07/ subdirectory
def process_subdirectory(url):
    # Fetch the HTML content
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Error accessing {url}: {e}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all links (files)
    for link in soup.find_all('a', href=True):
        href = link['href']
        
        # Filter out parent directory link ('../') and non-PDF links
        if href.lower().endswith('.pdf'):
            # Construct full URL of the PDF file
            pdf_url = urljoin(url, href)
            
            # Check if the PDF file has already been downloaded
            if check_already_downloaded(pdf_url, log_file):
                print(f"Already downloaded: {pdf_url}")
            else:
                # Download the PDF file
                try:
                    downloaded_file = download_file(pdf_url, download_directory)
                    # Log the download
                    log_download(pdf_url, log_file)
                    
                    # Generate UUID and rename the file
                    uuid = generate_uuid_from_url(pdf_url)
                    renamed_file = rename_file_with_uuid(downloaded_file, uuid)
                    print(f"Renamed file: {renamed_file}")
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading {pdf_url}: {e}")

# Start the process
def start_process(base_url):
    # Fetch the HTML content
    try:
        response = requests.get(base_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Error accessing {base_url}: {e}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all links (directories)
    for link in soup.find_all('a', href=True):
        href = link['href']
        
        # Filter out parent directory link ('../') and non-directory links
        if href.endswith('/'):
            # Construct full URL of the directory
            directory_url = urljoin(base_url, href)
            
            # Process the 2024/07/ subdirectory for this directory
            process_subdirectory(urljoin(directory_url, "2024/07/"))

# Start the process
start_process(base_url)
