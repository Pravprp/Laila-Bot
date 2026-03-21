import time
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai
import os

# ENV VARIABLES
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Active chats memory
active_chats = {}

ACTIVE_DURATION = 300  # 5 minutes

# Personality prompt
SYSTEM_PROMPT = """
You are Laila 💕, a charming, playful, flirty girlfriend.

Rules:
- Always flirt in a cute and romantic way
- Keep responses short (1-2 sentences max)
- Be funny, teasing, and emotionally engaging
- Talk like a real human girlfriend
- NEVER say you are an AI or bot
- Adapt to user's language automatically
- Use emojis sometimes ❤️😉🔥
"""

def is_active(chat_id):
    if chat_id in active_chats:
        return time.time() < active_chats[chat_id]
    return False

def activate(chat_id):
    active_chats[chat_id] = time.time() + ACTIVE_DURATION

async def generate_reply(user_text):
    try:
        response = model.generate_content(
            SYSTEM_PROMPT + "\nUser: " + user_text
        )
        return response.text.strip()
    except Exception as e:
        return "Hmm... you're making me shy now 😳"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_id = message.chat_id
    text = message.text.lower()

    # Check if message mentions "laila"
    if "laila" in text:
        activate(chat_id)

    # Check if replying to bot
    if message.reply_to_message:
        if message.reply_to_message.from_user.id == context.bot.id:
            activate(chat_id)

    # If not active → ignore
    if not is_active(chat_id):
        return

    # Generate reply
    reply = await generate_reply(message.text)

    await message.reply_text(reply)

async def keep_alive():
    while True:
        await asyncio.sleep(600)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Laila is running... 💕")

    app.run_polling()

if __name__ == "__main__":
    main()