#!/usr/bin/env python3
"""
Demo script showing how the video classification works
"""

import requests
import base64
import time
import configparser
config = configparser.ConfigParser()
config.read('config.ini')

ollama_host = config.get('DEFAULT', 'ollama_host', fallback='http://ollama:11434')

def classify_demo_video(video_obj):
    """Demonstrate video classification."""
    try:
        # If there's a thumbnail, convert image to base64
        if video_obj.get('thumbnail'):
            with open(video_obj['thumbnail'], "rb") as image_file:
                print(image_file.read())
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
                print(image_data)
        else:
            image_data = None

        existing_classifications = ["Tech Reviews", "Cooking", "Gaming", "Music"]
        
        prompt = f"""
        Please classify this YouTube video based on its title and thumbnail.
        
        Video Title: {video_obj['title']}
        
        Existing Classifications: {", ".join(existing_classifications)}
        
        Instructions:
        1. If the video fits into one of the existing classifications, use that exact classification name.
        2. If the video doesn't fit any existing classification, create a new appropriate classification name.
        3. Classification names should be concise (1-3 words) and descriptive.
        4. Examples of good classifications: "Tech Reviews", "Cooking", "Gaming", "Education", "Music", "Comedy", etc.
        5. Respond with ONLY the classification name, nothing else.
        """
        
        print(f"Classifying: '{video_obj['title']}'")
        print(f"Using thumbnail: {video_obj.get('thumbnail', 'None')}")
        print("Sending request to Ollama...")
        
        # Prepare the request payload
        payload = {
            'model': 'qwen2.5vl:7b',
            'prompt': prompt,
            'stream': False
        }
        
        # Only include images if image_data is available
        if image_data:
            payload['images'] = [image_data]
        
        response = requests.post(
            f'{ollama_host}/api/generate',
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            classification = result['response'].strip().strip('"\'')
            print(f"✅ Classification: '{classification}'")
            return classification
        else:
            print(f"❌ Error: {response.status_code}")
            return "Uncategorized"
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return "Uncategorized"

def run_demo():
    """Run classification demo with sample videos."""
    sample_videos = [
        {
            "title": "I can't believe this change!", 
            "thumbnail": "img/iphone_thumbnail.png"
        },
        {
            "title": "iPhone 15 Pro Review - Best Camera Phone?"
        },
        {
            "title": "Easy Pasta Recipe for Beginners", 
        },
        {
            "title": "Minecraft Survival Guide - Episode 1", 
        },
        {
            "title": "Classical Piano Music for Studying", 
        },
        {
            "title": "Machine Learning Explained Simply", 
        },
    ]
    
    print("YouTube Video Classification Demo")
    print("=" * 40)
    
    results = []
    
    for i, video_obj in enumerate(sample_videos, 1):
        print(f"\n--- Demo {i}/{len(sample_videos)} ---")
        
        # Classify the video
        classification = classify_demo_video(video_obj)
        results.append((video_obj['title'], classification))
        
        time.sleep(1)  # Be nice to the API
    
    print("\n" + "=" * 40)
    print("DEMO RESULTS:")
    print("=" * 40)
    
    for title, classification in results:
        print(f"{classification:15} | {title}")
    
    print("\nDemo complete! The script can:")
    print("• Use existing categories when appropriate")
    print("• Create new categories for unique content")
    print("• Analyze both title and thumbnail information")

if __name__ == '__main__':
    print(ollama_host)
    # Check if Ollama is running
    try:
        response = requests.get(f'{ollama_host}/api/tags', timeout=5)
        if response.status_code != 200:
            print("❌ Ollama is not running. Please start it with: ollama serve")
            exit(1)
    except:
        print("❌ Cannot connect to Ollama. Please start it with: ollama serve")
        exit(1)
    
    run_demo()
