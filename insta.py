from playwright.sync_api import sync_playwright
import time
import json
import os

# Replace these with your Instagram credentials
username = "YourInstagramMailId"
password = "YourPassword"
SESSION_FILE = "instagram_session.json"  # File to store session data

import requests

def download_video(video_url, save_path):
    try:
        response = requests.get(video_url, stream=True)
        response.raise_for_status()  # Ensure the request was successful
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded video to {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download video: {e}")


def save_session(context):
    context.storage_state(path=SESSION_FILE)

def load_session():
    # Check if session file exists and is valid
    if os.path.exists(SESSION_FILE):
        return SESSION_FILE  # Return the session file path if it exists
    return None  # No session file available

def login_to_instagram():
    media_urls = []

    def is_media_file(response):
        content_type = response.headers.get("content-type", "")
        return "video" in content_type

    with sync_playwright() as p:
        storage_state = load_session()
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=storage_state)

        page = context.new_page()
        page.on("response", lambda response:
            media_urls.append(response.url) if is_media_file(response) else None
        )
        page.goto("https://www.instagram.com/")
        page.wait_for_load_state("networkidle")
        try:
            page.fill("input[name='username']", username)
            if page.url == "https://www.instagram.com/":

                page.fill("input[name='username']", username)
                page.fill("input[name='password']", password)
                page.click("button[type='submit']")
                page.wait_for_load_state("networkidle")
                save_session(context)
        except :
            pass

        page.goto("https://www.instagram.com/explore/")
        page.wait_for_load_state("networkidle")
        for i in range(3):
            page.evaluate("window.scrollBy(0, 2000)")
            time.sleep(3)

        # Extract links
        total_links = [link.get_attribute("href") for link in page.query_selector_all('a[role="link"]')]
        total_links = [link for link in total_links if '/p/' in link]
        
        for link in total_links:
            page.goto(f"https://www.instagram.com{link}")
            time.sleep(3)

        # Close the browser
        browser.close()
        
        # Download the video and save it
        media_urls = list(set(media_urls))
        for i, video_url in enumerate(media_urls):
            download_video(video_url, f"instagram/instagram_video_{i}.mp4")

login_to_instagram()