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

# Rich logging imports
from rich.console import Console
from rich import print as rprint
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Initialize rich console
console = Console()

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Configuration variables
OLLAMA_HOST = config.get(
    'DEFAULT',
    'ollama_host',
    fallback='http://localhost:11434')
OLLAMA_MODEL = config.get('DEFAULT', 'ollama_model')
OLLAMA_FALLBACK_MODEL = config.get('DEFAULT', 'ollama_fallback_model')

# Timeout settings
LLM_PRIMARY_TIMEOUT = config.getint('DEFAULT', 'llm_primary_timeout')
LLM_FALLBACK_TIMEOUT = config.getint('DEFAULT', 'llm_fallback_timeout')

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


def log(message, style="", emoji="", add_newline_before=False):
    """Enhanced logging function with rich formatting."""
    if emoji:
        width = 1
        if (emoji == "⚠️") or (emoji == "⏱️") or (emoji == "🏷️") or (emoji == "🗣️") or (emoji == "🗑️") or (emoji == "⌨️"):
            width = 2
        pad = " " * width
        formatted_message = f"{emoji}{pad}{message.strip()}"
    else:
        formatted_message = message.strip()
    
    if add_newline_before:
        console.print()
    
    if style:
        console.print(formatted_message, style=style)
    else:
        console.print(formatted_message)


def log_success(message, emoji="✅", add_newline_before=False):
    """Log success messages in green."""
    log(message, style="bold green", emoji=emoji, add_newline_before=add_newline_before)


def log_warning(message, emoji="⚠️", add_newline_before=False):
    """Log warning messages in yellow."""
    log(message, style="bold yellow", emoji=emoji, add_newline_before=add_newline_before)


def log_error(message, emoji="❌"):
    """Log error messages in red."""
    log(message, style="bold red", emoji=emoji)


def log_info(message, emoji="ℹ️", add_newline_before=False):
    """Log info messages in blue."""
    log(message, style="bold blue", emoji=emoji, add_newline_before=add_newline_before)


def log_process(message, emoji="🔄", add_newline_before=False):
    """Log process messages in cyan."""
    log(message, style="bold cyan", emoji=emoji, add_newline_before=add_newline_before)


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
            log_info(f"Using Chrome binary: {chrome_binary}", "🔧")
        else:
            log_warning("Could not find Chrome binary, using system default")

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
                    log_success(f"Initialized with system chromedriver: {chromedriver_path}")
            except Exception as e:
                log_error(f"System chromedriver failed: {e}")

        # Try 2: WebDriverManager with explicit OS detection
        if not driver_initialized:
            try:
                # Force the correct OS for WebDriverManager
                import tempfile
                import shutil

                # Clear any cached drivers that might have wrong architecture
                wdm_cache_dir = os.path.expanduser("~/.wdm")
                if os.path.exists(wdm_cache_dir):
                    log_process("Clearing WebDriverManager cache to avoid architecture conflicts...", "🧹")
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
                log_success("Initialized with WebDriverManager")
            except Exception as e:
                log_error(f"WebDriverManager failed: {e}")

        # Try 3: Default Chrome without specifying service
        if not driver_initialized:
            try:
                driver = webdriver.Chrome(options=chrome_options)
                driver_initialized = True
                log_success("Initialized with default Chrome")
            except Exception as e:
                log_error(f"Default Chrome initialization failed: {e}")

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
                log_success("Initialized with fallback Chrome options")
            except Exception as e:
                log_error(f"Fallback Chrome initialization failed: {e}")

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
                    log_success(f"Initialized with system-found chromedriver: {chromedriver_path}")
            except Exception as e:
                log_error(f"System command fallback failed: {e}")

        if not driver_initialized:
            log_error("All browser initialization attempts failed")
            return False

        # Remove automation indicators
        try:
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except BaseException:
            pass  # Ignore if this fails

        log_success("Browser initialized successfully!", "🎉")

        # Navigate to the playlist URL
        driver.get(playlist_url)
        log_info(f"Current browser navigated to: {playlist_url}", "🌐")

        # Create a beautiful setup panel
        setup_panel = Panel.fit(
            """[bold cyan]SETUP INSTRUCTIONS:[/bold cyan]

1. The browser should now be visible on your screen
2. If not already logged in, please log in to your YouTube account
3. Navigate to your playlist if not already there
4. Ensure the playlist URL in config.ini is correct
5. The script will process videos automatically
6. Press 'q' to quit at any time""",
            title="[bold magenta]🚀 YouTube Video Classifier Setup[/bold magenta]",
            border_style="bright_blue"
        )
        
        console.print()
        console.print(setup_panel)
        console.print()
        
        input("Press Enter to continue after confirming login status...")

        # Wait a moment for any redirects
        time.sleep(5)

        return True

    except Exception as e:
        log_error(f"Error initializing browser: {e}")
        return False


def check_ollama_models():
    """Check if required Ollama models are available."""
    try:
        response = requests.get(f'{OLLAMA_HOST}/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json()
            available_models = [model['name'] for model in models.get('models', [])]
            
            primary_available = any(OLLAMA_MODEL in model for model in available_models)
            fallback_available = any(OLLAMA_FALLBACK_MODEL in model for model in available_models)
            
            log_info(f"Available models: {available_models}", "🤖")
            
            if not primary_available:
                log_warning(f"Primary model '{OLLAMA_MODEL}' not found!")
                log_info(f"Run: ollama pull {OLLAMA_MODEL}", "💡")
            
            if not fallback_available:
                log_warning(f"Fallback model '{OLLAMA_FALLBACK_MODEL}' not found!")
                log_info(f"Run: ollama pull {OLLAMA_FALLBACK_MODEL}", "💡")
            
            if not primary_available and not fallback_available:
                log_error("No required models available! Please install at least one.")
                return False
            
            return True
        else:
            log_error(f"Cannot connect to Ollama at {OLLAMA_HOST}")
            return False
    except Exception as e:
        log_error(f"Error checking Ollama models: {e}")
        return False


def call_ollama_with_fallback(prompt, image_data, purpose="processing"):
    """
    Call Ollama with timeout and fallback support using continuous loop.
    
    Args:
        prompt: The text prompt to send
        image_data: Base64 encoded image data
        purpose: Description of what this call is for (for logging)
    
    Returns:
        str: The response from the LLM, or empty string if manually cancelled
    """
    models = [OLLAMA_MODEL, OLLAMA_FALLBACK_MODEL]
    base_timeouts = [LLM_PRIMARY_TIMEOUT, LLM_FALLBACK_TIMEOUT]
    
    attempt = 0
    while not quit:  # Continue until we get a response or user quits
        for i, model in enumerate(models):
            attempt += 1
            # Calculate increasing timeout: base + (10 * number of complete cycles)
            cycles_completed = (attempt - 1) // len(models)
            current_timeout = base_timeouts[i] + (10 * cycles_completed)
            
            try:
                log_process(f"Attempt {attempt}: Trying {model} for {purpose} (timeout: {current_timeout}s)", "🔄")
                
                response = requests.post(
                    f'{OLLAMA_HOST}/api/generate',
                    json={
                        'model': model,
                        'prompt': prompt,
                        'images': [image_data],
                        'stream': False
                    },
                    timeout=current_timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result['response'].strip()
                    if response_text:  # Make sure we got actual content
                        log_success(f"Response received from {model} on attempt {attempt}", "✅")
                        return response_text
                    else:
                        log_warning(f"{model} returned empty response")
                        continue
                else:
                    log_warning(f"{model} returned status {response.status_code}")
                    
            except requests.exceptions.Timeout:
                log_warning(f"{model} timed out after {current_timeout}s")
                
            except requests.exceptions.ConnectionError:
                log_error(f"Cannot connect to {model}")
                # Wait a bit before trying again if connection failed
                time.sleep(2)
                
            except Exception as e:
                log_error(f"Error calling {model}: {e}")
        
        # After trying both models in this cycle
        if attempt >= 2:  # After first complete cycle
            log_info(f"Completed cycle {cycles_completed + 1}, increasing timeouts by 10s for next cycle", "🔄")
        
        # Small delay between cycles to prevent overwhelming the server
        time.sleep(1)
    
    log_warning(f"LLM calls cancelled by user for {purpose}")
    return ""


def detect_video_language(video_title, thumbnail_path):
    """Use Ollama to detect the language of the video."""
    try:
        # Convert image to base64
        with open(thumbnail_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')

        # Prepare the prompt
        prompt = LANGUAGE_DETECTION_PROMPT.format(video_title=video_title)

        # Call with fallback support
        language = call_ollama_with_fallback(prompt, image_data, "language detection")
        
        return language if language else "Unknown"

    except Exception as e:
        log_error(f"Error detecting language: {e}")
        return "Unknown"


def extract_channel_name(video_element):
    """Extract the channel name and link from the video element."""
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
                        # Get the resolved absolute URL
                        channel_link = channel_element.get_attribute("href")
                        # If it's a relative URL, resolve it
                        if channel_link and channel_link.startswith("/"):
                            channel_link = f"https://www.youtube.com{channel_link}"
                        return channel_name, channel_link or "Unknown Channel Link"
            except BaseException:
                continue
        
        # Fallback: try without class checking
        for selector in channel_selectors:
            try:
                channel_element = video_element.find_element(By.CSS_SELECTOR, selector)
                channel_name = channel_element.text.strip()
                if channel_name:
                    # Get the resolved absolute URL
                    channel_link = channel_element.get_attribute("href")
                    # If it's a relative URL, resolve it
                    if channel_link and channel_link.startswith("/"):
                        channel_link = f"https://www.youtube.com{channel_link}"
                    return channel_name, channel_link or "Unknown Channel Link"
            except BaseException:
                continue
        
        return "Unknown Channel", "Unknown Channel Link"
    
    except Exception as e:
        log_error(f"Error extracting channel name: {e}")
        return "Unknown Channel", "Unknown Channel Link"


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
        log_error(f"Error extracting video length: {e}")
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
        log_error(f"Error extracting video date: {e}")
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
        log_error(f"Error parsing natural date: {e}")
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
            log_error("Could not find video element in playlist")
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

        log_info(f"Extracted video title: {video_title}", "📝", True)

        # Extract channel name and link
        channel_name, channel_link = extract_channel_name(video_element)
        log_info(f"Extracted channel name: {channel_name}", "👤")
        log_info(f"Extracted channel link: {channel_link}", "🔗")

        # Extract video length
        video_length = extract_video_length(video_element)
        log_info(f"Extracted video length: {video_length} seconds", "⏱️")

        # Extract video date
        video_date = extract_video_date(video_element)
        log_info(f"Extracted video date: {video_date}", "📅")

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
                log_error(f"Error getting URL from share modal: {e}")

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
            log_error(f"Error extracting video URL: {e}")
            # Fallback: try to get href from video title link
            try:
                title_link = video_element.find_element(
                    By.CSS_SELECTOR, "a#video-title")
                href = title_link.get_attribute("href")
                if href:
                    video_url = href
            except BaseException:
                video_url = f"https://youtube.com/watch?v=unknown_{int(time.time())}"

        log_info(f"Extracted video URL: {video_url}", "🔗")

        # Take screenshot of video thumbnail and get thumbnail URL
        thumbnail_url = None
        thumbnail_path = "temp_thumbnail.png"
        try:
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
                    # Get the thumbnail URL from src attribute
                    thumbnail_url = thumbnail_element.get_attribute("src")
                    thumbnail_element.screenshot(thumbnail_path)
                    screenshot_taken = True
                    break
                except BaseException:
                    continue

            if not screenshot_taken:
                # Take screenshot of the entire video element
                video_element.screenshot(thumbnail_path)

        except Exception as e:
            log_error(f"Error taking thumbnail screenshot: {e}")
            # Create a placeholder image
            try:
                img = Image.new('RGB', (320, 180), color='lightgray')
                img.save(thumbnail_path)
            except BaseException:
                thumbnail_path = None

        # If we couldn't get thumbnail URL, construct it from video URL
        if not thumbnail_url and video_url:
            try:
                # Extract video ID and construct thumbnail URL
                if 'youtu.be/' in video_url:
                    video_id = video_url.split('youtu.be/')[-1].split('?')[0]
                elif 'v=' in video_url:
                    video_id = video_url.split('v=')[-1].split('&')[0]
                else:
                    video_id = None
                if video_id:
                    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            except:
                thumbnail_url = None

        return video_title, video_url, thumbnail_path, thumbnail_url, channel_name, channel_link, video_length, video_date

    except Exception as e:
        log_error(f"Error extracting video info: {e}")
        return None, None, None, None, None, None, None


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
            log_info("No more videos in playlist", "📭")
            return False

    except Exception as e:
        log_error(f"Error checking for next video: {e}")
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
                        log_success("Video removed from playlist", "🗑️")
                        removed = True
                        break
                if removed:
                    break
            except BaseException:
                continue

        if not removed:
            log_error("Could not find remove button")
            # Try to close the menu
            try:
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            except BaseException:
                pass
            return False

        time.sleep(2)  # Wait for removal to complete
        return True

    except Exception as e:
        log_error(f"Error removing video: {e}")
        return False


def extract_playlist_info():
    """Extract playlist name and URL from the current page."""
    global driver
    try:
        # Extract playlist name
        playlist_name = "Unknown Playlist"
        playlist_name_selector = "yt-page-header-renderer > yt-page-header-view-model > div.page-header-view-model-wiz__scroll-container > div > div.page-header-view-model-wiz__page-header-headline > div > yt-dynamic-text-view-model > h1 > span"
        
        try:
            playlist_name_element = driver.find_element(By.CSS_SELECTOR, playlist_name_selector)
            playlist_name = playlist_name_element.text.strip()
        except BaseException:
            # Try alternative selectors
            alt_selectors = [
                "h1 span",
                ".page-header-headline h1 span",
                "yt-dynamic-text-view-model h1 span",
                "#page-header h1 span"
            ]
            
            for selector in alt_selectors:
                try:
                    playlist_name_element = driver.find_element(By.CSS_SELECTOR, selector)
                    playlist_name = playlist_name_element.text.strip()
                    if playlist_name:
                        break
                except BaseException:
                    continue
        
        # Get current playlist URL
        playlist_link = driver.current_url
        
        log_info(f"Playlist name: {playlist_name}", "📋")
        log_info(f"Playlist link: {playlist_link}", "🔗")
        
        return playlist_name, playlist_link
    
    except Exception as e:
        log_error(f"Error extracting playlist info: {e}")
        return "Unknown Playlist", driver.current_url if driver else "Unknown URL"


def init_csv():
    """Initialize the CSV file with headers if it doesn't exist."""
    if not os.path.exists(classifications_csv):
        with open(classifications_csv, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Video Title', 'Video URL', 'Thumbnail URL', 'Classification', 
                           'Language', 'Channel Name', 'Channel URL', 'Duration (seconds)', 'Upload Date', 
                           'Tags', 'Playlist Name', 'Playlist URL', 'Classified At'])
        log_success(f"Created {classifications_csv}", "📊")


def load_existing_classifications():
    """Load existing classifications from CSV."""
    try:
        if os.path.exists(classifications_csv):
            df = pd.read_csv(classifications_csv)
            return set(df['classification'].unique()
                       ) if not df.empty else set()
        return set()
    except Exception as e:
        log_error(f"Error loading classifications: {e}")
        return set()


def save_classification(video_title, video_url, thumbnail_url, classification, language, channel_name, channel_link, video_length, video_date, detailed_subtags, playlist_name, playlist_link):
    """Save a video classification to CSV."""
    try:
        from datetime import datetime, timezone
        iso_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        with open(classifications_csv, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([video_title, video_url, thumbnail_url, classification, 
                           language, channel_name, channel_link, video_length, video_date, detailed_subtags, 
                           playlist_name, playlist_link, iso_timestamp])
        log_success(f"Saved classification: {video_title} -> {classification}", "💾")
    except Exception as e:
        log_error(f"Error saving classification: {e}")


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

        # Call with fallback support
        classification = call_ollama_with_fallback(prompt, image_data, "video classification")
        
        return classification if classification else "Uncategorized"

    except Exception as e:
        log_error(f"Error classifying video: {e}")
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

        # Call with fallback support
        subtags = call_ollama_with_fallback(prompt, image_data, "sub-tags generation")
        
        return subtags if subtags else ""

    except Exception as e:
        log_error(f"Error generating sub-tags: {e}")
        return ""


def create_playlist_and_add_video(classification, video_url):
    """Create a playlist based on classification and add video to it."""
    log_process(f"[TODO] Would add video to playlist: {classification}", "📋")


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
            log_warning('Closing program...', "🛑")
            quit = True
    except AttributeError:
        pass


def cleanup_browser():
    """Clean up browser resources."""
    global driver
    if driver:
        try:
            driver.quit()
            log_info("Browser closed.", "🚪")
        except BaseException:
            pass


# Updated main execution logic
if __name__ == '__main__':
    try:
        # Create a beautiful title
        title = Text("🎬 YouTube Video Classifier", style="bold magenta")
        console.print(Panel.fit(title, border_style="bright_magenta"))
        console.print()

        # Check Ollama models before starting
        log_info("Checking Ollama models availability...", "🔍")
        if not check_ollama_models():
            log_error("Required models not available. Please install them first.")
            sys.exit(1)

        # Initialize CSV file
        init_csv()

        # Load existing classifications
        existing_classifications = load_existing_classifications()
        log_info(f"Loaded {len(existing_classifications)} existing classifications: {existing_classifications}", "📚")

        # Initialize browser
        if not init_browser():
            log_error("Failed to initialize browser. Exiting.")
            sys.exit(1)

        counter = 0

        # Set up keyboard listener for quitting
        listener = kb.Listener(on_press=on_press_to_quit)
        listener.start()

        log_success("Starting video processing...", "🚀", True)
        log_info("Press 'q' to quit at any time.", "⌨️")
        log_info(f"Primary model: {OLLAMA_MODEL} (timeout: {LLM_PRIMARY_TIMEOUT}s)", "🤖")
        log_info(f"Fallback model: {OLLAMA_FALLBACK_MODEL} (timeout: {LLM_FALLBACK_TIMEOUT}s)", "🤖")

        playlist_name = "Unknown Playlist"
        playlist_link = "Unknown URL"

        while not quit:
            try:
                # Extract playlist information once per session
                if counter == 0:
                    playlist_name, playlist_link = extract_playlist_info()
                    console.print()  # Add spacing after playlist info
                
                # Extract video information using web scraping
                video_data = get_video_info()
                
                if len(video_data) == 8:  # New format with thumbnail_url
                    video_title, video_url, thumbnail_path, thumbnail_url, channel_name, channel_link, video_length, video_date = video_data
                elif len(video_data) == 7:  # Old format with all data including channel_link
                    video_title, video_url, thumbnail_path, channel_name, channel_link, video_length, video_date = video_data
                    thumbnail_url = None
                elif len(video_data) == 6:  # Old format with channel_name but no channel_link
                    video_title, video_url, thumbnail_path, channel_name, video_length, video_date = video_data
                    channel_link = "Unknown Channel Link"
                    thumbnail_url = None
                else:  # Fallback to old format
                    video_title, video_url, thumbnail_path = video_data[:3]
                    channel_name, channel_link, video_length, video_date = "Unknown Channel", "Unknown Channel Link", 0, "Unknown Date"
                    thumbnail_url = None

                if video_title and video_url and thumbnail_path:
                    # Detect language using Ollama with fallback
                    log_process(f"Detecting language for video: {video_title}", "🌐", True)
                    language = detect_video_language(video_title, thumbnail_path)
                    log_success(f"Language detected: {language}", "🗣️")
                    
                    # Classify video using Ollama with fallback
                    log_process(f"Classifying video: {video_title}", "🏷️", True)
                    classification = classify_video_with_ollama(
                        video_title, thumbnail_path, existing_classifications)
                    log_success(f"Classification result: {classification}", "📂")

                    # Let's be gentle with the API
                    time.sleep(1)

                    # Generate detailed sub-tags using Ollama with fallback
                    log_process(f"Generating detailed sub-tags for video: {video_title}", "🏷️", True)
                    detailed_subtags = generate_detailed_subtags(video_title, thumbnail_path, classification)
                    log_success(f"Detailed sub-tags: {detailed_subtags}", "🔖")

                    # Save classification to CSV with new data including channel link
                    save_classification(
                        video_title, video_url, thumbnail_url, classification, 
                        language, channel_name, channel_link, video_length, video_date, detailed_subtags, 
                        playlist_name, playlist_link)

                    # Update existing classifications set
                    existing_classifications.add(classification)

                    # Create playlist and add video (commented for testing)
                    log_process("Actions with playlist:", "📋", True)
                    create_playlist_and_add_video(classification, video_url)

                    # Remove video from current playlist
                    remove_success = remove_video_from_playlist()

                    if remove_success:
                        counter += 1
                        log_success(f"Processed {counter} videos.", "✅", True)

                        # Navigate to next video
                        if not navigate_to_next_video():
                            log_info("No more videos to process.", "🏁")
                            break
                    else:
                        # If can't remove, try to navigate to next video anyway
                        if not navigate_to_next_video():
                            log_error("Could not navigate to next video.")
                            break
                        counter += 1
                        log_warning(f"Processed {counter} videos (removal failed).", add_newline_before=True)

                    # Clean up temporary thumbnail
                    if os.path.exists(thumbnail_path):
                        os.remove(thumbnail_path)

                    time.sleep(2)  # Brief pause between videos

                else:
                    log_error("Could not extract video information")
                    # Try to navigate to next video anyway
                    if not navigate_to_next_video():
                        break

            except Exception as e:
                log_error(f"Error in main processing loop: {e}")
                # Try to continue with next video
                if not navigate_to_next_video():
                    break

        listener.stop()
        cleanup_browser()
        
        # Final summary
        completion_panel = Panel.fit(
            f"[bold green]✨ Script completed successfully![/bold green]\n[cyan]Total videos processed: {counter}[/cyan]",
            title="[bold blue]🎯 Completion Summary[/bold blue]",
            border_style="bright_green"
        )
        console.print()
        console.print(completion_panel)

    except KeyboardInterrupt:
        log_warning("Script interrupted by user.", add_newline_before=True)
        cleanup_browser()
    except Exception as e:
        log_error(f"Unexpected error: {e}", "💥")
        cleanup_browser()
