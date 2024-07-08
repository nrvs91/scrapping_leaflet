import requests
import json

url = "https://api.marketdino.pl/api/v1/sections_contents/banners/leaflet_slider/?format=json&size=desktop_leaflet_banner"

def save_json_response():
    try:
        # Send GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Save the JSON response to a file
            with open("response.json", "w") as file:
                file.write(response.text)
            print("JSON response saved to 'response.json'")
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
    
    except Exception as e:
        print(f"An error occurred while saving JSON response: {str(e)}")

def print_image_urls_from_json():
    try:
        # Load the saved JSON file
        with open("response.json", "r") as file:
            data = json.load(file)
            
            # Extract and print all image URLs from the JSON data
            banners = data.get('banners', [])
            for banner in banners:
                file_info = banner.get('file', {})
                if 'url' in file_info:
                    print(file_info['url'])
    
    except FileNotFoundError:
        print("No 'response.json' file found. Run save_json_response() first.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in 'response.json': {str(e)}")
    except Exception as e:
        print(f"An error occurred while loading JSON file: {str(e)}")

# Save the JSON response to a file
save_json_response()

# Print image URLs from the saved JSON file
print_image_urls_from_json()
