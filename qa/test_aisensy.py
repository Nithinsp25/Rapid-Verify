import requests
import json
import time

# Configuration
WEBHOOK_URL = "http://localhost:5000/whatsapp/webhook"

def simulate_message(message_text, sender="919876543210", msg_type="text"):
    print(f"\n📱 Sending AiSensy message: '{message_text}'")
    
    payload = {
        "sender": sender,
        "message": message_text,
        "type": msg_type
    }
    
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            print("✅ Webhook accepted (200 OK)")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")

def run_tests():
    print("🚀 Starting AiSensy Bot Simulation...")
    print("Note: Since we don't have a valid API Key, the 'Send' part will fail/log error,")
    print("but we can verify the webhook processing logic.")
    
    # Test 1: Greeting
    simulate_message("")
    
    # Test 2: Fake News Text
    simulate_message("Drinking bleach cures COVID-19")
    
    # Test 3: Real News Text
    simulate_message("The 2024 Olympics were held in Paris")
    
    # Test 4: URL Verification
    simulate_message("Check this: https://www.bbc.com/news/world-europe-68000000")

if __name__ == "__main__":
    run_tests()
