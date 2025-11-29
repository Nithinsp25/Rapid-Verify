import os
import sys
from datetime import datetime, timedelta
import time

# Add api directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from blockchain_service import blockchain_service

def seed_data():
    print("🌱 Seeding dashboard with real-world examples...")
    
    examples = [
        {
            "text": "NASA confirms Voyager 1 is sending readable data again after months of silence.",
            "score": 0.95,
            "status": "verified",
            "verdict": "Confirmed by NASA official statement. Engineers successfully fixed the FDS memory issue.",
            "time_offset": 120  # seconds ago
        },
        {
            "text": "Viral message claims lemon juice and hot water can cure cancer immediately.",
            "score": 0.10,
            "status": "debunked",
            "verdict": "FALSE. No scientific evidence supports this. Cancer requires medical treatment.",
            "time_offset": 300
        },
        {
            "text": "RBI announces withdrawal of Rs 2000 notes from circulation, legal tender status continues.",
            "score": 0.98,
            "status": "verified",
            "verdict": "True. RBI press release confirms withdrawal but notes remain legal tender.",
            "time_offset": 600
        },
        {
            "text": "Government offering free iPhone 15 to all students who pass 10th grade.",
            "score": 0.05,
            "status": "debunked",
            "verdict": "SCAM. No such official scheme exists. Phishing link detected.",
            "time_offset": 900
        },
        {
            "text": "New AI regulation bill proposed in EU parliament to categorize AI risk levels.",
            "score": 0.85,
            "status": "verified",
            "verdict": "Accurate. The EU AI Act proposes risk-based categorization.",
            "time_offset": 1500
        },
        {
            "text": "Video shows alien spacecraft landing in Las Vegas backyard.",
            "score": 0.15,
            "status": "debunked",
            "verdict": "CGI / VFX. Video analysis confirms digital manipulation. Source is a VFX artist channel.",
            "time_offset": 2000
        },
        {
            "text": "WHO declares new pandemic 'Disease X' has started spreading.",
            "score": 0.20,
            "status": "investigating",
            "verdict": "Misleading. 'Disease X' is a hypothetical placeholder for planning, not a current outbreak.",
            "time_offset": 3600
        }
    ]
    
    count = 0
    for ex in examples:
        # Adjust timestamp to look recent
        # We can't easily fake the internal timestamp in record_verification without modifying the service,
        # but the dashboard uses the record timestamp.
        # For simplicity, we'll just record them now.
        
        print(f"Processing: {ex['text'][:50]}...")
        blockchain_service.record_verification(
            claim_text=ex['text'],
            verification_score=ex['score'],
            status=ex['status'],
            verdict=ex['verdict']
        )
        count += 1
        time.sleep(0.1) # Small delay
        
    print(f"✅ Successfully seeded {count} records!")
    print("🚀 Restart the backend to see them in the dashboard.")

if __name__ == "__main__":
    seed_data()
