"""
RapidVerify WhatsApp Bot Integration (AiSensy)
Receives messages/images/links -> Verifies -> Sends results back to user
Uses AiSensy WhatsApp API
"""
import os
import re
import json
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv

load_dotenv()

# Create Blueprint for WhatsApp routes
whatsapp_bp = Blueprint('whatsapp', __name__)

# AiSensy Configuration
AISENSY_API_KEY = os.getenv('AISENSY_API_KEY')
AISENSY_BASE_URL = "https://backend.aisensy.com/v1"

# Import verifier (will be available after app starts)
verifier = None

def get_verifier():
    """Lazy load verifier to avoid circular imports"""
    global verifier
    if verifier is None:
        try:
            from news_scraper import NewsVerifier
            verifier = NewsVerifier()
        except ImportError:
            pass
    return verifier


def extract_urls(text: str) -> list:
    """Extract URLs from text"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)


def send_aisensy_message(to_number: str, message_text: str):
    """Send WhatsApp message via AiSensy"""
    if not AISENSY_API_KEY:
        print("⚠️ AiSensy API Key missing")
        return False

    try:
        # AiSensy API Endpoint for sending text messages
        # Note: Using the standard 'send' endpoint. 
        # If using templates, the payload structure differs.
        # For simple text replies to user initiated conversations (24h window), 
        # we can often use the direct message API or similar.
        
        # Assuming we are replying to a user, we use the /message/send endpoint or similar.
        # Since AiSensy is a BSP wrapper, we'll use a standard structure.
        
        url = f"{AISENSY_BASE_URL}/message/send"
        
        payload = {
            "apiKey": AISENSY_API_KEY,
            "destination": to_number,
            "type": "text",
            "message": message_text
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Message sent to {to_number}")
            return True
        else:
            print(f"❌ AiSensy Send Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ AiSensy Connection Error: {e}")
        return False


def format_whatsapp_response(result: dict, content_type: str) -> str:
    """Format verification result for WhatsApp"""
    
    response = "🛡️ *RapidVerify Analysis*\n"
    response += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Verification result
    verification = result.get('verification', {})
    score = verification.get('score', 0.5)
    status = verification.get('status', 'investigating')
    
    # Status emoji and text
    if status == 'debunked':
        status_emoji = "🚫"
        status_text = "LIKELY FAKE"
    elif status == 'verified':
        status_emoji = "✅"
        status_text = "LIKELY AUTHENTIC"
    else:
        status_emoji = "⚠️"
        status_text = "NEEDS VERIFICATION"
    
    response += f"{status_emoji} *{status_text}*\n"
    response += f"📊 Authenticity Score: *{int(score * 100)}%*\n\n"
    
    # Verdict
    verdict = verification.get('verdict', '')
    if verdict:
        response += f"📋 *Verdict:*\n{verdict}\n\n"
    
    # For URL verification, show article info
    if content_type == 'url' and result.get('article'):
        article = result['article']
        response += "📰 *Article Details:*\n"
        if article.get('title'):
            response += f"Title: {article['title'][:100]}...\n" if len(article.get('title', '')) > 100 else f"Title: {article['title']}\n"
        if article.get('source'):
            response += f"Source: {article['source']}\n"
        
        # Source credibility
        cred = result.get('source_credibility', {})
        if cred.get('is_known_source'):
            response += f"Source Rating: {'⭐' * (4 if cred['tier'] == 'tier1' else 3 if cred['tier'] == 'tier2' else 2)}\n"
        response += "\n"
    
    # Warnings
    warnings = result.get('warnings', [])
    if warnings:
        response += "⚠️ *Warnings:*\n"
        for warning in warnings[:3]:
            response += f"• {warning}\n"
        response += "\n"
    
    # Fact-check sources
    fact_checks = result.get('fact_checks', [])
    if fact_checks:
        response += "🔍 *Verification Sources:*\n"
        for fc in fact_checks[:3]:
            if fc.get('type') == 'manual_search':
                response += f"• {fc['source']}: {fc.get('search_url', '')[:50]}...\n"
            elif fc.get('rating'):
                response += f"• {fc['source']}: {fc['rating']}\n"
            else:
                response += f"• {fc['source']}\n"
        response += "\n"
    
    # Cross-references (including Google Search)
    cross_refs = result.get('cross_references', [])
    if cross_refs:
        response += "📚 *Check These Sources:*\n"
        count = 0
        for ref in cross_refs:
            if ref.get('type') == 'google_search':
                response += f"• {ref['source']}\n"
                count += 1
            elif ref.get('type') == 'search' and ref.get('source') in ['Google News', 'Reuters']:
                response += f"• {ref['source']}\n"
                count += 1
            
            if count >= 3:  # Show top 3 sources
                break
        response += "\n"
    
    # Recommendation
    response += "━━━━━━━━━━━━━━━━━━━━━\n"
    if score < 0.4:
        response += "🚫 *DO NOT SHARE* this content!\n"
        response += "It shows strong signs of misinformation.\n"
    elif score < 0.7:
        response += "⚠️ *VERIFY BEFORE SHARING*\n"
        response += "Check official sources first.\n"
    else:
        response += "✅ Content appears credible.\n"
        response += "But always verify important news.\n"
    
    response += "\n_Powered by RapidVerify AI_\n"
    
    return response


def basic_text_verification(text: str) -> str:
    """Basic text verification when full verifier is not available"""
    
    text_lower = text.lower()
    warnings = []
    score = 0.6
    
    # Check for fake patterns
    fake_patterns = [
        ('shocking', 'Sensationalist language'),
        ('urgent', 'Creates urgency'),
        ('forward to everyone', 'Viral manipulation'),
        ('share before deleted', 'Fear tactics'),
        ('free money', 'Potential scam'),
        ('lottery winner', 'Known scam pattern'),
        ('government scheme', 'Verify with PIB'),
        ('miracle cure', 'Health misinformation'),
        ('they dont want you to know', 'Conspiracy pattern'),
    ]
    
    for pattern, warning in fake_patterns:
        if pattern in text_lower:
            score -= 0.15
            warnings.append(warning)
    
    score = max(0.1, min(0.9, score))
    
    # Build response
    response = "🛡️ *RapidVerify Analysis*\n"
    response += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    if score < 0.4:
        response += "🚫 *LIKELY FAKE*\n"
    elif score < 0.7:
        response += "⚠️ *VERIFY BEFORE SHARING*\n"
    else:
        response += "✅ *APPEARS CREDIBLE*\n"
    
    response += f"📊 Score: *{int(score * 100)}%*\n\n"
    
    if warnings:
        response += "⚠️ *Red Flags Found:*\n"
        for w in warnings[:5]:
            response += f"• {w}\n"
        response += "\n"
    
    response += "🔍 *Verify with:*\n"
    response += "• pib.gov.in (Govt)\n"
    response += "• boomlive.in\n"
    response += "• altnews.in\n\n"
    
    if score < 0.5:
        response += "🚫 *DO NOT FORWARD!*\n"
    else:
        response += "✅ Verify before sharing\n"
    
    response += "\n_Powered by RapidVerify_"
    
    return response


@whatsapp_bp.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """
    Handle incoming WhatsApp messages from AiSensy
    """
    try:
        data = request.get_json()
        print(f"📨 AiSensy Webhook: {json.dumps(data, indent=2)}")
        
        # AiSensy Payload Structure (Simplified)
        # {
        #   "sender": "919876543210",
        #   "message": "Hello",
        #   "type": "text",
        #   ...
        # }
        
        # Extract details
        # Note: Adjust these keys based on exact AiSensy webhook payload
        sender = data.get('sender') or data.get('mobile')
        incoming_msg = data.get('message', '').strip()
        msg_type = data.get('type', 'text')
        
        if not sender:
            return jsonify({'status': 'ignored', 'reason': 'no_sender'}), 200
            
        # Get verifier
        v = get_verifier()
        
        response_text = ""
        
        # Handle empty/greeting
        if not incoming_msg and msg_type == 'text':
             response_text = (
                "👋 Welcome to *RapidVerify Bot*!\n\n"
                "Send me:\n"
                "📝 Any suspicious *text/message*\n"
                "🔗 A *news article link*\n"
                "I'll verify it instantly!"
            )
        
        # Check for URLs
        elif msg_type == 'text':
            urls = extract_urls(incoming_msg)
            if urls:
                print(f"🔗 Verifying URL: {urls[0]}")
                if v:
                    result = v.verify_url(urls[0])
                    response_text = format_whatsapp_response(result, 'url')
                else:
                    response_text = "⚠️ Verifier initializing..."
            else:
                print(f"📝 Verifying text: {incoming_msg[:50]}...")
                if v:
                    result = v.verify_text(incoming_msg)
                    response_text = format_whatsapp_response(result, 'text')
                else:
                    response_text = basic_text_verification(incoming_msg)
        
        elif msg_type == 'image':
             response_text = "⚠️ Image verification via WhatsApp is coming soon! Please use our website."
        
        # Send reply
        if response_text:
            send_aisensy_message(sender, response_text)
            
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        print(f"❌ Webhook Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@whatsapp_bp.route('/status', methods=['GET'])
def whatsapp_status():
    """Check WhatsApp bot status"""
    return jsonify({
        'status': 'active',
        'provider': 'AiSensy',
        'api_key_configured': bool(AISENSY_API_KEY),
        'verifier_loaded': get_verifier() is not None,
        'webhook_url': '/whatsapp/webhook'
    })
