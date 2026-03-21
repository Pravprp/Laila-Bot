import time
import asyncio
import os
import threading

from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# =========================
# ENV VARIABLES
# =========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# =========================
# GEMINI SETUP
# =========================
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# =========================
# FLASK (KEEP ALIVE)
# =========================
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Laila is alive 💕"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

# =========================
# BOT MEMORY
# =========================
active_chats = {}
ACTIVE_DURATION = 300  # 5 minutes

SYSTEM_PROMPT = """
You are Laila 💕, a charming, flirty girlfriend.

Rules:
- Always flirt playfully
- Keep replies short (1-2 sentences)
- Be teasing, romantic, funny
- Talk like a real human
- NEVER say you are an AI or bot
- Reply in the same language as the user
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
        return response.text if response.text else "Say that again, baby 😏"
    except Exception as e:
        print("Gemini ERROR:", e)   # 👈 ADD THIS
        return "You’re making me blush now 😳"

# =========================
# MESSAGE HANDLER
# =========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_id = message.chat_id

    if not message.text:
        return

    text = message.text.lower()

    # Trigger: name "laila"
    if "laila" in text:
        activate(chat_id)

    # Trigger: reply to bot
    if message.reply_to_message:
        if message.reply_to_message.from_user.id == context.bot.id:
            activate(chat_id)

    # If inactive → ignore
    if not is_active(chat_id):
        return

    reply = await generate_reply(message.text)
    await message.reply_text(reply)

# =========================
# MAIN
# =========================
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Laila is running 💕")
    app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    main()
