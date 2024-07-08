import requests
import json
import uuid
import os
from bs4 import BeautifulSoup
from datetime import datetime

# Define headers and data
headers = {
    'accept': '*/*',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://topaz24.pl',
    'priority': 'u=1, i',
    'referer': 'https://topaz24.pl/aktualna-gazetka',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

data = {
    'cityAndStreet': '',
}

url = 'https://topaz24.pl/api/map/latest'

# Function to generate UUID based on the URL
def generate_uuid(url):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, url))

# Function to log download information
def log_download(uuid, filename, log_file):
    # Ensure the directory exists, create it if necessary
    log_directory = os.path.dirname(log_file)
    try:
        os.makedirs(log_directory, exist_ok=True)  # Create directory if it doesn't exist
    except OSError as e:
        print(f"Error creating directory: {e}")
    
    # Format timestamp
    timestamp = datetime.now().strftime('%d-%m-%y %H:%M')
    # Prepare log message
    log_message = f"{timestamp}: UUID {uuid} - File {filename} downloaded.\n"
    # Append log message to log file
    try:
        with open(log_file, 'a') as log:
            log.write(log_message)
    except IOError as e:
        print(f"Error writing to log file: {e}")

# Function to generate UUID from URL
def generate_uuid_from_url(url):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, url))

# Function to check if UUID has already been downloaded
def check_already_downloaded(uuid, log_file):
    try:
        with open(log_file, 'r') as log:
            log_content = log.read()
            return uuid in log_content
    except IOError as e:
        print(f"Error reading log file: {e}")
        return False

def download_pdf(url, download_directory, log_file):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_link_tag = soup.find('a', id='pdf')
        
        if pdf_link_tag and 'href' in pdf_link_tag.attrs:
            pdf_link = pdf_link_tag['href']
            if not pdf_link.startswith('http'):
                pdf_link = f"https://topaz24.pl{pdf_link}"
            
            # Generate UUID using the original URL, not the PDF link
            pdf_uuid = generate_uuid(url)
            pdf_filename = f"{pdf_uuid}.pdf"
            pdf_filepath = os.path.join(download_directory, pdf_filename)
            
            # Check if PDF with UUID has already been downloaded
            if check_already_downloaded(pdf_uuid, log_file):
                print(f"PDF with UUID {pdf_uuid} has already been downloaded. Skipping.")
                return None
            
            # Proceed with downloading the PDF
            pdf_response = requests.get(pdf_link)
            if pdf_response.status_code == 200:
                # Save the PDF to a file named with the UUID
                with open(pdf_filepath, 'wb') as pdf_file:
                    pdf_file.write(pdf_response.content)
                
                # Log the download
                log_download(pdf_uuid, pdf_filename, log_file)
                print(f"PDF {pdf_filename} downloaded and saved.")
                return pdf_filepath
            else:
                print(f"Failed to download PDF from {pdf_link}, status code: {pdf_response.status_code}")
        else:
            print(f"PDF link not found on {url}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")

# Make POST request
response = requests.post(url, headers=headers, data=data)

# Check if request was successful (status code 200)
if response.status_code == 200:
    try:
        # Parse JSON response
        json_data = response.json()
        
        # Debug print to check JSON response
        print("Full JSON response:")
        print(json.dumps(json_data, indent=4, ensure_ascii=False))
        
        # Dictionary to store links and their associated entries
        link_groups = {}

        # Function to recursively extract links and their associated cities from the JSON
        def extract_links_and_entries(data, city=None, street=None):
            if isinstance(data, dict):
                city = data.get('city', city)
                street = data.get('street', street)
                link = data.get('link', None)
                name = data.get('name', None)
                
                if link and name:
                    link_with_prefix = f"https://topaz24.pl/{link.lstrip('/')}"
                    if link_with_prefix not in link_groups:
                        link_groups[link_with_prefix] = []
                    entry = {
                        'name': name,
                        'link': link,
                        'city': city,
                        'street': street
                    }
                    link_groups[link_with_prefix].append(entry)
                    
                for value in data.values():
                    extract_links_and_entries(value, city, street)
            elif isinstance(data, list):
                for item in data:
                    extract_links_and_entries(item, city, street)

        # Start extraction from the root of the JSON data
        extract_links_and_entries(json_data)

        # Ensure output directory exists
        download_directory = "C:\\Users\\bartd\\Desktop\\Bartus files\\WORK\\upload"
        log_file = "C:\\Users\\bartd\\Desktop\\Bartus files\\PYTHON\\scrapping_log\\scrapping_log.txt"
        os.makedirs(download_directory, exist_ok=True)

        # Iterate over the extracted link groups and create JSON and download PDF
        for link, entries in link_groups.items():
            # Generate UUID for the link
            link_uuid = generate_uuid(link)
            
            # Download the PDF associated with each link
            pdf_filepath = download_pdf(link, download_directory, log_file)
            
            if pdf_filepath:
                # Create the data to be saved in JSON only if PDF was successfully downloaded
                group_data = {
                    'link': link,
                    'entries': entries
                }
                
                # Save the JSON data to a file named with the link UUID in the same directory as PDF
                json_file_path = os.path.join(download_directory, f'{link_uuid}.json')
                with open(json_file_path, 'w', encoding='utf-8') as json_file:
                    json.dump(group_data, json_file, ensure_ascii=False, indent=4)
                
                # Print the UUID and the link for reference
                print(f'UUID: {link_uuid}, Link: {link}')
    
    except ValueError as e:
        print("Error parsing JSON:", e)

else:
    print(f"Error: {response.status_code}")
