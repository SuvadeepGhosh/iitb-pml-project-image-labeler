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
    "authority": "www.espncricinfo.com",
    "method": "GET",
    "path": "/photo",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "cookie": 'country=in; edition=espncricinfo-en-in; edition-view=espncricinfo-en-in; region=unknown; _dcf=1; connectionspeed=full; SWID=493e545b-2047-4d97-a908-ded367115e78; _cc_id=cbabd7d05340ec2e28cc87c2ae9cf0cb; panoramaId_expiry=1764685219473; connectId={"ttl":86400000,"lastUsed":1764598819552,"lastSynced":1764598819552}; s_ensCDS=0; AMCVS_EE0201AC512D2BE80A490D4C%40AdobeOrg=1; s_cc=true; WZRK_G=13e07da5ca4d46458e4e05d1926e3572; _ga=GA1.1.1616905896.1764598821; cto_bundle=I7JLRV92anJ4TnMzODB3cWVhUzcxbUJITmVaNGlrdzhFTHA3RmFQVDlCZEsyckpoVU5ENWtCcUp6SFF4bmI0dUttWGJ0ckMzMlZzMDY3TVNoMkpDQWpPTW4yTjJtTkpqdkdEV3ZiWDBGTjNVS09NbTJYcjV2aXBkbjRvOG1YcUxkOWE3UDdNUVN4RHRZYmIlMkJUY29ZR2YybWdBTExaTHN3MU84S3dsZDhDT2Q1Vnl2b1lkWTNFOWdZU09LNm9QdTdqMWF5Qw; __gads=ID=1ea0310e21291808:T=1764598819:RT=1764613964:S=ALNI_MZbuyd3jensc3zJ9wKa9l2yfFMPgA; __gpi=UID=000011c04d32acc2:T=1764598819:RT=1764613964:S=ALNI_Mb7sbJv5TkJmy5xVT7s6k3Kmo7Jyg; __eoi=ID=d69155c2c9f5e584:T=1764598819:RT=1764613964:S=AA-AfjYKxNgACkoBHEIdiEM-zMP3; bm_ss=ab8e18ef4e; _ga_XS3N0WC54W=GS2.1.s1764613965$o2$g1$t1764614180$j60$l0$h0; bm_so=613DB6E3DB34A96653EA02FCF35835BE8084CDDD28943C384234BE3161FCC735~YAAQ0RzFF7GIU6qaAQAASb0z2wVuS9IF2s6JPpF6S32uCIQrfd+T0PBm2i0LJ9RTqd9DZW5xyWbhhD3BbA1qzHdOG0T3jHc7/uwM/3bb+JxVC+927OsqPC9ZKp/10Yjnu0RlcZIncxEINCTumDzBsacmmdNXZnXFfYvF+201r0qx0XVIX8bqKdpk4A7oHVE8MiH5U+NGJ9BHsqDdDd86d33ERQtjfLCNBtkGzz72HfePG87KzhDoIyF/3SriKbrDFasijBo0hVTDBXTfFi7IPnShoVkTBHPo3cZ7hO4ckhWS8HiORngu2Ak5V75Z16r6w00aip/qAgB676t5Oe674Li70nl3lQingg3YzS7xJ81BcNMnFPGVAMFIrIqW5JU46/9zVI6Ly7NAto5QYaALzUOebl0LI85itacqLd7pzrmKiTJD853QXc5WMwMTJbwrbHsnC86RG9vFyjRaNzaArSJqtLgJBX4YfuoAVv+DleirmPHh0/zSRBa18nQ1; s_c24_s=Less%20than%201%20day; s_ips=788; AMCV_EE0201AC512D2BE80A490D4C%40AdobeOrg=1585540135%7CMCIDTS%7C20424%7CMCMID%7C27154492460493620753357092718737483078%7CMCAAMLH-1765218993%7C12%7CMCAAMB-1765218993%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1764621393s%7CNONE%7CvVersion%7C4.4.0; bm_lso=613DB6E3DB34A96653EA02FCF35835BE8084CDDD28943C384234BE3161FCC735~YAAQ0RzFF7GIU6qaAQAASb0z2wVuS9IF2s6JPpF6S32uCIQrfd+T0PBm2i0LJ9RTqd9DZW5xyWbhhD3BbA1qzHdOG0T3jHc7/uwM/3bb+JxVC+927OsqPC9ZKp/10Yjnu0RlcZIncxEINCTumDzBsacmmdNXZnXFfYvF+201r0qx0XVIX8bqKdpk4A7oHVE8MiH5U+NGJ9BHsqDdDd86d33ERQtjfLCNBtkGzz72HfePG87KzhDoIyF/3SriKbrDFasijBo0hVTDBXTfFi7IPnShoVkTBHPo3cZ7hO4ckhWS8HiORngu2Ak5V75Z16r6w00aip/qAgB676t5Oe674Li70nl3lQingg3YzS7xJ81BcNMnFPGVAMFIrIqW5JU46/9zVI6Ly7NAto5QYaALzUOebl0LI85itacqLd7pzrmKiTJD853QXc5WMwMTJbwrbHsnC86RG9vFyjRaNzaArSJqtLgJBX4YfuoAVv+DleirmPHh0/zSRBa18nQ1^1764614195556; bm_s=YAAQ0RzFF86JU6qaAQAAqfYz2wTGO3td7e9ZxW3g/nYj0fblGC8QvOP0KFL2LdJNS1gYmjmfZl60ehp4/tRxO3JQLCRfl8DaZ2zddhpsECLWaKr2mjAVR/c+bYI8cjz+A8YlPhuCUU7m36k2swfWD1XSYV4GRHQefms+tNq44RM/+NJEGFXpdw+YDVm9w0hyMHiT46VO4u7VD6aAsQYUzLl4c45bKEoqY7MUMHxLDqFNmyf12hyjKime44mDecQBWgv19btWlgSWPvUp2rBGpg1jt4ogiAMFLDCzjSy9iN1GRqXedxviiUB52r/oSdd+B+XOtHhzgtVjAo/uIGX0dPFtjO5WgKbTDhSkF1Vrl54mqo2jE5T9LiCalRjcMZAbNhLE3ERk4IYDV4qB/RrKA9yvmMZdPbp2+s/lHhwrFyPSGRcPeBrzNz+D9X3wDt0Cw+Lkr7NbT9s6gRsN9LMrRSFVQZd31GHAOJcef+/UIJXuxr6ClfmIzi4KsULp7a/Qd9N2sPnZUAnIRRYAix0l6M2QtbP0T4grvUGw9+F3bqqzFeuhnqBIWabGNrpDcngYy5vpOkVg/5aNFh96696gUtY7a68ADX4f0xASlb1H8lQLU5TX7hVd4FsA+SHidTQ4PWtvhAreamS1WH2z; s_ensNR=1764614208113-Repeat; FCCDCF=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B32%2C%22%5B%5C%22d0d0066b-5380-4c64-83ea-88959170ba07%5C%22%2C%5B1764598819%2C744000000%5D%5D%22%5D%5D%5D; WZRK_S_884-7R5-R85Z=%7B%22p%22%3A3%2C%22s%22%3A1764614193%2C%22t%22%3A1764614208%7D; nol_fpid=v1q4dpufhvfjhqgk0suqdmvqf1u6t1764598820|1764598820741|1764614208762|1764614208842; FCNEC=%5B%5B%22AKsRol-8_sYwssqYepEbY7z-hXr-B0rRZiCQwtisxxTpo_ZwWVEqghpIMEPDwy5Yj6bp3aneSl393lgWo_vb8_HFcFDTBOYSmWggqewsU6_Is5P_Awxh2y_TjUsN3YD_te6imXWqneHJX7TPyJH5CyvGRJXAe8aeXA%3D%3D%22%5D%5D; s_nr30=1764614218970-Repeat; s_gpv=espncricinfo%3Aphoto%3Ashoaib-bashir-and-will-jacks-had-a-session-bowling-under-lights; s_c24=1764614218971; s_tp=788; s_ppv=espncricinfo%253Aphoto%253Ashoaib-bashir-and-will-jacks-had-a-session-bowling-under-lights%2526pidt%253D1%2526oid%253Dfunctionrg%252528%252529%25257B%25257D%2526oidt%253D2%2526ot%253DI',
    "priority": "u=0, i",
    "referer": "https://www.espncricinfo.com/photo/shoaib-bashir-and-will-jacks-had-a-session-bowling-under-lights-1513992",
    "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
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
