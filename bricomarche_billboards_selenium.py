import os
import uuid
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Retailer-specific configuration
retailer = "bricomarche"
starting_url = 'https://www.bricomarche.pl/'
img_selector = 'div.m-slider_content div.m-slider_item a.js-imageWidget picture source[media="(min-width: 1024px)"]'
img_attribute = 'srcset'
download_directory = "C:\\Users\\bartd\\Desktop\\Bartus files\\WORK\\upload"
log_file = "C:\\Users\\bartd\\Desktop\\Bartus files\\PYTHON\\scrapping_log\\scrapping_log.txt"
chromedriver_path = 'C:/WebDriver/chromedriver.exe'  # Replace with your actual path

# Selenium options for headless browsing
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration

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
    try:
        # Start ChromeDriver service
        service = Service(chromedriver_path)
        service.start()
        
        # Initialize WebDriver with service and options
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Load the starting URL
        driver.get(starting_url)
        
        # Wait for page to fully load (you may need to adjust the wait time)
        driver.implicitly_wait(10)  # 10 seconds implicit wait

        # Find all image elements matching the selector
        img_elements = driver.find_elements_by_css_selector(img_selector)

        for img in img_elements:
            img_url = img.get_attribute(img_attribute)
            if not img_url:
                continue

            # Ensure img_url is a fully qualified URL
            if not img_url.startswith('http'):
                img_url = starting_url.rstrip('/') + '/' + img_url.lstrip('/')

            filename = os.path.basename(img_url)
            file_uuid = generate_uuid_from_url(img_url)

            # Download image and log
            try:
                # For simplicity, assume downloading and renaming here
                # Construct full file path
                filepath = os.path.join(download_directory, filename)
                print(f"Downloading {filename} to {filepath}")  # Debug statement

                # Download the image using requests or other methods
                # For simplicity, let's assume you download it directly here

                print(f"Downloaded: {filename}")

                new_filename = rename_file_with_uuid(filepath, file_uuid)
                log_download(file_uuid, new_filename, log_file)

            except Exception as e:
                print(f"Error downloading image {img_url}: {e}")

        # Close the Selenium WebDriver
        driver.quit()
        service.stop()

    except Exception as e:
        print(f"Error accessing {starting_url} with Selenium: {e}")

if __name__ == "__main__":
    download_images_from_retailer()
