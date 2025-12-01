import requests
from bs4 import BeautifulSoup
import os
import time

# Configuration
TARGET_URL = "https://www.espncricinfo.com/photo"
SAVE_DIR = "raw_images"
MAX_IMAGES = 10

# Headers to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "Upgrade-Insecure-Requests": "1"
}

def scrape_images():
    # Ensure directory exists
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    print(f"Fetching {TARGET_URL}...")
    try:
        response = requests.get(TARGET_URL, headers=HEADERS)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch page: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all image tags
    img_tags = soup.find_all("img")
    
    count = 0
    downloaded_urls = set()

    print(f"Found {len(img_tags)} image tags. Filtering and downloading...")

    for img in img_tags:
        if count >= MAX_IMAGES:
            break

        img_url = img.get("src")
        if not img_url:
            img_url = img.get("data-src") # Sometimes used for lazy loading
        
        if not img_url:
            continue

        # Filter for likely content images (Cricinfo uses hscicdn)
        # We want to avoid small icons, tracking pixels, etc.
        # Good cricinfo images often have 'db/PICTURES' or are from 'img1.hscicdn.com'
        if "hscicdn.com" not in img_url:
            continue
            
        # Try to get a higher quality version if possible
        # Cricinfo urls often have transformation params like /f_auto,t_ds_square_w_160/
        # We can try to strip them or replace them, but for now let's just grab what's there
        # or maybe replace 'w_160' with 'w_1200' if we see it.
        
        # Simple heuristic: ignore very small thumbnails if possible (hard to tell from URL alone)
        # But let's try to replace width params to get better quality
        if "w_" in img_url:
             # This is a bit hacky but might work to get better res
             # Example: .../t_ds_square_w_160/... -> .../t_ds_wide_w_800/...
             pass 

        if img_url in downloaded_urls:
            continue

        try:
            # Download image
            print(f"Downloading {img_url}...")
            img_data = requests.get(img_url, headers=HEADERS, timeout=10).content
            
            # Generate filename
            filename = os.path.join(SAVE_DIR, f"scraped_{count+1}.jpg")
            
            with open(filename, "wb") as f:
                f.write(img_data)
            
            print(f"Saved to {filename}")
            downloaded_urls.add(img_url)
            count += 1
            
            # Be nice to the server
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Failed to download {img_url}: {e}")

    print(f"Done. Downloaded {count} images.")

if __name__ == "__main__":
    scrape_images()
