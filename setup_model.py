#!/usr/bin/env python3
"""
Script to ensure the Qwen2.5VL model is available in the Ollama container
"""

import configparser
import time
import sys
import requests

def load_config():
    """Load configuration from config.ini"""
    config = configparser.ConfigParser()
    config.read('config.ini')

    ollama_host = config.get('DEFAULT', 'ollama_host', fallback='http://ollama:11434')
    ollama_model = config.get('DEFAULT', 'ollama_model', fallback='qwen2.5vl:7b')

    return ollama_host, ollama_model

def wait_for_ollama(host, max_attempts=30):
    """Wait for Ollama container to be ready"""
    print(f"⏳ Waiting for Ollama container at {host}...")

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(f"{host}/api/tags", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama container is ready!")
                return True
        except requests.exceptions.RequestException:
            pass

        print(f"   Attempt {attempt}/{max_attempts} - waiting...")
        time.sleep(2)

    print("❌ Ollama container is not responding after maximum attempts")
    return False

def check_model_exists(host, model_name):
    """Check if the model is already available"""
    try:
        response = requests.get(f"{host}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            model_names = [model['name'] for model in models.get('models', [])]
            return any(model_name in name for name in model_names), model_names
        return False, []
    except requests.exceptions.RequestException as e:
        print(f"❌ Error checking models: {e}")
        return False, []

def pull_model(host, model_name):
    """Pull the model from Ollama"""
    print(f"📥 Pulling model '{model_name}' (this may take several minutes)...")

    try:
        response = requests.post(
            f"{host}/api/pull",
            json={"name": model_name},
            timeout=600  # 10 minutes timeout
        )

        if response.status_code == 200:
            print(f"✅ Successfully pulled model '{model_name}'")
            return True
        else:
            print(f"❌ Failed to pull model: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error pulling model: {e}")
        return False

def main():
    """Main function to set up the model"""
    print("🔧 Model Setup for YouTube Video Classifier")
    print("=" * 50)

    # Load configuration
    try:
        ollama_host, ollama_model = load_config()
        print("📋 Configuration:")
        print(f"   Host: {ollama_host}")
        print(f"   Model: {ollama_model}")
        print()
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        sys.exit(1)

    # Wait for Ollama to be ready
    if not wait_for_ollama(ollama_host):
        sys.exit(1)

    # Check if model exists
    model_exists, available_models = check_model_exists(ollama_host, ollama_model)

    if model_exists:
        print(f"✅ Model '{ollama_model}' is already available!")
    else:
        print(f"📋 Available models: {available_models}")
        print(f"❌ Model '{ollama_model}' not found")

        if pull_model(ollama_host, ollama_model):
            print(f"🎉 Model '{ollama_model}' is now ready for use!")
        else:
            print(f"❌ Failed to set up model '{ollama_model}'")
            sys.exit(1)

    print("\n🎬 YouTube Video Classifier is ready!")
    print("🧪 Run 'python test_ollama.py' to verify the setup")

if __name__ == "__main__":
    main()
