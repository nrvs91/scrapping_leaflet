import requests
import os
from datetime import datetime
import uuid

download_directory = "C:\\Users\\bartd\\Desktop\\Bartus files\\WORK\\upload"
log_file = "C:\\Users\\bartd\\Desktop\\Bartus files\\PYTHON\\scrapping_log\\scrapping_log.txt"

# Function to generate UUID based on URL
def generate_uuid_from_url(url):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, url))

# Function to log download details
def log_download(uuid, filename, log_file):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    timestamp = datetime.now().strftime('%d-%m-%y %H:%M')
    log_message = f"{timestamp}: UUID {uuid} - File {filename} downloaded.\n"
    try:
        with open(log_file, 'a') as log:
            log.write(log_message)
    except IOError as e:
        print(f"Error writing to log file: {e}")

# Function to rename file with UUID
def rename_file_with_uuid(filename, uuid):
    base_name, extension = os.path.splitext(filename)
    new_filename = f"{uuid}.{extension.strip('.')}"
    try:
        os.rename(filename, new_filename)
        return new_filename
    except OSError as e:
        print(f"Error renaming file: {e}")
        return filename

# Function to fetch JSON data from a URL
def get_json_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# Function to extract download URL from a subpage JSON data
def extract_download_url(subpage_url, prefix):
    response = requests.get(subpage_url)
    response.raise_for_status()
    data = response.json()
    download_url = data.get('config', {}).get('downloadPdfUrl')
    return prefix + download_url if download_url else None

# Function to download a PDF file from a URL to a specified directory
def download_pdf(url, download_directory):
    filename = url.split('/')[-1]
    filepath = os.path.join(download_directory, filename)
    os.makedirs(download_directory, exist_ok=True)
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
        return filepath
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        raise

# Function to check if a file with the given UUID has already been downloaded
def check_already_downloaded(uuid, log_file):
    try:
        with open(log_file, 'r') as log:
            return uuid in log.read()
    except IOError as e:
        print(f"Error reading log file: {e}")
        return False

# Main function to orchestrate the downloading process
def main(json_urls, prefix, download_directory, log_file):
    os.makedirs(download_directory, exist_ok=True)

    for json_url in json_urls:
        try:
            print(f"Processing JSON data from {json_url}")
            json_data = get_json_from_url(json_url)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching JSON data from {json_url}: {e}")
            continue

        urls = [entry['url'] for entry in json_data]
        extracted_urls = []
        for url in urls:
            try:
                print(f"Processing URL: {url}")
                download_url = extract_download_url(url, prefix)
                if download_url:
                    extracted_urls.append(download_url)
            except requests.exceptions.RequestException as e:
                print(f"Error extracting download URL from {url}: {e}")

        for pdf_url in extracted_urls:
            try:
                print(f"Downloading PDF from: {pdf_url}")
                file_uuid = generate_uuid_from_url(pdf_url)
                if check_already_downloaded(file_uuid, log_file):
                    print(f"File with UUID {file_uuid} has already been downloaded. Skipping.")
                    continue
                filepath = download_pdf(pdf_url, download_directory)
                renamed_filepath = rename_file_with_uuid(filepath, file_uuid)
                log_download(file_uuid, os.path.basename(renamed_filepath), log_file)
            except (requests.exceptions.RequestException, OSError) as e:
                print(f"Error processing {pdf_url}: {e}")

    print("All PDFs downloaded successfully!")


if __name__ == "__main__":
    json_urls = [
        "https://api.publitas.com/v1/groups/gazetka-promocyjna-makro-login/publications.json",
        "https://api.publitas.com/v1/groups/gazetka-promocyjna-makro/publications.json"
    ]
    prefix = "https://gazetki-login.makro.pl"
    download_directory = "C:\\Users\\bartd\\Desktop\\Bartus files\\WORK\\upload"
    log_file = "C:\\Users\\bartd\\Desktop\\Bartus files\\PYTHON\\scrapping_log\\scrapping_log.txt"

    main(json_urls, prefix, download_directory, log_file)
