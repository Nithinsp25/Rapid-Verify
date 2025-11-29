import requests
import time

# Configuration
WEBHOOK_URL = "http://localhost:5000/whatsapp/webhook"

def simulate_message(body, from_number="whatsapp:+1234567890"):
    print(f"\n📱 Sending message: '{body}'")
    
    payload = {
        'Body': body,
        'From': from_number,
        'NumMedia': '0'
    }
    
    try:
        response = requests.post(WEBHOOK_URL, data=payload)
        if response.status_code == 200:
            print("✅ Response received:")
            print("-" * 40)
            print(response.text)
            print("-" * 40)
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")

def run_tests():
    print("🚀 Starting WhatsApp Bot Simulation...")
    
    # Test 1: Greeting
    simulate_message("")
    
    # Test 2: Fake News Text
    simulate_message("Drinking bleach cures COVID-19")
    
    # Test 3: Real News Text (using the Google Search logic)
    simulate_message("The 2024 Olympics were held in Paris")
    
    # Test 4: URL Verification
    simulate_message("Check this: https://www.bbc.com/news/world-europe-68000000")

if __name__ == "__main__":
    run_tests()
