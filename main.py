import os
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# Load env variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONNIFY_API_KEY = os.getenv("MONNIFY_API_KEY")
MONNIFY_SECRET_KEY = os.getenv("MONNIFY_SECRET_KEY")
MONNIFY_CONTRACT_CODE = os.getenv("MONNIFY_CONTRACT_CODE")
WEBHOOK_ENDPOINT = os.getenv("WEBHOOK_ENDPOINT")
PORT = int(os.getenv("PORT", 5000))

# Initialize Flask & Bot
app = Flask(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=0, use_context=True)

# In-memory user subscription storage (replace with DB for production)
user_subscriptions = {}

# ===== Subscription Check =====
def check_subscription(user_id):
    if user_id in user_subscriptions:
        if user_subscriptions[user_id]["active"]:
            return True
    return False

# ===== Telegram Command Handlers =====
def start(update: Update, context):
    update.message.reply_text(
        "Welcome to Sarah AI! Use /ask <your question> to ask me anything about forex.\n"
        "To subscribe, use /subscribe."
    )

def subscribe(update: Update, context):
    user_id = update.message.chat.id
    # Simple subscription record
    user_subscriptions[user_id] = {"active": False}
    payment_link = "https://paylink.monnify.com/Triadpips"
    update.message.reply_text(
        f"To activate your subscription, pay ₦20,000 here:\n{payment_link}\n"
        "After payment, your subscription will be activated."
    )

def ask(update: Update, context):
    user_id = update.message.chat.id
    if not check_subscription(user_id):
        update.message.reply_text("You need an active subscription. Use /subscribe.")
        return

    question = " ".join(context.args)
    if not question:
        update.message.reply_text("Please ask a question after /ask.")
        return

    try:
        # Simulate Sarah AI response (replace with actual AI integration)
        response = f"SARAH BOT RESPONSE: You asked '{question}'"
        update.message.reply_text(response)
    except Exception as e:
        update.message.reply_text(f"Error processing your question: {str(e)}")

# ===== Handler Registration =====
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("subscribe", subscribe))
dispatcher.add_handler(CommandHandler("ask", ask))

# ===== Flask Webhook Endpoint =====
@app.route(f"/{WEBHOOK_ENDPOINT}", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
    except Exception as e:
        print(f"Webhook error: {e}")
    return "ok"

# ===== Run Flask App =====
if __name__ == "__main__":
    print(f"Bot running on port {PORT}")
    app.run(host="0.0.0.0", port=PORT)
