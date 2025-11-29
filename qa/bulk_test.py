import requests
import json
import time
from datetime import datetime

# Configuration
API_URL = "http://localhost:5000/api/verify"
REPORT_FILE = "qa/bulk_test_report.md"

# Dataset: 50 Fake, 50 Real
DATASET = [
    # --- FAKE CLAIMS (50) ---
    {"claim": "Drinking bleach cures COVID-19", "label": "fake"},
    {"claim": "The Earth is flat and Antarctica is an ice wall.", "label": "fake"},
    {"claim": "Bill Gates is putting microchips in COVID-19 vaccines.", "label": "fake"},
    {"claim": "5G networks cause the spread of coronavirus.", "label": "fake"},
    {"claim": "Lemon juice in the nose kills the COVID-19 virus.", "label": "fake"},
    {"claim": "The moon landing was staged in a Hollywood studio.", "label": "fake"},
    {"claim": "Vaccines cause autism.", "label": "fake"},
    {"claim": "Eating garlic prevents COVID-19 infection.", "label": "fake"},
    {"claim": "The Great Wall of China is visible from the moon with the naked eye.", "label": "fake"},
    {"claim": "Humans use only 10% of their brains.", "label": "fake"},
    {"claim": "Goldfish have a three-second memory.", "label": "fake"},
    {"claim": "Bulls are angered by the color red.", "label": "fake"},
    {"claim": "Napoleon Bonaparte was extremely short.", "label": "fake"},
    {"claim": "Vikings wore horned helmets.", "label": "fake"},
    {"claim": "Sugar causes hyperactivity in children.", "label": "fake"},
    {"claim": "Cracking your knuckles causes arthritis.", "label": "fake"},
    {"claim": "Shaving hair makes it grow back thicker and darker.", "label": "fake"},
    {"claim": "Bats are blind.", "label": "fake"},
    {"claim": "Alcohol warms your body temperature.", "label": "fake"},
    {"claim": "You lose most of your body heat through your head.", "label": "fake"},
    {"claim": "Different parts of the tongue taste different flavors.", "label": "fake"},
    {"claim": "Chameleons change color to blend in with their surroundings.", "label": "fake"},
    {"claim": "Deoxygenated blood is blue.", "label": "fake"},
    {"claim": "Camels store water in their humps.", "label": "fake"},
    {"claim": "Lightning never strikes the same place twice.", "label": "fake"},
    {"claim": "Penny dropped from Empire State Building can kill a person.", "label": "fake"},
    {"claim": "Touching a toad gives you warts.", "label": "fake"},
    {"claim": "Bananas grow on trees.", "label": "fake"},
    {"claim": "Dogs sweat through their tongues.", "label": "fake"},
    {"claim": "Ostriches bury their heads in the sand when scared.", "label": "fake"},
    {"claim": "Einstein failed math in school.", "label": "fake"},
    {"claim": "Twinkies have an infinite shelf life.", "label": "fake"},
    {"claim": "Microwaving food removes its nutrients.", "label": "fake"},
    {"claim": "Gum takes 7 years to digest.", "label": "fake"},
    {"claim": "Swimming after eating causes cramps.", "label": "fake"},
    {"claim": "Coffee stunts your growth.", "label": "fake"},
    {"claim": "Reading in the dark damages your eyes.", "label": "fake"},
    {"claim": "Hair and nails continue to grow after death.", "label": "fake"},
    {"claim": "Birds abandon babies if humans touch them.", "label": "fake"},
    {"claim": "Waking a sleepwalker is dangerous.", "label": "fake"},
    {"claim": "Salty water boils faster.", "label": "fake"},
    {"claim": "Glass is a slow-moving liquid.", "label": "fake"},
    {"claim": "The government is spraying chemtrails to control the weather.", "label": "fake"},
    {"claim": "Barack Obama was not born in the United States.", "label": "fake"},
    {"claim": "Climate change is a hoax invented by China.", "label": "fake"},
    {"claim": "The 2020 US election was stolen via voting machines.", "label": "fake"},
    {"claim": "COVID-19 vaccines contain magnetic particles.", "label": "fake"},
    {"claim": "Wearing a mask causes CO2 poisoning.", "label": "fake"},
    {"claim": "Ivermectin is a proven cure for COVID-19.", "label": "fake"},
    {"claim": "The Loch Ness Monster is a real prehistoric creature.", "label": "fake"},

    # --- REAL CLAIMS (50) ---
    {"claim": "The Earth revolves around the Sun.", "label": "real"},
    {"claim": "Water boils at 100 degrees Celsius at standard atmospheric pressure.", "label": "real"},
    {"claim": "COVID-19 is caused by the SARS-CoV-2 virus.", "label": "real"},
    {"claim": "The 2020 Summer Olympics were held in Tokyo in 2021.", "label": "real"},
    {"claim": "Joe Biden is the 46th President of the United States.", "label": "real"},
    {"claim": "The capital of France is Paris.", "label": "real"},
    {"claim": "Photosynthesis is the process by which plants make food.", "label": "real"},
    {"claim": "The human heart has four chambers.", "label": "real"},
    {"claim": "Mount Everest is the highest mountain on Earth above sea level.", "label": "real"},
    {"claim": "The Pacific Ocean is the largest ocean on Earth.", "label": "real"},
    {"claim": "Neil Armstrong was the first person to walk on the moon.", "label": "real"},
    {"claim": "The Amazon Rainforest is located in South America.", "label": "real"},
    {"claim": "Diamond is the hardest natural substance.", "label": "real"},
    {"claim": "Honey never spoils if stored correctly.", "label": "real"},
    {"claim": "The speed of light is approximately 299,792 kilometers per second.", "label": "real"},
    {"claim": "Humans have 23 pairs of chromosomes.", "label": "real"},
    {"claim": "The chemical symbol for gold is Au.", "label": "real"},
    {"claim": "The Titanic sank in 1912.", "label": "real"},
    {"claim": "Shakespeare wrote Romeo and Juliet.", "label": "real"},
    {"claim": "The Great Barrier Reef is located off the coast of Australia.", "label": "real"},
    {"claim": "Penicillin was discovered by Alexander Fleming.", "label": "real"},
    {"claim": "The Statue of Liberty was a gift from France to the USA.", "label": "real"},
    {"claim": "DNA stands for Deoxyribonucleic Acid.", "label": "real"},
    {"claim": "The currency of the United Kingdom is the Pound Sterling.", "label": "real"},
    {"claim": "The Nile is one of the longest rivers in the world.", "label": "real"},
    {"claim": "Spiders have eight legs.", "label": "real"},
    {"claim": "The boiling point of water is 212 degrees Fahrenheit.", "label": "real"},
    {"claim": "Plants absorb carbon dioxide and release oxygen.", "label": "real"},
    {"claim": "The human body is composed of about 60% water.", "label": "real"},
    {"claim": "Gravity keeps us on the ground.", "label": "real"},
    {"claim": "The sun is a star.", "label": "real"},
    {"claim": "Sharks are fish.", "label": "real"},
    {"claim": "Whales are mammals.", "label": "real"},
    {"claim": "The Eiffel Tower is in Paris.", "label": "real"},
    {"claim": "World War II ended in 1945.", "label": "real"},
    {"claim": "The internet was developed from ARPANET.", "label": "real"},
    {"claim": "Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne.", "label": "real"},
    {"claim": "Microsoft was founded by Bill Gates and Paul Allen.", "label": "real"},
    {"claim": "The Mona Lisa was painted by Leonardo da Vinci.", "label": "real"},
    {"claim": "Bees produce honey.", "label": "real"},
    {"claim": "Antarctica is the coldest continent.", "label": "real"},
    {"claim": "The Sahara is the largest hot desert.", "label": "real"},
    {"claim": "Mount Fuji is in Japan.", "label": "real"},
    {"claim": "Canada is the second largest country by land area.", "label": "real"},
    {"claim": "Russia is the largest country by land area.", "label": "real"},
    {"claim": "The United Nations headquarters is in New York City.", "label": "real"},
    {"claim": "The Euro is the currency of the Eurozone.", "label": "real"},
    {"claim": "Mars is known as the Red Planet.", "label": "real"},
    {"claim": "Jupiter is the largest planet in our solar system.", "label": "real"},
    {"claim": "Saturn has rings.", "label": "real"}
]

def run_test():
    results = []
    correct_count = 0
    total_count = len(DATASET)
    
    print(f"🚀 Starting Bulk Test with {total_count} claims...")
    
    for i, item in enumerate(DATASET):
        claim = item['claim']
        expected_label = item['label']
        
        try:
            response = requests.post(API_URL, json={"claim": claim, "source": "Bulk Test"})
            if response.status_code == 200:
                data = response.json()
                score = data.get('score', 0.5)
                status = data.get('status', 'unknown')
                
                # Determine prediction based on score
                # Score < 0.4 => Fake/Debunked
                # Score >= 0.7 => Real/Verified
                # 0.4 <= Score < 0.7 => Uncertain/Investigating
                
                prediction = "uncertain"
                if score < 0.4:
                    prediction = "fake"
                elif score >= 0.6: # Slightly adjusting threshold for binary classification test
                    prediction = "real"
                
                # Check correctness
                is_correct = False
                if expected_label == "fake" and prediction == "fake":
                    is_correct = True
                elif expected_label == "real" and prediction == "real":
                    is_correct = True
                elif prediction == "uncertain":
                    # Treat uncertain as incorrect for strict testing, or separate category
                    is_correct = False 
                
                if is_correct:
                    correct_count += 1
                
                result = {
                    "id": i + 1,
                    "claim": claim,
                    "expected": expected_label,
                    "predicted": prediction,
                    "score": score,
                    "status": status,
                    "correct": is_correct
                }
                results.append(result)
                
                symbol = "✅" if is_correct else "❌"
                print(f"[{i+1}/{total_count}] {symbol} {expected_label.upper()} vs {prediction.upper()} (Score: {score}) - {claim[:50]}...")
                
            else:
                print(f"[{i+1}/{total_count}] ⚠️ API Error: {response.status_code}")
                results.append({
                    "id": i + 1,
                    "claim": claim,
                    "expected": expected_label,
                    "predicted": "error",
                    "score": 0,
                    "status": "error",
                    "correct": False
                })
                
        except Exception as e:
            print(f"[{i+1}/{total_count}] ⚠️ Exception: {e}")
            results.append({
                "id": i + 1,
                "claim": claim,
                "expected": expected_label,
                "predicted": "error",
                "score": 0,
                "status": "error",
                "correct": False
            })
            
        # Small delay to avoid rate limiting if any
        time.sleep(0.5)

    # Calculate Metrics
    accuracy = (correct_count / total_count) * 100
    
    # Generate Report
    generate_report(results, accuracy)
    
    print(f"\n✨ Test Complete!")
    print(f"Accuracy: {accuracy:.2f}% ({correct_count}/{total_count})")
    print(f"Report saved to: {REPORT_FILE}")

def generate_report(results, accuracy):
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(f"# 📊 RapidVerify Bulk Test Report\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Claims:** {len(results)}\n")
        f.write(f"**Accuracy:** {accuracy:.2f}%\n\n")
        
        f.write("## 📈 Summary Metrics\n")
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")
        f.write(f"| Total Test Cases | {len(results)} |\n")
        f.write(f"| Passed | {sum(1 for r in results if r['correct'])} |\n")
        f.write(f"| Failed | {sum(1 for r in results if not r['correct'])} |\n")
        
        f.write("\n## 📝 Detailed Results\n\n")
        f.write("| ID | Claim | Expected | Predicted | Score | Status | Result |\n")
        f.write("|----|-------|----------|-----------|-------|--------|--------|\n")
        
        for r in results:
            icon = "✅" if r['correct'] else "❌"
            # Escape pipes in claim
            claim_clean = r['claim'].replace("|", "\|")
            f.write(f"| {r['id']} | {claim_clean} | {r['expected']} | {r['predicted']} | {r['score']} | {r['status']} | {icon} |\n")

if __name__ == "__main__":
    run_test()
