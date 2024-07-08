import requests
from requests_html import HTMLSession
import os
from datetime import datetime
import uuid

# Retailer-specific configuration
retailer = "bricomarche"
starting_url = 'https://www.bricomarche.pl/'
img_selector = 'div.m-slider_content div.m-slider_item a.js-imageWidget picture source[media="(min-width: 1024px)"]'
img_attribute = 'srcset'
download_directory = "C:\\Users\\bartd\\Desktop\\Bartus files\\WORK\\upload"
log_file = "C:\\Users\\bartd\\Desktop\\Bartus files\\PYTHON\\scrapping_log\\scrapping_log.txt"
headers = {
    'Dnt': '1',
    'Referer': 'https://www.bricomarche.pl/',
    'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

def log_download(uuid, filename, log_file=log_file):
    log_directory = os.path.dirname(log_file)
    try:
        os.makedirs(log_directory, exist_ok=True)
    except OSError as e:
        print(f"Error creating directory: {e}")
    
    timestamp = datetime.now().strftime('%d-%m-%y %H:%M')
    log_message = f"{timestamp}: UUID {uuid} - File {filename} downloaded.\n"
    try:
        with open(log_file, 'a') as log:
            log.write(log_message)
    except IOError as e:
        print(f"Error writing to log file: {e}")

def generate_uuid_from_url(url):
    uuid_name = uuid.uuid5(uuid.NAMESPACE_URL, url)
    return str(uuid_name)

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

def download_images_from_retailer():
    session = HTMLSession()
    try:
        response = session.get(starting_url)
        response.raise_for_status()
        
        # Render JavaScript to ensure content is fully loaded
        response.html.render()

        img_elements = response.html.find(img_selector)

        for img in img_elements:
            img_url = img.attrs.get(img_attribute)
            if not img_url:
                continue

            # Ensure img_url is a fully qualified URL
            if not img_url.startswith('http'):
                img_url = starting_url.rstrip('/') + '/' + img_url.lstrip('/')

            filename = os.path.basename(img_url)
            file_uuid = generate_uuid_from_url(img_url)

            # Download image and log
            try:
                img_response = session.get(img_url)
                img_response.raise_for_status()

                # Ensure download directory exists
                os.makedirs(download_directory, exist_ok=True)

                # Construct full file path
                filepath = os.path.join(download_directory, filename)
                print(f"Downloading {filename} to {filepath}")  # Debug statement

                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                print(f"Downloaded: {filename}")

                new_filename = rename_file_with_uuid(filepath, file_uuid)
                log_download(file_uuid, new_filename, log_file)

            except requests.exceptions.RequestException as e:
                print(f"Error downloading image {img_url}: {e}")

    except requests.exceptions.RequestException as e:
        print(f"Error accessing {starting_url}: {e}")

    finally:
        session.close()

if __name__ == "__main__":
    download_images_from_retailer()
