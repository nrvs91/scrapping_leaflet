import requests
import json
import os
from urllib.parse import urlparse
from pathlib import Path

def fetch_and_parse_jsonp(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        content = response.text
        json_start = content.index('{')
        json_end = content.rindex('}') + 1
        json_content = content[json_start:json_end]
        
        data = json.loads(json_content)
        
        n_values = []
        
        if 'n' in data['set']:
            n_values.append(data['set']['n'])
        
        for item in data['set']['item']:
            if 'i' in item:
                if isinstance(item['i'], dict) and 'n' in item['i']:
                    n_values.append(item['i']['n'])
                elif isinstance(item['i'], list):
                    for sub_item in item['i']:
                        if isinstance(sub_item, dict) and 'n' in sub_item:
                            n_values.append(sub_item['n'])
        
        return n_values
    else:
        return f"Failed to fetch content. Status code: {response.status_code}"

def download_images(n_values, download_dir):
    base_url = "https://s7g10.scene7.com/is/image/"
    
    # Create the images directory within the specified download directory
    images_dir = os.path.join(download_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    for index, value in enumerate(n_values, start=1):
        full_url = base_url + value
        
        # Get the file extension from the URL
        parsed_url = urlparse(full_url)
        extension = Path(parsed_url.path).suffix or '.jpg'  # Default to .jpg if no extension
        
        filename = os.path.join(images_dir, f"image_{index:03d}{extension}")
        
        try:
            response = requests.get(full_url, stream=True)
            response.raise_for_status()
            
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            print(f"Downloaded {filename}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {full_url}: {e}")

# URL to fetch
url = "https://s7g10.scene7.com/is/image/jeronimomartins/2024_FOOD_T27_B_LADA_vm8qjnpv9m?req=set,json,UTF-8&labelkey=label&id=33120103&handler=s7classics7sdkJSONResponse"

# Specify the download directory
download_dir = r"C:\Users\bartd\Desktop\Bartus files\WORK\upload"

# Fetch and parse the 'n' values
n_values = fetch_and_parse_jsonp(url)

# Download the images
download_images(n_values, download_dir)