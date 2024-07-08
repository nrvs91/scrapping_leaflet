import requests
import os
import uuid
from datetime import datetime

url = 'https://api-serwis.grupaeurocash.pl/newspaper-module'
download_directory = 'C:\\Users\\bartd\\Desktop\\Bartus files\\PYTHON\\downloaded_leaflets'
log_directory = 'C:\\Users\\bartd\\Desktop\\Bartus files\\PYTHON\\scrapping_log'
log_file = 'scrapping_log.txt'

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
    'App-Id': 'cf40a7ef-98d7-4dbc-ac09-429ec44a3b36',
    'Dnt': '1',
    'Origin': 'https://serwis.grupaeurocash.pl',
    'Priority': 'u=1, i',
    'Referer': 'https://serwis.grupaeurocash.pl/',
    'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Token': 'f4311c4338d8d76fabbdffd34e32a7f9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}

# Function to generate UUID based on URL
def generate_uuid_from_url(url):
    # Generate UUID based on the URL
    uuid_name = uuid.uuid5(uuid.NAMESPACE_URL, url)
    # Convert UUID to string and return
    return str(uuid_name)

# Function to log download details
def log_download(uuid, filename, log_directory):
    # Ensure the directory exists, create it if necessary
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    
    # Construct full path to the log file
    log_file_path = os.path.join(log_directory, log_file)
    
    # Format timestamp
    timestamp = datetime.now().strftime('%d-%m-%y %H:%M')
    # Prepare log message
    log_message = f"{timestamp}: UUID {uuid} - File {filename} downloaded.\n"
    # Append log message to log file
    with open(log_file_path, 'a') as log:
        log.write(log_message)

# Function to download a PDF file from a URL to a specified directory
def download_pdf(url, directory):
    filename = url.split('/')[-1]  # Extract filename from URL
    filepath = os.path.join(directory, filename)
    response = requests.get(url)
    response.raise_for_status()
    with open(filepath, 'wb') as f:
        f.write(response.content)
    print(f"Downloaded: {filename}")
    return filepath  # Return the full path of the downloaded file

# Send GET request to the API endpoint
response = requests.get(url, headers=headers)

# Check if request was successful (status code 200)
if response.status_code == 200:
    # Parse JSON response
    data = response.json()

    # Function to recursively search for 'newsletter_url'
    def find_newsletter_urls(obj):
        urls = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == 'newsletter_url':
                    urls.append(value)
                elif isinstance(value, (dict, list)):
                    urls.extend(find_newsletter_urls(value))
        elif isinstance(obj, list):
            for item in obj:
                urls.extend(find_newsletter_urls(item))
        return urls

    # Search for occurrences of 'newsletter_url' in the JSON response
    newsletter_urls = find_newsletter_urls(data)
    
    # Download each file
    if newsletter_urls:
        for idx, newsletter_url in enumerate(newsletter_urls):
            # Extract filename from URL
            filename = os.path.basename(newsletter_url)
            print(f"Downloading file {idx + 1}/{len(newsletter_urls)}: {filename}...")
            
            try:
                # Send request to download the file
                file_response = requests.get(newsletter_url)
                
                # Check if download was successful (status code 200)
                if file_response.status_code == 200:
                    # Save the file to the download directory
                    downloaded_filepath = download_pdf(newsletter_url, download_directory)
                    print(f"File {filename} downloaded successfully.")
                    
                    # Generate UUID based on the URL
                    file_uuid = generate_uuid_from_url(newsletter_url)
                    
                    # Log the download
                    log_download(file_uuid, os.path.basename(downloaded_filepath), log_directory)
                else:
                    print(f"Failed to download file {filename}. Status code: {file_response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Error downloading {filename}: {e}")
    else:
        print("No 'newsletter_url' found in the JSON response.")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
