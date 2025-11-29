"""
RapidVerify Telegram Bot
Runs in polling mode (no ngrok needed)
"""
import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Global verifier instance
verifier = None

def get_verifier():
    """Lazy load verifier"""
    global verifier
    if verifier is None:
        try:
            from news_scraper import NewsVerifier
            verifier = NewsVerifier()
            print("✅ Telegram Bot: Verifier loaded")
        except ImportError:
            print("❌ Telegram Bot: Failed to load verifier")
    return verifier

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "👋 *Welcome to RapidVerify Bot!*\n\n"
        "I can verify news and claims instantly.\n\n"
        "📝 *Send me text* to check a claim\n"
        "🔗 *Send me a link* to verify an article\n"
        "🖼️ *Send me an image* (coming soon)\n\n"
        "_Just forward any suspicious message to me!_",
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(
        "ℹ️ *How to use:*\n\n"
        "1. Forward a message from another chat\n"
        "2. Paste a link to a news article\n"
        "3. Type a claim directly\n\n"
        "I'll analyze it using AI and fact-checking sources.",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages"""
    user_text = update.message.text
    
    if not user_text:
        return

    # Notify user we are working
    status_msg = await update.message.reply_text("🔍 Verifying...")
    
    try:
        v = get_verifier()
        if not v:
            await status_msg.edit_text("⚠️ Error: Verifier service unavailable.")
            return

        # Check if it's a URL
        if 'http' in user_text:
            # Simple URL extraction
            url = next((word for word in user_text.split() if word.startswith('http')), None)
            if url:
                result = v.verify_url(url)
                response = format_response(result, 'url')
            else:
                result = v.verify_text(user_text)
                response = format_response(result, 'text')
        else:
            result = v.verify_text(user_text)
            response = format_response(result, 'text')
            
        await status_msg.edit_text(response, parse_mode='Markdown')
        
    except Exception as e:
        print(f"❌ Telegram Error: {e}")
        await status_msg.edit_text("❌ An error occurred during verification.")

def format_response(result: dict, type: str) -> str:
    """Format verification result for Telegram"""
    verification = result.get('verification', {})
    score = verification.get('score', 0.5)
    status = verification.get('status', 'investigating')
    
    if status == 'debunked':
        icon = "🚫"
        label = "LIKELY FAKE"
    elif status == 'verified':
        icon = "✅"
        label = "LIKELY AUTHENTIC"
    else:
        icon = "⚠️"
        label = "NEEDS VERIFICATION"
        
    response = f"{icon} *{label}*\n"
    response += f"📊 Score: *{int(score * 100)}%*\n\n"
    
    if verification.get('verdict'):
        response += f"📋 *Verdict:*\n{verification['verdict']}\n\n"
        
    # Sources
    cross_refs = result.get('cross_references', [])
    if cross_refs:
        response += "📚 *Sources:*\n"
        for ref in cross_refs[:3]:
            source = ref.get('source', 'Unknown')
            response += f"• {source}\n"
            
    return response

def run_telegram_bot():
    """Entry point to run the bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("⚠️ Telegram Token not found. Bot will not start.")
        return

    # Create a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Create App
    application = ApplicationBuilder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    # Run
    print("🚀 Starting Telegram Bot (Polling Mode)...")
    application.run_polling(stop_signals=None)

if __name__ == '__main__':
    run_telegram_bot()
