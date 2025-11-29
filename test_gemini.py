import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

if not GOOGLE_API_KEY:
    print("❌ GOOGLE_API_KEY not found in environment")
    exit(1)

print(f"✅ Found API Key: {GOOGLE_API_KEY[:5]}...")

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # List available models
    print("\nAvailable models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            
    print("\nTesting gemini-1.5-flash...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello, are you working?")
    print(f"Response: {response.text}")
    print("✅ gemini-1.5-flash is working")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
