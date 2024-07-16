import os
import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = "-1002170013697"  # Replace with your actual private channel ID
CHANNEL_INVITE_LINK = "https://t.me/+dUXsdWu9dlk4ZTk9"  # Replace with your actual invitation link
bot = Bot(TOKEN)

# Dummy storage for demonstration (replace with actual persistent storage solution)
user_membership_status = {}

def welcome(update: Update, context) -> None:
    user_id = update.message.from_user.id
    print(f"[DEBUG] User ID: {user_id}")
    if user_membership_status.get(user_id) is None or not user_membership_status[user_id]:
        if user_in_channel(user_id):
            user_membership_status[user_id] = True
            print(f"[DEBUG] User {user_id} joined the channel and is now verified.")
            start_bot_functions(update, context)
        else:
            user_membership_status[user_id] = False
            print(f"[DEBUG] User {user_id} did not join the channel.")
            update.message.reply_text(f"Please join our channel to use this bot: {CHANNEL_INVITE_LINK}")
    else:
        print(f"[DEBUG] User {user_id} is already verified.")
        start_bot_functions(update, context)

def user_in_channel(user_id):
    url = f"https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id={CHANNEL_ID}&user_id={user_id}"
    print(f"[DEBUG] Checking membership status for user {user_id} with URL: {url}")
    try:
        response = requests.get(url).json()
        print(f"[DEBUG] Response from Telegram API: {response}")
        if response.get('ok') and 'result' in response:
            status = response['result']['status']
            print(f"[DEBUG] User {user_id} status in channel: {status}")
            return status in ['member', 'administrator', 'creator']
        else:
            print(f"[ERROR] Invalid response structure or 'ok' field is False.")
            return False
    except Exception as e:
        print(f"[ERROR] Exception while checking user channel status: {e}")
        return False

def start_bot_functions(update: Update, context) -> None:
    update.message.reply_text(f"Hello {update.message.from_user.first_name}, Welcome to Movie dekhee.\n"
                              f"🔥 Download Your Favourite Movies For 💯 Free And 🍿 Enjoy it.")
    update.message.reply_text("👇 Enter Movie Name 👇")

def setup_dispatcher():
    dispatcher = Dispatcher(bot, None, use_context=True)
    dispatcher.add_handler(CommandHandler('start', welcome))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, find_movie))
    return dispatcher

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    setup_dispatcher().process_update(update)
    return 'ok'

if __name__ == '__main__':
    app.run(debug=True)
