import pyautogui as pgui
import time
from pynput import keyboard as kb
import sys
import csv
import os
import requests
import pandas as pd
import base64
from io import BytesIO
from PIL import Image
import json
import configparser
import pyperclip
import pytesseract
import platform  # Add this import for OS detection
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Configuration variables
OLLAMA_HOST = config.get(
    'DEFAULT',
    'ollama_host',
    fallback='http://localhost:11434')
OLLAMA_MODEL = config.get('DEFAULT', 'ollama_model', fallback='qwen2.5vl:7b')

CLASSIFICATION_PROMPT = """
Please classify this YouTube video based on its title and thumbnail.

Video Title: {video_title}

Existing Classifications: {existing_categories}

Instructions:
1. If the video fits into one of the existing classifications, use that exact classification name.
2. If the video doesn't fit any existing classification, create a new appropriate classification name.
3. Classification names should be concise (1-3 words) and descriptive.
4. Examples of good classifications: "Tech Reviews", "Cooking", "Gaming", "Education", "Music", "Comedy", etc.
5. Respond with ONLY the classification name, nothing else.
"""

LANGUAGE_DETECTION_PROMPT = """
Please detect the language of this YouTube video based on its title and thumbnail.

Video Title: {video_title}

Instructions:
1. Analyze the title text to determine the primary language
2. Consider any text visible in the thumbnail image
3. Respond with the language name in English (e.g., "English", "Spanish", "French", "Japanese", etc.)
4. If multiple languages are present, choose the dominant one
5. If uncertain, respond with "Unknown"
6. Respond with ONLY the language name, nothing else.
"""

DETAILED_SUBTAGS_PROMPT = """
Please analyze this YouTube video and provide 5-10 specific sub-tags based on its title and thumbnail.

Video Title: {video_title}
Main Classification: {classification}

Instructions:
1. Provide 5-10 specific sub-tags that describe the video content
2. Sub-tags should be single words or short phrases (1-2 words max)
3. Focus on: format, style, difficulty level, specific topics
4. Examples: tutorial, review, beginner, advanced, tips, guide, demo, comparison, analysis
5. Separate sub-tags with commas
6 In case of a game, include specific game titles and genres
7 If the video is a music video, include specific genres and artists
8 If the video is a movie or TV show review, include specific titles and genres
9. If the video is a review or analysis, include specific products and brands
10. Respond with ONLY the comma-separated list, nothing else
"""

playlist_url = config.get(
    'DEFAULT',
    'playlist_url',
    fallback='https://www.youtube.com/playlist?list=WL')
classifications_csv = config.get(
    'DEFAULT',
    'classifications_csv',
    fallback='video_classifications.csv')

quit = False
driver = None  # Global driver variable


def get_chrome_binary_path():
    """Get the Chrome binary path based on the operating system."""
    system = platform.system().lower()

    if system == "linux":
        # Common paths for Google Chrome on Linux
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/opt/google/chrome/google-chrome",
            "/usr/local/bin/google-chrome",
            "/usr/bin/chromium-browser",  # Add chromium as fallback
            "/snap/bin/chromium"
        ]
    elif system == "darwin":  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium"
        ]
    elif system == "windows":
        chrome_paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe")]
    else:
        chrome_paths = []

    # Find the first existing Chrome binary
    for path in chrome_paths:
        if os.path.exists(path):
            return path

    return None


def get_system_chromedriver_path():
    """Get the system chromedriver path based on the operating system."""
    system = platform.system().lower()

    if system == "linux":
        chromedriver_paths = [
            "/usr/bin/chromedriver",
            "/usr/local/bin/chromedriver",
            "/snap/bin/chromedriver"
        ]
    elif system == "darwin":  # macOS
        chromedriver_paths = [
            "/usr/local/bin/chromedriver",
            "/opt/homebrew/bin/chromedriver"
        ]
    elif system == "windows":
        chromedriver_paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe",
            "C:\\Windows\\System32\\chromedriver.exe"
        ]
    else:
        chromedriver_paths = []

    # Find the first existing chromedriver
    for path in chromedriver_paths:
        if os.path.exists(path):
            return path

    return None


def init_browser():
    """Initialize Chrome browser with options for automation."""
    global driver
    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(
            "--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Remove headless mode to make browser visible
        # chrome_options.add_argument("--headless=new")  # Commented out to
        # show browser
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        # Add options for dev container to display browser on host
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")

        # Get the appropriate Chrome binary path
        chrome_binary = get_chrome_binary_path()
        if chrome_binary:
            chrome_options.binary_location = chrome_binary
            print(f"Using Chrome binary: {chrome_binary}")
        else:
            print("Warning: Could not find Chrome binary, using system default")

        # Initialize the driver with various fallback options
        driver_initialized = False

        # Try 1: System chromedriver with detected Chrome binary
        if not driver_initialized:
            try:
                chromedriver_path = get_system_chromedriver_path()
                if chromedriver_path:
                    service = Service(chromedriver_path)
                    driver = webdriver.Chrome(
                        service=service, options=chrome_options)
                    driver_initialized = True
                    print(
                        f"Initialized with system chromedriver: {chromedriver_path}")
            except Exception as e:
                print(f"System chromedriver failed: {e}")

        # Try 2: WebDriverManager with explicit OS detection
        if not driver_initialized:
            try:
                # Force the correct OS for WebDriverManager
                import tempfile
                import shutil

                # Clear any cached drivers that might have wrong architecture
                wdm_cache_dir = os.path.expanduser("~/.wdm")
                if os.path.exists(wdm_cache_dir):
                    print(
                        "Clearing WebDriverManager cache to avoid architecture conflicts...")
                    shutil.rmtree(wdm_cache_dir, ignore_errors=True)

                # Initialize ChromeDriverManager with explicit OS detection
                from webdriver_manager.core.os_manager import ChromeType
                manager = ChromeDriverManager(
                    chrome_type=ChromeType.CHROMIUM if "chromium" in (
                        chrome_binary or "").lower() else ChromeType.GOOGLE)
                service = Service(manager.install())
                driver = webdriver.Chrome(
                    service=service, options=chrome_options)
                driver_initialized = True
                print("Initialized with WebDriverManager")
            except Exception as e:
                print(f"WebDriverManager failed: {e}")

        # Try 3: Default Chrome without specifying service
        if not driver_initialized:
            try:
                driver = webdriver.Chrome(options=chrome_options)
                driver_initialized = True
                print("Initialized with default Chrome")
            except Exception as e:
                print(f"Default Chrome initialization failed: {e}")

        # Try 4: Fallback with minimal options (still visible)
        if not driver_initialized:
            try:
                chrome_options_fallback = Options()
                chrome_options_fallback.add_argument("--no-sandbox")
                chrome_options_fallback.add_argument("--disable-dev-shm-usage")
                chrome_options_fallback.add_argument("--disable-extensions")
                chrome_options_fallback.add_argument("--disable-plugins")
                chrome_options_fallback.add_argument("--window-size=1920,1080")

                # Try without custom binary location
                driver = webdriver.Chrome(options=chrome_options_fallback)
                driver_initialized = True
                print("Initialized with fallback Chrome options")
            except Exception as e:
                print(f"Fallback Chrome initialization failed: {e}")

        # Try 5: Last resort - use system command to find chromedriver
        if not driver_initialized:
            try:
                import subprocess
                result = subprocess.run(
                    ['which', 'chromedriver'], capture_output=True, text=True)
                if result.returncode == 0:
                    chromedriver_path = result.stdout.strip()
                    service = Service(chromedriver_path)
                    chrome_options_minimal = Options()
                    chrome_options_minimal.add_argument("--no-sandbox")
                    chrome_options_minimal.add_argument(
                        "--window-size=1920,1080")

                    driver = webdriver.Chrome(
                        service=service, options=chrome_options_minimal)
                    driver_initialized = True
                    print(
                        f"Initialized with system-found chromedriver: {chromedriver_path}")
            except Exception as e:
                print(f"System command fallback failed: {e}")

        if not driver_initialized:
            print("All browser initialization attempts failed")
            return False

        # Remove automation indicators
        try:
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except BaseException:
            pass  # Ignore if this fails

        print("Browser initialized successfully!")

        # Navigate to the playlist URL
        driver.get(playlist_url)

        print("\n" + "=" * 60)
        print("SETUP INSTRUCTIONS:")
        print("1. The browser should now be visible on your screen")
        print("2. Please log in to your YouTube account in the browser")
        print("3. Navigate to your playlist if not already there")
        print("4. Ensure the playlist URL in config.ini is correct")
        print("5. The script will process videos automatically")
        print("6. Press 'q' to quit at any time")
        print("7. If you're in a dev container, use the command below to open the browser:")
        print(f'   "$BROWSER" {playlist_url}')
        input("Press Enter to continue after logging in...")
        print("=" * 60)

        print(f"Current browser navigated to: {playlist_url}")

        # Wait a moment for any redirects
        time.sleep(5)

        return True

    except Exception as e:
        print(f"Error initializing browser: {e}")
        return False


def detect_video_language(video_title, thumbnail_path):
    """Use Ollama to detect the language of the video."""
    try:
        # Convert image to base64
        with open(thumbnail_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')

        # Prepare the prompt
        prompt = LANGUAGE_DETECTION_PROMPT.format(video_title=video_title)

        # Make request to Ollama
        response = requests.post(
            f'{OLLAMA_HOST}/api/generate',
            json={
                'model': OLLAMA_MODEL,
                'prompt': prompt,
                'images': [image_data],
                'stream': False
            }
        )

        if response.status_code == 200:
            result = response.json()
            language = result['response'].strip()
            return language
        else:
            print(f"Error from Ollama for language detection: {response.status_code}")
            return "Unknown"

    except Exception as e:
        print(f"Error detecting language: {e}")
        return "Unknown"


def extract_channel_name(video_element):
    """Extract the channel name from the video element."""
    try:
        channel_selectors = [
            "#text > a",
            "#channel-name #text > a",
            ".ytd-channel-name a"
        ]
        
        for selector in channel_selectors:
            try:
                channel_element = video_element.find_element(By.CSS_SELECTOR, selector)
                # Check if it has the expected classes
                classes = channel_element.get_attribute("class")
                if "yt-simple-endpoint" in classes and "style-scope" in classes and "yt-formatted-string" in classes:
                    channel_name = channel_element.text.strip()
                    if channel_name:
                        return channel_name
            except BaseException:
                continue
        
        # Fallback: try without class checking
        for selector in channel_selectors:
            try:
                channel_element = video_element.find_element(By.CSS_SELECTOR, selector)
                channel_name = channel_element.text.strip()
                if channel_name:
                    return channel_name
            except BaseException:
                continue
        
        return "Unknown Channel"
    
    except Exception as e:
        print(f"Error extracting channel name: {e}")
        return "Unknown Channel"


def extract_video_length(video_element):
    """Extract video length and convert to Excel-readable format (total seconds)."""
    try:
        length_selector = "#overlays > ytd-thumbnail-overlay-time-status-renderer > div.thumbnail-overlay-badge-shape.style-scope.ytd-thumbnail-overlay-time-status-renderer > badge-shape > div"
        
        try:
            length_element = video_element.find_element(By.CSS_SELECTOR, length_selector)
            length_text = length_element.text.strip()
            
            # Parse time format (e.g., "1:23", "12:34", "1:23:45")
            time_parts = length_text.split(':')
            total_seconds = 0
            
            if len(time_parts) == 2:  # MM:SS format
                minutes, seconds = map(int, time_parts)
                total_seconds = minutes * 60 + seconds
            elif len(time_parts) == 3:  # HH:MM:SS format
                hours, minutes, seconds = map(int, time_parts)
                total_seconds = hours * 3600 + minutes * 60 + seconds
            
            return total_seconds
        
        except BaseException:
            # Try alternative selectors
            alt_selectors = [
                ".ytd-thumbnail-overlay-time-status-renderer .badge-shape div",
                "#overlays .thumbnail-overlay-badge-shape div",
                ".thumbnail-overlay-time-status-renderer badge-shape div"
            ]
            
            for selector in alt_selectors:
                try:
                    length_element = video_element.find_element(By.CSS_SELECTOR, selector)
                    length_text = length_element.text.strip()
                    
                    # Parse time format
                    time_parts = length_text.split(':')
                    total_seconds = 0
                    
                    if len(time_parts) == 2:  # MM:SS format
                        minutes, seconds = map(int, time_parts)
                        total_seconds = minutes * 60 + seconds
                    elif len(time_parts) == 3:  # HH:MM:SS format
                        hours, minutes, seconds = map(int, time_parts)
                        total_seconds = hours * 3600 + minutes * 60 + seconds
                    
                    return total_seconds
                
                except BaseException:
                    continue
        
        return 0  # Default if no length found
    
    except Exception as e:
        print(f"Error extracting video length: {e}")
        return 0


def extract_video_date(video_element):
    """Extract video date and convert to datetime format."""
    try:
        date_selector = "#video-info > span:nth-child(3)"
        
        try:
            date_element = video_element.find_element(By.CSS_SELECTOR, date_selector)
            date_text = date_element.text.strip()
            
            # Parse natural date format (e.g., "2 days ago", "1 week ago", "3 months ago")
            date_datetime = parse_natural_date(date_text)
            return date_datetime.strftime('%Y-%m-%d %H:%M:%S')
        
        except BaseException:
            # Try alternative selectors
            alt_selectors = [
                "#video-info span:nth-child(3)",
                ".ytd-video-meta-block span:nth-child(3)",
                "#metadata-line span:nth-child(3)"
            ]
            
            for selector in alt_selectors:
                try:
                    date_element = video_element.find_element(By.CSS_SELECTOR, selector)
                    date_text = date_element.text.strip()
                    
                    date_datetime = parse_natural_date(date_text)
                    return date_datetime.strftime('%Y-%m-%d %H:%M:%S')
                
                except BaseException:
                    continue
        
        return "Unknown Date"
    
    except Exception as e:
        print(f"Error extracting video date: {e}")
        return "Unknown Date"


def parse_natural_date(date_text):
    """Parse natural date format to datetime object."""
    try:
        import re
        from datetime import datetime, timedelta
        
        current_time = datetime.now()
        date_text = date_text.lower()
        
        # Remove common prefixes/suffixes
        date_text = re.sub(r'^(published|uploaded|added)\s+', '', date_text)
        date_text = re.sub(r'\s+ago$', '', date_text)
        
        # Extract number and unit
        match = re.search(r'(\d+)\s*(second|minute|hour|day|week|month|year)s?', date_text)
        
        if match:
            number = int(match.group(1))
            unit = match.group(2)
            
            if unit == 'second':
                return current_time - timedelta(seconds=number)
            elif unit == 'minute':
                return current_time - timedelta(minutes=number)
            elif unit == 'hour':
                return current_time - timedelta(hours=number)
            elif unit == 'day':
                return current_time - timedelta(days=number)
            elif unit == 'week':
                return current_time - timedelta(weeks=number)
            elif unit == 'month':
                return current_time - timedelta(days=number * 30)  # Approximate
            elif unit == 'year':
                return current_time - timedelta(days=number * 365)  # Approximate
        
        # If no match, return current time
        return current_time
    
    except Exception as e:
        print(f"Error parsing natural date: {e}")
        return datetime.now()


def get_video_info_web():
    """Extract video information using web scraping from playlist items."""
    global driver
    try:
        # Wait for playlist elements to be present
        wait = WebDriverWait(driver, 10)

        # Find the first video in the playlist
        video_selectors = [
            "ytd-playlist-video-renderer",
            ".ytd-playlist-video-renderer",
            "#contents ytd-playlist-video-renderer:first-child"
        ]

        video_element = None
        for selector in video_selectors:
            try:
                video_element = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, selector)))
                if video_element:
                    break
            except BaseException:
                continue

        if not video_element:
            print("Could not find video element in playlist")
            return None, None, None, None, None, None, None

        # Extract video title
        video_title = None
        title_selectors = [
            "a#video-title",
            ".ytd-playlist-video-renderer #video-title",
            "h3 a#video-title"
        ]

        for selector in title_selectors:
            try:
                title_element = video_element.find_element(
                    By.CSS_SELECTOR, selector)
                video_title = title_element.get_attribute(
                    "title") or title_element.text.strip()
                if video_title:
                    break
            except BaseException:
                continue

        if not video_title:
            video_title = f"Video_{int(time.time())}"

        print(f"Extracted video title: {video_title}")

        # Extract channel name
        channel_name = extract_channel_name(video_element)
        print(f"Extracted channel name: {channel_name}")

        # Extract video length
        video_length = extract_video_length(video_element)
        print(f"Extracted video length: {video_length} seconds")

        # Extract video date
        video_date = extract_video_date(video_element)
        print(f"Extracted video date: {video_date}")

        # Get video URL using share functionality
        video_url = None
        try:
            # Find and click the options button for this video
            options_button = video_element.find_element(
                By.CSS_SELECTOR, "#button.style-scope.yt-icon-button")
            driver.execute_script("arguments[0].click();", options_button)
            time.sleep(1)

            # Find and click the share button
            share_button = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR,
                     "#items > ytd-menu-service-item-renderer:nth-child(6) > tp-yt-paper-item > yt-formatted-string")))
            driver.execute_script("arguments[0].click();", share_button)
            time.sleep(1)

            # Wait for share modal to appear and get the URL
            try:
                url_input = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "input[readonly]")))
                video_url = url_input.get_attribute("value")

                # If that doesn't work, try alternative selectors
                if not video_url:
                    url_selectors = [
                        "#share-url",
                        "input[type='text'][readonly]",
                        ".style-scope.ytd-copy-link-renderer input"
                    ]
                    for selector in url_selectors:
                        try:
                            url_element = driver.find_element(
                                By.CSS_SELECTOR, selector)
                            video_url = url_element.get_attribute("value")
                            if video_url:
                                break
                        except BaseException:
                            continue

            except Exception as e:
                print(f"Error getting URL from share modal: {e}")

            # Close the share modal
            try:
                close_button = driver.find_element(
                    By.CSS_SELECTOR, "#button.style-scope.yt-icon-button > yt-icon[icon='close']")
                driver.execute_script("arguments[0].click();", close_button)
                time.sleep(0.5)
            except BaseException:
                # Try alternative close methods
                try:
                    close_button = driver.find_element(
                        By.CSS_SELECTOR, "yt-icon-button[aria-label*='Close']")
                    driver.execute_script(
                        "arguments[0].click();", close_button)
                    time.sleep(0.5)
                except BaseException:
                    # Press Escape key as fallback
                    from selenium.webdriver.common.keys import Keys
                    driver.find_element(
                        By.TAG_NAME, "body").send_keys(
                        Keys.ESCAPE)
                    time.sleep(0.5)

        except Exception as e:
            print(f"Error extracting video URL: {e}")
            # Fallback: try to get href from video title link
            try:
                title_link = video_element.find_element(
                    By.CSS_SELECTOR, "a#video-title")
                href = title_link.get_attribute("href")
                if href:
                    video_url = href
            except BaseException:
                video_url = f"https://youtube.com/watch?v=unknown_{int(time.time())}"

        print(f"Extracted video URL: {video_url}")

        # Take screenshot of video thumbnail
        try:
            thumbnail_path = "temp_thumbnail.png"

            # Try to find the video thumbnail image
            thumbnail_selectors = [
                "img#img",
                ".ytd-thumbnail img",
                "ytd-thumbnail img",
                "#thumbnail img"
            ]

            screenshot_taken = False
            for selector in thumbnail_selectors:
                try:
                    thumbnail_element = video_element.find_element(
                        By.CSS_SELECTOR, selector)
                    thumbnail_element.screenshot(thumbnail_path)
                    screenshot_taken = True
                    break
                except BaseException:
                    continue

            if not screenshot_taken:
                # Take screenshot of the entire video element
                video_element.screenshot(thumbnail_path)

        except Exception as e:
            print(f"Error taking thumbnail screenshot: {e}")
            # Create a placeholder image
            try:
                img = Image.new('RGB', (320, 180), color='lightgray')
                img.save(thumbnail_path)
            except BaseException:
                thumbnail_path = None

        return video_title, video_url, thumbnail_path, channel_name, video_length, video_date

    except Exception as e:
        print(f"Error extracting video info: {e}")
        return None, None, None, None, None, None


def navigate_to_next_video():
    """Navigate to the next video in the playlist by removing the current one."""
    global driver
    try:
        # The next video becomes the first video after removal
        # So we don't need to navigate, just wait for the page to update
        time.sleep(3)

        # Check if there are still videos in the playlist
        try:
            wait = WebDriverWait(driver, 5)
            next_video = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "ytd-playlist-video-renderer")))
            return True
        except BaseException:
            print("No more videos in playlist")
            return False

    except Exception as e:
        print(f"Error checking for next video: {e}")
        return False


def remove_video_from_playlist():
    """Remove the current video from the playlist."""
    global driver
    try:
        wait = WebDriverWait(driver, 10)

        # Find the first video in the playlist
        video_element = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "ytd-playlist-video-renderer")))

        # Find and click the options button
        options_button = video_element.find_element(
            By.CSS_SELECTOR, "#button.style-scope.yt-icon-button")
        driver.execute_script("arguments[0].click();", options_button)
        time.sleep(1)

        # Find and click the remove button
        remove_selectors = [
            "ytd-menu-service-item-renderer tp-yt-paper-item[role='menuitem']",
            "#items > ytd-menu-service-item-renderer tp-yt-paper-item",
            "tp-yt-paper-item[role='menuitem']"
        ]

        removed = False
        for selector in remove_selectors:
            try:
                menu_items = driver.find_elements(By.CSS_SELECTOR, selector)
                for item in menu_items:
                    item_text = item.text.strip().lower()
                    if "remove" in item_text or "delete" in item_text:
                        driver.execute_script("arguments[0].click();", item)
                        print("Video removed from playlist")
                        removed = True
                        break
                if removed:
                    break
            except BaseException:
                continue

        if not removed:
            print("Could not find remove button")
            # Try to close the menu
            try:
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            except BaseException:
                pass
            return False

        time.sleep(2)  # Wait for removal to complete
        return True

    except Exception as e:
        print(f"Error removing video: {e}")
        return False

# Initialize CSV file if it doesn't exist


def init_csv():
    """Initialize the CSV file with headers if it doesn't exist."""
    if not os.path.exists(classifications_csv):
        with open(classifications_csv, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['video_title', 'video_url', 'thumbnail_url', 'classification', 
                           'language', 'channel_name', 'video_length_seconds', 'video_date', 'detailed_subtags', 'image_data', 'timestamp'])
        print(f"Created {classifications_csv}")


def load_existing_classifications():
    """Load existing classifications from CSV."""
    try:
        if os.path.exists(classifications_csv):
            df = pd.read_csv(classifications_csv)
            return set(df['classification'].unique()
                       ) if not df.empty else set()
        return set()
    except Exception as e:
        print(f"Error loading classifications: {e}")
        return set()


def save_classification(video_title, video_url, thumbnail_url, classification, language, channel_name, video_length, video_date, detailed_subtags, image_data):
    """Save a video classification to CSV."""
    try:
        with open(classifications_csv, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([video_title, video_url, thumbnail_url, classification, 
                           language, channel_name, video_length, video_date, detailed_subtags, image_data,
                           time.strftime('%Y-%m-%d %H:%M:%S')])
        print(f"Saved classification: {video_title} -> {classification}")
    except Exception as e:
        print(f"Error saving classification: {e}")


def get_video_info():
    """Extract video information using web scraping (replaces old GUI method)."""
    return get_video_info_web()


def classify_video_with_ollama(
        video_title,
        thumbnail_path,
        existing_classifications):
    """Use Ollama with Qwen2.5-VL to classify the video."""
    try:
        # Convert image to base64
        with open(thumbnail_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')

        # Prepare existing classifications string
        existing_cats = ", ".join(
            existing_classifications) if existing_classifications else "None"

        # Prepare the prompt
        prompt = CLASSIFICATION_PROMPT.format(
            video_title=video_title,
            existing_categories=existing_cats)

        # Make request to Ollama
        response = requests.post(
            f'{OLLAMA_HOST}/api/generate',
            json={
                'model': OLLAMA_MODEL,
                'prompt': prompt,
                'images': [image_data],
                'stream': False
            }
        )

        if response.status_code == 200:
            result = response.json()
            classification = result['response'].strip()
            return classification
        else:
            print(f"Error from Ollama: {response.status_code}")
            return "Uncategorized"

    except Exception as e:
        print(f"Error classifying video: {e}")
        return "Uncategorized"


def generate_detailed_subtags(video_title, thumbnail_path, classification):
    """Use Ollama to generate detailed sub-tags for the video."""
    try:
        # Convert image to base64
        with open(thumbnail_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')

        # Prepare the prompt
        prompt = DETAILED_SUBTAGS_PROMPT.format(
            video_title=video_title,
            classification=classification
        )

        # Make request to Ollama
        response = requests.post(
            f'{OLLAMA_HOST}/api/generate',
            json={
                'model': OLLAMA_MODEL,
                'prompt': prompt,
                'images': [image_data],
                'stream': False
            }
        )

        if response.status_code == 200:
            result = response.json()
            subtags = result['response'].strip()
            return subtags
        else:
            print(f"Error from Ollama for sub-tags generation: {response.status_code}")
            return ""

    except Exception as e:
        print(f"Error generating sub-tags: {e}")
        return ""

def create_playlist_and_add_video(classification, video_url):
    """Create a playlist based on classification and add video to it."""
    # This functionality would need to be implemented with Selenium
    # For now, it's commented out
    """
    try:
        # Use Selenium to navigate to YouTube playlist creation
        # This would require additional implementation
        print(f"Would create/add to playlist: {classification}")

    except Exception as e:
        print(f"Error creating playlist/adding video: {e}")
    """
    print(f"[TODO] Would add video to playlist: {classification}")


def delete_video():
    """Delete functionality - now handled by remove_video_from_playlist()."""
    print("[DEPRECATED] Use remove_video_from_playlist() instead")
    return True

# Keyboard listener for quitting


def on_press_to_quit(key):
    """Quit program if 'q' is pressed."""
    global quit
    try:
        if key.char == 'q':
            print('Closing program...')
            quit = True
    except AttributeError:
        pass


def cleanup_browser():
    """Clean up browser resources."""
    global driver
    if driver:
        try:
            driver.quit()
            print("Browser closed.")
        except BaseException:
            pass


# Updated main execution logic
if __name__ == '__main__':
    try:
        # Initialize CSV file
        init_csv()

        # Load existing classifications
        existing_classifications = load_existing_classifications()
        print(f"Loaded {len(existing_classifications)} existing classifications: {existing_classifications}")

        # Initialize browser
        if not init_browser():
            print("Failed to initialize browser. Exiting.")
            sys.exit(1)

        counter = 0

        # Set up keyboard listener for quitting
        listener = kb.Listener(on_press=on_press_to_quit)
        listener.start()

        print("\nStarting video processing...")
        print("Press 'q' to quit at any time.")

        while not quit:
            try:
                # Extract video information using web scraping
                video_data = get_video_info()
                
                if len(video_data) == 6:  # New format with all data
                    video_title, video_url, thumbnail_path, channel_name, video_length, video_date = video_data
                else:  # Fallback to old format
                    video_title, video_url, thumbnail_path = video_data[:3]
                    channel_name, video_length, video_date = "Unknown Channel", 0, "Unknown Date"

                if video_title and video_url and thumbnail_path:
                    # Convert thumbnail to base64 for storage
                    image_data = ""
                    try:
                        with open(thumbnail_path, "rb") as image_file:
                            image_data = base64.b64encode(image_file.read()).decode('utf-8')
                        print(f"Thumbnail converted to base64 ({len(image_data)} characters)")
                    except Exception as e:
                        print(f"Error converting thumbnail to base64: {e}")
                        image_data = ""

                    # Detect language using Ollama
                    print(f"\nDetecting language for video: {video_title}")
                    language = detect_video_language(video_title, thumbnail_path)
                    print(f"Language detected: {language}")
                    
                    # Classify video using Ollama
                    print(f"Classifying video: {video_title}")
                    classification = classify_video_with_ollama(
                        video_title, thumbnail_path, existing_classifications)
                    print(f"Classification result: {classification}")

                    # Let's be gentle with the API
                    time.sleep(1)

                    # Generate detailed sub-tags using Ollama
                    print(f"Generating detailed sub-tags for video: {video_title}")
                    detailed_subtags = generate_detailed_subtags(video_title, thumbnail_path, classification)
                    print(f"Detailed sub-tags: {detailed_subtags}")

                    # Save classification to CSV with new data including image data
                    save_classification(
                        video_title, video_url, thumbnail_path, classification, 
                        language, channel_name, video_length, video_date, detailed_subtags, image_data)

                    # Update existing classifications set
                    existing_classifications.add(classification)

                    # Create playlist and add video (commented for testing)
                    create_playlist_and_add_video(classification, video_url)

                    # Remove video from current playlist
                    remove_success = remove_video_from_playlist()

                    if remove_success:
                        counter += 1
                        print(f"Processed {counter} videos.")

                        # Navigate to next video
                        if not navigate_to_next_video():
                            print("No more videos to process.")
                            break
                    else:
                        # If can't remove, try to navigate to next video anyway
                        if not navigate_to_next_video():
                            print("Could not navigate to next video.")
                            break
                        counter += 1
                        print(f"Processed {counter} videos (removal failed).")

                    # Clean up temporary thumbnail
                    if os.path.exists(thumbnail_path):
                        os.remove(thumbnail_path)

                    time.sleep(2)  # Brief pause between videos

                else:
                    print("Could not extract video information")
                    # Try to navigate to next video anyway
                    if not navigate_to_next_video():
                        break

            except Exception as e:
                print(f"Error in main processing loop: {e}")
                # Try to continue with next video
                if not navigate_to_next_video():
                    break

        listener.stop()
        cleanup_browser()
        print("Script finished.")

    except KeyboardInterrupt:
        print("\nScript interrupted by user.")
        cleanup_browser()
    except Exception as e:
        print(f"Unexpected error: {e}")
        cleanup_browser()
