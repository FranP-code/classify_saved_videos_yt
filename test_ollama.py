#!/usr/bin/env python3
"""
Test script to verify Ollama connection and Qwen2.5-VL model
"""

import requests
import configparser

def load_config():
    """Load configuration from config.ini"""
    config = configparser.ConfigParser()
    config.read('config.ini')

    ollama_host = config.get('DEFAULT', 'ollama_host', fallback='http://ollama:11434')
    ollama_model = config.get('DEFAULT', 'ollama_model')

    return ollama_host, ollama_model

def test_ollama_connection(host, model_name):
    """Test if Ollama is running and accessible."""
    try:
        response = requests.get(f'{host}/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json()
            print("✅ Ollama is running!")
            model_names = [model['name'] for model in models.get('models', [])]
            print(f"Available models: {model_names}")

            # Check if the configured model is available
            model_available = any(model_name in name for name in model_names)
            if model_available:
                print(f"✅ {model_name} model is available!")
            else:
                print(f"❌ {model_name} model not found. Available models: {model_names}")
                print(f"Model may still be downloading. Check with: curl {host}/api/tags")

            return True
        else:
            print(f"❌ Ollama responded with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama container. Is the ollama service running?")
        print("💡 Try: docker-compose up -d ollama")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

def test_classification(host, model_name):
    """Test a simple classification without image."""
    try:
        response = requests.post(
            f'{host}/api/generate',
            json={
                'model': model_name,
                'prompt': 'Classify this video title into a category: "How to Cook Pasta - Italian Recipe Tutorial". Respond with only the category name.',
                'stream': False
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            classification = result['response'].strip()
            print(f"✅ Test classification successful: '{classification}'")
            return True
        else:
            print(f"❌ Classification test failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing classification: {e}")
        return False

if __name__ == '__main__':
    print("Testing Ollama setup for YouTube Video Classifier...")
    print("-" * 50)

    # Load configuration
    try:
        ollama_host, ollama_model = load_config()
        print(f"📋 Configuration:")
        print(f"   Host: {ollama_host}")
        print(f"   Model: {ollama_model}")
        print()
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        exit(1)

    if test_ollama_connection(ollama_host, ollama_model):
        print("\nTesting classification...")
        test_classification(ollama_host, ollama_model)

    print("\nSetup verification complete!")
    print("\nIf all tests passed, you can run the main script with: python script.py")
    print("If any tests failed, please:")
    print("1. Make sure the ollama container is running: docker-compose up -d ollama")
    print(f"2. Wait for the model to download: curl {ollama_host}/api/tags")
    print("3. Check container logs: docker-compose logs ollama")
