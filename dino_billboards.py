import requests
import os
import json
import uuid
from datetime import datetime
import tempfile

# Retailer-specific configuration
retailer = "dino"
url = "https://api.marketdino.pl/api/v1/sections_contents/banners/leaflet_slider/?format=json&size=desktop_leaflet_banner"
download_directory = "C:\\Users\\bartd\\Desktop\\Bartus files\\WORK\\upload"
log_file = "C:\\Users\\bartd\\Desktop\\Bartus files\\PYTHON\\scrapping_log\\scrapping_log.txt"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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

def check_already_downloaded(uuid, log_file):
    try:
        with open(log_file, 'r') as log:
            log_content = log.read()
            return uuid in log_content
    except IOError as e:
        print(f"Error reading log file: {e}")

def save_json_response():
    try:
        # Send GET request to the URL
        response = requests.get(url, headers=headers)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Create a temporary file to store the JSON response
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(response.content)
                temp_filename = temp_file.name
            print(f"Temporary JSON file saved: {temp_filename}")
            return temp_filename
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return None
    
    except Exception as e:
        print(f"An error occurred while saving JSON response: {str(e)}")
        return None

def download_images_from_json(json_filename):
    try:
        # Load the temporary JSON file
        with open(json_filename, "r") as file:
            data = json.load(file)
            
            # Extract and download images from the JSON data
            banners = data.get('banners', [])
            for banner in banners:
                file_info = banner.get('file', {})
                if 'url' in file_info:
                    img_url = file_info['url']
                    filename = os.path.basename(img_url)
                    file_uuid = generate_uuid_from_url(img_url)

                    if check_already_downloaded(file_uuid, log_file):
                        print(f"Image with UUID {file_uuid} has already been downloaded. Skipping.")
                        continue

                    try:
                        img_response = requests.get(img_url, headers=headers)
                        img_response.raise_for_status()

                        os.makedirs(download_directory, exist_ok=True)

                        filepath = os.path.join(download_directory, filename)

                        with open(filepath, 'wb') as f:
                            f.write(img_response.content)

                        new_filename = rename_file_with_uuid(filepath, file_uuid)
                        log_download(file_uuid, new_filename, log_file)

                        print(f"Downloaded: {filename}")

                    except requests.exceptions.RequestException as e:
                        print(f"Error downloading image {img_url}: {e}")

    except FileNotFoundError:
        print("No JSON file found. Run save_json_response() first.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {str(e)}")
    except Exception as e:
        print(f"An error occurred while processing JSON data: {str(e)}")
    finally:
        # Clean up: delete the temporary JSON file
        if os.path.exists(json_filename):
            os.remove(json_filename)
            print(f"Temporary JSON file deleted: {json_filename}")

if __name__ == "__main__":
    # Save the JSON response to a temporary file
    temp_json_file = save_json_response()
    
    if temp_json_file:
        # Download images using the temporary JSON file
        download_images_from_json(temp_json_file)
