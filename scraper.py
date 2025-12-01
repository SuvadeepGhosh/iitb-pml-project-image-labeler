from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import os
import requests

# Configuration
TARGET_URL = "https://www.espncricinfo.com/photo"
SAVE_DIR = "raw_images"
MAX_IMAGES = 10
SCROLL_PAUSE_TIME = 2

def scrape_images():
    # Ensure directory exists
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    print("Setting up Selenium (Headless Chrome)...")
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Mimic a real user agent
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Failed to initialize Selenium: {e}")
        print("Make sure you have Chrome installed.")
        return

    try:
        print(f"Fetching {TARGET_URL}...")
        driver.get(TARGET_URL)
        
        # Scroll to load more images
        # We'll scroll down a few times
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        images_found = 0
        downloaded_urls = set()
        
        while images_found < MAX_IMAGES:
            # Find all image elements
            img_elements = driver.find_elements(By.TAG_NAME, "img")
            
            print(f"Found {len(img_elements)} images on page so far...")
            
            for img in img_elements:
                if images_found >= MAX_IMAGES:
                    break
                    
                try:
                    src = img.get_attribute("src")
                    if not src:
                        continue
                        
                    # Filter for content images (hscicdn)
                    if "hscicdn.com" not in src:
                        continue
                        
                    if src in downloaded_urls:
                        continue
                        
                    # Download
                    print(f"Downloading {src}...")
                    response = requests.get(src, timeout=10)
                    if response.status_code == 200:
                        filename = os.path.join(SAVE_DIR, f"scraped_{images_found+1}.jpg")
                        with open(filename, "wb") as f:
                            f.write(response.content)
                        print(f"Saved to {filename}")
                        downloaded_urls.add(src)
                        images_found += 1
                    else:
                        print(f"Failed to download (Status {response.status_code})")
                        
                except Exception as e:
                    print(f"Error processing image: {e}")
            
            if images_found >= MAX_IMAGES:
                break
                
            # Scroll down
            print("Scrolling down to load more...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            
            # Check if we reached bottom
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("Reached bottom of page or no new content loaded.")
                break
            last_height = new_height
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Closing browser...")
        driver.quit()

    print(f"Done. Downloaded {images_found} images.")

if __name__ == "__main__":
    scrape_images()
